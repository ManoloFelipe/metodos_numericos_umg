from django.shortcuts import render
from .calculos import calcular_newton_raphson, calcular_taylor, calcular_biseccion
from .grafico  import generar_grafico_newton, generar_grafico_taylor, generar_grafico_biseccion


def main(request):
    return render(request, 'metodos/principal.html', {'metodo_activo': 'main'})

def _validar_params(post):
    """Valida y retorna (funcion, x0, tolerancia, max_iter, errores)."""
    funcion    = post.get('funcion', '').strip()
    x0_raw     = post.get('x0', '').strip()
    tol_raw    = post.get('tolerancia', '').strip()
    iter_raw   = post.get('max_iter', '').strip()

    errores = []
    x0 = tolerancia = max_iter = None

    if not funcion:
        errores.append('La función es requerida.')
    if not x0_raw:
        errores.append('El valor inicial x₀ es requerido.')
    else:
        try:
            x0 = float(x0_raw)
        except ValueError:
            errores.append('El valor inicial debe ser un número.')
    if not tol_raw:
        errores.append('La tolerancia es requerida.')
    else:
        try:
            tolerancia = float(tol_raw)
            if tolerancia <= 0:
                errores.append('La tolerancia debe ser mayor a 0.')
        except ValueError:
            errores.append('La tolerancia debe ser un número.')
    if not iter_raw:
        errores.append('El número de iteraciones es requerido.')
    else:
        try:
            max_iter = int(iter_raw)
            if max_iter < 1:
                errores.append('Las iteraciones deben ser al menos 1.')
        except ValueError:
            errores.append('Las iteraciones deben ser un entero.')

    return funcion, x0, tolerancia, max_iter, errores


def _campos_comunes(post, funcion_display=None):
    return {
        'funcion_display': funcion_display or post.get('funcion-display', ''),
        'x0':        post.get('x0', ''),
        'tolerancia': post.get('tolerancia', ''),
        'max_iter':  post.get('max_iter', ''),
    }

# ── Newton-Raphson ──────────────────────────────
def newton_raphson(request):
    context = {'metodo_activo': 'newton'}

    if request.method == 'POST':
        
        print('Validando parámetros:', request.POST);
        funcion_display = request.POST.get('funcion-display', '').strip()
        funcion, x0, tolerancia, max_iter, errores = _validar_params(request.POST)
        context.update(_campos_comunes(request.POST, funcion_display))
        if errores:
            context['errores'] = errores
        else:
            resultado = calcular_newton_raphson(funcion, x0, tolerancia, max_iter, funcion_display)
            if 'iteraciones' in resultado and resultado['iteraciones']:
                resultado['grafico'] = generar_grafico_newton(
                    funcion, resultado['iteraciones'], resultado.get('raiz'))
            context['resultado'] = resultado
    return render(request, 'metodos/newton_raphson.html', context)


# ── Taylor ─────────────────────────────────────
def taylor(request):
    context = {'metodo_activo': 'taylor'}

    if request.method == 'POST':
        funcion_display = request.POST.get('funcion-display', '').strip()
        funcion, x0, tolerancia, max_iter, errores = _validar_params(request.POST)
        context.update(_campos_comunes(request.POST, funcion_display))
        if errores:
            context['errores'] = errores
        else:
            resultado = calcular_taylor(funcion, x0, tolerancia, max_iter, funcion_display)
            if 'iteraciones' in resultado and resultado['iteraciones']:
                resultado['grafico'] = generar_grafico_taylor(
                    funcion, resultado['iteraciones'], resultado.get('raiz'))
            context['resultado'] = resultado
    return render(request, 'metodos/taylor.html', context)


# ── Bisección ──────────────────────────────────
def coseno(request):
    context = {'metodo_activo': 'coseno'} #El nombre 'coseno' es por un error, cambiarlo llevaría demasiado tiempo
    if request.method == 'POST':
        funcion_display = request.POST.get('funcion-display', '').strip()
        funcion = request.POST.get('funcion', '').strip()
        if not funcion:
            funcion = funcion_display.replace('^', '**').replace('ln(', 'log(')

        xi_raw   = request.POST.get('xi', '').strip()
        xf_raw   = request.POST.get('xf', '').strip()
        tol_raw  = request.POST.get('tolerancia', '').strip()
        iter_raw = request.POST.get('max_iter', '').strip()

        context.update({
            'funcion_display': funcion_display,
            'xi': xi_raw, 'xf': xf_raw,
            'tolerancia': tol_raw, 'max_iter': iter_raw,
        })

        errores = []
        if not funcion:            errores.append('La función es requerida.')
        xi = xf = tolerancia = max_iter = None
        try:    xi = float(xi_raw)
        except: errores.append('xi debe ser un número.')
        try:    xf = float(xf_raw)
        except: errores.append('xf debe ser un número.')
        try:
            tolerancia = float(tol_raw)
            if tolerancia <= 0: errores.append('La tolerancia debe ser mayor a 0.')
        except: errores.append('La tolerancia debe ser un número.')
        try:
            max_iter = int(iter_raw)
            if max_iter < 1: errores.append('Las iteraciones deben ser al menos 1.')
        except: errores.append('Las iteraciones deben ser un entero.')

        if not errores and xi is not None and xf is not None:
            if xi >= xf:
                errores.append('xi debe ser menor que xf.')

        if errores:
            context['errores'] = errores
        else:
            resultado = calcular_biseccion(funcion, xi, xf, tolerancia, max_iter, funcion_display)
            if 'iteraciones' in resultado and resultado['iteraciones']:
                resultado['grafico'] = generar_grafico_biseccion(
                    funcion, resultado['iteraciones'], resultado.get('raiz'))
            context['resultado'] = resultado
    return render(request, 'metodos/coseno.html', context)
