// ============================================================================
// A TV do Corpflix tocando (ver tv-demo.css). Um roteiro JSON por página, dentro
// da própria TV: <script type="application/json" class="tvd-roteiro">.
//
// Comportamento copiado do player real (midia_indoor_player/player.coffee):
//   - cada peça fica `segundos` na tela e troca por CORTE SECO;
//   - a cada troca, spinner de 900 ms no canto do conteúdo;
//   - a manchete do rodapé troca no lugar a cada peça;
//   - data, dia da semana e relógio HH:mm são os do visitante.
// Pausa fora da tela e com a aba escondida. Com prefers-reduced-motion fica
// parada na primeira peça.
// ============================================================================
(function () {
  'use strict';

  var DIAS = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
  var MESES = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'];
  var SPINNER_MS = 900;
  // QR de https://www.corpflix.com.br — uma linha hexadecimal por fileira de módulos.
  var QR = ["1fc2e47f", "10562941", "175d525d", "175e695d", "1744ef5d", "104fd041", "1fd5557f", "001e8300", "10596ece", "0a374f36", "0b420880", "13b574e8", "1ee8c061", "1d07c753", "19defd6c", "160fd5b5", "14746a2c", "1b3a13f7", "18ffd7c9", "14857570", "12e117f7", "00109d18", "1fcdfb5c", "104b8f13", "1748bbfa", "174595ae", "1747467e", "104f606d", "1fd096bc"];

  var reduz = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }
  function dois(n) { return n < 10 ? '0' + n : '' + n; }

  function qrSvg() {
    var n = QR.length, d = '';
    for (var y = 0; y < n; y++) {
      var bits = BigIntLike(QR[y], n);
      for (var x = 0; x < n; x++) if (bits[x]) d += 'M' + x + ' ' + y + 'h1v1h-1z';
    }
    return '<svg viewBox="0 0 ' + n + ' ' + n + '" shape-rendering="crispEdges" aria-hidden="true"><path fill="#111" d="' + d + '"/></svg>';
  }
  // hex → vetor de bits com `n` posições (sem BigInt, pra rodar em navegador antigo)
  function BigIntLike(hex, n) {
    var bits = [];
    for (var i = 0; i < hex.length; i++) {
      var v = parseInt(hex.charAt(i), 16);
      bits.push((v >> 3) & 1, (v >> 2) & 1, (v >> 1) & 1, v & 1);
    }
    return bits.slice(bits.length - n);
  }

  function hoje() {
    var d = new Date();
    return { dia: d.getDate(), mes: MESES[d.getMonth()], semana: DIAS[d.getDay()],
             hora: dois(d.getHours()) + ':' + dois(d.getMinutes()),
             data: dois(d.getDate()) + '/' + dois(d.getMonth() + 1) + '/' + d.getFullYear() };
  }

  function montarPeca(p, qr) {
    var peca = el('div', 'tvd-peca tvd-' + p.tipo);
    if (p.tipo === 'cliente') {
      var f = el('div', 'tvd-fundo');
      f.style.background = p.fundo;
      peca.appendChild(f);
      var t = el('div', 'tvd-txt');
      if (p.olho) t.appendChild(el('span', 'tvd-olho', p.olho));
      t.appendChild(el('span', 'tvd-tit', p.titulo));
      peca.appendChild(t);
    } else if (p.tipo === 'noticia') {
      var foto = el('div', 'tvd-fundo');
      foto.setAttribute('data-foto', p.foto);
      peca.appendChild(foto);
      var topo = el('div', 'tvd-topo');
      topo.appendChild(el('span', 'tvd-fonte', p.fonte || 'N'));
      topo.appendChild(el('span', 'tvd-cat', p.categoria));
      peca.appendChild(topo);
      var faixa = el('div', 'tvd-faixa');
      faixa.appendChild(el('b', null, p.manchete));
      faixa.appendChild(el('small', 'tvd-hoje'));
      peca.appendChild(faixa);
      var q = el('div', 'tvd-qr');
      q.innerHTML = qr;
      q.appendChild(el('small', null, 'NOTÍCIA COMPLETA'));
      peca.appendChild(q);
    } else if (p.tipo === 'info') {
      peca.appendChild(el('div', 'tvd-deco'));
      var c = el('div', 'tvd-cartao');
      c.appendChild(el('b', null, p.titulo));
      c.appendChild(el('span', null, p.texto));
      peca.appendChild(c);
    }
    return peca;
  }

  function iniciar(tv) {
    var fonte = tv.querySelector('script.tvd-roteiro');
    if (!fonte) return;
    var cfg;
    try { cfg = JSON.parse(fonte.textContent); } catch (e) { return; }

    var main = tv.querySelector('.tvd-main');
    var spin = el('div', 'tvd-spin');
    var qr = qrSvg();
    var pecas = cfg.pecas.map(function (p) { return montarPeca(p, qr); });

    // troca o conteúdo estático (a peça 1 que já veio no HTML) pelo roteiro inteiro
    main.textContent = '';
    pecas.forEach(function (p) { main.appendChild(p); });
    main.appendChild(spin);

    var rodapeCat = tv.querySelector('.tvd-msg small');
    var rodapeTxt = tv.querySelector('.tvd-msg b');
    var eDia = tv.querySelector('.tvd-dia b'), eMes = tv.querySelector('.tvd-dia small');
    var eSemana = tv.querySelector('.tvd-semana'), eHora = tv.querySelector('.tvd-hora');

    function relogio() {
      var h = hoje();
      eDia.textContent = h.dia; eMes.textContent = h.mes;
      eSemana.textContent = h.semana; eHora.textContent = h.hora;
      var datas = tv.querySelectorAll('.tvd-hoje');
      for (var i = 0; i < datas.length; i++) datas[i].textContent = h.data;
    }

    var idx = -1, decorrido = 0, visivel = true;
    var passo = (cfg.segundos || 8) * 1000;

    function mostrar(i) {
      var anterior = pecas[idx];
      if (anterior) anterior.classList.remove('ativa');
      idx = i % pecas.length;
      var p = pecas[idx];
      var foto = p.querySelector('[data-foto]');
      if (foto && !foto.style.backgroundImage) foto.style.backgroundImage = 'url(' + foto.getAttribute('data-foto') + ')';
      // reinicia o zoom: sem o reflow a animação não recomeça na 2ª volta
      var fundo = p.querySelector('.tvd-fundo');
      if (fundo) { fundo.style.animation = 'none'; void fundo.offsetWidth; fundo.style.animation = ''; }
      p.classList.add('ativa');
      var m = cfg.manchetes[idx % cfg.manchetes.length];
      rodapeCat.textContent = m.categoria;
      rodapeTxt.textContent = m.texto;
      tv.setAttribute('data-peca', idx);
      if (!reduz) {
        spin.classList.add('on');
        setTimeout(function () { spin.classList.remove('on'); }, SPINNER_MS);
      }
    }

    relogio();
    mostrar(0);
    if (reduz) return;

    // pré-carrega as fotos das notícias depois que a página terminou de carregar
    window.addEventListener('load', function () {
      cfg.pecas.forEach(function (p) { if (p.foto) { var im = new Image(); im.src = p.foto; } });
    });

    function rodando() { return visivel && !document.hidden; }
    function atualizaPausa() { tv.classList.toggle('pausado', !rodando()); }

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        visivel = es[0].isIntersecting;
        atualizaPausa();
      }, { threshold: 0.15 }).observe(tv);
    }
    document.addEventListener('visibilitychange', atualizaPausa);

    var TICK = 250;
    setInterval(function () {
      if (!rodando()) return;
      decorrido += TICK;
      if (decorrido % 15000 < TICK) relogio();
      if (decorrido % passo < TICK) mostrar(idx + 1);
    }, TICK);
  }

  function boot() {
    var tvs = document.querySelectorAll('.tvdemo');
    for (var i = 0; i < tvs.length; i++) iniciar(tvs[i]);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
