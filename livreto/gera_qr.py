#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera `livreto/qr_whatsapp.svg` — o QR da contracapa, apontando pro WhatsApp com text= próprio.

    python3 livreto/gera_qr.py

Rodar SÓ quando mudar o número (`.whatsapp`) ou o texto (`content.py > WA_QR_TXT`).
O SVG é commitado: o runner do CI não tem a lib `qrcode`, e o `build.py` só lê o arquivo.
Um guard no `build.py` compara a URL gravada no SVG com a atual e aborta se divergir —
QR velho apontando pra número antigo é o tipo de erro que só aparece no celular do cliente.
"""
import importlib.util, pathlib
import qrcode

ROOT = pathlib.Path(__file__).resolve().parent
sp = importlib.util.spec_from_file_location("content", str(ROOT / "content.py"))
C = importlib.util.module_from_spec(sp); sp.loader.exec_module(C)

url = C.WA + C.WA_QR_TXT
q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
q.add_data(url); q.make(fit=True)
m = q.get_matrix(); n = len(m)
d = "".join(f"M{x} {y}h1v1h-1z" for y, row in enumerate(m) for x, v in enumerate(row) if v)
svg = (f'<!-- url: {url} -->\n'
       f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges">'
       f'<path fill="#0A0716" d="{d}"/></svg>\n')
(ROOT / "qr_whatsapp.svg").write_text(svg)
print(f"[qr] {n}x{n} → {url}")
