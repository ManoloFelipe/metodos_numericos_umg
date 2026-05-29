import numpy as np
import plotly.graph_objects as go
import sympy as sp


def _base_layout():
    return dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#0f1318',
        font=dict(family='JetBrains Mono, monospace', color='#7a8a99', size=11),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            bgcolor='rgba(15,19,24,0.8)',
            bordercolor='#1e2730',
            borderwidth=1,
            font=dict(size=10),
        ),
        xaxis=dict(gridcolor='#1e2730', zerolinecolor='#1e2730', tickfont=dict(size=10)),
        yaxis=dict(gridcolor='#1e2730', zerolinecolor='#1e2730', tickfont=dict(size=10)),
        hovermode='closest',
    )


def _to_html(fig):
    return fig.to_html(
        full_html=False,
        include_plotlyjs='cdn',
        config={'displayModeBar': True,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                'displaylogo': False},
    )


def _preparar_curva(funcion_str, xs_iter, raiz=None):
    """Parsea f, calcula rango y curva. Retorna (f_lamb, x_range, y_range, y_min, y_max) o None."""
    x_sym = sp.Symbol('x')
    try:
        f_expr = sp.sympify(funcion_str, locals={'e': sp.E, 'pi': sp.pi})
        f = sp.lambdify(x_sym, f_expr, modules=['numpy'])
    except Exception:
        return None

    puntos = list(xs_iter)
    if raiz is not None:
        puntos.append(raiz)
    span = max(abs(max(puntos) - min(puntos)), 0.5)
    x_min = min(puntos) - span * 0.6
    x_max = max(puntos) + span * 0.6

    x_range = np.linspace(x_min, x_max, 500)
    try:
        y_range = np.array(f(x_range), dtype=float)
        y_range = np.where(np.isfinite(y_range), y_range, np.nan)
    except Exception:
        return None

    y_finite = y_range[np.isfinite(y_range)]
    if len(y_finite) == 0:
        return None

    margin = (np.nanmax(y_finite) - np.nanmin(y_finite)) * 0.25 + 0.5
    y_min = np.nanmin(y_finite) - margin
    y_max = np.nanmax(y_finite) + margin

    return f, x_range, y_range, y_min, y_max


def _alpha(i, n):
    """Opacidad creciente: primera iteración tenue, última opaca."""
    return 0.15 + (i / max(n - 1, 1)) * 0.85


# ─────────────────────────────────────────────────
#  NEWTON-RAPHSON
# ─────────────────────────────────────────────────
def generar_grafico_newton(funcion_str, iteraciones, raiz=None):
    if not iteraciones:
        return None

    xs = [it['xi'] for it in iteraciones]
    resultado = _preparar_curva(funcion_str, xs, raiz)
    if resultado is None:
        return None
    f, x_range, y_range, y_min, y_max = resultado

    fig = go.Figure()

    # Curva f(x)
    fig.add_trace(go.Scatter(
        x=x_range, y=y_range, mode='lines', name='f(x)',
        line=dict(color='#00e5a0', width=2.5),
        hovertemplate='x: %{x:.4f}<br>f(x): %{y:.4f}<extra></extra>',
    ))
    fig.add_hline(y=0, line=dict(color='#4a5568', width=1, dash='dot'))

    n = len(iteraciones)
    for i, it in enumerate(iteraciones):
        xi   = it['xi'];  fxi  = it['fxi'];  dfxi = it['dfxi']
        a    = _alpha(i, n)

        # Tangente
        tx = np.array([xi - 0.4, xi + 0.4])
        ty = np.clip(dfxi * (tx - xi) + fxi, y_min, y_max)
        fig.add_trace(go.Scatter(
            x=tx, y=ty, mode='lines',
            line=dict(color=f'rgba(0,153,255,{a:.2f})', width=1.5, dash='dash'),
            hoverinfo='skip', showlegend=False,
        ))

        # Punto xₙ
        fig.add_trace(go.Scatter(
            x=[xi], y=[fxi], mode='markers',
            name=f'x{it["n"]} = {xi}',
            marker=dict(color=f'rgba(255,107,53,{a:.2f})', size=8,
                        line=dict(color=f'rgba(255,107,53,{min(a+0.2,1):.2f})', width=1.5)),
            hovertemplate=f'n={it["n"]}<br>x: {xi}<br>f(x): {fxi}<extra></extra>',
        ))

    # Raíz
    if raiz is not None:
        try:
            f_raiz = float(f(raiz))
        except Exception:
            f_raiz = 0
        fig.add_trace(go.Scatter(
            x=[raiz], y=[f_raiz], mode='markers', name=f'Raíz ≈ {raiz}',
            marker=dict(color='#00e5a0', size=12, symbol='star',
                        line=dict(color='white', width=1.5)),
            hovertemplate=f'Raíz: {raiz}<br>f(raíz): {f_raiz:.6f}<extra></extra>',
        ))

    layout = _base_layout()
    layout['yaxis']['range'] = [y_min, y_max]
    fig.update_layout(**layout)
    return _to_html(fig)


# ─────────────────────────────────────────────────
#  TAYLOR
# ─────────────────────────────────────────────────
def generar_grafico_taylor(funcion_str, iteraciones, raiz=None):
    if not iteraciones:
        return None

    xs = [it['xi'] for it in iteraciones]
    resultado = _preparar_curva(funcion_str, xs, raiz)
    if resultado is None:
        return None
    f, x_range, y_range, y_min, y_max = resultado

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_range, y=y_range, mode='lines', name='f(x)',
        line=dict(color='#00e5a0', width=2.5),
        hovertemplate='x: %{x:.4f}<br>f(x): %{y:.4f}<extra></extra>',
    ))
    fig.add_hline(y=0, line=dict(color='#4a5568', width=1, dash='dot'))

    n = len(iteraciones)
    for i, it in enumerate(iteraciones):
        xi  = it['xi'];  fxi = it['fxi']
        a   = _alpha(i, n)
        # Color según orden: azul=2, naranja=1
        color_hex = '0,153,255' if it['orden'] == 2 else '255,107,53'

        fig.add_trace(go.Scatter(
            x=[xi], y=[fxi], mode='markers',
            name=f'x{it["n"]} = {xi} (ord {it["orden"]})',
            marker=dict(
                color=f'rgba({color_hex},{a:.2f})', size=9,
                symbol='diamond' if it['orden'] == 2 else 'circle',
                line=dict(color=f'rgba({color_hex},{min(a+0.2,1):.2f})', width=1.5),
            ),
            hovertemplate=f'n={it["n"]}<br>x: {xi}<br>f(x): {fxi}<br>Orden: {it["orden"]}<extra></extra>',
        ))

    if raiz is not None:
        try:
            f_raiz = float(f(raiz))
        except Exception:
            f_raiz = 0
        fig.add_trace(go.Scatter(
            x=[raiz], y=[f_raiz], mode='markers', name=f'Raíz ≈ {raiz}',
            marker=dict(color='#00e5a0', size=12, symbol='star',
                        line=dict(color='white', width=1.5)),
            hovertemplate=f'Raíz: {raiz}<br>f(raíz): {f_raiz:.6f}<extra></extra>',
        ))

    layout = _base_layout()
    layout['yaxis']['range'] = [y_min, y_max]
    fig.update_layout(**layout)
    return _to_html(fig)


# ─────────────────────────────────────────────────
#  COSENO
# ─────────────────────────────────────────────────
def generar_grafico_coseno(funcion_str, iteraciones, raiz=None):
    if not iteraciones:
        return None

    xs = [it['xi'] for it in iteraciones]
    resultado = _preparar_curva(funcion_str, xs, raiz)
    if resultado is None:
        return None
    f, x_range, y_range, y_min, y_max = resultado

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_range, y=y_range, mode='lines', name='f(x)',
        line=dict(color='#00e5a0', width=2.5),
        hovertemplate='x: %{x:.4f}<br>f(x): %{y:.4f}<extra></extra>',
    ))
    fig.add_hline(y=0, line=dict(color='#4a5568', width=1, dash='dot'))

    # Línea de trayectoria entre iteraciones
    tray_x = [it['xi'] for it in iteraciones]
    tray_y = [it['fxi'] for it in iteraciones]
    fig.add_trace(go.Scatter(
        x=tray_x, y=tray_y, mode='lines',
        line=dict(color='rgba(255,107,53,0.25)', width=1, dash='dot'),
        hoverinfo='skip', showlegend=False,
    ))

    n = len(iteraciones)
    for i, it in enumerate(iteraciones):
        xi  = it['xi'];  fxi = it['fxi'];  cos_v = it['cos_fxi']
        a   = _alpha(i, n)

        fig.add_trace(go.Scatter(
            x=[xi], y=[fxi], mode='markers',
            name=f'x{it["n"]} = {xi}',
            marker=dict(color=f'rgba(255,107,53,{a:.2f})', size=8,
                        line=dict(color=f'rgba(255,107,53,{min(a+0.2,1):.2f})', width=1.5)),
            hovertemplate=f'n={it["n"]}<br>x: {xi}<br>f(x): {fxi}<br>cos(f): {cos_v}<extra></extra>',
        ))

    if raiz is not None:
        try:
            f_raiz = float(f(raiz))
        except Exception:
            f_raiz = 0
        fig.add_trace(go.Scatter(
            x=[raiz], y=[f_raiz], mode='markers', name=f'Raíz ≈ {raiz}',
            marker=dict(color='#00e5a0', size=12, symbol='star',
                        line=dict(color='white', width=1.5)),
            hovertemplate=f'Raíz: {raiz}<br>f(raíz): {f_raiz:.6f}<extra></extra>',
        ))

    layout = _base_layout()
    layout['yaxis']['range'] = [y_min, y_max]
    fig.update_layout(**layout)
    return _to_html(fig)


# ─────────────────────────────────────────────────
#  BISECCIÓN
# ─────────────────────────────────────────────────
def generar_grafico_biseccion(funcion_str, iteraciones, raiz=None):
    if not iteraciones:
        return None

    xs = [it['xi'] for it in iteraciones] + [it['xf'] for it in iteraciones]
    resultado = _preparar_curva(funcion_str, xs, raiz)
    if resultado is None:
        return None
    f, x_range, y_range, y_min, y_max = resultado

    fig = go.Figure()

    # Curva f(x)
    fig.add_trace(go.Scatter(
        x=x_range, y=y_range, mode='lines', name='f(x)',
        line=dict(color='#00e5a0', width=2.5),
        hovertemplate='x: %{x:.4f}<br>f(x): %{y:.4f}<extra></extra>',
    ))
    fig.add_hline(y=0, line=dict(color='#4a5568', width=1, dash='dot'))

    n = len(iteraciones)
    for i, it in enumerate(iteraciones):
        a = _alpha(i, n)

        # Línea vertical en xm
        try:
            fxm = float(f(it['xm']))
        except Exception:
            fxm = 0
        fig.add_trace(go.Scatter(
            x=[it['xm'], it['xm']], y=[0, fxm],
            mode='lines',
            line=dict(color=f'rgba(0,153,255,{a:.2f})', width=1, dash='dash'),
            hoverinfo='skip', showlegend=False,
        ))

        # Punto xm
        fig.add_trace(go.Scatter(
            x=[it['xm']], y=[it['fxm']], mode='markers',
            name=f'xm{it["n"]} = {it["xm"]}',
            marker=dict(color=f'rgba(255,107,53,{a:.2f})', size=8,
                        line=dict(color=f'rgba(255,107,53,{min(a+0.2,1):.2f})', width=1.5)),
            hovertemplate=f'n={it["n"]}<br>xm: {it["xm"]}<br>f(xm): {it["fxm"]}<extra></extra>',
        ))

    # Raíz
    if raiz is not None:
        try:
            f_raiz = float(f(raiz))
        except Exception:
            f_raiz = 0
        fig.add_trace(go.Scatter(
            x=[raiz], y=[f_raiz], mode='markers', name=f'Raíz ≈ {raiz}',
            marker=dict(color='#00e5a0', size=12, symbol='star',
                        line=dict(color='white', width=1.5)),
            hovertemplate=f'Raíz: {raiz}<br>f(raíz): {f_raiz:.6f}<extra></extra>',
        ))

    layout = _base_layout()
    layout['yaxis']['range'] = [y_min, y_max]
    fig.update_layout(**layout)
    return _to_html(fig)
