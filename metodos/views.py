from django.shortcuts import render
from .calculos import calcular_newton_raphson, calcular_taylor, calcular_coseno


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


# ── Newton-Raphson ──────────────────────────────
def newton_raphson(request):
    context = {'metodo_activo': 'newton'}

    if request.method == 'POST':
        funcion, x0, tolerancia, max_iter, errores = _validar_params(request.POST)
        context.update({
            'funcion': request.POST.get('funcion', ''),
            'x0': request.POST.get('x0', ''),
            'tolerancia': request.POST.get('tolerancia', ''),
            'max_iter': request.POST.get('max_iter', ''),
        })
        if errores:
            context['errores'] = errores
        else:
            context['resultado'] = calcular_newton_raphson(funcion, x0, tolerancia, max_iter)

    return render(request, 'metodos/newton_raphson.html', context)


# ── Taylor ─────────────────────────────────────
def taylor(request):
    context = {'metodo_activo': 'taylor'}

    if request.method == 'POST':
        funcion, x0, tolerancia, max_iter, errores = _validar_params(request.POST)
        context.update({
            'funcion': request.POST.get('funcion', ''),
            'x0': request.POST.get('x0', ''),
            'tolerancia': request.POST.get('tolerancia', ''),
            'max_iter': request.POST.get('max_iter', ''),
        })
        if errores:
            context['errores'] = errores
        else:
            context['resultado'] = calcular_taylor(funcion, x0, tolerancia, max_iter)

    return render(request, 'metodos/taylor.html', context)


# ── Coseno ─────────────────────────────────────
def coseno(request):
    context = {'metodo_activo': 'coseno'}

    if request.method == 'POST':
        funcion, x0, tolerancia, max_iter, errores = _validar_params(request.POST)
        context.update({
            'funcion': request.POST.get('funcion', ''),
            'x0': request.POST.get('x0', ''),
            'tolerancia': request.POST.get('tolerancia', ''),
            'max_iter': request.POST.get('max_iter', ''),
        })
        if errores:
            context['errores'] = errores
        else:
            context['resultado'] = calcular_coseno(funcion, x0, tolerancia, max_iter)

    return render(request, 'metodos/coseno.html', context)

