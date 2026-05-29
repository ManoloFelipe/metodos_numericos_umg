/* ═══════════════════════════════════════
   PASO A PASO — Core compartido
   ═══════════════════════════════════════ */

function _htmlPasoBase(it, esUltimo, raiz, lineas) {
  const header = `
    <div class="pap-paso-header">
      <span class="pap-n">Iteración ${it.n}</span>
      ${esUltimo && raiz !== null ? '<span class="pap-badge-ok">✓ Convergió</span>' : ''}
    </div>`;

  const filas = lineas.map(l => {
    if (l.highlight) return `
      <div class="pap-linea pap-linea-formula">
        <span class="pap-lbl">${l.lbl}</span>
        <span class="pap-eq">${l.eq}</span>
      </div>`;
    if (l.raiz) return `
      <div class="pap-linea pap-linea-raiz">
        <span class="pap-lbl">${l.lbl}</span>
        <span class="pap-eq pap-raiz-val">${l.eq}</span>
      </div>`;
    return `
      <div class="pap-linea">
        <span class="pap-lbl">${l.lbl}</span>
        <span class="pap-eq">${l.eq}</span>
      </div>`;
  }).join('');

  return `<div class="pap-paso ${esUltimo ? 'pap-paso-final' : ''}">${header}${filas}</div>`;
}

function _initPap({ iteraciones, raiz, htmlPaso,
                    btnAbrir, seccion, contenedor,
                    btnPrev, btnNext, btnVerTodo, contador,
                    getActual, setActual, getModoTodo, setModoTodo }) {

  function renderActual() {
    setModoTodo(false);
    contenedor.innerHTML = htmlPaso(iteraciones[getActual()], getActual());
    actualizarControles();
    contenedor.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function renderTodo() {
    setModoTodo(true);
    contenedor.innerHTML = iteraciones
      .map((it, idx) => htmlPaso(it, idx))
      .join('<div class="pap-separador"></div>');
    actualizarControles();
  }

  function actualizarControles() {
    const todo = getModoTodo();
    const n    = iteraciones.length;
    contador.textContent   = todo ? `${n} / ${n}` : `${getActual() + 1} / ${n}`;
    btnPrev.disabled       = todo || getActual() === 0;
    btnNext.disabled       = todo || getActual() === n - 1;
    btnVerTodo.textContent = todo ? '← Ver uno a uno' : 'Ver todo';
  }

  btnAbrir.addEventListener('click', () => {
    const abierto = seccion.style.display !== 'none';
    if (abierto) {
      seccion.style.display = 'none';
      btnAbrir.textContent  = '▶ Paso a paso';
    } else {
      seccion.style.display = 'block';
      setActual(0);
      renderActual();
      btnAbrir.textContent = '▲ Ocultar paso a paso';
      seccion.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });

  btnPrev.addEventListener('click', () => {
    if (getActual() > 0) { setActual(getActual() - 1); renderActual(); }
  });
  btnNext.addEventListener('click', () => {
    if (getActual() < iteraciones.length - 1) { setActual(getActual() + 1); renderActual(); }
  });
  btnVerTodo.addEventListener('click', () => {
    getModoTodo() ? renderActual() : renderTodo();
  });
}
