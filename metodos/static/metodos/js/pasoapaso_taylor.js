/* ═══════════════════════════════════════
   PASO A PASO — Serie de Taylor
   ═══════════════════════════════════════ */
(function () {
  const dataEl = document.getElementById('pap-data');
  if (!dataEl) return;
  const { iteraciones, raiz } = JSON.parse(dataEl.textContent);
  if (!iteraciones || iteraciones.length === 0) return;

  let actual = 0, modoTodo = false;

  function htmlPaso(it, idx) {
    const esUltimo = idx === iteraciones.length - 1;
    const a    = parseFloat((it.d2fxi / 2.0).toFixed(8));
    const disc = parseFloat((it.dfxi**2 - 4*a*it.fxi).toFixed(8));
    const h    = parseFloat((it.xi_nuevo - it.xi).toFixed(8));
    const esOrden2 = it.orden === 2;

    const formulaEq = esOrden2
      ? `Ec. cuadrática: (${a})h² + (${it.dfxi})h + (${it.fxi}) = 0<br>` +
        `Discriminante = ${disc}<br>` +
        `h = ${h}<br>` +
        `x<sub>${it.n}</sub> = ${it.xi} + (${h}) = <strong class="pap-resultado">${it.xi_nuevo}</strong>`
      : `Discriminante < 0 → orden 1 (Newton)<br>` +
        `h = −f(x)/f'(x) = −(${it.fxi})/(${it.dfxi}) = ${h}<br>` +
        `x<sub>${it.n}</sub> = ${it.xi} + (${h}) = <strong class="pap-resultado">${it.xi_nuevo}</strong>`;

    const ordenEq = esOrden2
      ? `<span style="color:var(--accent)">Orden 2 — cuadrático</span>`
      : `<span style="color:var(--accent3)">Orden 1 — lineal (disc < 0)</span>`;

    const lineas = [
      { lbl: 'Valor actual',    eq: `x<sub>${it.n-1}</sub> = <strong>${it.xi}</strong>` },
      { lbl: 'Evaluar f(x)',    eq: `f(${it.xi}) = <strong>${it.fxi}</strong>` },
      { lbl: "Evaluar f'(x)",   eq: `f'(${it.xi}) = <strong>${it.dfxi}</strong>` },
      { lbl: "Evaluar f''(x)",  eq: `f''(${it.xi}) = <strong>${it.d2fxi}</strong>` },
      { lbl: 'Aplicar fórmula', highlight: true, eq: formulaEq },
      { lbl: 'Orden usado',     eq: ordenEq },
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
