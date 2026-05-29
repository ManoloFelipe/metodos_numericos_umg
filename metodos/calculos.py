import sympy as sp
import math


def _parsear_funcion(funcion_str):
    """Parsea una cadena a expresión SymPy. Retorna (expr, error_str)."""
    x = sp.Symbol('x')
    try:
        expr = sp.sympify(funcion_str, locals={'e': sp.E, 'pi': sp.pi})
        return expr, None
    except Exception as e:
        return None, f'Función inválida: {str(e)}'


def _sympy_to_display(expr_str):
    """Convierte ** → ^ para mostrar al usuario."""
    return expr_str.replace('**', '^')

def _safe_round(val, decimals=8):
    try:
        return round(float(val), decimals)
    except (TypeError, ValueError):
        if hasattr(val, 'real'):
            return round(float(val.real), decimals)
        raise


def _error_pct(xi_nuevo, xi):
    if xi_nuevo != 0:
        return _safe_round(abs((xi_nuevo - xi) / xi_nuevo) * 100, 6)
    return 0.0

# ── Paso a paso: generadores de líneas ──────────
def _pasos_newton(it, funcion_display, derivada_display):
    paso = _safe_round(it['fxi'] / it['dfxi'], 8)
    return [
        {'lbl': 'Valor actual',    'eq': f"x<sub>{it['n']-1}</sub> = <strong>{it['xi']}</strong>"},
        {'lbl': 'Evaluar f(x)',    'eq': f"f({it['xi']}) = <strong>{it['fxi']}</strong>"},
        {'lbl': "Evaluar f'(x)",   'eq': f"f'({it['xi']}) = <strong>{it['dfxi']}</strong>"},
        {'lbl': 'Aplicar fórmula', 'eq': (
            f"x<sub>{it['n']}</sub> = x<sub>{it['n']-1}</sub> − f(x) / f'(x)<br>"
            f"= {it['xi']} − ({it['fxi']}) / ({it['dfxi']})<br>"
            f"= {it['xi']} − ({paso})<br>"
            f"= <strong class='pap-resultado'>{it['xi_nuevo']}</strong>"
        ), 'highlight': True},
        {'lbl': 'Error relativo',  'eq': f"|x<sub>{it['n']}</sub> − x<sub>{it['n']-1}</sub>| = <strong>{it['error']}%</strong>"},
    ]


def _pasos_taylor(it, funcion_display, derivadas_display):
    a = _safe_round(it['d2fxi'] / 2.0, 8)
    b = it['dfxi']
    c = it['fxi']
    disc = _safe_round(b**2 - 4*a*c, 8)
    h = _safe_round(it['xi_nuevo'] - it['xi'], 8)

    if it['orden'] == 2:
        formula_eq = (
            f"Ec. cuadrática: ({a})h² + ({b})h + ({c}) = 0<br>"
            f"Discriminante = {disc}<br>"
            f"h = {h}<br>"
            f"x<sub>{it['n']}</sub> = {it['xi']} + ({h}) = <strong class='pap-resultado'>{it['xi_nuevo']}</strong>"
        )
        orden_lbl = '<span style="color:var(--accent)">Orden 2 (cuadrático)</span>'
    else:
        formula_eq = (
            f"Discriminante negativo → orden 1 (Newton)<br>"
            f"h = −f(x)/f'(x) = −({c})/({b}) = {h}<br>"
            f"x<sub>{it['n']}</sub> = {it['xi']} + ({h}) = <strong class='pap-resultado'>{it['xi_nuevo']}</strong>"
        )
        orden_lbl = '<span style="color:var(--accent3)">Orden 1 (lineal, disc < 0)</span>'

    return [
        {'lbl': 'Valor actual',     'eq': f"x<sub>{it['n']-1}</sub> = <strong>{it['xi']}</strong>"},
        {'lbl': 'Evaluar f(x)',     'eq': f"f({it['xi']}) = <strong>{it['fxi']}</strong>"},
        {'lbl': "Evaluar f'(x)",    'eq': f"f'({it['xi']}) = <strong>{it['dfxi']}</strong>"},
        {'lbl': "Evaluar f''(x)",   'eq': f"f''({it['xi']}) = <strong>{it['d2fxi']}</strong>"},
        {'lbl': 'Aplicar fórmula',  'eq': formula_eq, 'highlight': True},
        {'lbl': 'Orden usado',      'eq': orden_lbl},
        {'lbl': 'Error relativo',   'eq': f"|x<sub>{it['n']}</sub> − x<sub>{it['n']-1}</sub>| = <strong>{it['error']}%</strong>"},
    ]


def _pasos_biseccion(it):
    return [
        {'lbl': 'Intervalo actual',     'eq': f"xi = <strong>{it['xi']}</strong>, xf = <strong>{it['xf']}</strong>"},
        {'lbl': 'Calcular xm',          'eq': f"xm = (xi + xf) / 2 = ({it['xi']} + {it['xf']}) / 2 = <strong>{it['xm']}</strong>"},
        {'lbl': 'Evaluar f(xi)',        'eq': f"f({it['xi']}) = <strong>{it['fxi']}</strong>"},
        {'lbl': 'Evaluar f(xm)',        'eq': f"f({it['xm']}) = <strong>{it['fxm']}</strong>"},
        {'lbl': 'Producto f(xi)·f(xm)', 'eq': f"{it['fxi']} × {it['fxm']} = <strong>{it['producto']}</strong>"},
        {'lbl': 'Decisión',             'eq': it['decision']},
        {'lbl': 'Error',                'highlight': True, 'eq':
            f"error = (xm − xi) / xm × 100<br>"
            f"= ({it['xm']} − {it['xi']}) / {it['xm']} × 100<br>"
            f"= <strong class='pap-resultado'>{it['error']}%</strong>"},
    ]


# ──────────────────────────────────────────────
#  NEWTON-RAPHSON
# ──────────────────────────────────────────────
def calcular_newton_raphson(funcion_str, x0, tolerancia, max_iter, funcion_display=''):
    """
    Calcula el método de Newton-Raphson.
    
    Retorna un diccionario con:
      - derivada_str: expresión de la derivada
      - iteraciones: lista de dicts con cada paso
      - raiz: valor aproximado de la raíz
      - error: mensaje de error si falla
    """
    x = sp.Symbol('x')
    
    try:
        f_expr = sp.sympify(funcion_str, locals={'e': sp.E, 'pi': sp.pi})
    except Exception as e:
        return {'error': f'Función inválida: {str(e)}'}
    
    try:
        df_expr = sp.diff(f_expr, x)
    except Exception as e:
        return {'error': f'No se pudo derivar: {str(e)}'}

    derivada_str     = str(df_expr)
    derivada_display = _sympy_to_display(derivada_str)
    f  = sp.lambdify(x, f_expr,  modules=['math'])
    df = sp.lambdify(x, df_expr, modules=['math'])

    iteraciones = []
    xi = float(x0)

    for i in range(int(max_iter)):
        try:
            fxi  = _safe_round(f(xi))
            dfxi = _safe_round(df(xi))
        except Exception as e:
            return {
                'derivada_str': derivada_str, 'derivada_display': derivada_display,
                'iteraciones': iteraciones,
                'error': f'Resultado complejo en x={xi:.6f}. Prueba con un x₀ diferente.'
            }
        if abs(dfxi) < 1e-15:
            return {
                'derivada_str': derivada_str, 'derivada_display': derivada_display,
                'iteraciones': iteraciones,
                'error': f'Derivada cero en x={xi:.6f}. El método no puede continuar.'
            }

        xi_nuevo  = _safe_round(xi - fxi / dfxi)
        error_pct = _error_pct(xi_nuevo, xi)

        it = {'n': i+1, 'xi': _safe_round(xi), 'fxi': fxi, 'dfxi': dfxi,
              'xi_nuevo': xi_nuevo, 'error': error_pct}
        it['pasos'] = _pasos_newton(it, funcion_display, derivada_display)
        iteraciones.append(it)

        if abs(xi_nuevo - xi) < float(tolerancia):
            return {
                'derivada_str': derivada_str, 'derivada_display': derivada_display,
                'iteraciones': iteraciones, 'raiz': xi_nuevo,
            }
            
        xi = xi_nuevo

    return {
        'derivada_str': derivada_str, 'derivada_display': derivada_display,
        'iteraciones': iteraciones, 'raiz': _safe_round(xi),
        'advertencia': f'Se alcanzó el máximo de {max_iter} iteraciones sin convergencia.'
    }


# ──────────────────────────────────────────────
#  SERIE DE TAYLOR
# ──────────────────────────────────────────────
def calcular_taylor(funcion_str, x0, tolerancia, max_iter, funcion_display=''):
    """
    Método de Taylor para encontrar raíces.

    Usa la expansión de Taylor de f alrededor del punto actual x_n:
        f(x) ≈ f(x_n) + f'(x_n)(x - x_n) + f''(x_n)/2 * (x - x_n)² + ...

    En cada iteración calcula el siguiente punto resolviendo la expansión
    de orden 2 (cuadrática), eligiendo la raíz que más se acerque al actual.
    Si el discriminante es negativo, cae a orden 1 (Newton clásico).

    Retorna un diccionario con:
      - derivadas: lista de strings con f', f'' calculadas simbólicamente
      - iteraciones: lista de dicts por paso
      - raiz: valor aproximado
      - error / advertencia si aplica
    """
    x = sp.Symbol('x')
    
    f_expr, err = _parsear_funcion(funcion_str)
    if err:
        return {'error': err}
    
    try:
        df_expr  = sp.diff(f_expr, x)
        d2f_expr = sp.diff(df_expr, x)
    except Exception as e:
        return {'error': f'No se pudieron calcular derivadas: {str(e)}'}

    derivadas = [
        f"f'(x)  = {_sympy_to_display(str(df_expr))}",
        f"f''(x) = {_sympy_to_display(str(d2f_expr))}",
    ]
    derivadas_display = derivadas

    f   = sp.lambdify(x, f_expr,   modules=['math'])
    df  = sp.lambdify(x, df_expr,  modules=['math'])
    d2f = sp.lambdify(x, d2f_expr, modules=['math'])

    iteraciones = []
    xi = float(x0)

    for i in range(int(max_iter)):
        try:
            fxi   = _safe_round(f(xi))
            dfxi  = _safe_round(df(xi))
            d2fxi = _safe_round(d2f(xi))
        except Exception as e:
            return {'derivadas': derivadas, 'iteraciones': iteraciones,
                    'error': f'Resultado complejo en x={xi:.6f}. Prueba con un x₀ diferente.'}

        orden_usado = 2
        if abs(d2fxi) > 1e-15:
            a = d2fxi / 2.0
            b = dfxi; c = fxi
            disc = b**2 - 4*a*c
            if disc >= 0:
                sq = math.sqrt(disc)
                h1 = (-b + sq) / (2*a); h2 = (-b - sq) / (2*a)
                h = h1 if abs(h1) < abs(h2) else h2
            else:
                # Discriminante negativo → caer a orden 1
                if abs(dfxi) < 1e-15:
                    return {'derivadas': derivadas, 'iteraciones': iteraciones,
                            'error': f'Derivada primera cero en x={xi:.6f}.'}
                h = -fxi / dfxi; orden_usado = 1
        else:
            if abs(dfxi) < 1e-15:
                return {'derivadas': derivadas, 'iteraciones': iteraciones,
                        'error': f'Derivadas primera y segunda cero en x={xi:.6f}.'}
            h = -fxi / dfxi; orden_usado = 1

        xi_nuevo  = _safe_round(xi + h)
        error_pct = _error_pct(xi_nuevo, xi)

        it = {'n': i+1, 'xi': _safe_round(xi), 'fxi': fxi, 'dfxi': dfxi,
              'd2fxi': d2fxi, 'xi_nuevo': xi_nuevo, 'error': error_pct, 'orden': orden_usado}
        it['pasos'] = _pasos_taylor(it, funcion_display, derivadas_display)
        iteraciones.append(it)

        if abs(xi_nuevo - xi) < float(tolerancia):
            return {'derivadas': derivadas, 'iteraciones': iteraciones, 'raiz': xi_nuevo}
        xi = xi_nuevo

    return {
        'derivadas': derivadas, 'iteraciones': iteraciones, 'raiz': _safe_round(xi),
        'advertencia': f'Se alcanzó el máximo de {max_iter} iteraciones sin convergencia.'
    }


# ──────────────────────────────────────────────
#  BISECCIÓN
# ──────────────────────────────────────────────
def calcular_biseccion(funcion_str, xi, xf, tolerancia, max_iter, funcion_display=''):
    f_expr, err = _parsear_funcion(funcion_str)
    if err:
        return {'error': err}

    x = sp.Symbol('x')
    f = sp.lambdify(x, f_expr, modules=['math'])

    try:
        fxi = float(f(xi))
        fxf = float(f(xf))
    except Exception as e:
        return {'error': f'Error evaluando la función: {str(e)}'}

    # Expandir intervalo si no hay cambio de signo
    intervalo_modificado = None
    pasos_expansion = 0
    xi_orig, xf_orig = xi, xf

    while fxi * fxf > 0 and pasos_expansion < 1000:
        pasos_expansion += 1
        if fxi < fxf:
            xf += 1
            fxf = float(f(xf))
        else:
            xi -= 1
            fxi = float(f(xi))

    if pasos_expansion >= 1000:
        return {'error': 'No se encontró cambio de signo expandiendo el intervalo. '
                         'Verifica que la función tenga una raíz real.'}

    if pasos_expansion > 0:
        intervalo_modificado = (
            f'El intervalo original [{xi_orig}, {xf_orig}] no contenía cambio de signo. '
            f'Se expandió automáticamente a [{_safe_round(xi, 4)}, {_safe_round(xf, 4)}].'
        )

    iteraciones = []

    for i in range(int(max_iter)):
        xm    = _safe_round((xi + xf) / 2)
        fxi_v = _safe_round(f(xi))
        fxm_v = _safe_round(f(xm))
        prod  = _safe_round(fxi_v * fxm_v)
        error_pct = _safe_round(abs((xm - xi) / xm) * 100, 6) if xm != 0 else 0.0

        if prod == 0:
            decision = "f(xi)·f(xm) = 0 → <strong style='color:var(--accent)'>Raíz exacta en xm</strong>"
        elif prod > 0:
            decision = "f(xi)·f(xm) > 0 → la raíz está en [xm, xf] → <strong>xi = xm</strong>"
        else:
            decision = "f(xi)·f(xm) < 0 → la raíz está en [xi, xm] → <strong>xf = xm</strong>"

        it = {
            'n': i+1, 'xi': _safe_round(xi), 'xf': _safe_round(xf),
            'xm': xm, 'fxi': fxi_v, 'fxm': fxm_v,
            'producto': prod, 'decision': decision, 'error': error_pct,
        }
        it['pasos'] = _pasos_biseccion(it)
        iteraciones.append(it)

        if prod == 0 or error_pct < float(tolerancia):
            return {
                'iteraciones': iteraciones, 'raiz': xm,
                'intervalo_modificado': intervalo_modificado,
            }

        if prod > 0:
            xi = float(xm)
        else:
            xf = float(xm)

    return {
        'iteraciones': iteraciones, 'raiz': _safe_round((xi + xf) / 2),
        'intervalo_modificado': intervalo_modificado,
        'advertencia': f'Se alcanzó el máximo de {max_iter} iteraciones sin convergencia.',
    }
