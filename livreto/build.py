#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o livreto do Corpflix → livreto/index.html (rota /livreto/).

    python3 livreto/build.py

v2 (17/09/2026) — o livreto é montado em FOLHAS. Cada `<section class="folha">` é exatamente
uma página A4 no PDF (altura fixa, `break-after:page`) e uma seção normal na tela. É isso que
acaba com a página meio vazia da v1: lá o conteúdo corria solto e o Chrome quebrava onde
dava — capa com 2/3 em branco, card cortado no pé, capítulo começando no rodapé.

⚠️ REGRA DE OURO DA FOLHA: o conteúdo de uma folha TEM que caber em 297mm. A folha tem
`overflow:hidden` no print, então conteúdo a mais some calado. Adicionou card? Rode o build +
`build_pdf.sh` e OLHE a página (o CI só mede página em branco, não corte).

Doutrina herdada do livreto do SeuCondomínio (repo denoww/seucondominio, livreto/CLAUDE.md):
  - Selo só onde é verdade. Nunca vender roadmap como pronto → folha "O que não faz".
  - NUNCA editar o HTML gerado. Edita-se `content.py` (95% das mudanças) ou este arquivo.

PEGADINHAS DO PRINT (não mexer sem entender):
  - `@media print` PRECISA forçar `.rev{opacity:1}` — senão o PDF sai EM BRANCO.
  - `print-color-adjust:exact` — senão capa, CTA, fotos e gradiente saem sem cor.
  - `@page{size:A4;margin:0}` + folha de 210×297mm — margem vem do padding da folha.
  - Traço de SVG: `stroke` explícito no <g> (classe utilitária já apagou traço calado).

CORES (contrato da marca — nomes exatos, não invente token novo):
  --roxo #9100FF é a primária: branco sobre ela dá 5,76:1, pode ser botão.
  --roxo-esc #6A00E0 é o hover e TODO texto pequeno colorido (7,81:1).
  --azul #1886FF só existe DENTRO do --grad. Nunca superfície com texto (3,56:1).
  Sem Google Fonts e sem analytics: pilha de sistema, nada de terceiro na página.
"""
import pathlib, importlib.util, datetime, hashlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent
OUT  = REPO / "livreto" / "index.html"

sp = importlib.util.spec_from_file_location("content", str(ROOT / "content.py"))
C = importlib.util.module_from_spec(sp); sp.loader.exec_module(C)

WA = C.WA + C.WA_TXT

# QR da contracapa: SVG gerado por `gera_qr.py` e commitado (o CI não tem a lib qrcode).
# Guard: a URL gravada no SVG tem que ser a atual — QR velho aponta pro número errado.
_qr = (ROOT / "qr_whatsapp.svg").read_text()
_qr_url = re.search(r"<!-- url: (.*?) -->", _qr).group(1)
if _qr_url != C.WA + C.WA_QR_TXT:
    sys.exit("[livreto] qr_whatsapp.svg está VELHO (número ou texto mudou) — rode python3 livreto/gera_qr.py")
QR_SVG = _qr.split("-->", 1)[1].strip()

# Quadro da TV que não existe em disco sai quebrado no PDF e nada reclama.
for _slug, _alt in C.QUADROS.values():
    if not (REPO / "assets" / f"{_slug}.jpg").is_file():
        sys.exit(f"[livreto] assets/{_slug}.jpg não existe")

# --------------------------------------------------------------------- cenas
# Line-art dos storyboards, viewBox 56×44. As chaves casam 1:1 com `content.py > BOARDS`
# e com as cenas dos públicos (espera, refeitorio, elevador).
SCENES = {
 "espera":    '<rect x="15" y="5" width="26" height="15" rx="2"/><path d="M25.5 9.5l6 3-6 3z"/>'
              '<path d="M9 28h9v6H9zM9 34v5M18 34v5"/><path d="M38 28h9v6h-9zM38 34v5M47 34v5"/>'
              '<path d="M24 40h8"/>',
 "refeitorio":'<rect x="16" y="4" width="24" height="14" rx="2"/><path d="M20 9h10M20 13h14"/>'
              '<path d="M8 30h40M13 30v9M43 30v9"/><path d="M20 24h5v6h-5z"/>'
              '<ellipse cx="34" cy="28.5" rx="5" ry="1.5"/>',
 "elevador":  '<rect x="10" y="4" width="36" height="36" rx="2"/><path d="M10 10h36M28 10v30"/>'
              '<path d="M25 8l1.5-1.5L28 8M31 6.5l1.5 1.5L34 6.5"/>'
              '<rect x="15" y="15" width="8" height="13" rx="1"/><circle cx="37" cy="21" r="1.3"/>'
              '<circle cx="37" cy="25.5" r="1.3"/>',
 "pedido":    '<path d="M11 8h34a3 3 0 0 1 3 3v15a3 3 0 0 1-3 3H26l-8 6v-6h-7a3 3 0 0 1-3-3V11a3 3 0 0 1 3-3z"/>'
              '<path d="M15 24l6-7 5 5 4-3 7 5"/><circle cx="36" cy="14" r="2"/>',
 "grade":     '<rect x="8" y="9" width="24" height="24" rx="2"/><path d="M8 16h24M14 6v6M26 6v6"/>'
              '<path d="M13 21h4M20 21h4M13 27h4"/><circle cx="40" cy="30" r="8"/><path d="M40 26v4l3 2"/>',
 "rede":      '<rect x="6" y="7" width="13" height="9" rx="1.5"/><rect x="37" y="7" width="13" height="9" rx="1.5"/>'
              '<rect x="21.5" y="29" width="13" height="9" rx="1.5"/><circle cx="28" cy="18" r="2.5"/>'
              '<path d="M19 12.5l6.8 4.2M37 12.5l-6.8 4.2M28 20.5V29"/>',
 "lua":       '<rect x="8" y="10" width="28" height="18" rx="2"/><path d="M17 33h10M22 28v5"/>'
              '<path d="M44 7a6 6 0 1 0 5.5 8.5A5 5 0 0 1 44 7z"/><path d="M40 24h5l-5 5h5"/>',
 "instala":   '<rect x="6" y="8" width="30" height="19" rx="2"/><path d="M16 32h10M21 27v5"/>'
              '<rect x="40" y="27" width="11" height="6" rx="1.2"/><path d="M36 18c5 0 9.5 3 9.5 9"/>'
              '<circle cx="48.5" cy="30" r=".8"/>',
 "tvtroca":   '<rect x="8" y="6" width="40" height="25" rx="2"/><path d="M22 36h12M28 31v5"/>'
              '<path d="M22 18.5a6 6 0 0 1 10.4-4.1M34 18.5a6 6 0 0 1-10.4 4.1"/>'
              '<path d="M32.6 11.2v3.4h-3.4M23.4 25.8v-3.4h3.4"/>',
 "offline":   '<rect x="5" y="12" width="29" height="19" rx="2"/><path d="M16 17l7 4.5-7 4.5z"/>'
              '<path d="M14 36h11M19.5 31v5"/>'
              '<path d="M41 9.5a4 4 0 0 1 7.6 1.2 3 3 0 0 1-.1 6H40a3.4 3.4 0 0 1 1-7.2z"/>'
              '<path d="M38 6l13 14"/>',
 "pulso":     '<rect x="8" y="6" width="40" height="25" rx="2"/><path d="M22 36h12M28 31v5"/>'
              '<path d="M12 19h8l3-6 4 11 3-8 2 3h12"/>',
 "alerta":    '<path d="M20 30v-9a8 8 0 0 1 16 0v9l3 3H17z"/><path d="M25 36a3 3 0 0 0 6 0"/>'
              '<path d="M12 18a13 13 0 0 1 4.5-7.5M44 18a13 13 0 0 0-4.5-7.5"/>',
 "reinicio":  '<path d="M39.5 17A12.5 12.5 0 1 0 40 26"/><path d="M40 9.5V17h-7.5"/>'
              '<path d="M28 16v7"/><path d="M23.5 18.5a6.5 6.5 0 1 0 9 0"/>',
 "resumo":    '<rect x="15" y="6" width="26" height="32" rx="2"/>'
              '<path d="M19.5 14l1.6 1.6 3-3.2M27 14h9M19.5 22l1.6 1.6 3-3.2M27 22h9"/>'
              '<path d="M20 29.5l3.5 3.5M23.5 29.5L20 33M27 31h9"/>',
}
def scene(n, cls="scene"):
    return (f'<svg class="{cls}" viewBox="0 0 56 44" aria-hidden="true">'
            f'<g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round">{SCENES[n]}</g></svg>')

# ---------------------------------------------------------------- componentes
def folha(fid, conteudo, cls="", label=""):
    return (f'<section class="folha {cls}" id="{fid}" aria-label="{label or fid}">'
            f'<div class="folha-in">{conteudo}</div></section>')

def cabeca(eyebrow, h2, lead="", cls=""):
    return (f'<header class="cabeca rev {cls}"><span class="eyebrow">{eyebrow}</span><h2>{h2}</h2>'
            f'{f"<p class=lead>{lead}</p>" if lead else ""}</header>')

def tag(t):
    return f'<span class="tg">{t}</span>' if t else ''

def cards(items, cols=3, cls=""):
    cs = "".join(f'<article class="fc"><span class="fc-mk"></span><h3>{t}{tag(g)}</h3><p>{d}</p></article>'
                 for t, d, g in items)
    return f'<div class="fgrid cols-{cols} {cls} rev">{cs}</div>'

def board(key):
    cor, titulo, panels = C.BOARDS[key]
    cells = "".join(f'<li class="bp"><span class="bp-n">{i+1}</span><span class="bp-art">{scene(sc)}</span>'
                    f'<b>{h}</b><i>{cap}</i></li>' for i, (sc, h, cap) in enumerate(panels))
    return (f'<figure class="board c-{cor} n-{len(panels)} rev"><figcaption class="board-cap">{titulo}</figcaption>'
            f'<ol class="board-strip">{cells}</ol></figure>')

def quadro(chave, cls=""):
    slug, alt = C.QUADROS[chave]
    return (f'<figure class="quadro {cls}"><img src="/assets/{slug}.jpg" alt="{alt}" width="1440" '
            f'height="872" decoding="async"></figure>')

def lista(items):
    return ('<ul class="check rev">' +
            "".join(f'<li><span class="ck"></span>{t}</li>' for t in items) + '</ul>')

# ---------------------------------------------------------------------- CSS
CSS = """
:root{
  --branco:#fff;--nevoa:#f5f5f7;--tinta:#1d1d1f;--tinta-2:#6e6e73;--claro:#f5f5f7;--claro-2:#a1a1a6;
  --roxo:#9100FF;--roxo-esc:#6A00E0;--roxo-leve:#F3E8FF;
  --azul:#1886FF;--grad:linear-gradient(90deg,#9100FF,#1886FF);
  --noite:#0A0716;--noite-2:#1F0E36;--linha:rgba(0,0,0,.10);--maxw:1080px;
  --sec:var(--roxo-esc);--soft:var(--roxo-leve);--mk:var(--grad);
  --ease:cubic-bezier(.45,0,.55,1);
}
.c-roxo{--sec:#6A00E0;--soft:#F3E8FF;--mk:var(--grad)}
.c-noite{--sec:#1F0E36;--soft:#EEEAF4;--mk:#1F0E36}
*{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--nevoa);color:var(--tinta);
  font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Inter',system-ui,'Segoe UI',Roboto,sans-serif;
  font-size:17px;line-height:1.47;letter-spacing:-.018em;-webkit-font-smoothing:antialiased}
h1,h2,h3{margin:0;font-weight:600;line-height:1.08;letter-spacing:-.015em;text-wrap:balance}
p{margin:0}ul,ol{margin:0;padding:0;list-style:none}
a{color:var(--roxo-esc);text-decoration:none}
img{display:block;max-width:100%;height:auto}
:focus-visible{outline:3px solid var(--roxo);outline-offset:3px;border-radius:6px}
.g{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent}

/* nav (só tela) */
.nav{position:sticky;top:0;z-index:50;height:52px;display:flex;align-items:center;justify-content:space-between;
  padding:0 clamp(16px,4vw,40px);background:rgba(10,7,22,.88);backdrop-filter:saturate(180%) blur(20px);
  -webkit-backdrop-filter:saturate(180%) blur(20px);border-bottom:1px solid rgba(255,255,255,.08)}
.nav .brand img{height:18px;width:auto}
.nav-r{display:flex;align-items:center;gap:clamp(12px,3vw,24px);font-size:13px}
.nav-links{display:inline-flex;gap:clamp(12px,2vw,22px)}
.nav-r a{color:var(--claro);opacity:.85}
.nav-r a:hover{opacity:1;color:#C9A7FF}
.nav-cta{background:var(--roxo);color:#fff!important;opacity:1!important;padding:6px 14px;border-radius:980px;font-weight:500}
@media(max-width:820px){.nav-links{display:none}}

.btn{display:inline-flex;align-items:center;gap:8px;background:var(--roxo);color:#fff;padding:12px 22px;
  border-radius:980px;font-size:17px}
.btn:hover{background:var(--roxo-esc)}
.btn-branco{background:#fff;color:var(--tinta)}
.btn-branco:hover{background:var(--roxo-leve)}

/* ---------- a folha ---------- */
.folha{background:var(--branco);padding:clamp(56px,8vw,96px) clamp(16px,4vw,40px)}
.folha:nth-of-type(even){background:var(--nevoa)}
.folha-in{max-width:var(--maxw);margin:0 auto;display:flex;flex-direction:column;gap:clamp(28px,4vw,44px)}
.escura{background:var(--noite)!important;color:var(--claro);
  background-image:radial-gradient(900px 520px at 20% -10%,rgba(145,0,255,.45),transparent 60%),
                   radial-gradient(800px 480px at 90% 0%,rgba(24,134,255,.25),transparent 60%)!important}
.escura h1,.escura h2,.escura h3{color:#fff}
.escura .lead{color:var(--claro-2)}

.eyebrow{display:block;font-size:17px;font-weight:600;letter-spacing:.01em;color:var(--sec);margin-bottom:6px}
.escura .eyebrow{color:#C9A7FF}
.cabeca h2{font-size:clamp(30px,2.6vw+14px,46px)}
.lead{font-size:clamp(17px,1vw+12px,21px);line-height:1.42;color:var(--tinta-2);margin-top:12px;max-width:62ch}

/* capa */
.capa-topo{display:flex;align-items:center;justify-content:space-between;gap:16px}
.capa-topo img{height:26px;width:auto}
/* na tela o nav já mostra a marca; o logo da capa é só do PDF */
@media screen{.capa-topo img{visibility:hidden}}
.capa-topo span{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:#C9A7FF}
.capa h1{font-size:clamp(40px,4.6vw+16px,76px);max-width:15ch;letter-spacing:-.025em}
.capa .sub{font-size:clamp(18px,1vw+13px,22px);line-height:1.45;color:var(--claro-2);max-width:54ch;margin-top:18px}
.quadro{margin:0}
.quadro img{width:100%;border-radius:18px}
.capa-pe{display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center;justify-content:space-between;
  font-size:14px;color:var(--claro-2)}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chips span{border:1px solid rgba(255,255,255,.18);border-radius:980px;padding:5px 12px;color:var(--claro)}

/* públicos */
.publicos{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
@media(max-width:820px){.publicos{grid-template-columns:1fr}}
.pub{background:var(--branco);border:1px solid var(--linha);border-radius:20px;padding:22px}
.pub-art{display:flex;align-items:center;justify-content:center;height:92px;border-radius:14px;
  background:var(--roxo-leve);color:var(--roxo-esc)}
.pub-art .scene{width:92px;height:72px}
.pub b{display:block;margin-top:14px;font-size:19px;font-weight:600}
.pub span{display:block;margin-top:6px;font-size:15px;line-height:1.5;color:var(--tinta-2)}

.check{display:grid;gap:12px}
.check li{display:flex;gap:12px;align-items:flex-start;font-size:17px;line-height:1.45}
.ck{flex:0 0 auto;width:20px;height:20px;margin-top:2px;border-radius:50%;background:var(--roxo-leve);position:relative}
.ck::after{content:"";position:absolute;left:6px;top:5px;width:5px;height:9px;border:2px solid var(--roxo-esc);
  border-top:0;border-left:0;transform:rotate(42deg)}
.credo{border-radius:24px;padding:clamp(24px,3vw,36px);background:var(--noite);color:#fff;
  font-size:clamp(22px,1.6vw+14px,32px);font-weight:600;line-height:1.2;letter-spacing:-.02em}
.credo .g{background-image:linear-gradient(90deg,#C08BFF,#6FB4FF)}

/* cards */
.fgrid{display:grid;gap:14px}
.cols-2{grid-template-columns:repeat(2,1fr)}
.cols-3{grid-template-columns:repeat(3,1fr)}
.cols-4{grid-template-columns:repeat(4,1fr)}
@media(max-width:900px){.cols-3,.cols-4{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.cols-2,.cols-3,.cols-4{grid-template-columns:1fr}}
.fc{background:var(--branco);border:1px solid var(--linha);border-radius:18px;padding:20px 20px}
.folha:nth-of-type(even) .fc{border-color:rgba(0,0,0,.05)}
.fc-mk{display:block;width:24px;height:3px;border-radius:3px;background:var(--mk);margin-bottom:12px}
.fc h3{font-size:18px;letter-spacing:-.01em}
.fc p{margin-top:6px;color:var(--tinta-2);font-size:15px;line-height:1.5}
.tg{display:inline-block;margin-left:8px;font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
  color:var(--sec);background:var(--soft);padding:3px 8px;border-radius:980px;vertical-align:middle}
.escura .fc{background:var(--noite-2);border-color:rgba(255,255,255,.12)}
.escura .fc p{color:var(--claro-2)}

/* storyboard */
.board{margin:0;padding:22px;border-radius:22px;background:var(--soft)}
.board-cap{font-size:19px;font-weight:600;letter-spacing:-.01em;margin-bottom:14px}
.board-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.board.n-5 .board-strip{grid-template-columns:repeat(5,1fr)}
@media(max-width:820px){.board-strip,.board.n-5 .board-strip{grid-template-columns:repeat(2,1fr)}}
.bp{background:#fff;border-radius:14px;padding:14px;position:relative}
.bp-n{position:absolute;top:10px;right:12px;font-size:12px;font-weight:700;color:var(--sec)}
.bp-art{display:block;color:var(--sec)}
.scene{width:48px;height:38px}
.bp b{display:block;margin-top:8px;font-size:15px;font-weight:600;line-height:1.25}
.bp i{display:block;margin-top:4px;font-style:normal;font-size:13.5px;line-height:1.42;color:var(--tinta-2)}

/* passos */
.passos{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
@media(max-width:820px){.passos{grid-template-columns:1fr}}
.passo{border-radius:20px;padding:22px;background:#fff;border:1px solid var(--linha)}
.passo .n{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:50%;
  background:var(--grad);color:#fff;font-weight:600;font-size:15px}
.passo h3{margin-top:12px;font-size:19px}
.passo p{margin-top:6px;font-size:15px;line-height:1.5;color:var(--tinta-2)}

/* capítulo de público: TV + texto */
.duo{display:grid;grid-template-columns:1.25fr 1fr;gap:28px;align-items:center}
@media(max-width:820px){.duo{grid-template-columns:1fr}}
.palco{background:var(--noite);border-radius:22px;padding:10px}
.palco .quadro img{border-radius:14px}
.duo h3{font-size:clamp(22px,1vw+16px,28px)}
.duo p{margin-top:10px;color:var(--tinta-2);font-size:16px;line-height:1.5}

/* anatomia */
.anatomia{display:grid;gap:12px}
.anatomia li{border-left:3px solid transparent;border-image:var(--grad) 1;padding:4px 0 4px 14px}
.anatomia b{display:block;font-size:17px}
.anatomia span{display:block;margin-top:2px;font-size:15px;line-height:1.45;color:var(--tinta-2)}

/* tiles (o que vem junto) */
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
@media(max-width:820px){.tiles{grid-template-columns:repeat(2,1fr)}}
.tile{background:var(--noite);color:#fff;border-radius:14px;padding:14px 16px}
.tile b{display:block;font-size:15px}
.tile span{display:block;margin-top:3px;font-size:13.5px;line-height:1.4;color:var(--claro-2)}

/* contracapa */
.contra h2{font-size:clamp(34px,3vw+16px,60px);max-width:14ch}
.contra .lead{max-width:48ch}
.qr-box{display:grid;grid-template-columns:auto 1fr;gap:26px;align-items:center;background:#fff;color:var(--tinta);
  border-radius:24px;padding:24px;max-width:640px}
.qr-box svg{width:170px;height:170px;display:block}
.qr-box b{display:block;font-size:22px;letter-spacing:-.01em}
.qr-box span{display:block;margin-top:8px;font-size:15px;line-height:1.5;color:var(--tinta-2)}
@media(max-width:560px){.qr-box{grid-template-columns:1fr}}
.comecar{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
@media(max-width:820px){.comecar{grid-template-columns:1fr}}
.comecar li{background:var(--noite-2);border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:20px}
.comecar .n{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;
  background:var(--grad);color:#fff;font-weight:600;font-size:14px}
.comecar b{display:block;margin-top:12px;font-size:18px;color:#fff}
.comecar span:not(.n){display:block;margin-top:6px;font-size:15px;line-height:1.5;color:var(--claro-2)}
.contra-pe{display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px;font-size:13px;color:var(--claro-2)}
.contra-pe img{height:18px;width:auto}
.contra-pe a{color:var(--claro)}
.so-tela{display:flex;flex-wrap:wrap;gap:12px}

/* reveal */
.rev{opacity:0;transform:translateY(24px);transition:opacity .8s var(--ease),transform .8s var(--ease)}
.rev.vis{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.rev{opacity:1;transform:none}html{scroll-behavior:auto}}

/* ======================= IMPRESSÃO / PDF =======================
   Cada .folha = 1 página A4. Tamanhos em pt/mm, independentes da tela. */
@media print{
  @page{size:A4;margin:0}
  html,body{background:#fff}
  .rev{opacity:1!important;transform:none!important}
  *{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
  .nav,.so-tela{display:none!important}
  body{font-size:9.5pt;line-height:1.42}
  .folha{width:210mm;height:297mm;padding:14mm 14mm 12mm;overflow:hidden;break-after:page;page-break-after:always}
  .folha:last-of-type{break-after:auto;page-break-after:auto}
  .folha-in{max-width:none;height:100%;gap:6.5mm}
  .eyebrow{font-size:10pt;margin-bottom:1.5mm}
  .cabeca h2{font-size:22pt}
  .lead{font-size:10.5pt;margin-top:2.5mm}
  .fgrid{gap:3mm}
  .cols-3,.cols-4{grid-template-columns:repeat(3,1fr)!important}
  .cols-4{grid-template-columns:repeat(4,1fr)!important}
  .cols-2{grid-template-columns:repeat(2,1fr)!important}
  .fc{border-radius:10px;padding:3.6mm 3.8mm}
  .fc-mk{width:6mm;height:.8mm;margin-bottom:2.2mm}
  .fc h3{font-size:10.5pt}
  .fc p{font-size:8.6pt;line-height:1.42;margin-top:1.2mm}
  .board{padding:4.5mm;border-radius:12px}
  .board-cap{font-size:11pt;margin-bottom:3mm}
  .board-strip,.board.n-5 .board-strip{gap:2.2mm}
  .board-strip{grid-template-columns:repeat(4,1fr)!important}
  .board.n-5 .board-strip{grid-template-columns:repeat(5,1fr)!important}
  .bp{padding:3mm;border-radius:8px}
  .scene{width:11mm;height:8.6mm}
  .bp b{font-size:9pt;margin-top:1.5mm}
  .bp i{font-size:8pt;line-height:1.35;margin-top:.8mm}
  .publicos{grid-template-columns:repeat(3,1fr)!important;gap:3mm}
  .pub{padding:4mm;border-radius:10px}
  .pub-art{height:20mm;border-radius:8px}
  .pub-art .scene{width:22mm;height:17mm}
  .pub b{font-size:11pt;margin-top:2.5mm}
  .pub span{font-size:8.8pt}
  .check{gap:2.4mm}
  .check li{font-size:10pt}
  .credo{font-size:16pt;border-radius:12px;padding:6mm}
  .passos{grid-template-columns:repeat(3,1fr)!important;gap:3mm}
  .passo{padding:4mm;border-radius:10px}
  .passo .n{width:7mm;height:7mm;font-size:9pt}
  .passo h3{font-size:11pt;margin-top:2.5mm}
  .passo p{font-size:8.8pt}
  .duo{grid-template-columns:1.3fr 1fr!important;gap:6mm}
  .palco{border-radius:12px;padding:2mm}
  .palco .quadro img{border-radius:8px}
  .duo h3{font-size:15pt}
  .duo p{font-size:9.6pt;margin-top:2mm}
  .anatomia{gap:3mm}
  .anatomia b{font-size:11pt}
  .anatomia span{font-size:9pt}
  .tiles{grid-template-columns:repeat(3,1fr)!important;gap:2.2mm}
  .tile{padding:2.8mm 3.4mm;border-radius:8px}
  .tile b{font-size:9.4pt}
  .tile span{font-size:8pt}
  /* capa e contracapa ocupam a folha inteira, com o pé colado embaixo */
  .capa .folha-in,.contra .folha-in{justify-content:space-between}
  .capa-topo img{height:7mm}
  .capa h1{font-size:34pt}
  .capa .sub{font-size:12pt;margin-top:4mm}
  .quadro img{border-radius:10px}
  .capa-pe{font-size:9pt}
  .contra h2{font-size:34pt}
  .qr-box{padding:6mm;border-radius:14px;gap:7mm;max-width:none}
  .qr-box svg{width:44mm;height:44mm}
  .qr-box b{font-size:15pt}
  .qr-box span{font-size:10pt}
  .contra-pe{font-size:8.5pt}
  .comecar{grid-template-columns:repeat(3,1fr)!important;gap:4mm}
  .comecar li{padding:5mm;border-radius:12px}
  .comecar .n{width:8mm;height:8mm;font-size:10pt}
  .comecar b{font-size:12.5pt;margin-top:3mm}
  .comecar span:not(.n){font-size:9.8pt;margin-top:1.5mm}
  a{color:inherit}

  /* folhas com menos texto: a letra cresce em vez de sobrar papel em branco no pé */
  #quem .folha-in{gap:9mm}
  #quem .pub-art{height:30mm}
  #quem .pub-art .scene{width:32mm;height:25mm}
  #quem .pub b{font-size:13pt}
  #quem .pub span{font-size:10pt}
  #quem .check{gap:4mm}
  #quem .check li{font-size:12pt}
  #quem .credo{font-size:20pt;padding:9mm}
  #tela .folha-in{gap:9mm}
  #tela .duo{grid-template-columns:1.45fr 1fr!important}
  #tela .anatomia{gap:5mm}
  #tela .anatomia b{font-size:13pt}
  #tela .anatomia span{font-size:10.2pt}
  #tela .fgrid{gap:4mm}
  #tela .fc{padding:5mm 5.5mm}
  #tela .fc-mk{margin-bottom:2.8mm}
  #tela .fc h3{font-size:12pt}
  #tela .fc p{font-size:10.2pt;margin-top:1.6mm}
  #no-ar .folha-in{gap:9mm}
  #no-ar .board{padding:6mm}
  #no-ar .scene{width:14mm;height:11mm}
  #no-ar .bp{padding:4.5mm}
  #no-ar .bp b{font-size:10.5pt}
  #no-ar .bp i{font-size:9.2pt}
  #no-ar .fgrid{gap:4.5mm}
  #no-ar .fc{padding:6mm 5.5mm}
  #no-ar .fc-mk{margin-bottom:3.5mm}
  #no-ar .fc h3{font-size:13pt}
  #no-ar .fc p{font-size:10.4pt;margin-top:2mm}
  #limites .folha-in{gap:9mm}
  #limites .fgrid{gap:5mm}
  #limites .fc{padding:7mm 6mm}
  #limites .fc-mk{margin-bottom:3.5mm}
  #limites .fc h3{font-size:13pt}
  #limites .fc p{font-size:10.6pt;margin-top:2mm}
}
"""

SCRIPT = """<script>
(function(){
  if(!("IntersectionObserver" in window)||matchMedia("(prefers-reduced-motion: reduce)").matches){
    document.querySelectorAll(".rev").forEach(function(e){e.classList.add("vis")});return;}
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    if(e.isIntersecting){e.target.classList.add("vis");io.unobserve(e.target)}})},
    {threshold:0,rootMargin:"0px 0px -10% 0px"});
  document.querySelectorAll(".rev").forEach(function(e){io.observe(e)});
})();
</script>"""

WA_SVG = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" style="width:18px;height:18px">'
          '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.6 0-3.1-.4-4.4-1.2'
          'l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Z"/></svg>')

# --------------------------------------------------------------------- montagem
def capitulo_publico(fid, chave_quadro, eyebrow, h2, lead, h3, texto, board_key, itens):
    return folha(fid,
        cabeca(eyebrow, h2, lead) +
        f'<div class="duo rev"><div class="palco">{quadro(chave_quadro)}</div>'
        f'<div><h3>{h3}</h3><p>{texto}</p></div></div>' +
        board(board_key) + cards(itens, 3), label=eyebrow)

def build():
    nav = f'''<nav class="nav">
  <a class="brand" href="/" aria-label="Corpflix — início"><img src="/assets/wordmark.png" alt="Corpflix"></a>
  <span class="nav-r"><span class="nav-links">
    <a href="#comercio">Comércio</a><a href="#empresa">Empresa</a><a href="#elevador">Condomínio</a>
    <a href="#no-ar">No ar</a><a href="#limites">O que não faz</a></span>
  <a class="nav-cta" href="{WA}">Falar no WhatsApp</a></span>
</nav>'''

    # 1 · capa
    capa = folha("capa",
        f'<div class="capa-topo"><img src="/assets/wordmark.png" alt="Corpflix"><span>{C.HERO["eyebrow"]}</span></div>'
        f'<div><h1>{C.HERO["h1"]}</h1><p class="sub">{C.HERO["sub"]}</p>'
        f'<div class="so-tela" style="margin-top:28px"><a class="btn btn-branco" href="{WA}">{WA_SVG} Falar no WhatsApp</a>'
        f'<a class="btn" href="/livreto.pdf" download="livreto-corpflix.pdf">Baixar o PDF</a></div></div>'
        f'<div class="palco">{quadro("capa")}</div>'
        f'<div class="capa-pe"><span class="chips"><span>Sala de espera</span><span>Refeitório</span>'
        f'<span>Elevador</span></span><span>corpflix.com.br · mídia indoor gerenciada</span></div>',
        cls="escura capa", label="Capa")

    # 2 · para quem é + dores
    cenas_pub = {"publico-comercio": "espera", "publico-corporativa": "refeitorio", "publico-elevador": "elevador"}
    pubs = "".join(f'<div class="pub"><span class="pub-art">{scene(cenas_pub[s])}</span><b>{r}</b><span>{d}</span></div>'
                   for s, r, d in C.PUBLICOS)
    quem = folha("quem",
        cabeca("Para quem é", "Três lugares, uma pergunta: quem está olhando?",
               "A mesma operação serve a sala de espera, o refeitório e o elevador. O que muda é quem "
               "paga e o que ele quer que a tela diga.") +
        f'<div class="publicos rev">{pubs}</div>' +
        cabeca("O que dói hoje", "A tela está ligada — só não está trabalhando.") +
        lista(C.DORES) +
        f'<div class="credo rev">{C.CREDO}</div>', label="Para quem é")

    # 3 · como funciona
    passos = "".join(f'<div class="passo"><span class="n">{i+1}</span><h3>{t}</h3><p>{d}</p></div>'
                     for i, (t, d) in enumerate(C.PASSOS))
    tiles = "".join(f'<div class="tile"><b>{n}</b><span>{d}</span></div>' for n, d, _g in C.TILES)
    como = folha("como",
        cabeca("Como funciona", "Sem pendrive, sem servidor, sem técnico.",
               "Você não precisa aprender sistema nenhum. Diz o que quer mostrar e quando — o resto é com a gente.") +
        f'<div class="passos rev">{passos}</div>' + board("rede") +
        cabeca("Tudo o que vem junto", "A mesma plataforma, do balcão à cabine.") +
        f'<div class="tiles rev">{tiles}</div>', label="Como funciona")

    # 4 · o que roda na tela
    anat = "".join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in C.ANATOMIA)
    tela = folha("tela",
        cabeca("O que roda na tela", "A grade é sua. O intervalo, a gente preenche.",
               "Entre uma peça sua e outra, a tela informa sozinha — notícia, clima e cotação —, no "
               "layout que cabe na parede, no refeitório ou na cabine.") +
        f'<div class="duo rev"><div class="palco">{quadro("aviso")}</div><ul class="anatomia">{anat}</ul></div>' +
        cards(C.TELA, 2), label="O que roda na tela")

    # 5-7 · os três públicos
    comercio = capitulo_publico("comercio", "comercio", "Comércio e serviço", "Quem está esperando, está olhando.",
        "Restaurante, clínica, academia, salão, pet, loja. A tela da sua sala de espera pode vender o seu "
        "cardápio e a sua promoção — em vez da novela ou do anúncio de outro negócio.",
        "A tela que já está na parede.",
        "Ela está ali o dia inteiro, na frente de quem já entrou e ainda não comprou tudo. Com o Corpflix "
        "ela passa a trabalhar pelo seu negócio — e não pelo de outro.",
        "comercio", C.COMERCIO)
    empresa = capitulo_publico("empresa", "empresa", "Empresa", "O recado chega a quem não lê e-mail.",
        "Metade da empresa não senta na frente de um computador. A tela do refeitório e do corredor alcança "
        "essa metade — sem anúncio de terceiro no meio.",
        "Onde o time passa, não onde ele não abre.",
        "O RH manda a campanha, a regra nova, o recado da diretoria. A gente publica, e a mensagem fica no "
        "refeitório, no corredor e na recepção — cada ambiente com o seu.",
        "empresa", C.EMPRESA)
    elevador = capitulo_publico("elevador", "condominio", "Condomínio", "A tela que ninguém ignora.",
        "Todo morador passa pelo elevador todo dia. Ele vira o canal de recado do síndico — e um espaço que "
        "ainda pode ser cedido ao comércio da região.",
        "O aviso alcança quem não abre o aplicativo.",
        "Manutenção, assembleia, regra da piscina. O síndico manda, a gente publica — e o aviso sai da tela "
        "quando deixa de valer, em vez de ficar colado na parede um mês.",
        "elevador", C.ELEVADOR)

    # 8 · operação
    noar = folha("no-ar",
        cabeca("Operação", "Tela apagada é dinheiro parado.",
               "Uma TV desligada não avisa ninguém: ela só fica preta até alguém reparar. A mesma operação que "
               "já cuida de dezenas de telas no ar vigia a sua de longe — e age antes de o cliente comentar.") +
        board("noar") + cards(C.OPERACAO, 2), label="Operação")

    # 9 · honestidade
    limites = folha("limites",
        cabeca("Honestidade", "O que o Corpflix não faz.",
               "Um livreto que só lista virtude não ajuda ninguém a decidir. Isto aqui é o que ele "
               "<b>não</b> resolve — para você não descobrir depois de fechar.") +
        cards(C.NAO_FAZ, 2, cls="c-noite"), label="O que o Corpflix não faz")

    # 10 · contracapa
    h2, p = C.CTA
    body_sem_pe = "\n".join([capa, quem, como, tela, comercio, empresa, elevador, noar, limites])
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    sha = hashlib.sha1(body_sem_pe.encode()).hexdigest()[:7]
    contra = folha("contato",
        f'<div><span class="eyebrow">Fale com a gente</span><h2>{h2}</h2><p class="lead">{p}</p>'
        f'<div class="so-tela" style="margin-top:26px"><a class="btn btn-branco" href="{WA}">{WA_SVG} Falar no WhatsApp</a></div></div>'
        '<ol class="comecar">' +
        "".join(f'<li><span class="n">{i+1}</span><b>{t}</b><span>{d}</span></li>'
                for i, (t, d) in enumerate(C.COMECAR)) + '</ol>'
        f'<div class="qr-box">{QR_SVG}<div><b>Aponte a câmera do celular.</b>'
        f'<span>O QR abre o WhatsApp do Corpflix com a mensagem pronta. Conte onde a tela fica e o que você '
        f'quer mostrar — a gente responde por lá.</span></div></div>'
        f'<div class="contra-pe"><span><img src="/assets/wordmark.png" alt="Corpflix"></span>'
        f'<span>{C.SITE.replace("https://", "")} · <a href="{C.SITE}/privacidade">Privacidade</a> · '
        f'Livreto v{hoje} · {sha}</span></div>',
        cls="escura contra", label="Contato")

    body = nav + "\n" + body_sem_pe + "\n" + contra

    desc = ("Livreto do Corpflix: TV de mídia indoor gerenciada para a sala de espera do comércio, "
            "o refeitório da empresa e o elevador do condomínio. A gente instala o player, publica "
            "o que você manda e vigia a tela de longe — com notícias, clima e cotações no intervalo.")
    url = f"{C.SITE}/livreto/"
    head = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Livreto do Corpflix — a TV do seu ponto, publicada e monitorada</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta name="theme-color" content="#0A0716">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Corpflix">
<meta property="og:locale" content="pt_BR">
<meta property="og:url" content="{url}">
<meta property="og:title" content="Livreto do Corpflix">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{C.SITE}/assets/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Service",
"name":"Corpflix","serviceType":"Mídia indoor gerenciada","areaServed":"BR",
"url":"{url}","inLanguage":"pt-BR","description":"{desc}",
"provider":{{"@type":"Organization","name":"Corpflix","url":"{C.SITE}/","logo":"{C.SITE}/assets/brand-mark.png"}},
"audience":[{{"@type":"BusinessAudience","name":"Comércio e serviço com sala de espera"}},
{{"@type":"BusinessAudience","name":"Empresa — comunicação interna"}},
{{"@type":"BusinessAudience","name":"Condomínio — TV no elevador"}}]}}</script>
<style>{CSS}</style>
</head>
<body>
'''
    doc = head + body + "\n" + SCRIPT + "\n</body>\n</html>\n"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc)
    print(f"[livreto] {OUT} — {len(doc)//1024} KB · v{hoje} · {sha}")

build()
