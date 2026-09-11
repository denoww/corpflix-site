# -*- coding: utf-8 -*-
"""Conteúdo do livreto do Corpflix — 95% das mudanças acontecem AQUI.

VOCÊ SÓ PRECISA EDITAR ESTE ARQUIVO. O HTML e o PDF se regeneram sozinhos no CI
(.github/workflows/livreto.yml) assim que você der push — o PDF é um ESPELHO
automático. Não rode build.py nem build_pdf.sh na mão; se rodar, o CI só confirma
que já estava em dia. O CI ainda abre o PDF e barra o build se alguma página sair
EM BRANCO (a falha clássica do @media print, que quebra em silêncio).

Fonte da verdade factual, nesta ordem de precedência (repo do ERP, denoww/seucondominio):
  1. O código: `app/models/publicidade/` e `app/services/publicidade/`. É lá que se
     confere o que existe — layouts, resoluções, feeds, heartbeat, alerta, restart.
  2. `livreto/CLAUDE.md` do ERP, seção "TVs / mídia indoor (Corpflix)" — as proibições
     já auditadas contra o código.
  3. `livreto/build/content.py` do ERP (TV_COM, TV_CORP, TV_ELEV, TV_OPS e o storyboard
     `tv_rede`) — a mesma copy, na voz do produto inteiro. ⚠️ Ela tem duas frases que
     NÃO podem vir para cá: "você troca de onde estiver pelo celular" e "você veta o que
     não quer". Nenhuma das duas é verdade para o cliente do Corpflix.

⛔ REGRAS DE COPY — o que NÃO pode ser prometido (conferido no código em 2026-09-11).
   O guard `.github/scripts/seo.py` reprova o push que escrever qualquer uma sem negar:

  • Vetar categoria ou anunciante. Não existe entidade de anunciante nem trava no
    sistema. A restrição é combinada com o time e respeitada na montagem da grade.
  • Relatório ou prova de veiculação, contagem de exibições. A coluna `exibidos`
    existe na tela e nada no backend a incrementa — fica zero.
  • Cobrança, boleto ou repasse de anunciante. O "R$ 0,025 por exibição" é conta do
    front e não persiste. Nada de preço nem valor por exibição neste livreto.
  • "Você mesmo publica pelo celular/painel". Quem publica é o time: você manda, a gente
    publica.
  • Aniversariantes, ou comunicado de outro sistema indo automático para a TV.
  • "99,9%", "uptime", "nunca falha", "100%", "garantimos".
  • Prova social inventada (depoimento, número de clientes, nota) e concorrente pelo nome.
    O parque tem dezenas de telas no ar — não cite número exato.
  • Cotação é dólar, euro e bitcoin + Ibovespa e Nasdaq (`GradesService#mount_finance_obj`).
"""

# O número vive em UM lugar só: o arquivo `.whatsapp` na raiz do repo. Dotfile não é
# publicado pelo GitHub Pages, e o workflow `guarda.yml` barra o push se algum `wa.me`
# do HTML divergir dele. Trocou de número? Edite `.whatsapp` e mais nada aqui.
from pathlib import Path

WA = "https://wa.me/" + (Path(__file__).parent.parent / ".whatsapp").read_text().strip()
WA_TXT = "?text=Ol%C3%A1!%20Vi%20o%20livreto%20do%20Corpflix%20e%20quero%20saber%20mais."
SITE = "https://www.corpflix.com.br"

# ---------------------------------------------------------------- hero / credo
HERO = {
    "eyebrow": "Livreto",
    "h1": "A tela que já está na parede, trabalhando para você.",
    "sub": "A gente instala o player na sua TV, publica o que você quer mostrar e vigia a "
           "tela de longe. Para a sala de espera do seu negócio, o refeitório da sua empresa "
           "e o elevador do seu prédio.",
}

CREDO = ('Você manda, a gente publica — e fica de olho para que a tela '
         '<span class="g">não apague sem ninguém ver</span>.')

# ---------------------------------------------------------------- storyboards
# (chave, capítulo-cor, título, [(cena, título, legenda)])
# As cenas vivem em build.py > SCENES — a chave tem que casar 1:1.
BOARDS = {
    "comercio": ("roxo", "Da sala de espera à promoção do dia", [
        ("espera",  "O cliente senta",        "E olha para a tela — é o único lugar para onde olhar enquanto espera."),
        ("pedido",  "Você manda a peça",      "Cardápio, promoção, vídeo novo. Você manda, a gente publica."),
        ("grade",   "Entra na hora certa",    "O almoço executivo ao meio-dia, o happy hour às dezoito."),
        ("rede",    "Uma loja ou a rede",     "Cada unidade com o conteúdo dela, no mesmo painel."),
    ]),
    "empresa": ("roxo", "Do recado do RH ao intervalo do café", [
        ("refeitorio", "O time para no refeitório", "Quem não senta na frente de um computador passa por aqui todo dia."),
        ("pedido",     "O RH manda o recado",       "Campanha, mudança de processo, regra de convivência."),
        ("rede",       "Cada ambiente com o seu",   "Refeitório, recepção e corredor podem mostrar coisas diferentes."),
        ("grade",      "No turno certo",            "O aviso do turno da noite entra à noite."),
    ]),
    "elevador": ("roxo", "Do aviso do síndico à cabine", [
        ("elevador", "Todo morador entra",   "Inclusive quem nunca abre o aplicativo nem lê o mural."),
        ("pedido",   "O síndico manda",      "Manutenção da bomba, assembleia, regra da piscina."),
        ("grade",    "Só na semana certa",   "O aviso da manutenção sai da grade quando a manutenção acaba."),
        ("lua",      "A tela dorme",         "Agenda de ligar e desligar: nada de tela acesa às três da manhã."),
    ]),
    "noar": ("noite", "Da tela calada ao aviso para o nosso time", [
        ("pulso",    "A tela avisa que está viva", "Cada TV dá sinal ao servidor a cada três segundos."),
        ("alerta",   "Calou, a gente sabe",        "Mais de uma hora fora do ar vira alerta para o nosso time."),
        ("reinicio", "Reinicia de longe",          "Travou? O player é reiniciado do painel, sem visita."),
        ("resumo",   "Todo dia, o resumo",         "Quem caiu, quem voltou — antes de alguém reclamar."),
    ]),
    "rede": ("roxo", "Do seu pedido à tela, sem pendrive", [
        ("instala", "A gente instala",          "O player vai na TV que você já tem, ou num aparelho pequeno ligado a ela."),
        ("pedido",  "Você manda",               "Vídeo, imagem, áudio ou um recado escrito."),
        ("grade",   "A gente programa",         "Dia da semana e horário, peça por peça."),
        ("tvtroca", "A tela troca sozinha",     "Publicada, a peça chega na TV em segundos."),
        ("offline", "E aguenta a internet cair","O conteúdo fica guardado no player e a tela segue tocando."),
    ]),
}

# ---------------------------------------------------------------- capítulos
# (título, descrição, selo)  — selo "" = produção. Nunca vender roadmap como pronto.
COMERCIO = [
    ("A tela deixa de ser TV aberta",
     "Nada de novela, jornal da tarde ou anúncio de outra loja rodando na sua sala de espera. "
     "Quem está esperando olha para o que é seu.", ""),
    ("Sua marca o tempo todo",
     "Cardápio, promoção do dia, serviço novo, vídeo institucional — o que você quer vender, "
     "no loop.", ""),
    ("Você manda, a gente publica",
     "Mudou o preço, entrou um prato novo? Você manda a peça para o nosso time e ele publica. "
     "Ninguém vai até a loja com pendrive.", ""),
    ("Promoção com hora marcada",
     "O happy hour entra às dezoito, o almoço executivo só ao meio-dia, o fim de semana tem a "
     "sua própria grade. Cada peça tem dia e horário.", ""),
    ("A espera passa mais rápido",
     "Notícias, clima da cidade e cotação do dólar preenchem o intervalo — o cliente para de "
     "olhar o relógio.", ""),
    ("Uma tela ou a rede inteira",
     "Franquia e rede ficam no mesmo painel, com o conteúdo de cada unidade — a promoção de "
     "uma cidade não aparece na outra.", ""),
]

EMPRESA = [
    ("O aviso chega a quem não lê e-mail",
     "A produção, a portaria, a cozinha, o depósito. Quem não senta na frente de um computador "
     "passa pela tela.", ""),
    ("Regra de convivência à vista",
     "O combinado do refeitório, do corredor e da área de serviço fica exposto onde a regra "
     "vale — não num manual que ninguém abriu.", ""),
    ("Novidade, campanha e recado",
     "Lançamento, mudança de processo, campanha interna, recado da diretoria. O RH manda, a "
     "gente publica.", ""),
    ("A tela é só da empresa",
     "Nenhum anunciante de fora entra na grade de uma empresa: ela é montada só com o que o "
     "RH mandou, mais notícias, clima e cotações.", ""),
    ("Cada ambiente com o seu conteúdo",
     "Refeitório, recepção, sala de reunião e corredor podem exibir coisas diferentes, no mesmo "
     "painel.", ""),
    ("Programado por turno",
     "O aviso do turno da noite entra à noite. Dia da semana e horário, peça por peça.", ""),
]

ELEVADOR = [
    ("O recado que ninguém escapa",
     "Todo morador entra no elevador. O aviso alcança quem nunca abre o aplicativo nem para "
     "diante do mural.", ""),
    ("O síndico manda, a gente publica",
     "Manutenção, assembleia, regra nova da piscina. O recado é escrito para a tela e entra na "
     "cabine em segundos, sem trocar cartaz.", ""),
    ("Programado por horário",
     "Cada peça entra no dia e na hora combinados — o aviso de manutenção só na semana da "
     "manutenção.", ""),
    ("Notícias, clima e cotações",
     "O morador informado enquanto espera: manchetes de oito veículos, a previsão do tempo da "
     "cidade e o dólar do dia.", ""),
    ("Vertical ou horizontal",
     "Sete layouts, três deles com a tela em pé — o formato se adapta ao que cabe na cabine.", ""),
    ("O espaço pode virar receita",
     "O condomínio pode ceder parte do tempo ao comércio da região. A grade separa o que é "
     "anúncio do que é utilidade; o contrato com quem anuncia é combinado por fora.", ""),
]

# Operação/telemetria — o diferencial real, igual pros três públicos.
OPERACAO = [
    ("A tela avisa que está viva",
     "Cada TV dá sinal ao servidor a cada três segundos. Ninguém descobre que a tela apagou "
     "pelo cliente.", ""),
    ("Alerta quando cai",
     "Tela fora do ar por mais de uma hora vira alerta para o nosso time — e todo dia sai um "
     "resumo de quem caiu e quem voltou.", ""),
    ("Reinício à distância",
     "Travou? O player é reiniciado do painel, sem alguém subir até o elevador ou atravessar a "
     "cidade até a loja.", ""),
    ("Aguenta a internet cair",
     "O conteúdo fica guardado no próprio player: o link cai e a tela continua tocando o que já "
     "tinha baixado.", ""),
    ("Diagnóstico do aparelho",
     "Versão instalada, espaço em disco, tempo ligado e as falhas do player chegam até a gente "
     "sem ir até o local.", ""),
    ("Você não compra servidor",
     "O conteúdo vive na nuvem. Na ponta, uma TV com Android ou um aparelho pequeno ligado a "
     "qualquer tela.", ""),
]

# O que roda na tela — a caixa de ferramentas da grade.
TELA = [
    ("Vídeo, imagem e áudio",
     "A peça que você já tem serve: o vídeo institucional, a arte da promoção, a trilha da loja.", ""),
    ("Notícias de oito veículos",
     "Dezenove categorias, de economia a esporte, trazidas de oito fontes de notícia — o "
     "assunto do dia sem ninguém digitar.", ""),
    ("O clima da cidade da TV",
     "Cada tela mostra a previsão da cidade onde está, não da capital.", ""),
    ("Cotações do dia",
     "Dólar, euro, bitcoin, Ibovespa e Nasdaq na tela, atualizados sozinhos.", ""),
    ("Sete layouts",
     "Tela cheia ou com barras de informação — e três formatos verticais, para a TV em pé.", ""),
    ("Seis resoluções",
     "Do painel em alta definição ao monitor mais antigo, na horizontal ou girado.", ""),
    ("Agenda de ligar e desligar",
     "Por dia da semana: a tela acende quando a loja abre e dorme quando fecha.", ""),
    ("Programação peça por peça",
     "Cada item da grade tem os seus dias e horários. O que não é hora, não passa.", ""),
]

# Os 3 públicos, lado a lado: (foto /assets/<slug>.jpg, rótulo, quem paga e por quê)
PUBLICOS = [
    ("publico-comercio",    "Comércio e serviço",
     "Restaurante, clínica, academia, salão, pet, loja. O dono do ponto quer a sala de espera "
     "vendendo o que é dele."),
    ("publico-corporativa", "Empresa",
     "Refeitório, corredor e recepção. O RH quer o recado chegando a quem não abre e-mail."),
    ("publico-elevador",    "Condomínio",
     "Elevador e hall. O síndico quer o aviso lido por todo morador, não só por quem abre o app."),
]

DORES = [
    "A TV da sala de espera passa novela — ou o anúncio da loja do outro lado da rua.",
    "A promoção mudou há duas semanas e a tela ainda mostra a antiga, porque alguém tem que ir até lá com pendrive.",
    "O comunicado do RH foi por e-mail para quem não tem e-mail.",
    "O aviso da manutenção ficou colado no elevador um mês depois da manutenção.",
    "A tela apagou na terça, e alguém só percebeu na sexta — quando o cliente comentou.",
]

# Como funciona — três passos, sem jargão: (título, descrição)
PASSOS = [
    ("A gente instala",
     "O player vai na TV que você já tem, ou num aparelho pequeno ligado a ela. Não tem "
     "servidor para comprar."),
    ("Você manda, a gente publica",
     "Você manda a peça e diz quando ela deve passar. O nosso time monta a grade e publica."),
    ("A gente vigia a tela",
     "Cada tela dá sinal a cada três segundos. Se calar, o nosso time é avisado e age de longe."),
]

# ---------------------------------------------------------------- honestidade
# O capítulo mais importante do livreto. Nunca vender roadmap como pronto: se não
# roda hoje, está aqui. Cada item foi conferido no código do ERP (app/models/publicidade).
# ⚠️ O guard seo.py só aceita o termo proibido se um "não/sem/nenhum" vier ANTES dele,
# na mesma frase, a até 60 caracteres. Reescreveu? Mantenha o negador na frente.
NAO_FAZ = [
    ("Não é painel para você operar sozinho",
     "Quem publica é o nosso time. Não existe login para você mesmo subir a peça pelo celular: "
     "você manda, a gente publica — e cuida da grade junto.", ""),
    ("Não gera relatório de veiculação",
     "O sistema não conta quantas vezes cada peça passou nem emite comprovante de exibição. "
     "Nenhuma prova de veiculação sai daqui para mostrar a um anunciante.", ""),
    ("Não cobra o anunciante",
     "Não há boleto, repasse nem divisão de receita dentro do sistema. Se a tela tiver espaço "
     "vendido, o contrato e a cobrança correm por fora.", ""),
    ("Não trava anunciante automaticamente",
     "Não existe filtro no sistema que bloqueie uma categoria ou uma marca. O que não pode "
     "aparecer na sua tela é combinado com o nosso time e respeitado na montagem da grade.", ""),
    ("Não puxa comunicado de outro sistema",
     "O recado é escrito para a tela. Nenhum aviso de e-mail, mural ou aplicativo vai para a TV "
     "sozinho — e não há lista de aniversariantes automática.", ""),
    ("Não mede audiência",
     "Nenhuma câmera conta quem olhou para a tela. O que a gente acompanha é se ela está ligada "
     "e tocando.", ""),
    ("Não toca conteúdo novo sem internet",
     "Sem link, a tela segue com o que já tinha baixado. A peça nova chega quando a conexão "
     "volta — e sem energia, naturalmente, não há tela.", ""),
]

# ---------------------------------------------------------------- lineup
# (nome, descrição, selo)
TILES = [
    ("Player instalado",      "Na TV que você já tem ou num aparelho pequeno.", ""),
    ("Você manda",            "E o nosso time publica e monta a grade.",        ""),
    ("Grade por horário",     "Dia da semana e hora, peça por peça.",           ""),
    ("Conteúdo por tela",     "Loja, ambiente ou cabine, cada um com o seu.",   ""),
    ("Notícias e clima",      "Oito veículos, dezenove categorias, a cidade da TV.", ""),
    ("Cotações",              "Dólar, euro, bitcoin, Ibovespa e Nasdaq.", ""),
    ("Tela em pé",            "Sete layouts, três verticais, seis resoluções.",  ""),
    ("Sinal a cada 3 s",      "Alerta depois de uma hora fora e resumo diário.", ""),
    ("Toca sem internet",     "O conteúdo fica guardado no player.",             ""),
]

CTA = ("Vamos acender a sua tela.",
       "Conte onde ela fica e o que você quer mostrar. A gente instala, publica e cuida para "
       "ela não apagar sem ninguém ver.")
