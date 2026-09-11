#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o livreto do Corpflix → livreto/index.html (rota /livreto/).

    python3 livreto/build.py

Doutrina herdada do livreto do SeuCondomínio (repo denoww/seucondominio, livreto/CLAUDE.md):
  - Long-scroll Apple, capítulos alternando branco/névoa, storyboards de fluxo.
  - Selo só onde é verdade. Nunca vender roadmap como pronto → capítulo "O que não faz".
  - NUNCA editar o HTML gerado. Edita-se `content.py` (95% das mudanças) ou este arquivo.

Diferença de infra: o SeuCondomínio gera o PDF em RUNTIME (Gotenberg). Aqui o site é
estático (GitHub Pages, sem runtime), então o PDF é gerado no build por Chromium headless
(`livreto/build_pdf.sh`) e commitado pelo CI.

PEGADINHAS DO PRINT (custaram correção no repo original — não mexer sem entender):
  - `@media print` PRECISA forçar `.rev{opacity:1}` — senão o PDF sai EM BRANCO.
  - `print-color-adjust:exact` — senão hero/CTA/fotos saem sem cor.
  - `break-inside:avoid` só nas unidades atômicas (card, painel). NUNCA por capítulo:
    gera páginas quase vazias.
  - `@page{size:A4}` — senão o Chrome imprime em Letter.
  - Traço de SVG: `stroke` explícito no <g>. (No repo original, as classes utilitárias
    `.s`/`.w` forçavam `stroke:none` e o traço sumia calado.)

CORES (contrato da marca — nomes exatos, não invente token novo):
  --roxo #9100FF é a primária: branco sobre ela dá 5,76:1, pode ser botão.
  --roxo-esc #6A00E0 é o hover e TODO texto pequeno colorido (7,81:1).
  --azul #1886FF só existe DENTRO do --grad. Nunca superfície com texto (3,56:1).
  Sem Google Fonts e sem analytics: pilha de sistema, nada de terceiro na página.
"""
import pathlib, importlib.util, datetime, hashlib

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent
OUT  = REPO / "livreto" / "index.html"

sp = importlib.util.spec_from_file_location("content", str(ROOT / "content.py"))
C = importlib.util.module_from_spec(sp); sp.loader.exec_module(C)

WA = C.WA + C.WA_TXT

# --------------------------------------------------------------------- cenas
# Line-art dos storyboards, viewBox 56×44.
# ⚠️ Traço: `stroke="currentColor"` + `fill="none"` são aplicados pelo `scene()` no <g>.
# NÃO usar classe utilitária aqui — no repo de origem as classes `.s`/`.w` forçavam
# `stroke:none` e o desenho sumia sem erro nenhum.
# As chaves têm que casar 1:1 com as cenas citadas em `content.py > BOARDS` e com as
# três cenas de público usadas em `cap_quem` (espera, refeitorio, elevador).
SCENES = {
 # ── os três lugares ──────────────────────────────────────────────────────
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
 # ── do pedido à tela ─────────────────────────────────────────────────────
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
 # ── a tela no ar ─────────────────────────────────────────────────────────
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
_CHAP = [0]
def chapter(cid, eyebrow, h2, lead, *blocks):
    bg = "nevoa" if _CHAP[0] % 2 else ""   # alterna sozinho — não passe bg
    _CHAP[0] += 1
    return f'''<section class="cap {bg}" id="{cid}" aria-label="{eyebrow}">
  <div class="cap-in">
    <div class="cap-head rev"><span class="eyebrow">{eyebrow}</span><h2>{h2}</h2>
      {f'<p class="lead">{lead}</p>' if lead else ''}</div>
    {"".join(blocks)}
  </div>
</section>'''

def tag(t):
    return f'<span class="tg">{t}</span>' if t else ''

def cards(items, cor):
    cs = "".join(f'<article class="fc"><span class="fc-mk"></span><h3>{t}{tag(g)}</h3><p>{d}</p></article>'
                 for t, d, g in items)
    return f'<div class="fgrid c-{cor} rev">{cs}</div>'

def board(key):
    cor, titulo, panels = C.BOARDS[key]
    cells = []
    for i, (sc, h, cap) in enumerate(panels):
        cells.append(f'<li class="bp"><span class="bp-n">{i+1}</span>'
                     f'<span class="bp-art">{scene(sc)}</span><b>{h}</b><i>{cap}</i></li>')
        if i < len(panels) - 1:
            cells.append('<li class="bp-arr" aria-hidden="true">→</li>')
    return (f'<figure class="board c-{cor} rev"><figcaption class="board-cap">'
            f'<span class="eyebrow">Como funciona</span><b>{titulo}</b></figcaption>'
            f'<ol class="board-strip">{"".join(cells)}</ol></figure>')

# Só os nomes do contrato de assets: hero, publico-comercio, publico-corporativa,
# publico-elevador. Foto que não existe em disco sai quebrada no PDF e nenhum
# workflow do livreto reclama (o guard seo.py pega, mas só na página publicada).
def foto(slug, alt, extra=""):
    return (f'<figure class="shot{extra}"><img src="/assets/{slug}.jpg" alt="{alt}" '
            f'loading="lazy" decoding="async"></figure>')

def mrow(media, h, p, flip=False):
    return (f'<div class="mrow{" flip" if flip else ""} rev"><div class="m-media">{media}</div>'
            f'<div class="m-copy"><h3>{h}</h3><p>{p}</p></div></div>')

def lista(items):
    return ('<ul class="check rev">' +
            "".join(f'<li><span class="ck"></span>{t}</li>' for t in items) + '</ul>')

# ---------------------------------------------------------------------- CSS
CSS = """
:root{
  --branco:#fff;--nevoa:#f5f5f7;--preto:#000;
  --tinta:#1d1d1f;--tinta-2:#6e6e73;--claro:#f5f5f7;--claro-2:#a1a1a6;
  --roxo:#9100FF;--roxo-esc:#6A00E0;--roxo-leve:#F3E8FF;
  --azul:#1886FF;--grad:linear-gradient(90deg,#9100FF,#1886FF);
  --noite:#0A0716;--noite-2:#1F0E36;
  --linha:rgba(0,0,0,.12);--maxw:1120px;
  --sec:var(--roxo-esc);--soft:var(--roxo-leve);--mk:var(--grad);
  --ease:cubic-bezier(.45,0,.55,1);
}
/* --sec pinta TEXTO pequeno (eyebrow, selo, número do painel): por isso roxo-esc e
   noite-2, nunca --roxo cru nem --azul. O marcador de card (--mk) é traço sem texto
   e pode levar o gradiente. */
.c-roxo{--sec:#6A00E0;--soft:#F3E8FF;--mk:var(--grad)}
.c-noite{--sec:#1F0E36;--soft:#EEEAF4;--mk:#1F0E36}
*{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--branco);color:var(--tinta);
  font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Inter',system-ui,'Segoe UI',Roboto,sans-serif;
  font-size:17px;line-height:1.4705882353;letter-spacing:-.022em;-webkit-font-smoothing:antialiased}
h1,h2,h3{margin:0;font-weight:600;line-height:1.06;letter-spacing:-.015em;text-wrap:balance}
p{margin:0}ul,ol{margin:0;padding:0;list-style:none}
a{color:var(--roxo-esc);text-decoration:none}
img{display:block;max-width:100%}
:focus-visible{outline:3px solid var(--roxo);outline-offset:3px;border-radius:6px}
.eyebrow{display:block;font-size:21px;font-weight:600;letter-spacing:.011em;color:var(--sec);margin-bottom:8px}
.lead{font-size:21px;line-height:1.381;letter-spacing:.011em;color:var(--tinta-2);margin-top:14px}
/* texto em gradiente: só em tamanho grande (título, credo), onde o trecho azul passa de 3:1 */
.g{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent;
  -webkit-text-fill-color:transparent}

.nav{position:sticky;top:0;z-index:50;height:52px;display:flex;align-items:center;justify-content:space-between;
  padding:0 clamp(20px,4vw,40px);background:rgba(255,255,255,.72);
  backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);
  border-bottom:1px solid rgba(0,0,0,.08)}
.nav .brand{display:flex;align-items:center;gap:8px;color:var(--tinta)}
.nav .brand img{height:20px;width:auto}
.nav-r{display:flex;align-items:center;gap:clamp(14px,3vw,26px);font-size:13px}
/* os <a> vivem DENTRO de .nav-links — sem display:flex aqui eles saem colados
   ("ComércioEmpresa"), porque o gap do .nav-r só separa os filhos diretos. */
.nav-links{display:inline-flex;align-items:center;gap:clamp(14px,2.2vw,24px)}
.nav-r a{color:var(--tinta);opacity:.85}
.nav-r a:hover{opacity:1;color:var(--roxo-esc)}
.nav-cta{background:var(--roxo);color:#fff!important;opacity:1!important;padding:6px 14px;border-radius:980px;font-weight:500}
.nav-cta:hover{background:var(--roxo-esc)}
@media(max-width:760px){.nav-links{display:none}}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--roxo);color:#fff;
  padding:12px 22px;border-radius:980px;font-weight:400;font-size:17px;letter-spacing:-.022em;
  transition:background-color .1s linear}
.btn:hover{background:var(--roxo-esc)}
.btn-branco{background:#fff;color:var(--tinta)}
.btn-branco:hover{background:var(--roxo-leve)}
.btns{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:32px}

/* hero — a capa */
.hero{background:var(--noite);color:var(--claro);text-align:center;padding:clamp(64px,9vh,104px) 24px 0;overflow:hidden;
  background-image:radial-gradient(700px 420px at 35% -10%,rgba(145,0,255,.55),transparent 62%),
                   radial-gradient(640px 400px at 70% -5%,rgba(24,134,255,.35),transparent 62%)}
.hero-mark{height:clamp(30px,3vw+14px,44px);width:auto;margin:0 auto 28px}
.hero .eyebrow{display:inline-block;background:var(--grad);-webkit-background-clip:text;background-clip:text;
  color:transparent;-webkit-text-fill-color:transparent}
.hero h1{font-size:clamp(40px,4.4vw+14px,76px);color:#fff;max-width:17ch;margin:0 auto}
.hero .sub{margin:22px auto 0;max-width:56ch;font-size:21px;line-height:1.4;color:var(--claro-2);letter-spacing:.011em}
.hero-stage{margin:56px auto 0;max-width:900px}
/* banner: a foto sobe do hero e é cortada pelo fim da seção (o corte é de propósito).
   Sem aspect-ratio ela entra inteira e o corte cai em lugar aleatório. */
.hero-stage img{width:100%;aspect-ratio:16/8;object-fit:cover;object-position:50% 40%;
  border-radius:24px 24px 0 0;box-shadow:0 -10px 60px rgba(145,0,255,.35)}

.credo{max-width:960px;margin:0 auto;padding:clamp(80px,10vw,130px) 24px;text-align:center}
.credo h2{font-size:clamp(30px,3.4vw+10px,52px);letter-spacing:-.02em}

/* capítulos */
.cap{padding:clamp(72px,9vw,120px) 0}
.cap.nevoa{background:var(--nevoa)}
.cap-in{max-width:var(--maxw);margin:0 auto;padding:0 24px}
.cap-head{max-width:760px}
.cap-head h2{font-size:clamp(30px,2.4vw+14px,48px);letter-spacing:-.01em;margin-top:2px}

.fgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-top:44px}
.fc{background:var(--branco);border:1px solid var(--linha);border-radius:20px;padding:26px 24px;break-inside:avoid}
.cap.nevoa .fc{background:#fff;border-color:rgba(0,0,0,.06)}
.fc-mk{display:block;width:26px;height:3px;border-radius:3px;background:var(--mk);margin-bottom:16px}
.fc h3{font-size:20px;letter-spacing:-.01em}
.fc p{margin-top:8px;color:var(--tinta-2);font-size:16px;line-height:1.5}
.tg{display:inline-block;margin-left:8px;font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
  color:var(--sec);background:var(--soft);padding:3px 8px;border-radius:980px;vertical-align:middle}

/* storyboard */
.board{margin:48px 0 0;padding:30px;border-radius:24px;background:var(--soft);break-inside:avoid}
.board-cap{margin-bottom:22px}
.board-cap b{display:block;font-size:22px;font-weight:600;letter-spacing:-.01em}
.board-strip{display:flex;align-items:stretch;gap:10px;flex-wrap:wrap}
.bp{flex:1 1 180px;background:#fff;border-radius:16px;padding:20px 18px;position:relative;break-inside:avoid}
.bp-n{position:absolute;top:14px;right:16px;font-size:12px;font-weight:700;color:var(--sec)}
.bp-art{display:block;color:var(--sec)}
.scene{width:56px;height:44px}
.bp b{display:block;margin-top:12px;font-size:17px;font-weight:600;letter-spacing:-.01em}
.bp i{display:block;margin-top:6px;font-style:normal;font-size:14.5px;line-height:1.45;color:var(--tinta-2)}
.bp-arr{display:flex;align-items:center;color:var(--sec);font-size:20px;opacity:.55}
@media(max-width:860px){.bp-arr{display:none}}

/* media row */
.mrow{display:grid;grid-template-columns:1.05fr .95fr;gap:44px;align-items:center;margin-top:48px}
.mrow.flip .m-media{order:2}
@media(max-width:860px){.mrow{grid-template-columns:1fr}.mrow.flip .m-media{order:0}}
.m-copy h3{font-size:26px;letter-spacing:-.012em}
.m-copy p{margin-top:12px;color:var(--tinta-2);font-size:17px;line-height:1.5}
.shot{margin:0}
.shot img{width:100%;aspect-ratio:3/2;object-fit:cover;border-radius:20px}

/* checklist */
.check{margin-top:36px;display:grid;gap:14px}
.check li{display:flex;gap:12px;align-items:flex-start;font-size:17px;line-height:1.45;break-inside:avoid}
.ck{flex:0 0 auto;width:20px;height:20px;margin-top:2px;border-radius:50%;background:var(--roxo-leve);position:relative}
.ck::after{content:"";position:absolute;left:6px;top:5px;width:5px;height:9px;border:2px solid var(--roxo-esc);
  border-top:0;border-left:0;transform:rotate(42deg)}

/* os três públicos — cena line-art grande em vez de foto (a foto vem no capítulo) */
.publicos{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:44px}
@media(max-width:860px){.publicos{grid-template-columns:1fr}}
.pub{background:#fff;border:1px solid var(--linha);border-radius:24px;padding:28px 26px;break-inside:avoid;
  display:block;color:var(--tinta)}
.pub .pub-art{display:flex;align-items:center;justify-content:center;height:120px;border-radius:16px;
  background:var(--roxo-leve);color:var(--roxo-esc)}
.pub .pub-art .scene{width:112px;height:88px}
.pub b{display:block;margin-top:18px;font-size:20px;font-weight:600;letter-spacing:-.01em}
.pub span{display:block;margin-top:6px;font-size:15.5px;line-height:1.5;color:var(--tinta-2)}
.pub em{display:inline-block;margin-top:14px;font-style:normal;font-size:14px;font-weight:500;color:var(--roxo-esc)}

/* como funciona — três passos */
.passos{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:44px}
@media(max-width:860px){.passos{grid-template-columns:1fr}}
.passo{border-radius:24px;padding:28px 26px;background:#fff;border:1px solid var(--linha);break-inside:avoid}
.passo .n{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:50%;
  background:var(--grad);color:#fff;font-weight:600;font-size:15px}
.passo h4{margin:16px 0 0;font-size:20px;font-weight:600;letter-spacing:-.01em}
.passo p{margin-top:8px;font-size:15.5px;line-height:1.5;color:var(--tinta-2)}

/* lineup */
.lineup{background:var(--noite);color:var(--claro);padding:clamp(80px,10vw,130px) 0}
.lineup-in{max-width:var(--maxw);margin:0 auto;padding:0 24px}
.lineup h2{font-size:clamp(30px,2.4vw+14px,48px);color:#fff}
.lineup .lead{color:var(--claro-2)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:44px}
.tile{background:var(--noite-2);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:24px;break-inside:avoid}
.tile h3{font-size:18px;color:#fff}
.tile p{margin-top:8px;font-size:15px;line-height:1.5;color:var(--claro-2)}
.tile-mk{display:block;width:26px;height:3px;border-radius:3px;background:var(--grad);margin-bottom:14px}

/* cta / download / rodapé */
.cta{text-align:center;padding:clamp(88px,11vw,140px) 24px;color:var(--claro);background:
  radial-gradient(900px 520px at 30% 0%,rgba(145,0,255,.55),transparent 65%),
  radial-gradient(800px 480px at 75% 10%,rgba(24,134,255,.3),transparent 65%),var(--noite-2)}
.cta h2{font-size:clamp(30px,3vw+12px,52px);color:#fff;max-width:18ch;margin:0 auto}
.cta p{margin:20px auto 0;max-width:52ch;font-size:19px;line-height:1.5;color:var(--claro-2)}
.dl{text-align:center;padding:clamp(64px,8vw,96px) 24px;background:var(--nevoa)}
.dl h2{font-size:30px}
.dl p{margin-top:12px;color:var(--tinta-2)}
.foot{border-top:1px solid var(--linha);padding:36px 24px;background:var(--nevoa)}
.foot-in{max-width:var(--maxw);margin:0 auto;display:flex;justify-content:space-between;align-items:center;
  gap:16px;flex-wrap:wrap;color:var(--tinta-2);font-size:13px}
.foot-brand{display:flex;align-items:center;gap:12px}
.foot-brand img{height:16px;width:auto}

/* reveal */
.rev{opacity:0;transform:translateY(30px);transition:opacity .9s var(--ease),transform .9s var(--ease)}
.rev.vis{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.rev{opacity:1;transform:none}html{scroll-behavior:auto}}

/* ======================= IMPRESSÃO / PDF =======================
   As quatro travas do playbook. Mexer aqui quebra o PDF em silêncio. */
@media print{
  /* 1. sem isto o PDF sai EM BRANCO (o reveal nunca dispara sem scroll) */
  .rev{opacity:1!important;transform:none!important}
  /* 2. sem isto hero/CTA/fotos/gradiente saem sem cor */
  *{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
  /* 3. só nas unidades atômicas — NUNCA por capítulo (gera página quase vazia) */
  .fc,.bp,.pub,.passo,.tile,.board,.mrow,.check li{break-inside:avoid}
  .nav,.dl,.btns{display:none!important}
  /* a folha A4 tem ~690px úteis — abaixo do breakpoint de 860px, então sem isto
     toda grade vira UMA coluna e o PDF dobra de tamanho com página meio vazia */
  .publicos,.passos{grid-template-columns:repeat(3,1fr)!important;gap:14px}
  .mrow{grid-template-columns:1fr 1fr!important;gap:28px}
  .mrow.flip .m-media{order:2!important}
  .bp-arr{display:none}
  /* título de capítulo não fica órfão no pé da página */
  .cap-head{break-inside:avoid;break-after:avoid}
  .cap{padding:28px 0}
  .hero{padding-top:36px}
  .hero h1{font-size:44px}
  .hero-stage{margin-top:28px}
  .lineup{padding:40px 0}
  .cta{padding:56px 24px}
  .credo{padding:44px 24px}
  body{font-size:11.5pt}
  a{color:inherit;text-decoration:none}
  /* 4. sem isto o Chrome imprime em Letter (padrão americano) — no Brasil é A4 */
  @page{size:A4;margin:14mm}
}
"""

SCRIPT = """<script>
(function(){
  if(!("IntersectionObserver" in window)||matchMedia("(prefers-reduced-motion: reduce)").matches){
    document.querySelectorAll(".rev").forEach(function(e){e.classList.add("vis")});return;}
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    if(e.isIntersecting){e.target.classList.add("vis");io.unobserve(e.target)}})},
    {threshold:0,rootMargin:"0px 0px -12% 0px"});
  document.querySelectorAll(".rev").forEach(function(e){io.observe(e)});
})();
</script>"""

# --------------------------------------------------------------------- montagem
def build():
    _CHAP[0] = 0
    wa_svg = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" style="width:18px;height:18px">'
              '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.6 0-3.1-.4-4.4-1.2'
              'l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Z"/></svg>')

    nav = f'''<nav class="nav">
  <a class="brand" href="/" aria-label="Corpflix — início"><img src="/assets/wordmark-escuro.png" alt="Corpflix"></a>
  <span class="nav-r"><span class="nav-links">
    <a href="#comercio">Comércio</a><a href="#empresa">Empresa</a><a href="#elevador">Condomínio</a>
    <a href="#no-ar">No ar</a><a href="#limites">O que não faz</a></span>
  <a class="nav-cta" href="{WA}">Falar no WhatsApp</a></span>
</nav>'''

    hero = f'''<header class="hero">
  <img class="hero-mark" src="/assets/wordmark.png" alt="Corpflix">
  <span class="eyebrow">{C.HERO["eyebrow"]}</span>
  <h1>{C.HERO["h1"]}</h1>
  <p class="sub">{C.HERO["sub"]}</p>
  <div class="btns"><a class="btn btn-branco" href="{WA}">{wa_svg} Falar no WhatsApp</a></div>
  <div class="hero-stage rev"><img src="/assets/hero.jpg" width="1600" height="800"
    alt="Tela de mídia indoor ligada na parede de um ambiente com gente esperando."></div>
</header>'''

    credo = f'<section class="credo rev"><h2>{C.CREDO}</h2></section>'

    # Para quem é — os três lugares, com a cena line-art de cada um.
    cenas_pub = {"publico-comercio": ("espera", "#comercio"),
                 "publico-corporativa": ("refeitorio", "#empresa"),
                 "publico-elevador": ("elevador", "#elevador")}
    pubs = "".join(
        f'<a class="pub rev" href="{cenas_pub[s][1]}"><span class="pub-art">{scene(cenas_pub[s][0])}</span>'
        f'<b>{r}</b><span>{d}</span><em>Ver o capítulo →</em></a>' for s, r, d in C.PUBLICOS)
    cap_quem = chapter("quem", "Para quem é", "Três lugares, uma pergunta: quem está olhando?",
        "A mesma plataforma serve a sala de espera, o refeitório e o elevador. O que muda é quem paga "
        "e o que ele quer que a tela diga.",
        f'<div class="publicos">{pubs}</div>',
        '<div class="cap-head rev" style="margin-top:64px"><h2 style="font-size:30px">'
        'O que dói hoje.</h2></div>',
        lista(C.DORES))

    cap_comercio = chapter("comercio", "Comércio e serviço", "Quem está esperando, está olhando.",
        "Restaurante, clínica, academia, salão, pet, loja. A tela da sua sala de espera pode vender o "
        "seu cardápio e a sua promoção — em vez da novela ou do anúncio de outro negócio.",
        mrow(foto("publico-comercio", "Clientes esperando num estabelecimento, com uma tela ligada na parede."),
             "A tela que já está na parede.",
             "Ela está ali o dia inteiro, na frente de quem já entrou e ainda não comprou tudo. "
             "Com o Corpflix ela passa a trabalhar pelo seu negócio — e não pelo de outro."),
        board("comercio"), cards(C.COMERCIO, "roxo"))

    cap_empresa = chapter("empresa", "Empresa", "O recado chega a quem não lê e-mail.",
        "Metade da empresa não senta na frente de um computador. A tela do refeitório e do corredor "
        "alcança essa metade — sem anúncio de terceiro no meio.",
        mrow(foto("publico-corporativa", "Funcionários no refeitório da empresa, diante de uma tela com um comunicado interno."),
             "Onde o time passa, não onde ele não abre.",
             "O RH manda a campanha, a regra nova, o recado da diretoria. A gente publica, e a "
             "mensagem fica no refeitório, no corredor e na recepção — cada ambiente com o seu.", True),
        board("empresa"), cards(C.EMPRESA, "roxo"))

    cap_elevador = chapter("elevador", "Condomínio", "A tela que ninguém ignora.",
        "Todo morador passa pelo elevador todo dia. Ele vira o canal de recado do síndico — e um "
        "espaço que ainda pode ser cedido ao comércio da região.",
        mrow(foto("publico-elevador", "Moradora olhando a tela instalada dentro da cabine do elevador."),
             "O aviso alcança quem não abre o aplicativo.",
             "Manutenção, assembleia, regra da piscina. O síndico manda, a gente publica — e o aviso "
             "sai da tela quando deixa de valer, em vez de ficar colado na parede um mês."),
        board("elevador"), cards(C.ELEVADOR, "roxo"))

    cap_noar = chapter("no-ar", "Operação", "Tela apagada é dinheiro parado.",
        "Uma TV desligada não avisa ninguém: ela só fica preta até alguém reparar. A mesma operação "
        "que já cuida de dezenas de telas no ar vigia a sua de longe — e age antes de o cliente "
        "comentar.",
        board("noar"), cards(C.OPERACAO, "noite"))

    cap_tela = chapter("tela", "O que roda na tela", "A grade é sua. O intervalo, a gente preenche.",
        "Entre uma peça sua e outra, a tela informa sozinha — notícia, clima e cotação —, no layout "
        "que cabe na parede, no refeitório ou na cabine.",
        cards(C.TELA, "roxo"))

    passos = "".join(f'<div class="passo"><span class="n">{i+1}</span><h4>{t}</h4><p>{d}</p></div>'
                     for i, (t, d) in enumerate(C.PASSOS))
    cap_como = chapter("como", "Como funciona", "Sem pendrive, sem servidor, sem técnico.",
        "Você não precisa aprender sistema nenhum. Diz o que quer mostrar e quando — o resto é com a "
        "gente.",
        f'<div class="passos rev">{passos}</div>',
        board("rede"))

    cap_limites = chapter("limites", "Honestidade", "O que o Corpflix não faz.",
        "Um livreto que só lista virtude não ajuda ninguém a decidir. Isto aqui é o que ele "
        "<b>não</b> resolve — para você não descobrir depois de fechar.",
        cards(C.NAO_FAZ, "noite"))

    tiles = "".join(f'<article class="tile"><span class="tile-mk"></span>'
                    f'<h3>{n}{tag(g)}</h3><p>{d}</p></article>' for n, d, g in C.TILES)
    lineup = f'''<section class="lineup" id="modulos">
  <div class="lineup-in">
    <h2 class="rev">Tudo o que vem junto.</h2>
    <p class="lead rev">A mesma plataforma na sala de espera, no refeitório e no elevador.</p>
    <div class="tiles rev">{tiles}</div>
  </div>
</section>'''

    h2, p = C.CTA
    cta = f'''<section class="cta">
  <h2 class="rev">{h2}</h2>
  <p class="rev">{p}</p>
  <div class="btns rev"><a class="btn btn-branco" href="{WA}">{wa_svg} Falar no WhatsApp</a></div>
</section>'''

    dl = '''<section class="dl">
  <h2>Leve o livreto com você.</h2>
  <p>Baixe o PDF para apresentar offline ou mandar por e-mail.</p>
  <div class="btns"><a class="btn" href="/livreto.pdf" download="livreto-corpflix.pdf">
    Baixar o livreto (PDF)</a></div>
</section>'''

    body = "\n".join([nav, hero, credo, cap_quem, cap_comercio, cap_empresa, cap_elevador,
                      cap_noar, cap_tela, cap_como, cap_limites, lineup, cta, dl])

    # Carimbo de versão: data do build + sha do corpo. É o que o comercial confere
    # para saber se o PDF que ele tem na mão é o mesmo que está no ar.
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    sha = hashlib.sha1(body.encode()).hexdigest()[:7]
    foot = (f'<footer class="foot"><div class="foot-in">'
            f'<span class="foot-brand"><img src="/assets/wordmark-escuro.png" alt="Corpflix">'
            f'<span>mídia indoor gerenciada · <a href="{C.SITE}/privacidade">Privacidade</a></span></span>'
            f'<span>Livreto v{hoje} · {sha}</span></div></footer>')

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
    doc = head + body + "\n" + foot + "\n" + SCRIPT + "\n</body>\n</html>\n"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc)
    print(f"[livreto] {OUT} — {len(doc)//1024} KB · v{hoje} · {sha}")

build()
