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


# ──────────────────────────────────────────────
#  NEWTON-RAPHSON
# ──────────────────────────────────────────────
def calcular_newton_raphson(funcion_str, x0, tolerancia, max_iter):
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

    derivada_str = str(df_expr)

    f = sp.lambdify(x, f_expr, modules=['math'])
    df = sp.lambdify(x, df_expr, modules=['math'])

    iteraciones = []
    xi = float(x0)

    for i in range(int(max_iter)):
        try:
            fxi = f(xi)
            dfxi = df(xi)
        except Exception as e:
            return {
                'derivada_str': derivada_str,
                'iteraciones': iteraciones,
                'error': f'Error evaluando en x={xi:.6f}: {str(e)}'
            }

        if abs(dfxi) < 1e-15:
            return {
                'derivada_str': derivada_str,
                'iteraciones': iteraciones,
                'error': f'Derivada cero en x={xi:.6f}. El método no puede continuar.'
            }

        xi_nuevo = xi - fxi / dfxi
        error_rel = abs(xi_nuevo - xi)

        iteraciones.append({
            'n': i + 1,
            'xi': round(xi, 8),
            'fxi': round(fxi, 8),
            'dfxi': round(dfxi, 8),
            'xi_nuevo': round(xi_nuevo, 8),
            'error': round(error_rel, 10),
        })

        if error_rel < float(tolerancia):
            return {
                'derivada_str': derivada_str,
                'iteraciones': iteraciones,
                'raiz': round(xi_nuevo, 8),
            }

        xi = xi_nuevo

    return {
        'derivada_str': derivada_str,
        'iteraciones': iteraciones,
        'raiz': round(xi, 8),
        'advertencia': f'Se alcanzó el máximo de {max_iter} iteraciones sin convergencia.'
    }


# ──────────────────────────────────────────────
#  SERIE DE TAYLOR
# ──────────────────────────────────────────────
def calcular_taylor(funcion_str, x0, tolerancia, max_iter):
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
        f"f'(x)  = {df_expr}",
        f"f''(x) = {d2f_expr}",
    ]

    f   = sp.lambdify(x, f_expr,  modules=['math'])
    df  = sp.lambdify(x, df_expr, modules=['math'])
    d2f = sp.lambdify(x, d2f_expr, modules=['math'])

    iteraciones = []
    xi = float(x0)

    for i in range(int(max_iter)):
        try:
            fxi   = f(xi)
            dfxi  = df(xi)
            d2fxi = d2f(xi)
        except Exception as e:
            return {
                'derivadas': derivadas,
                'iteraciones': iteraciones,
                'error': f'Error evaluando en x={xi:.6f}: {str(e)}'
            }

        # Expansión cuadrática: (d2f/2)*h² + df*h + f = 0
        # h = xi_nuevo - xi
        orden_usado = 2
        if abs(d2fxi) > 1e-15:
            a = d2fxi / 2.0
            b = dfxi
            c = fxi
            discriminante = b**2 - 4*a*c
            if discriminante >= 0:
                sqrt_d = math.sqrt(discriminante)
                h1 = (-b + sqrt_d) / (2*a)
                h2 = (-b - sqrt_d) / (2*a)
                # Elegir el h de menor magnitud (más cercano al actual)
                h = h1 if abs(h1) < abs(h2) else h2
            else:
                # Discriminante negativo → caer a orden 1
                if abs(dfxi) < 1e-15:
                    return {
                        'derivadas': derivadas,
                        'iteraciones': iteraciones,
                        'error': f'Derivada primera cero en x={xi:.6f}.'
                    }
                h = -fxi / dfxi
                orden_usado = 1
        else:
            # d2f ≈ 0 → Newton puro
            if abs(dfxi) < 1e-15:
                return {
                    'derivadas': derivadas,
                    'iteraciones': iteraciones,
                    'error': f'Derivadas primera y segunda cero en x={xi:.6f}.'
                }
            h = -fxi / dfxi
            orden_usado = 1

        xi_nuevo = xi + h
        error_rel = abs(h)

        iteraciones.append({
            'n':          i + 1,
            'xi':         round(xi, 8),
            'fxi':        round(fxi, 8),
            'dfxi':       round(dfxi, 8),
            'd2fxi':      round(d2fxi, 8),
            'xi_nuevo':   round(xi_nuevo, 8),
            'error':      round(error_rel, 10),
            'orden':      orden_usado,
        })

        if error_rel < float(tolerancia):
            return {
                'derivadas':   derivadas,
                'iteraciones': iteraciones,
                'raiz':        round(xi_nuevo, 8),
            }

        xi = xi_nuevo

    return {
        'derivadas':   derivadas,
        'iteraciones': iteraciones,
        'raiz':        round(xi, 8),
        'advertencia': f'Se alcanzó el máximo de {max_iter} iteraciones sin convergencia.',
    }


# ──────────────────────────────────────────────
#  MÉTODO DEL COSENO  (Steffensen trigonométrico)
# ──────────────────────────────────────────────
def calcular_coseno(funcion_str, x0, tolerancia, max_iter):
    """
    Método iterativo del Coseno para encontrar raíces.

    Reformula el problema como un punto fijo usando una transformación
    trigonométrica. Dado f(x) = 0, define:

        g(x) = x - f(x) * cos(f(x))

    La iteración es:  x_{n+1} = g(x_n) = x_n - f(x_n)·cos(f(x_n))

    El factor cos(f(x_n)) actúa como amortiguador adaptativo:
      - Cuando f(xn) ≈ 0  →  cos(f) ≈ 1  (comportamiento casi Newton)
      - Cuando f(xn) es grande → |cos(f)| ≤ 1 amortigua el paso

    Retorna un diccionario con iteraciones y resultado.
    """
    x = sp.Symbol('x')

    f_expr, err = _parsear_funcion(funcion_str)
    if err:
        return {'error': err}

    # Mostrar la función de iteración simbólica
    g_expr = x - f_expr * sp.cos(f_expr)
    g_str  = f"g(x) = x − f(x)·cos(f(x)) = {g_expr}"

    f = sp.lambdify(x, f_expr, modules=['math'])

    iteraciones = []
    xi = float(x0)

    for i in range(int(max_iter)):
        try:
            fxi = f(xi)
        except Exception as e:
            return {
                'g_str':       g_str,
                'iteraciones': iteraciones,
                'error':       f'Error evaluando en x={xi:.6f}: {str(e)}'
            }

        cos_fxi  = math.cos(fxi)
        paso     = fxi * cos_fxi
        xi_nuevo = xi - paso
        error_rel = abs(xi_nuevo - xi)

        iteraciones.append({
            'n':        i + 1,
            'xi':       round(xi, 8),
            'fxi':      round(fxi, 8),
            'cos_fxi':  round(cos_fxi, 8),
            'paso':     round(paso, 8),
            'xi_nuevo': round(xi_nuevo, 8),
            'error':    round(error_rel, 10),
        })

        if error_rel < float(tolerancia):
            return {
                'g_str':       g_str,
                'iteraciones': iteraciones,
                'raiz':        round(xi_nuevo, 8),
            }

        xi = xi_nuevo

    return {
        'g_str':       g_str,
        'iteraciones': iteraciones,
        'raiz':        round(xi, 8),
        'advertencia': f'Se alcanzó el máximo de {max_iter} iteraciones sin convergencia.',
    }
