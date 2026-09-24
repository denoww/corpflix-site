#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Avisa o Bing (IndexNow) das páginas que MUDARAM neste push.

POR QUE ISTO EXISTE
O canal medido das marcas é o assistente de IA — ~50% das sessões, contra ~5% do Google
(`ROADMAP_multi_produto.md` §8.6 no repo do ERP) — e o índice que o ChatGPT consulta é o
do Bing. Até 24/09/2026 este site não tinha sequer a CHAVE do IndexNow na raiz: ela só
existia nos hosts servidos pelo ERP (os blogs). Ou seja, publicar uma página aqui
significava esperar o rastreio acontecer sozinho.

Com a chave no lugar, o ping é uma requisição. O que sobrava era ninguém lembrar de
fazê-la — por isso ele roda no CI, no push da `main`, e não na mão.

O QUE ELE SUBMETE
Só o canonical das páginas cujo `.html` mudou no push (ou o sitemap inteiro com
`--tudo`). Submeter demais não é erro de protocolo, mas gasta reputação de host à toa.

FALHAR AQUI NÃO PODE QUEBRAR O DEPLOY: o site já está no ar quando isto roda. Todo erro
vira aviso, e o script sempre sai 0.
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CHAVE = '7b3e9c1a4f6d24b8e0a5c7d9f1234567'
ENDPOINT = 'https://api.indexnow.org/IndexNow'


def host() -> str:
    """O host canônico sai do CNAME — a mesma fonte que o GitHub Pages usa."""
    return (RAIZ / 'CNAME').read_text(encoding='utf-8').strip()


def canonical(arq: Path) -> str | None:
    m = re.search(r'rel="canonical"\s+href="([^"]+)"', arq.read_text(encoding='utf-8'))
    return m.group(1) if m else None


def html_mudados() -> list[Path]:
    """Os `.html` tocados pelo PUSH — não pelo último commit.

    ⚠️ A diferença importa. No CI este passo roda DEPOIS do job commitar o sitemap
    regenerado, então `HEAD~1..HEAD` seria o diff do commit do bot (só `sitemap.xml`) e o
    ping sairia vazio exatamente no push que criou a página. O SHA de antes do push chega
    em `GITHUB_EVENT_BEFORE`; `HEAD~1` fica só como plano B para rodar na mão.
    """
    antes = os.environ.get('GITHUB_EVENT_BEFORE', '')
    if not antes or set(antes) == {'0'}:            # push inicial de branch: sem "antes"
        antes = 'HEAD~1'
    saida = subprocess.run(['git', 'diff', '--name-only', antes, 'HEAD'],
                           cwd=RAIZ, capture_output=True, text=True)
    if saida.returncode != 0:
        return []
    return [RAIZ / p for p in saida.stdout.split()
            if p.endswith('.html') and (RAIZ / p).exists()]


def do_sitemap() -> list[str]:
    sm = RAIZ / 'sitemap.xml'
    if not sm.exists():
        return []
    return re.findall(r'<loc>([^<]+)</loc>', sm.read_text(encoding='utf-8'))


def main() -> int:
    h = host()
    if '--tudo' in sys.argv:
        urls = do_sitemap()
    else:
        urls = [u for u in (canonical(a) for a in html_mudados()) if u]

    if not urls:
        print('IndexNow: nenhuma página indexável mudou — nada a submeter')
        return 0

    corpo = json.dumps({
        'host': h,
        'key': CHAVE,
        'keyLocation': f'https://{h}/{CHAVE}.txt',
        'urlList': sorted(set(urls)),
    }).encode('utf-8')

    req = urllib.request.Request(ENDPOINT, data=corpo,
                                 headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            codigo = r.status
    except urllib.error.HTTPError as e:
        codigo = e.code
    except Exception as e:                                   # rede, DNS, timeout
        print(f'::warning::IndexNow não respondeu ({e}) — o site está no ar do mesmo jeito')
        return 0

    for u in sorted(set(urls)):
        print(f'  · {u}')
    if codigo in (200, 202):
        print(f'IndexNow: {len(set(urls))} URL(s) aceitas (HTTP {codigo})')
    elif codigo == 403:
        # A causa quase sempre é a chave sumindo da raiz — foi o estado deste site até 24/09.
        print(f'::warning::IndexNow devolveu 403 — confira https://{h}/{CHAVE}.txt')
    else:
        print(f'::warning::IndexNow devolveu HTTP {codigo}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
