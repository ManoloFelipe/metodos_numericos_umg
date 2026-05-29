/* ═══════════════════════════════════════
   PASO A PASO — Newton-Raphson
   ═══════════════════════════════════════ */
(function () {
  const dataEl = document.getElementById('pap-data');
  if (!dataEl) return;
  const { iteraciones, raiz } = JSON.parse(dataEl.textContent);
  if (!iteraciones || iteraciones.length === 0) return;

  let actual = 0, modoTodo = false;

  function htmlPaso(it, idx) {
    const esUltimo = idx === iteraciones.length - 1;
    const paso     = parseFloat((it.fxi / it.dfxi).toFixed(8));
    const lineas   = [
      { lbl: 'Valor actual',    eq: `x<sub>${it.n-1}</sub> = <strong>${it.xi}</strong>` },
      { lbl: 'Evaluar f(x)',    eq: `f(${it.xi}) = <strong>${it.fxi}</strong>` },
      { lbl: "Evaluar f'(x)",   eq: `f'(${it.xi}) = <strong>${it.dfxi}</strong>` },
      { lbl: 'Aplicar fórmula', highlight: true, eq:
          `x<sub>${it.n}</sub> = x<sub>${it.n-1}</sub> − f(x) / f'(x)<br>` +
          `= ${it.xi} − (${it.fxi}) / (${it.dfxi})<br>` +
          `= ${it.xi} − (${paso})<br>` +
          `= <strong class="pap-resultado">${it.xi_nuevo}</strong>` },
      { lbl: 'Error relativo',  eq: `|x<sub>${it.n}</sub> − x<sub>${it.n-1}</sub>| = <strong>${it.error}%</strong>` },
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
