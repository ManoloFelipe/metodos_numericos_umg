/* ═══════════════════════════════════════
   PASO A PASO — Bisección
   ═══════════════════════════════════════ */
(function () {
  const dataEl = document.getElementById('pap-data');
  if (!dataEl) return;
  const { iteraciones, raiz } = JSON.parse(dataEl.textContent);
  if (!iteraciones || iteraciones.length === 0) return;

  let actual = 0, modoTodo = false;

  function htmlPaso(it, idx) {
    const esUltimo = idx === iteraciones.length - 1;

    let decision;
    if (it.producto === 0)
      decision = "f(xi)·f(xm) = 0 → <strong style='color:var(--accent)'>Raíz exacta en xm</strong>";
    else if (it.producto > 0)
      decision = "f(xi)·f(xm) > 0 → la raíz está en [xm, xf] → <strong>xi = xm</strong>";
    else
      decision = "f(xi)·f(xm) < 0 → la raíz está en [xi, xm] → <strong>xf = xm</strong>";

    const lineas = [
      { lbl: 'Intervalo actual',      eq: `xi = <strong>${it.xi}</strong>, xf = <strong>${it.xf}</strong>` },
      { lbl: 'Calcular xm',           eq: `xm = (${it.xi} + ${it.xf}) / 2 = <strong>${it.xm}</strong>` },
      { lbl: 'Evaluar f(xi)',         eq: `f(${it.xi}) = <strong>${it.fxi}</strong>` },
      { lbl: 'Evaluar f(xm)',         eq: `f(${it.xm}) = <strong>${it.fxm}</strong>` },
      { lbl: 'Producto f(xi)·f(xm)',  eq: `${it.fxi} × ${it.fxm} = <strong>${it.producto}</strong>` },
      { lbl: 'Decisión',              eq: decision },
      { lbl: 'Error',                 highlight: true, eq:
          `error = (xm − xi) / xm × 100<br>` +
          `= (${it.xm} − ${it.xi}) / ${it.xm} × 100<br>` +
          `= <strong class="pap-resultado">${it.error}%</strong>` },
    ];

    if (esUltimo && raiz !== null)
      lineas.push({ lbl: 'Raíz encontrada', raiz: true, eq: `x ≈ <strong>${raiz}</strong>` });

    return _htmlPasoBase(it, esUltimo, raiz, lineas);
  }

  _initPap({
    iteraciones, raiz, htmlPaso,
    btnAbrir:   document.getElementById('btn-paso-a-paso'),
    seccion:    document.getElementById('pap-seccion'),
    contenedor: document.getElementById('pap-contenedor'),
    btnPrev:    document.getElementById('pap-prev'),
    btnNext:    document.getElementById('pap-next'),
    btnVerTodo: document.getElementById('pap-ver-todo'),
    contador:   document.getElementById('pap-contador'),
    getActual:    () => actual,
    setActual:    (v) => { actual = v; },
    getModoTodo:  () => modoTodo,
    setModoTodo:  (v) => { modoTodo = v; },
  });
})();
