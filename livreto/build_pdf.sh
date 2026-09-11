#!/usr/bin/env bash
# Gera livreto.pdf a partir do HTML já buildado.
#
#   bash livreto/build_pdf.sh
#
# VOCÊ NÃO PRECISA RODAR ISTO NA MÃO. O CI (.github/workflows/livreto.yml) regenera
# HTML+PDF a cada push que toca a fonte e commita o espelho — é a "regra de ouro" do
# roadmap do livreto: espelho automático, sem humano.
#
# Este script existe pra (a) o CI chamar e (b) você conferir o PDF localmente antes
# de dar push. O que ele produzir local pode diferir em bytes do que o CI produz
# (versão de Chrome diferente) — quem manda é o CI.
#
# Por que CI e não runtime: o SeuCondomínio gera sob demanda (Gotenberg, cache por
# hash do HTML), mas isso exige um servidor. Este site é estático (GitHub Pages, sem
# runtime), então o espelho acontece no CI.
#
# --print-to-pdf respeita o `@media print` (as 4 travas estão em build.py > CSS).
# --no-pdf-header-footer tira o "about:blank / data" que o Chrome carimba por padrão.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HTML="$ROOT/livreto/index.html"
PDF="$ROOT/livreto.pdf"

[ -f "$HTML" ] || { echo "HTML não existe — rode 'python3 livreto/build.py' antes."; exit 1; }

# serve local: file:// quebra as imagens absolutas (/assets/...) do livreto
python3 -m http.server 8891 --directory "$ROOT" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT
sleep 1

google-chrome \
  --headless=new \
  --disable-gpu \
  --no-sandbox \
  --no-pdf-header-footer \
  --print-to-pdf="$PDF" \
  --virtual-time-budget=10000 \
  "http://localhost:8891/livreto/" >/dev/null 2>&1

[ -s "$PDF" ] || { echo "PDF saiu vazio."; exit 1; }
echo "[livreto] $PDF — $(du -h "$PDF" | cut -f1)"
