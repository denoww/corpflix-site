# corpflix-site — playbook

Site institucional do **Corpflix** — TV de mídia indoor **gerenciada**: a gente instala o
player na TV do cliente, publica o conteúdo e monitora a tela. Estático, sem build de
framework. Servido por **GitHub Pages** em `https://www.corpflix.com.br`.

> ✅ **Tudo no `.com.br` desde 12/09/2026.** Em 11/09 o site passou a tarde em `www.corpflix.tv`,
> porque o Registro.br segurou a delegação; quando ela saiu, site, login (`app.`) e blog (`blog.`)
> voltaram pro domínio de venda. O `corpflix.tv` é só o redirect (repo `denoww/corpflix-tv`), e os
> hosts `.tv` seguem resolvendo pra quem salvou link daquele dia.

O produto é o **módulo de Publicidade do ERP SeuCondomínio** (`denoww/seucondominio`,
`app/services/publicidade/` + `app/models/publicidade/`) vendido com marca própria. Isso
define a regra prática: **a fonte da verdade do que pode ser prometido é o código de lá**,
não um pack de posicionamento. Nada entra na copy sem existir no ERP.

Três públicos, três pagadores — e por isso três páginas, não uma:

| Página | Público | Quem paga | O gancho |
|---|---|---|---|
| `/comercio` | sala de espera: restaurante, clínica, academia, salão, pet, loja | o dono do ponto | a tela vende a marca **dele** |
| `/corporativa` | comunicação interna: refeitório, corredor | o RH | **sem anunciante externo** (política de quem monta a grade) |
| `/elevador` | condomínio: elevador, hall | o síndico | comunicação com o morador; publicidade é upside |

`/corporativa` **não pode** ser fundida com `/comercio`: uma fala de anunciante, a outra
promete que não tem.

## Deploy

> **Deploy = `git push` em `main`.** Não existe passo separado.

GitHub Pages publica o `main` direto (~40–60s + CDN). Para conferir que produção já serve o
seu commit — não confie no "subiu":

```bash
diff <(curl -s https://www.corpflix.com.br/index.html) index.html && echo "prod == HEAD"
```

**Domínio:** o `CNAME` do repo é `www.corpflix.com.br` — é ele que define o host canônico.
O apex (`corpflix.com.br`) **redireciona para o www** (o Pages faz isso sozinho quando o apex
também aponta pros IPs dele). A zona **Route53 `Z00602744EG528NIKYXM`** está pronta: `www`
CNAME para `denoww.github.io`, apex com 4 registros A dos IPs do Pages (`185.199.108-111.153`).

⚠️ **Mas em 11/09/2026 essa zona NÃO estava valendo.** O Registro.br delegava o domínio para
`a.sec.dns.br`/`c.sec.dns.br` (o DNS do próprio Registro.br), que apontava `www` e apex para o
**Heroku** (`ssl-heroku.herokuapp.com`). Enquanto o NS do Registro.br não for trocado para os 4
`awsdns` da zona (`ns-1826.awsdns-36.co.uk`, `ns-907.awsdns-49.net`, `ns-1161.awsdns-17.org`,
`ns-311.awsdns-38.com`), o site não abre no domínio, o certificado do Pages não sai e o
`seo.yml` falha no `--http`. Confira sempre pelo DNS público, não pelo Route53:
`dig NS corpflix.com.br @a.dns.br +norecurse` e `dig +short www.corpflix.com.br`. O domínio **não manda
e-mail**: MX nulo (`0 .`), SPF `-all` e DMARC `p=reject` — não ponha e-mail `@corpflix.com.br`
na copy sem antes configurar caixa de verdade. Se um dia inverter o canônico, atualize junto: `canonical`, `og:url`,
`sitemap.xml`, `robots.txt` e o `BASE` do `seo.py` — senão eles apontam para uma URL que
redireciona.

⚠️ **Pages em `errored` não provisiona certificado.** Numa irmã, pushes seguidos geraram
deploys concorrentes, um falhou, e o site ficou horas em `"status": "errored"` — com o
certificado parado, sem nenhum aviso. Diagnóstico: `gh api repos/denoww/corpflix-site/pages`.
O conserto é um push que reconstrua; o relógio do certificado só corre com o status `built`.

⚠️ **`seo.py --http` falha até sair o certificado.** No primeiro deploy (e em qualquer troca
de domínio) o HTTPS do `www` ainda não existe e todo `<loc>` dá erro de conexão. URL nova vira
aviso, não erro — mas se o sitemap já listava a URL, o job fica vermelho até o cert emitir.
Não "conserte" tirando o `--http`: espere o cert e rode de novo.

## Estrutura

| O quê | Onde |
|---|---|
| Home (CSS + HTML + JS num arquivo) | `index.html` |
| Páginas de público | `comercio.html`, `corporativa.html`, `elevador.html` |
| Política de privacidade | `privacidade.html` |
| 404 (`noindex, follow`) | `404.html` |
| Livreto de vendas (gerado) | `livreto/` → `content.py` é 95% das mudanças; saída em `livreto/index.html` + `/livreto.pdf` |
| Imagens (nomes fixos, ver abaixo) | `assets/` |
| Guardas de CI | `.github/workflows/{guarda,seo,livreto}.yml` + `.github/scripts/seo.py` |

**Login (desde 11/09/2026): `.login` + `entrar.html` + pill "Entrar" no nav**, igual às irmãs.
O destino é o login do ERP **com a marca Corpflix** no host `app.corpflix.com.br` (caminho `/logar`,
com `?no_layout=true`) — o host é o tenant CloudFront `corpflix` na distribution multi-tenant `erpsc`, e o ERP reconhece
a marca pelo bloco `CORPFLIX` de `app/services/institucional/marcas.rb` (o registry aceita os dois
hosts, `app.corpflix.com.br` (canônico) e `app.corpflix.tv` (legado do dia da virada)). Quem entra é quem **opera** as telas (o time
da casa e os tenants liberados); o cliente final continua mandando a peça pelo WhatsApp — por isso
o "Entrar" é outline e o WhatsApp é o pill sólido.
- **Fonte da verdade:** o dotfile `.login` (sem newline no fim). A URL aparece 2× no
  `entrar.html` (meta refresh + `href` do `#ir`); o `guarda.yml` reprova se divergirem, se a
  ponte sumir ou se o `index.html` deixar de linkar `/entrar`, e faz um `curl` no destino como
  **aviso** (não erro — push de site não trava por ERP em deploy).
  ⚠️ Não escreva a URL completa do login em `.md`/`.html` fora desses lugares: o `guarda.yml`
  varre `*.md` também e reprova qualquer `https://…/logar…` que não seja idêntico ao `.login`.
- No nav escuro o texto do "Entrar" é o `--lilas` (#C9A7FF), não o `--roxo`: roxo sobre `--noite`
  reprova AA em 13px. Em ≤400px os dois pills encolhem o padding pra caber em 360px.

**Blog (desde 11/09/2026):** é o `Auto::Marcas::Corpflix` do ERP (post diário automático), servido
em `https://blog.corpflix.com.br`. O site só
linka: `<link rel="alternate">` do RSS no head das 4 páginas e "Blog"/"RSS" no rodapé (a
privacidade leva só "Blog"). Nasce **noindex** — o `SITEMAP_BLOG` do `seo.py` e o
`sitemap-index.xml` só recebem o blog **no flip** pra indexável (≥5 diários + 1 pilar revisados),
senão o `--http` e o Google recebem um sitemap de páginas `noindex`.

**Fonte única de contato:** o dotfile `.whatsapp` na raiz (dotfile não é publicado pelo
Pages). O `guarda.yml` reprova o push se algum `wa.me` do HTML ou o `telephone` do JSON-LD
divergir dele. Trocou de número? Edite `.whatsapp` e os literais — o guard aponta quais.

**Assets referenciados** (só estes; o `seo.py` reprova `/assets/…` que não existe em disco):
`brand-mark.png` · `wordmark.png` (branco, fundo escuro) · `wordmark-escuro.png` (fundo
claro) · `favicon-32.png` · `apple-touch-icon.png` · `og.jpg` (1200×630) · `hero.jpg` ·
`publico-comercio.jpg` · `publico-corporativa.jpg` · `publico-elevador.jpg`.

⚠️ Tudo em `assets/` entra no fingerprint do `livreto.yml` — arquivo novo lá dispara um PDF
novo e um commit do bot. Não deixe rascunho de imagem nessa pasta.

## Design — padrão Apple

Herdado dos sites irmãos (que tiraram os números do CSS de produção da apple.com):

- **Tipografia**: tracking **não-monotônico** — `-.015em` em 80px, ~zero em 40px,
  **positivo** (`+.011em`) em 21px, `-.022em` em 17px. Peso de título **600**, nunca 700.
- **Superfícies**: branco ↔ `#f5f5f7` ↔ escuro, alternando. **Sem borda entre seções** — o
  divisor é o contraste de fundo.
- **Cards**: radius 28px e **`box-shadow: none`**.
- **Botões**: pill `border-radius: 980px`, padding 12/22, peso 400; hover só troca a cor.
- **Movimento**: `opacity 0→1` + `translateY(30px)→0`, **900ms**, `cubic-bezier(.45,0,.55,1)`,
  stagger 150ms, dispara **uma vez** (IntersectionObserver + `unobserve`).
- **Tom**: frase curta, dor → alívio, sem jargão. Marca no texto é **"Corpflix"** (C maiúsculo).

**Sem Google Fonts e sem analytics (GA4 etc.), de propósito.** A stack começa em
`-apple-system`/`BlinkMacSystemFont` com Inter de fallback: webfont de terceiro no caminho
crítico por quase nada, e entregando o IP do visitante a um terceiro que a política de
privacidade teria de declarar.

### Tokens (nomes exatos)

| Token | Valor | Uso |
|---|---|---|
| `--roxo` | `#9100FF` | primária — **botão** (branco sobre ela = 5,76:1) |
| `--roxo-esc` | `#6A00E0` | hover e **texto pequeno colorido** (7,81:1) |
| `--roxo-leve` | `#F3E8FF` | fundo de selo |
| `--azul` | `#1886FF` | **só dentro do gradiente** |
| `--grad` | `linear-gradient(90deg,#9100FF,#1886FF)` | acento de marca |
| `--noite` | `#0A0716` | seções escuras |
| `--noite-2` | `#1F0E36` | seções escuras, fundo do app da TV |

Neutros iguais aos das irmãs (`--branco`, `--nevoa`, `--tinta`, `--tinta-2`…).

**A regra das duas cores:** `--roxo` é cor de **superfície** (botão, com texto branco em
tamanho de botão). Texto colorido **pequeno** usa `--roxo-esc`. E **`--azul` nunca é
superfície com texto**: branco sobre `#1886FF` dá 3,56:1, abaixo do AA — ele só existe como a
ponta direita do `--grad`. Se o texto sobre o gradiente for pequeno, a metade azul reprova.

## A regra que manda em tudo: só o que roda

**O que é real** (confirmado no código do ERP): cadastro de TVs, locais, playlists,
campanhas, grades e mídias (vídeo, imagem, áudio) · programação por dia da semana e horário
por item · conteúdo diferente por TV/ambiente/local (rede ou franquia no mesmo painel) ·
notícias (19 categorias, 8 fontes), clima da cidade da TV, cotações · 7 layouts (3 verticais),
6 resoluções, orientação · agenda de ligar/desligar a tela · heartbeat a cada 3 segundos,
alerta quando a TV passa de 1 hora fora do ar + resumo diário · reinício remoto do player ·
telemetria e crash report · continua tocando sem internet (cache no player) · não precisa
comprar servidor. Parque: **dezenas** de telas no ar — sem número exato.

⛔ **NUNCA prometer — porque não existe no ERP:**

| Promessa | Por que não |
|---|---|
| vetar categoria ou anunciante | não há entidade de anunciante nem trava de categoria; a restrição é combinada por contrato e aplicada por quem monta a grade |
| relatório / prova de veiculação / contagem de exibições | a coluna `exibidos` existe na UI, mas nada no backend a incrementa — fica zero |
| cobrança, boleto ou repasse de anunciante | não existe; o combinado comercial corre por fora |
| preço ou valor por exibição | o `R$ 0,025/exibição` da tela é conta do Angular que não persiste nem gera cobrança |
| "você mesmo publica pelo celular/painel" | quem publica é o nosso time. O verbo do cliente é **mandar**: "você manda, a gente publica" |
| aniversariantes ou comunicado automático do ERP na TV | não há integração ERP → TV; o recado é digitado no painel da mídia |
| "99,9%", "uptime", "nunca falha", "100%", "garantimos" | nenhum SLA medido sustenta; heartbeat e alerta são reais, garantia não |
| prova social (depoimento, nº de clientes, rating) | não temos o que citar — inventar é o pior tipo de mentira de site |
| concorrente pelo nome | envelhece mal e dá munição jurídica |

O guard `.github/scripts/seo.py` reprova o push que escrever qualquer uma. A frase honesta
que **nega** a promessa passa ("não existe relatório de veiculação"): o detector olha se há
negador antes do trecho, e as regras de produto usam `((?!\bn[ãa]o\b)[^.\n])` para aceitar o
"não" que cai **dentro** do trecho ("o relatório não existe"). Mexeu numa regra? Rode com uma
frase ruim **e** com a frase honesta equivalente — guard que reprova texto honesto é guard que
todo mundo aprende a ignorar.

## Cicatrizes (bugs reais dos sites irmãos, já cobertos aqui)

- **`git diff --quiet` não vê arquivo untracked.** O `livreto.yml` decidia assim se
  commitava o espelho; num repo novo o `livreto.pdf` nasce untracked, então o job gerava as
  páginas, passava no guard de página em branco e dizia "nada mudou" — `/livreto.pdf`
  respondia 404 sem nenhum workflow vermelho. Hoje usa `git status --porcelain`. Este repo
  **nasce** nessa situação: confira `/livreto.pdf` = 200 depois do primeiro push.
- **Pages em `errored`** trava o certificado em silêncio (ver Deploy).
- **Crop central decapita.** Foto 3:2 cortada para 16:9 perde topo e base — e é no topo que
  estão as cabeças. Âncora o recorte alto (~0.12), não no centro.
- **Referenciar asset que não existe não quebra nada visível.** Duas fotos foram para
  produção como `<img>` 404 dentro do PDF; o guard de página em branco não pega, porque a
  página tem texto. O `confere_assets` do `seo.py` cobre isso agora.
- **Foto de fundo atrás de texto no mobile** vira borrão. Texto em campo sólido, foto
  **inteira** embaixo. Não "resolva" com opacidade.
- **Evite scroll-snap horizontal em bloco alto** — no Chrome/Android o dedo fica preso.
- **Escopo de CSS vaza**: um `.ft a{text-decoration:underline}` grifou o logotipo do rodapé.
- **404 com a cor de outra marca.** A 404 é copiada entre irmãs e tem a cor da marca
  **literal** no CSS — uma delas ficou com o roxo de outra. Ao copiar, troque a cor.

## Imagens

**Doutrina: foto = gerador de imagem, UI = HTML/CSS.** Nunca peça interface ao gerador — ele
alucina texto e borra a tipografia. Tela de TV com conteúdo "no ar" na foto, só se o conteúdo
for composto por cima em HTML/CSS ou for ilegível na cena. **Amplie antes de aprovar**: numa
irmã, uma foto com o celular de costas para o próprio dono foi ao ar.

## Como verificar

- **Layout**: screenshot em **1440px e 412px**. Vários bugs só existem no mobile.
- **Guard**: `python3 .github/scripts/seo.py` local (precisa do repo git — lê `git ls-files`),
  e force uma violação de propósito para ver o vermelho: "um workflow que nunca foi executado
  não vale nada".
- **Contraste**: botão em `--roxo`, texto pequeno em `--roxo-esc`, nada de texto sobre `--azul`.
- **Produção**: compare o artefato local com o que o servidor entrega (o `diff` do topo), e
  `curl -sI https://www.corpflix.com.br/livreto.pdf` = 200.
