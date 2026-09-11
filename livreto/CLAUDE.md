# Livreto do Corpflix — playbook

Peça funda de vendas, servida em `/livreto/` com PDF espelho em `/livreto.pdf`
(download sai como `livreto-corpflix.pdf`). Um livreto só, com os três públicos em
capítulos próprios: comércio (sala de espera), empresa (refeitório, comunicação interna)
e condomínio (elevador).

## A regra de ouro

> **Edite `content.py` e dê push. NÃO rode `build.py` na mão.**

O CI (`.github/workflows/livreto.yml`) regenera o HTML, gera o PDF por Chromium headless,
**abre o PDF e mede** se alguma página saiu em branco, e commita o espelho de volta. Rodar o
build localmente não é errado — o CI só confirma que já estava em dia —, mas **editar
`livreto/index.html` à mão é**: é arquivo gerado, e o próximo push o sobrescreve.

⚠️ **`git diff --quiet` não enxerga arquivo untracked.** Num repo novo o `livreto.pdf` nasce
untracked; com `git diff` o job fica verde e o PDF nunca é commitado (`/livreto.pdf` → 404).
O passo de commit usa `git status --porcelain`.

## Onde editar

| Quero mudar | Arquivo |
|---|---|
| Texto dos cards, storyboards, dores, passos, "o que não faz" | `content.py` — 95% das mudanças |
| Quais capítulos entram, hero, CTA, SEO, JSON-LD, nav | `build.py` → `build()` |
| Cenas dos storyboards (SVG line-art: sala de espera, refeitório, elevador…) | `build.py` → `SCENES` |
| Cores e CSS de tela e de impressão | `build.py` → `CSS` |
| Número do WhatsApp | `../.whatsapp` (e mais nada) |

## Cores — os tokens do contrato da marca

`--roxo #9100FF` é botão (branco sobre ele = 5,76:1). **Texto pequeno colorido é sempre
`--roxo-esc #6A00E0`** (7,81:1) — por isso o `--sec` dos capítulos é roxo-esc, não roxo.
`--azul #1886FF` só existe **dentro** do `--grad`; nunca vira superfície com texto (3,56:1).
Texto em gradiente (`.g`) só em tamanho grande (credo, eyebrow do hero). Seções escuras usam
`--noite` / `--noite-2`. **Sem Google Fonts e sem analytics.**

## As 4 travas do `@media print` (quebram em silêncio)

1. **`.rev{opacity:1}`** — sem isto o PDF sai **EM BRANCO**: o reveal por scroll nunca
   dispara na impressão. É a falha nº 1 desta família de livretos.
2. **`print-color-adjust:exact`** — sem isto hero, CTA, gradiente e fotos saem sem cor.
3. **`break-inside:avoid` só nas unidades atômicas** (card, painel, passo). Nunca por
   capítulo — gera páginas quase vazias.
4. **`@page{size:A4}`** — sem isto o Chrome imprime em Letter.

Mais uma, desta peça: a folha A4 tem ~690px úteis, **abaixo do breakpoint de 860px**. Sem os
overrides de grade no `@media print` (`.publicos`, `.passos` em 3 colunas, `.mrow` em 2),
tudo vira uma coluna, o PDF passa de 21 páginas e a última sai só com o rodapé.

## Antes de adicionar uma foto

`foto("x")` gera `<img src="/assets/x.jpg">` sem validar nada. Se o arquivo não existir, a
página e o PDF ficam com imagem quebrada e **o workflow do livreto não reclama** (o guard de
página em branco só mede tinta, e texto conta). Use só os nomes do contrato de assets:
`hero`, `publico-comercio`, `publico-corporativa`, `publico-elevador` (+ `wordmark.png`,
`wordmark-escuro.png`, `favicon-32.png`, `apple-touch-icon.png`, `og.jpg`, `brand-mark.png`).

## Conteúdo: só o que roda

Fonte da verdade: o código do ERP (`app/models/publicidade/`, `app/services/publicidade/` no
repo `denoww/seucondominio`) e a seção "TVs / mídia indoor (Corpflix)" do `livreto/CLAUDE.md`
de lá. O cabeçalho do `content.py` lista os ⛔. Os que mais tentam voltar:

- **"Você mesmo publica pelo celular/painel"** — não. Quem publica é o time: *você manda, a
  gente publica*. (A copy do livreto do ERP diz o contrário; não copie de lá.)
- **Vetar categoria ou anunciante** — não existe trava no sistema; é combinado com o time.
- **Relatório/prova de veiculação, contagem de exibições** — `exibidos` nunca é incrementado.
- **Cobrança, boleto, repasse, preço, valor por exibição** — nada disso existe nem entra aqui.
- **Aniversariantes / comunicado de outro sistema automático na TV** — não existe.
- **"99,9%", "uptime", "nunca falha", "100%", "garantimos"**, prova social inventada,
  concorrente pelo nome. O parque é "dezenas de telas no ar" — sem número exato.
- Cotação é **dólar, euro e bitcoin** (moedas) + **Ibovespa e Nasdaq** (bolsa) — `GradesService#mount_finance_obj`. O comentário do `config/seo/institucional.yml` do ERP que diz "sem cotações" está desatualizado.

O capítulo `NAO_FAZ` existe para dizer os ⛔ em voz alta. O guard `seo.py` aceita o termo
proibido só se um **negador** ("não", "sem", "nenhum"…) vier **antes** dele, na mesma frase,
a até 60 caracteres. "Se o seu negócio depende de provar veiculação, ele não resolve" é
reprovado (o "não" vem depois); "Nenhuma prova de veiculação sai daqui" passa.

## Conferir localmente (opcional, antes do push)

```bash
python3 livreto/build.py && bash livreto/build_pdf.sh
pdfinfo livreto.pdf | egrep 'Pages|Page size'          # ≥ 8 páginas, A4
pdftoppm -jpeg -r 40 -f 5 -l 5 livreto.pdf /tmp/p5 && identify -format '%[standard-deviation]\n' /tmp/p5*.jpg   # > 1000
```
