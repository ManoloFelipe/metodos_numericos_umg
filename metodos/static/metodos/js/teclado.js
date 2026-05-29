const display  = document.getElementById('funcion-display');
const hidden   = document.getElementById('funcion-hidden');
const form     = document.getElementById('form-newton');

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('form-metodo');
  console.log('form encontrado:', form);

  if (form) {
    form.addEventListener('submit', function () {
      const hidden  = document.getElementById('funcion-hidden');
      const display = document.getElementById('funcion-display');
      hidden.value  = displayToInternal(display.value);
      console.log('hidden enviado:', hidden.value);
    });
  }
});

function displayToInternal(str) {
  return str
    .replace(/\^/g, '**')
    .replace(/\bln\(/g, 'log(');
}
function internalToDisplay(str) {
  return str
    .replace(/\*\*/g, '^')
    .replace(/(?<![a-zA-Z0-9_])log\(/g, 'ln(');
}

form.addEventListener('submit', function(e) {
  hidden.value = displayToInternal(display.value);
});

function insertar(texto) {
  display.focus();
  const start = display.selectionStart;
  const end   = display.selectionEnd;
  display.value = display.value.slice(0, start) + texto + display.value.slice(end);
  const pos = start + texto.length;
  display.setSelectionRange(pos, pos);
  display.focus();
}

function borrarUltimo() {
  display.focus();
  const start = display.selectionStart;
  const end   = display.selectionEnd;
  if (start === end && start > 0) {
    display.value = display.value.slice(0, start - 1) + display.value.slice(end);
    display.setSelectionRange(start - 1, start - 1);
  } else {
    display.value = display.value.slice(0, start) + display.value.slice(end);
    display.setSelectionRange(start, start);
  }
  display.focus();
}

function limpiar() {
  display.value = '';
  display.focus();
}

document.addEventListener('DOMContentLoaded', function() {
  const raw = display.value;
  if (raw) display.value = internalToDisplay(raw);
});