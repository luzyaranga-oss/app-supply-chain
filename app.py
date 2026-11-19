import base64
import json
from io import BytesIO
from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

BASE = Path(__file__).parent
st.set_page_config(
    page_title="DataCo Risk | Riesgo de retraso en entregas",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------ paleta
NAVY, NAVY2 = "#12142B", "#1C1F42"
VIOLET, VIOLET_D, VIOLET_S = "#6C5CE7", "#5546D6", "#EEEBFF"
LIME = "#CBF27A"
INK, MUTED, LINE = "#1A1C38", "#6A6E8E", "#E7E4F8"
CORAL, MINT = "#F0616D", "#1FA97F"

# ------------------------------------------------------------------ estilos
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root{--navy:#12142B;--navy2:#1C1F42;--violet:#6C5CE7;--violet-d:#5546D6;--violet-s:#EEEBFF;--lime:#CBF27A;
--ink:#1A1C38;--muted:#6A6E8E;--line:#E7E4F8;--coral:#F0616D;--mint:#1FA97F;}
.stApp{background:linear-gradient(135deg,#E4EDFF 0%,#EEE8FF 48%,#FCEAF0 100%);background-attachment:fixed;
font-family:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif;color:var(--ink);}
header[data-testid="stHeader"]{background:transparent;}
[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer,[data-testid="stAppDeployButton"]{display:none!important;}
.block-container{max-width:1240px;padding:2.2rem 2.4rem 4rem;}
p,li{line-height:1.65;}

/* ---------- barra lateral ---------- */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#12142B 0%,#1B1E42 100%);border-right:none;}
[data-testid="stSidebar"] > div:first-child{padding-top:.8rem;}
.brand{display:flex;align-items:center;gap:.85rem;padding:.6rem .4rem 1.4rem;}
.brand img{width:44px;height:44px;}
.brand b{display:block;color:#fff;font-size:1.08rem;font-weight:800;letter-spacing:-.01em;}
.brand span{color:#9A9EC9;font-size:.76rem;}
.side-label{color:#7F83B0;font-size:.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:0 .6rem .5rem;}
[data-testid="stSidebar"] [role="radiogroup"]{gap:.4rem;}
[data-testid="stSidebar"] [role="radiogroup"] label{background:transparent;border-radius:999px;padding:.75rem 1.15rem;width:100%;cursor:pointer;transition:all .18s ease;}
[data-testid="stSidebar"] [role="radiogroup"] label > *:not(input):not(:has(p)){display:none!important;}
[data-testid="stSidebar"] [role="radiogroup"] label p{color:#C3C6E6;font-size:.95rem;font-weight:600;margin:0;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:rgba(255,255,255,.08);}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:var(--lime);}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p{color:var(--navy);font-weight:800;}
.side-foot{margin-top:2.4rem;padding:1.1rem 1.1rem;border-radius:22px;background:rgba(255,255,255,.06);color:#B7BAE0;font-size:.8rem;line-height:1.55;}
.side-foot b{color:#fff;}

/* ---------- encabezados de pagina ---------- */
.eyebrow{display:inline-block;background:var(--violet-s);color:var(--violet);font-size:.72rem;font-weight:800;letter-spacing:.12em;
text-transform:uppercase;padding:.42rem .95rem;border-radius:999px;margin-bottom:.9rem;}
.page-title{font-size:2.3rem;font-weight:800;letter-spacing:-.03em;line-height:1.12;color:var(--navy);margin:0 0 .6rem;}
.page-sub{font-size:1.04rem;color:var(--muted);max-width:46rem;margin:0 0 1.8rem;line-height:1.65;}
.sec-title{font-size:1.28rem;font-weight:800;letter-spacing:-.015em;color:var(--navy);margin:2.2rem 0 .35rem;}
.sec-sub{font-size:.95rem;color:var(--muted);margin:0 0 1.1rem;max-width:44rem;}

/* ---------- hero ---------- */
.hero{display:grid;grid-template-columns:1.05fr .95fr;align-items:center;gap:1rem;background:linear-gradient(135deg,#12142B 0%,#262A6B 100%);
border-radius:34px;padding:3.2rem 3rem 3.2rem 3.4rem;color:#fff;overflow:hidden;box-shadow:0 30px 60px rgba(30,25,100,.25);}
.hero-tag{display:inline-block;background:rgba(203,242,122,.14);color:var(--lime);font-size:.74rem;font-weight:800;letter-spacing:.12em;
text-transform:uppercase;padding:.45rem 1rem;border-radius:999px;margin-bottom:1.3rem;}
.hero-title{font-size:3.05rem;font-weight:800;letter-spacing:-.035em;line-height:1.06;color:#fff;margin:0 0 1.1rem;}
.hero-title em{font-style:normal;color:var(--lime);}
.hero-text{font-size:1.06rem;color:#C5C8E8;line-height:1.7;max-width:33rem;margin:0 0 1.6rem;}
.chips{display:flex;flex-wrap:wrap;gap:.55rem;}
.chip{background:rgba(255,255,255,.1);color:#fff;font-size:.8rem;font-weight:600;padding:.45rem 1rem;border-radius:999px;}
.hero img{width:100%;height:auto;display:block;}

/* ---------- tarjetas ---------- */
[class*="st-key-card"]{background:#fff;border-radius:26px;padding:1.7rem 1.8rem;box-shadow:0 18px 44px rgba(60,50,140,.09);border:1px solid rgba(255,255,255,.8);}
[class*="st-key-dark"]{background:linear-gradient(135deg,#12142B 0%,#262A6B 100%);border-radius:26px;padding:1.7rem 1.8rem;box-shadow:0 18px 44px rgba(30,25,100,.25);}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1.1rem;margin:0 0 .4rem;}
.kpi{background:#fff;border-radius:24px;padding:1.3rem 1.4rem;box-shadow:0 14px 34px rgba(60,50,140,.08);}
.kpi .lab{color:var(--muted);font-size:.72rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;}
.kpi .val{color:var(--navy);font-size:2.05rem;font-weight:800;letter-spacing:-.03em;margin:.35rem 0 .15rem;line-height:1.1;}
.kpi .kn{color:var(--muted);font-size:.8rem;line-height:1.4;}
.kpi.dark{background:linear-gradient(135deg,#12142B,#262A6B);}
.kpi.dark .lab{color:#9A9EC9;}.kpi.dark .val{color:var(--lime);}.kpi.dark .kn{color:#B7BAE0;}
.tiles{display:grid;gap:1.1rem;margin:0 0 .4rem;}
.tiles.c3{grid-template-columns:repeat(3,1fr);}.tiles.c4{grid-template-columns:repeat(4,1fr);}.tiles.c5{grid-template-columns:repeat(5,1fr);}.tiles.c2{grid-template-columns:repeat(2,1fr);}
.tile{background:#fff;border-radius:24px;padding:1.5rem 1.5rem 1.4rem;box-shadow:0 14px 34px rgba(60,50,140,.08);}
.tile .num{width:38px;height:38px;border-radius:50%;background:var(--violet);color:#fff;font-weight:800;font-size:.95rem;display:flex;align-items:center;justify-content:center;margin-bottom:.95rem;}
.tile .num.lime{background:var(--lime);color:var(--navy);}
.tile h4{font-size:1.04rem!important;font-weight:800!important;color:var(--navy)!important;margin:0 0 .45rem!important;padding:0!important;letter-spacing:-.01em!important;line-height:1.3!important;}
.tile p{font-size:.9rem!important;color:var(--muted)!important;margin:0!important;line-height:1.6!important;}
.tile .meta{margin-top:.9rem;font-size:.78rem;font-weight:700;color:var(--violet);background:var(--violet-s);display:inline-block;padding:.3rem .8rem;border-radius:999px;}
.tile.final{background:linear-gradient(135deg,#12142B,#262A6B);}
.tile.final h4{color:#fff!important;}.tile.final p{color:#C5C8E8!important;}
.tile.final .meta{background:rgba(203,242,122,.16);color:var(--lime);}
.pill{display:inline-block;font-size:.74rem;font-weight:800;padding:.28rem .8rem;border-radius:999px;letter-spacing:.02em;}
.pill.lime{background:var(--lime);color:var(--navy);}.pill.violet{background:var(--violet-s);color:var(--violet);}
.pill.coral{background:#FFE3E5;color:#C23B49;}.pill.mint{background:#DDF5EA;color:#12795B;}
.note{background:var(--violet-s);border-left:4px solid var(--violet);border-radius:14px;padding:.95rem 1.15rem;font-size:.9rem;color:var(--ink);line-height:1.6;margin:.9rem 0;}
.note.warn{background:#FFF0F1;border-left-color:var(--coral);}.note.ok{background:#E7F8F0;border-left-color:var(--mint);}
.note b{color:var(--navy);}

/* ---------- tablas ---------- */
.tbl-wrap{overflow-x:auto;}
.tbl{width:100%;border-collapse:separate;border-spacing:0;font-size:.9rem;}
.tbl th{text-align:left;font-size:.7rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:.7rem .9rem;border-bottom:2px solid var(--line);}
.tbl td{padding:.85rem .9rem;border-bottom:1px solid var(--line);color:var(--ink);}
.tbl td:first-child{font-weight:700;color:var(--navy);}
.tbl td.best{font-weight:800;color:var(--violet);}
.tbl tr.final td{background:var(--violet-s);}
.tbl tr.final td:first-child{border-radius:14px 0 0 14px;}.tbl tr.final td:last-child{border-radius:0 14px 14px 0;}
.tbl tr:last-child td{border-bottom:none;}

/* ---------- prediccion ---------- */
.verdict{border-radius:20px;padding:1.05rem 1.3rem;font-size:1.05rem;font-weight:800;margin:.2rem 0 .8rem;line-height:1.4;}
.verdict.risk{background:#FFE3E5;color:#B42E3C;}.verdict.ok{background:#DDF5EA;color:#0F6E54;}
.verdict small{display:block;font-weight:600;font-size:.85rem;margin-top:.2rem;opacity:.9;}
.kv{display:grid;grid-template-columns:repeat(3,1fr);gap:.7rem;}
.kv div{background:#F7F6FF;border-radius:14px;padding:.65rem .85rem;}
.kv span{display:block;font-size:.68rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);}
.kv b{font-size:.92rem;color:var(--navy);word-break:break-word;}
.empty{text-align:center;padding:2.6rem 1rem;color:var(--muted);font-size:.95rem;}
.empty b{display:block;color:var(--navy);font-size:1.1rem;margin-bottom:.4rem;}

/* ---------- widgets ---------- */
[data-testid="stWidgetLabel"] p{font-size:.84rem;font-weight:700;color:var(--navy);}
[data-baseweb="select"] > div{background:#F7F6FF;border:1.5px solid var(--line);border-radius:14px!important;min-height:46px;}
[data-baseweb="input"]{background:#F7F6FF;border:1.5px solid var(--line);border-radius:14px!important;overflow:hidden;}
[data-baseweb="base-input"]{background:transparent!important;}
[data-testid="stNumberInput"] button{background:transparent;}
.stButton button,.stFormSubmitButton button,.stDownloadButton button{border-radius:999px;padding:.72rem 1.9rem;font-weight:700;font-size:.95rem;font-family:inherit;transition:all .18s ease;}
.stButton button[kind="primary"],.stFormSubmitButton button[kind="primaryFormSubmit"],.stFormSubmitButton button[kind="primary"],
button[data-testid="stBaseButton-primary"],button[data-testid="stBaseButton-primaryFormSubmit"]{background:var(--violet);color:#fff;border:none;box-shadow:0 12px 24px rgba(108,92,231,.35);}
.stButton button[kind="primary"]:hover,.stFormSubmitButton button:hover,button[data-testid="stBaseButton-primary"]:hover,button[data-testid="stBaseButton-primaryFormSubmit"]:hover{background:var(--violet-d);color:#fff;transform:translateY(-2px);}
.stButton button[kind="secondary"],button[data-testid="stBaseButton-secondary"]{background:#fff;color:var(--navy);border:1.5px solid var(--line);}
.stButton button[kind="secondary"]:hover,button[data-testid="stBaseButton-secondary"]:hover{border-color:var(--violet);color:var(--violet);transform:translateY(-2px);}
[data-baseweb="tab-list"]{gap:.4rem;background:#E9E5FB;padding:.35rem;border-radius:999px;width:fit-content;}
[data-baseweb="tab"]{border-radius:999px;padding:.55rem 1.35rem;height:auto;background:transparent;font-weight:700;}
[data-baseweb="tab"][aria-selected="true"]{background:#fff;box-shadow:0 6px 14px rgba(60,50,140,.12);}
[data-baseweb="tab"][aria-selected="true"] p{color:var(--violet);}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none;}
[data-testid="stExpander"] details{border:none;border-radius:20px;background:#fff;box-shadow:0 10px 26px rgba(60,50,140,.07);}
[data-testid="stExpander"] summary{padding:.9rem 1.2rem;font-weight:700;color:var(--navy);}
[data-testid="stSlider"] [data-testid="stThumbValue"]{color:var(--violet);font-weight:800;}
[data-testid="stForm"]{border:none;padding:0;}
[data-testid="stHorizontalBlock"]{align-items:stretch;}
.hero.hero-big{min-height:560px;padding:3.6rem 3.4rem;}
.hero.hero-big .hero-title{font-size:3.5rem;}
.hero.hero-big .hero-text{font-size:1.15rem;}
.stElementContainer:has(iframe[height="0"]){position:absolute;height:0;width:0;overflow:hidden;margin:0;}
@media (max-width:900px){.hero{grid-template-columns:1fr;padding:2rem 1.6rem;}.hero-title{font-size:2.2rem;}
.tiles.c3,.tiles.c4,.tiles.c5,.tiles.c2{grid-template-columns:1fr 1fr;}.kv{grid-template-columns:1fr 1fr;}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Evita que el traductor automático del navegador modifique la página (rompe Streamlit con el error "removeChild").
try:
    import streamlit.components.v1 as components

    components.html(
        """<script>
        const d = window.parent.document;
        d.documentElement.setAttribute('lang', 'es');
        d.documentElement.setAttribute('translate', 'no');
        d.body.classList.add('notranslate');
        if (!d.querySelector('meta[name="google"]')) {
            const m = d.createElement('meta'); m.name = 'google'; m.content = 'notranslate'; d.head.appendChild(m);
        }
        </script>""",
        height=0,
    )
except Exception:
    pass


# ------------------------------------------------------------------ utilidades
def H(texto):
    """Escribe HTML sin lineas en blanco (para que Markdown no lo corte)."""
    limpio = "\n".join(l.strip() for l in texto.strip().splitlines() if l.strip())
    st.markdown(limpio, unsafe_allow_html=True)


def svg_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()


LOGO = svg_uri(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="14" fill="#6C5CE7"/>'
    '<path d="M12 33 C18 18 28 36 36 15" stroke="#CBF27A" stroke-width="4" fill="none" stroke-linecap="round"/>'
    '<circle cx="12" cy="33" r="4" fill="#fff"/><circle cx="36" cy="15" r="4" fill="#fff"/></svg>'
)

HERO = svg_uri(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 440" width="600" height="440">'
    '<defs><linearGradient id="a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8F82FF"/><stop offset="1" stop-color="#5546D6"/></linearGradient></defs>'
    '<circle cx="450" cy="150" r="160" fill="#6C5CE7" opacity=".28"/>'
    '<circle cx="110" cy="340" r="110" fill="#CBF27A" opacity=".10"/>'
    '<path d="M40 372 C140 300 160 420 250 350 S470 250 560 96" fill="none" stroke="#CBF27A" stroke-width="4" stroke-linecap="round" stroke-dasharray="2 14"/>'
    '<circle cx="40" cy="372" r="11" fill="#fff" stroke="#CBF27A" stroke-width="4"/>'
    '<circle cx="560" cy="96" r="11" fill="#fff" stroke="#CBF27A" stroke-width="4"/>'
    '<polygon points="250,236 300,261 250,286 200,261" fill="#B9B0FF"/>'
    '<polygon points="200,261 250,286 250,342 200,317" fill="url(#a)"/>'
    '<polygon points="250,286 300,261 300,317 250,342" fill="#4234B8"/>'
    '<polygon points="236,243 266,258 266,274 236,259" fill="#CBF27A" opacity=".95"/>'
    '<rect x="40" y="36" width="240" height="124" rx="24" fill="#fff"/>'
    '<circle cx="100" cy="98" r="34" fill="none" stroke="#EEEBFF" stroke-width="10"/>'
    '<circle cx="100" cy="98" r="34" fill="none" stroke="#1FA97F" stroke-width="10" stroke-linecap="round" stroke-dasharray="58 214" transform="rotate(-90 100 98)"/>'
    '<text x="100" y="104" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="800" fill="#12142B">27 %</text>'
    '<text x="150" y="90" font-family="Arial, sans-serif" font-size="12" fill="#6A6E8E">Riesgo de retraso</text>'
    '<text x="150" y="114" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#12142B">Entrega a tiempo</text>'
    '<rect x="350" y="316" width="220" height="92" rx="22" fill="#1C1F42" stroke="#3A3F8F" stroke-width="2"/>'
    '<rect x="370" y="336" width="84" height="26" rx="13" fill="#CBF27A"/>'
    '<text x="412" y="353" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#12142B">RIESGO</text>'
    '<text x="370" y="388" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#FFFFFF">Pedido priorizado</text>'
    '<circle cx="470" cy="46" r="5" fill="#CBF27A"/><circle cx="500" cy="70" r="3" fill="#fff" opacity=".6"/><circle cx="430" cy="82" r="3" fill="#fff" opacity=".5"/>'
    "</svg>"
)


def page_head(eyebrow, titulo, sub):
    H(
        f"""<div class="eyebrow">{eyebrow}</div>
<div class="page-title">{titulo}</div>
<div class="page-sub">{sub}</div>"""
    )


def sec(titulo, sub=""):
    H(f'<div class="sec-title">{titulo}</div>' + (f'<div class="sec-sub">{sub}</div>' if sub else ""))


def kpis(items):
    celdas = ""
    for lab, val, nota, *dark in items:
        celdas += f'<div class="kpi{" dark" if dark and dark[0] else ""}"><div class="lab">{lab}</div><div class="val">{val}</div><div class="kn">{nota}</div></div>'
    H(f'<div class="kpis">{celdas}</div>')


def tiles(items, cols=3, numerado=True):
    celdas = ""
    for i, it in enumerate(items, 1):
        cls = " final" if it.get("final") else ""
        num = f'<div class="num{" lime" if it.get("final") else ""}">{it.get("num", i)}</div>' if numerado else ""
        meta = f'<div class="meta">{it["meta"]}</div>' if it.get("meta") else ""
        celdas += f'<div class="tile{cls}">{num}<h4>{it["t"]}</h4><p>{it["p"]}</p>{meta}</div>'
    H(f'<div class="tiles c{cols}">{celdas}</div>')


def nota(texto, tipo=""):
    H(f'<div class="note {tipo}">{texto}</div>')


def tabla(df, fmt="{:.4f}", final=None, mejor="max", col0="Modelo"):
    mejores = {c: (df[c].idxmax() if mejor == "max" else df[c].idxmin()) for c in df.columns if pd.api.types.is_numeric_dtype(df[c])}
    cab = f"<th>{col0}</th>" + "".join(f"<th>{c}</th>" for c in df.columns)
    filas = ""
    for idx, r in df.iterrows():
        celdas = ""
        for c in df.columns:
            v = r[c]
            txt = fmt.format(v) if isinstance(v, (int, float)) else str(v)
            clase = ' class="best"' if mejores.get(c) == idx else ""
            celdas += f"<td{clase}>{txt}</td>"
        filas += f'<tr{" class=final" if idx == final else ""}><td>{idx}</td>{celdas}</tr>'
    H(f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{cab}</tr></thead><tbody>{filas}</tbody></table></div>')


def estilo(fig, alto=360):
    fig.update_layout(
        height=alto,
        margin=dict(l=8, r=8, t=24, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, Segoe UI, sans-serif", color=INK, size=13),
        legend=dict(orientation="h", y=1.14, x=0, font=dict(size=12)),
        hoverlabel=dict(bgcolor=NAVY, font_color="#fff", bordercolor=NAVY),
    )
    fig.update_xaxes(showgrid=False, linecolor=LINE, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor="#EEEBFA", zeroline=False, tickfont=dict(color=MUTED))
    return fig


def mostrar(fig):
    try:
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def ir(pagina):
    st.session_state["pagina"] = pagina


# ------------------------------------------------------------------ carga de archivos
@st.cache_data
def cargar_info():
    return json.load(open(BASE / "datos" / "info_variables.json", encoding="utf-8"))


@st.cache_data
def cargar_muestra():
    return pd.read_csv(BASE / "datos" / "muestra_pedidos_test.csv")


@st.cache_data
def cargar_metricas_locales():
    return pd.read_csv(BASE / "datos" / "metricas_test_modelos.csv")


@st.cache_resource
def cargar_modelo(nombre):
    return joblib.load(BASE / "modelo" / f"{nombre}.joblib")


info = cargar_info()
NOMBRES = {
    "adaboost_arbol_FINAL": "AdaBoost + Árbol de Decisión (final)",
    "regresion_logistica": "Regresión Logística",
    "arbol_decision": "Árbol de Decisión",
    "random_forest": "Random Forest",
    "svm_muestra15000": "SVM (muestra de 15,000)",
    "bagging_arbol": "Bagging + Árbol de Decisión",
    "gradient_boosting": "Gradient Boosting",
}
PAGINAS = ["Inicio", "El problema", "Algoritmos", "Métricas", "Predicción"]
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "Inicio"

# ------------------------------------------------------------------ barra lateral
with st.sidebar:
    H(
        f"""<div class="brand"><img src="{LOGO}"/><div><b>DataCo Risk</b><span>Riesgo de retraso en entregas</span></div></div>
<div class="side-label">Navegación</div>"""
    )
    pagina = st.radio("Navegación", PAGINAS, key="pagina", label_visibility="collapsed")
    H("""<div class="side-foot"><b>Applied Machine Learning</b><br/>UTEC</div>""")

# ================================================================== constantes de la plantilla
DIAS = {"Same Day": 0, "First Class": 1, "Second Class": 2, "Standard Class": 4}
MAPA = {  # columna amigable -> columna del modelo
    "Fecha del pedido": None,
    "Tipo de pago": "Type",
    "Modo de envío": "Shipping Mode",
    "Segmento del cliente": "Customer Segment",
    "Mercado": "Market",
    "Región del pedido": "Order Region",
    "País de destino": "Order Country",
    "País del cliente": "Customer Country",
    "Estado del cliente": "Customer State",
    "Departamento": "Department Name",
    "Categoría": "Category Name",
    "Precio del producto": "Product Price",
    "Cantidad": "Order Item Quantity",
    "Descuento (monto)": "Order Item Discount",
    "Tasa de descuento": "Order Item Discount Rate",
    "Ratio de beneficio": "Order Item Profit Ratio",
    "Beneficio por pedido": "Order Profit Per Order",
}
LISTAS = [k for k, v in MAPA.items() if v in info["cols_cat"]]
NUMS = [k for k, v in MAPA.items() if v and v in info["cols_num"]]


def df_a_modelo(df):
    """Convierte la tabla amigable (plantilla) en las 20 columnas del modelo. Devuelve (X, filas_validas)."""
    faltan = [c for c in MAPA if c not in df.columns]
    if faltan:
        return None, faltan
    fechas = pd.to_datetime(df["Fecha del pedido"], errors="coerce")
    out = pd.DataFrame(index=df.index)
    for amigable, col in MAPA.items():
        if col:
            out[col] = df[amigable]
    for amigable in NUMS:
        col = MAPA[amigable]
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["order_year"], out["order_month"], out["order_dayofweek"] = fechas.dt.year, fechas.dt.month, fechas.dt.dayofweek
    out["Days for shipment (scheduled)"] = out["Shipping Mode"].map(DIAS)
    validas = out.notna().all(axis=1) & fechas.notna()
    out = out[validas].copy()
    for c in info["cols_cat"]:
        out[c] = out[c].astype(str).str.strip()
    for c in info["cols_num"]:
        if c in info["rangos"] and c not in ("order_year", "order_month", "order_dayofweek", "Days for shipment (scheduled)"):
            out[c] = out[c].clip(info["rangos"][c]["min"], info["rangos"][c]["max"])
        out[c] = out[c].astype(info["tipos"][c]) if info["tipos"][c].startswith("int") else out[c].astype(float)
    return out[info["columnas"]], validas


def plantilla_df():
    m = cargar_muestra().head(3)
    filas = []
    for _, r in m.iterrows():
        f = {"Fecha del pedido": f"{int(r['order_year'])}-{int(r['order_month']):02d}-15"}
        for amigable, col in MAPA.items():
            if col:
                f[amigable] = r[col]
        filas.append(f)
    return pd.DataFrame(filas)[list(MAPA)]


def ejemplo_df():
    m = cargar_muestra().head(40)
    out = pd.DataFrame({"Fecha del pedido": m["order_year"].astype(int).astype(str) + "-" + m["order_month"].astype(int).astype(str).str.zfill(2) + "-15"})
    for amigable, col in MAPA.items():
        if col:
            out[amigable] = m[col].values
    return out[list(MAPA)]


def a_csv(df):
    return df.to_csv(index=False).encode("utf-8-sig")


def plantilla_xlsx():
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    ws, wl = wb.active, wb.create_sheet("Listas")
    ws.title = "Pedidos"
    base = plantilla_df()
    ws.append(list(base.columns))
    for fila in base.itertuples(index=False):
        ws.append(list(fila))
    relleno = PatternFill("solid", fgColor="6C5CE7")
    for i, nombre in enumerate(base.columns, 1):
        c = ws.cell(row=1, column=i)
        c.font, c.fill, c.alignment = Font(bold=True, color="FFFFFF"), relleno, Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = max(16, len(nombre) + 4)
    ws.row_dimensions[1].height = 34
    ws.freeze_panes = "A2"
    for j, nombre in enumerate(LISTAS, 1):
        valores = info["categorias"][MAPA[nombre]]
        wl.cell(row=1, column=j, value=nombre).font = Font(bold=True)
        for k, v in enumerate(valores, 2):
            wl.cell(row=k, column=j, value=v)
        wl.column_dimensions[get_column_letter(j)].width = 24
        dv = DataValidation(type="list", formula1=f"=Listas!${get_column_letter(j)}$2:${get_column_letter(j)}${len(valores) + 1}", allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{get_column_letter(list(MAPA).index(nombre) + 1)}2:{get_column_letter(list(MAPA).index(nombre) + 1)}2000")
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def a_xlsx(df):
    buf = BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()


def leer_archivo(f):
    if f.name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(f)
    return pd.read_csv(f, sep=None, engine="python", encoding="utf-8-sig")


def tabla_resultados(df):
    cfg = {}
    try:
        cfg = {
            "Probabilidad de retraso (%)": st.column_config.ProgressColumn("Probabilidad de retraso", min_value=0, max_value=100, format="%.0f"),
        }
    except Exception:
        pass
    try:
        st.dataframe(df, hide_index=True, column_config=cfg, width="stretch", height=380)
    except TypeError:
        st.dataframe(df, hide_index=True, column_config=cfg, use_container_width=True, height=380)


NIVELES = {"Baja": 0.55, "Normal": 0.50, "Alta": 0.45}


def gauge(p, u):
    color = CORAL if p >= u else MINT
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=p * 100,
            number=dict(suffix=" %", valueformat=".0f", font=dict(size=46, color=NAVY)),
            gauge=dict(
                axis=dict(range=[0, 100], tickwidth=0, tickfont=dict(color=MUTED, size=11)),
                bar=dict(color=color, thickness=0.3),
                bgcolor="#F2F0FF",
                borderwidth=0,
                steps=[dict(range=[0, u * 100], color="#DDF5EA"), dict(range=[u * 100, 100], color="#FFE3E5")],
                threshold=dict(line=dict(color=NAVY, width=4), thickness=0.9, value=u * 100),
            ),
        )
    )
    estilo(fig, 205)
    fig.update_layout(margin=dict(l=36, r=44, t=30, b=0))
    return fig


# ================================================================== estilos y piezas de la segunda version
CSS2 = """
<style>
.ct{font-size:1.12rem;font-weight:800;letter-spacing:-.015em;color:var(--navy);margin:0 0 .3rem;line-height:1.3;}
.cs{font-size:.88rem;color:var(--muted);margin:0 0 1rem;line-height:1.55;}
.ct.w{color:#fff;}.cs.w{color:#B7BAE0;}
.lead{font-size:1.02rem;line-height:1.72;color:#3A3D5E;margin:0 0 .8rem;}
.grp{font-size:.7rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--violet);margin:.1rem 0 .6rem;}
.grid{display:grid;gap:1.1rem;margin:0 0 .4rem;}
.grid.g4{grid-template-columns:repeat(4,1fr);}.grid.g5{grid-template-columns:repeat(5,1fr);}.grid.g3{grid-template-columns:repeat(3,1fr);}
.mc{background:#fff;border-radius:24px;padding:1.35rem 1.4rem 1.3rem;box-shadow:0 14px 34px rgba(60,50,140,.08);display:flex;flex-direction:column;gap:.55rem;transition:transform .18s ease,box-shadow .18s ease;}
.mc:hover{transform:translateY(-4px);box-shadow:0 22px 40px rgba(60,50,140,.14);}
.mc .fam{align-self:flex-start;font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--violet);background:var(--violet-s);padding:.28rem .75rem;border-radius:999px;}
.mc h4{font-size:1.05rem!important;font-weight:800!important;color:var(--navy)!important;margin:.2rem 0 0!important;padding:0!important;letter-spacing:-.01em!important;line-height:1.25!important;}
.mc p{font-size:.86rem!important;color:var(--muted)!important;margin:0!important;line-height:1.55!important;flex:1;}
.mc .auc{margin-top:.5rem;font-size:.74rem;font-weight:700;color:var(--muted);display:flex;justify-content:space-between;}
.mc .auc b{color:var(--navy);}
.track{height:8px;border-radius:999px;background:#EEEBFF;overflow:hidden;margin-top:.35rem;}
.fill{height:100%;border-radius:999px;background:linear-gradient(90deg,#9A8FFF,#6C5CE7);animation:grow .9s ease-out;}
@keyframes grow{from{width:0}}
.mc.final{background:linear-gradient(135deg,#12142B,#262A6B);}
.mc.final .fam{background:rgba(203,242,122,.16);color:var(--lime);}
.mc.final h4{color:#fff!important;}.mc.final p{color:#C5C8E8!important;}
.mc.final .auc{color:#B7BAE0;}.mc.final .auc b{color:var(--lime);}
.mc.final .track{background:rgba(255,255,255,.14);}.mc.final .fill{background:var(--lime);}
.bar-row{display:grid;grid-template-columns:minmax(120px,170px) 1fr 54px;align-items:center;gap:.8rem;margin:.6rem 0;font-size:.86rem;}
.bar-row .rl{color:var(--ink);font-weight:600;line-height:1.25;}.bar-row .rv{font-weight:800;color:var(--navy);text-align:right;}
.bar-row .track{margin:0;height:10px;}
.bar-row.hl .rl{color:var(--violet);font-weight:800;}
.bar-row.hl .fill{background:linear-gradient(90deg,#12142B,#262A6B);}
.dark .bar-row .rl{color:#C5C8E8;}.dark .bar-row .rv{color:#fff;}.dark .bar-row .track{background:rgba(255,255,255,.14);}
.dark .bar-row .fill{background:#7F83B0;}.dark .bar-row.hl .rl{color:var(--lime);}.dark .bar-row.hl .fill{background:var(--lime);}
.rings{display:grid;grid-template-columns:repeat(5,1fr);gap:1.1rem;margin:0 0 .4rem;}
.ringc{background:#fff;border-radius:24px;padding:1.3rem 1rem 1.2rem;text-align:center;box-shadow:0 14px 34px rgba(60,50,140,.08);}
.ringc svg{width:98px;height:98px;display:block;margin:0 auto .6rem;}
.ringc svg text{font-family:inherit;}
.ringc .rl{font-size:.74rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);}
.ringc .rn{font-size:.8rem;color:var(--muted);margin-top:.25rem;line-height:1.4;}
.ringc.dark{background:linear-gradient(135deg,#12142B,#262A6B);}.ringc.dark .rl{color:#9A9EC9;}.ringc.dark .rn{color:#B7BAE0;}
.cm{display:grid;grid-template-columns:96px 1fr 1fr;gap:.55rem;align-items:stretch;}
.cm .ch{font-size:.7rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);text-align:center;padding:.2rem 0;}
.cm .rh{font-size:.7rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);display:flex;align-items:center;line-height:1.3;}
.cm .c{border-radius:18px;padding:1.1rem .6rem;text-align:center;font-size:1.6rem;font-weight:800;letter-spacing:-.02em;line-height:1.1;}
.cm .c small{display:block;font-size:.74rem;font-weight:600;letter-spacing:0;margin-top:.35rem;opacity:.85;}
.cm .good{background:#DDF5EA;color:#0F6E54;}.cm .bad{background:#FFE3E5;color:#B42E3C;}.cm .warn{background:#FFF1D9;color:#946014;}.cm .info{background:var(--violet-s);color:var(--violet-d);}
.dot-row{display:flex;gap:.85rem;align-items:flex-start;padding:.8rem 0;border-bottom:1px solid var(--line);}
.dot-row:last-child{border-bottom:none;padding-bottom:0;}.dot-row:first-child{padding-top:0;}
.dot{width:12px;height:12px;border-radius:50%;margin-top:.4rem;flex:none;}
.dot-row b{display:block;color:var(--navy);font-size:.95rem;line-height:1.35;}.dot-row span{color:var(--muted);font-size:.86rem;line-height:1.5;}
.split{display:flex;height:14px;border-radius:999px;overflow:hidden;margin:1.1rem 0 .7rem;background:rgba(255,255,255,.12);}
.split i{display:block;height:100%;}
.legend{display:flex;justify-content:space-between;font-size:.8rem;color:#C5C8E8;gap:1rem;}.legend b{color:#fff;display:block;font-size:1.05rem;}
.big-ring{text-align:center;}.big-ring svg{width:190px;height:190px;display:block;margin:.2rem auto 0;}.big-ring svg text{font-family:inherit;}
.flow{display:flex;gap:.7rem;flex-wrap:wrap;margin-top:.9rem;}
.flow div{flex:1;min-width:130px;background:#F7F6FF;border-radius:16px;padding:.75rem .95rem;}
.flow span{display:block;font-size:.66rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);}
.flow b{color:var(--navy);font-size:.92rem;line-height:1.35;display:block;margin-top:.15rem;}
.pills{display:flex;flex-wrap:wrap;gap:.45rem;margin:0 0 1rem;}
.pills:last-child{margin-bottom:0;}
.tip{background:var(--violet-s);border-radius:18px;padding:.95rem 1.15rem;font-size:.9rem;line-height:1.55;color:var(--ink);margin:.7rem 0 0;}
.tip b{color:var(--violet-d);}
.tip.dk{background:rgba(255,255,255,.08);color:#D8DAF2;}.tip.dk b{color:var(--lime);}
.stepc{display:flex;gap:.9rem;align-items:center;margin:0 0 .9rem;}
.stepc .num{width:36px;height:36px;border-radius:50%;background:var(--violet);color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center;flex:none;}
.stepc b{display:block;color:var(--navy);font-size:1rem;line-height:1.25;}.stepc span{color:var(--muted);font-size:.84rem;}
[data-testid="stColumn"] > [data-testid="stVerticalBlock"]{height:100%;}
[class*="st-key-card"]:only-child,[class*="st-key-dark"]:only-child{height:100%;}
@media (max-width:900px){.grid.g4,.grid.g3{grid-template-columns:1fr 1fr;}.rings{grid-template-columns:1fr 1fr;}.cm{grid-template-columns:70px 1fr 1fr;}}
</style>
"""
st.markdown(CSS2, unsafe_allow_html=True)


CSS3 = """
<style>
.pill.warm{background:#EEEBFF;color:#5546D6;}
.grp{color:#6C5CE7;}
.flow div{background:#F4F1FF;}
.tip{background:#F4F1FF;border-left:4px solid #8F82FF;border-radius:14px;}.tip b{color:#6C5CE7;}
.tip.dk{background:rgba(255,255,255,.08);border-left-color:var(--lime);}.tip.dk b{color:var(--lime);}
.tile .num{background:var(--navy);color:var(--lime);}
.dot{background:#8F82FF;}
.dot-row.sm{padding:.62rem 0;align-items:center;}.dot-row.sm .dot{margin-top:0;}.dot-row.sm b{font-size:.92rem;}
.drow{display:grid;grid-template-columns:104px 1fr;gap:.6rem;align-items:start;padding:.6rem 0;border-bottom:1px solid #ECE8FB;}
.drow:last-child{border-bottom:none;padding-bottom:0;}
.drow > span{font-size:.7rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#6C5CE7;padding-top:.38rem;}
.drow .pills{margin:0;gap:.35rem;}.drow .pill{font-size:.74rem;padding:.25rem .7rem;}
.big-ring svg{width:150px;height:150px;}
.mk{display:flex;flex-direction:column;gap:.35rem;}
.mk .fam{align-self:flex-start;font-size:.66rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#5546D6;background:#EEEBFF;padding:.25rem .7rem;border-radius:999px;}
.mk .fam.fin{background:var(--lime);color:var(--navy);}
.mk h4{font-size:1rem!important;font-weight:800!important;color:var(--navy)!important;margin:.15rem 0 0!important;padding:0!important;line-height:1.25!important;}
.mk p{font-size:.82rem!important;color:var(--muted)!important;margin:0 0 .35rem!important;line-height:1.45!important;}
[class*="st-key-mod"]{background:#fff;border-radius:22px;padding:1.05rem 1.15rem 1.1rem;box-shadow:0 12px 30px rgba(60,50,140,.08);border:2px solid transparent;transition:transform .18s ease;}
[class*="st-key-mod"]:hover{transform:translateY(-3px);}
[class*="st-key-modsel"]{border-color:var(--violet);box-shadow:0 16px 36px rgba(108,92,231,.22);}
[class*="st-key-mod"] button{width:100%;padding:.5rem 1rem;font-size:.86rem;}
[class*="st-key-dark_hint"]{display:flex;align-items:center;justify-content:center;text-align:center;}
[class*="st-key-card_f"]{justify-content:space-between;}
[data-testid="stButtonGroup"] button{border-radius:999px;}
</style>
"""
st.markdown(CSS3, unsafe_allow_html=True)


CSS4 = """
<style>
.block-container,[data-testid="stMainBlockContainer"]{padding-top:.4rem!important;padding-bottom:3rem;}
header[data-testid="stHeader"]{height:2rem;min-height:0;}
.eyebrow{margin-bottom:.55rem;}
.page-title{font-size:2.1rem;margin-bottom:.4rem;}
.page-sub{margin-bottom:1.1rem;font-size:1rem;}
.sec-title{margin:1.4rem 0 .3rem;}
[data-testid="stHorizontalBlock"]{align-items:flex-start;}
[data-testid="stHorizontalBlock"]:has(.st-key-card_f1),[data-testid="stHorizontalBlock"]:has(.st-key-card_b1){align-items:stretch;}
[data-testid="stHorizontalBlock"]:has(.st-key-card_f1) > [data-testid="stColumn"],[data-testid="stHorizontalBlock"]:has(.st-key-card_b1) > [data-testid="stColumn"]{display:flex;flex-direction:column;}
[data-testid="stHorizontalBlock"]:has(.st-key-card_f1) > [data-testid="stColumn"] > [data-testid="stVerticalBlock"],[data-testid="stHorizontalBlock"]:has(.st-key-card_b1) > [data-testid="stColumn"] > [data-testid="stVerticalBlock"]{flex:1 1 auto;}
[data-testid="stHorizontalBlock"]:has(.st-key-card_f1) > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"],[data-testid="stHorizontalBlock"]:has(.st-key-card_b1) > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]{flex:1 1 auto;display:flex;flex-direction:column;}
[data-testid="stHorizontalBlock"]:has(.st-key-card_f1) > [data-testid="stColumn"] [class*="st-key-card_f"],[data-testid="stHorizontalBlock"]:has(.st-key-card_b1) > [data-testid="stColumn"] [class*="st-key-card_b"]{flex:1 1 auto;height:100%;}
[class*="st-key-card"]{background:linear-gradient(160deg,#FFFFFF 0%,#F6F2FF 100%);padding:1.6rem 1.8rem 2.3rem;transition:transform .2s ease,box-shadow .2s ease;}
[class*="st-key-card"]:not([class*="st-key-card_f"]):hover{transform:translateY(-3px);box-shadow:0 24px 48px rgba(85,70,214,.16);}
[class*="st-key-dark"]{padding:1.6rem 1.8rem 2.3rem;background:linear-gradient(135deg,#12142B 0%,#2B2F7E 58%,#4A3FC4 100%);transition:transform .2s ease;}
[class*="st-key-dark"]:hover{transform:translateY(-3px);}
.tile,.kpi,.ringc{transition:transform .2s ease,box-shadow .2s ease;}
.tile:hover,.kpi:hover,.ringc:hover{transform:translateY(-4px);box-shadow:0 22px 40px rgba(85,70,214,.16);}
.tile{padding:1.25rem 1.4rem 1.5rem;background:linear-gradient(160deg,#fff,#F6F2FF);}
.tile .num{width:32px;height:32px;font-size:.85rem;margin-bottom:.6rem;background:linear-gradient(135deg,#8F82FF,#5546D6);color:#fff;}
.tile.final .num{background:var(--lime);color:var(--navy);}
.kpi{padding:1.05rem 1.25rem;}
.ringc{padding:1rem .8rem .95rem;background:linear-gradient(160deg,#fff,#F6F2FF);}
.ringc.dark{background:linear-gradient(135deg,#12142B,#2B2F7E 60%,#4A3FC4);}
.ringc svg{width:82px;height:82px;margin-bottom:.4rem;}
.fill{background:linear-gradient(90deg,#8F82FF,#C77DFF);}
.bar-row.hl .fill{background:linear-gradient(90deg,#5546D6,#C77DFF);}
.pill.warm,.mk .fam{background:linear-gradient(135deg,#EEEBFF,#F8E9FF);color:#5546D6;}
.mk .fam.fin{background:var(--lime);color:var(--navy);}
.mk p{min-height:2.9em;}
.grp,.drow > span{color:#6C5CE7;}
.flow div{background:linear-gradient(135deg,#F1EEFF,#FAEEFB);}
.tip{background:linear-gradient(135deg,#F1EEFF,#FAEEFB);border-left:4px solid #8F82FF;margin:1.2rem 0 .3rem;padding:1rem 1.25rem;}.tip b{color:#5546D6;}
.tip.dk{background:rgba(255,255,255,.08);border-left-color:var(--lime);}.tip.dk b{color:var(--lime);}
.dot{background:linear-gradient(135deg,#8F82FF,#F46FA5);}
.drow{border-bottom-color:#ECE8FB;}
.cs{margin-bottom:1.3rem;}
.dot-row:last-child{padding-bottom:.2rem;}
[class*="st-key-card_f"],[class*="st-key-card_b"],[class*="st-key-card_c0"],[class*="st-key-card_m2"]{padding-bottom:1.6rem;}
.legend{margin-bottom:.3rem;}
.stepc .num{background:linear-gradient(135deg,#8F82FF,#5546D6);}
.cm .warn{background:#FBE7FF;color:#8B2EA8;}.cm .info{background:#E4EAFF;color:#3B4FC4;}
.lead{font-size:.97rem;line-height:1.65;margin:0 0 .6rem;}
.dot-row.sm{padding:.7rem 0;}
.stButton button[kind="primary"],button[data-testid="stBaseButton-primary"]{background:linear-gradient(135deg,#8F82FF,#5546D6);}
.stButton button[kind="primary"]:hover,button[data-testid="stBaseButton-primary"]:hover{background:linear-gradient(135deg,#9C91FF,#4A3BC8);}
.stDownloadButton button{background:linear-gradient(135deg,#fff,#F4F1FF);border:1.5px solid var(--line);color:var(--navy);}
.stDownloadButton button:hover{border-color:var(--violet);color:var(--violet);transform:translateY(-2px);box-shadow:0 10px 20px rgba(108,92,231,.18);}
[data-baseweb="select"] > div,[data-baseweb="input"]{transition:all .15s ease;}
[data-baseweb="select"] > div:hover,[data-baseweb="input"]:hover{border-color:#8F82FF;box-shadow:0 0 0 3px rgba(143,130,255,.18);}
.verdict.risk{background:linear-gradient(135deg,#FFE3E5,#FFD0DA);}.verdict.ok{background:linear-gradient(135deg,#DDF5EA,#C6EFDF);}
</style>
"""
st.markdown(CSS4, unsafe_allow_html=True)


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def anillo_svg(valor, texto, color=VIOLET, pista="#EEEBFF", ink=NAVY, grosor=10):
    c = 263.9
    v = max(0.0, min(1.0, valor)) * c
    return (
        f'<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="42" fill="none" stroke="{pista}" stroke-width="{grosor}"/>'
        f'<circle cx="50" cy="50" r="42" fill="none" stroke="{color}" stroke-width="{grosor}" stroke-linecap="round" '
        f'stroke-dasharray="{v:.1f} {c - v:.1f}" transform="rotate(-90 50 50)"/>'
        f'<text x="50" y="58" text-anchor="middle" font-size="22" font-weight="800" fill="{ink}">{texto}</text></svg>'
    )


def anillos(items):
    celdas = ""
    for lab, valor, texto, nota_, *dark in items:
        d = bool(dark and dark[0])
        svg = anillo_svg(valor, texto, LIME if d else VIOLET, "rgba(255,255,255,.14)" if d else "#EEEBFF", "#FFFFFF" if d else NAVY)
        celdas += f'<div class="ringc{" dark" if d else ""}">{svg}<div class="rl">{lab}</div><div class="rn">{nota_}</div></div>'
    H(f'<div class="rings">{celdas}</div>')


def barras(items, destacado=None, fmt="{:.1%}", escala=None, oscuro=False):
    """items: lista (etiqueta, valor). escala=(min,max) para el ancho de la barra."""
    vals = [v for _, v in items]
    lo, hi = escala if escala else (0, max(vals))
    filas = ""
    for lab, v in items:
        w = max(3, min(100, (v - lo) / (hi - lo) * 100))
        hl = " hl" if lab == destacado else ""
        filas += f'<div class="bar-row{hl}"><div class="rl">{esc(lab)}</div><div class="track"><div class="fill" style="width:{w:.0f}%"></div></div><div class="rv">{fmt.format(v)}</div></div>'
    return f'<div class="{"dark" if oscuro else ""}">{filas}</div>'


def pills(textos, cls="violet"):
    return '<div class="pills">' + "".join(f'<span class="pill {cls}">{esc(t)}</span>' for t in textos) + "</div>"


def titulo_card(t, s="", w=False):
    suf = " w" if w else ""
    return f'<div class="ct{suf}">{t}</div>' + (f'<div class="cs{suf}">{s}</div>' if s else "")


def df_mostrar(df, alto=None):
    kw = {"hide_index": True}
    if alto:
        kw["height"] = alto
    try:
        st.dataframe(df, width="stretch", **kw)
    except TypeError:
        st.dataframe(df, use_container_width=True, **kw)


# ================================================================== datos por modelo
ORDEN = ["regresion_logistica", "svm_muestra15000", "arbol_decision", "random_forest", "bagging_arbol", "gradient_boosting", "adaboost_arbol_FINAL"]
DET = {
    "regresion_logistica": ("Base", "Regresión Logística", "Suma el peso de cada dato.",
        "Asigna un peso a cada dato del pedido y los suma para obtener una probabilidad. Es simple, rápida y fácil de explicar.",
        "Muy fácil de explicar y rápida.", "Solo capta relaciones sencillas entre los datos."),
    "svm_muestra15000": ("Base", "SVM", "Traza la mejor frontera.",
        "Busca la frontera que mejor separa los pedidos tardíos de los puntuales. Se entrenó con una muestra de 15,000 pedidos porque es lenta con muchos datos.",
        "Separa bien cuando los casos son claros.", "Lenta con muchos datos, por eso se usó una muestra."),
    "arbol_decision": ("Base", "Árbol de Decisión", "Preguntas de sí o no.",
        "Hace una serie de preguntas de sí o no sobre el pedido, como el modo de envío o el tipo de pago, hasta llegar a una decisión.",
        "Se entiende como un diagrama de decisiones.", "Un solo árbol puede ser inestable."),
    "random_forest": ("Ensamble", "Random Forest", "Cientos de árboles votan.",
        "Entrena cientos de árboles con muestras distintas y decide por votación. Así reduce los errores de un solo árbol.",
        "El mayor ROC-AUC de todos los modelos.", "Detecta menos retrasos reales que AdaBoost."),
    "bagging_arbol": ("Ensamble", "Bagging + Árbol", "Árboles con muestras distintas.",
        "Entrena muchos árboles, cada uno con una muestra diferente de los pedidos, y promedia sus respuestas.",
        "La mayor precisión: sus alertas casi siempre son reales.", "Deja pasar cerca de 4 de cada 10 retrasos."),
    "gradient_boosting": ("Ensamble", "Gradient Boosting", "Cada árbol corrige al anterior.",
        "Construye árboles en cadena: cada uno intenta corregir los errores del anterior hasta afinar la predicción.",
        "Alta precisión en sus alertas.", "Deja pasar cerca de 4 de cada 10 retrasos."),
    "adaboost_arbol_FINAL": ("Modelo final", "AdaBoost + Árbol", "Da más peso a los casos difíciles.",
        "Entrena árboles uno tras otro; cada nuevo árbol presta más atención a los pedidos que los anteriores clasificaron mal.",
        "Detecta más retrasos reales (recall de 68 %).", "Memoriza parte del entrenamiento; se controló con validación cruzada."),
}


def metricas_modelo(clave):
    """Métricas de prueba. El modelo final usa las cifras de nuestro notebook; los demás, las de su reentrenamiento en la app."""
    if clave == "adaboost_arbol_FINAL":
        return dict(acc=0.6714, prec=0.7102, rec=0.6771, f1=0.6932, auc=0.7416)
    r = cargar_metricas_locales().set_index("modelo").loc[clave]
    return dict(acc=float(r["accuracy"]), prec=float(r["precision"]), rec=float(r["recall"]), f1=float(r["f1"]), auc=float(r["roc_auc"]))


def nombre_corto(k):
    return DET[k][1]


# ================================================================== INICIO
if pagina == "Inicio":
    H(
        f"""<div class="hero hero-big"><div>
<div class="hero-tag">UTEC · Applied Machine Learning</div>
<div class="hero-title">Predicción de <em>riesgo de retraso</em> en entregas</div>
<div class="hero-text">DataCo Global</div>
</div><div><img src="{HERO}"/></div></div>"""
    )

# ================================================================== EL PROBLEMA
elif pagina == "El problema":
    page_head("El problema", "Un pedido tardío cuesta clientes", "Entender el retraso antes de que ocurra permite actuar a tiempo.")
    izq, der = st.columns([1.6, 1], gap="large")
    with izq:
        with st.container(key="card_p1"):
            H(
                titulo_card("Más de la mitad de los pedidos llega después de la fecha prometida")
                + '<p class="lead">DataCo Global vende suministros a clientes de cinco mercados. Cuando un pedido supera la fecha de entrega prevista, '
                "el cliente se molesta, aumentan los reclamos y se pierden ventas futuras.</p>"
                '<p class="lead">Hoy el retraso se descubre cuando ya ocurrió. Este modelo lo anticipa <b>antes del despacho</b>, '
                "para que logística pueda priorizar el pedido o cambiar el modo de envío.</p>"
                '<div class="flow"><div><span>Entrada</span><b>20 datos del pedido</b></div>'
                '<div><span>Resultado</span><b>Probabilidad de retraso</b></div>'
                '<div><span>Decisión</span><b>Priorizar o cambiar envío</b></div></div>'
            )
    with der:
        with st.container(key="dark_p2"):
            H(
                '<div class="big-ring">' + anillo_svg(0.5483, "54.8 %", LIME, "rgba(255,255,255,.14)", "#FFFFFF", 9) + "</div>"
                '<div class="ct w" style="text-align:center;margin:.5rem 0 0;font-size:1rem">de los pedidos llegó tarde</div>'
                '<div class="split"><i style="width:54.83%;background:#CBF27A"></i><i style="width:45.17%;background:#8F82FF"></i></div>'
                '<div class="legend"><div><b>98,977</b>con retraso</div><div style="text-align:right"><b>81,542</b>a tiempo</div></div>'
            )

    sec("Cómo funciona", "")
    tiles(
        [
            {"t": "Ingresas el pedido", "p": "Pago, envío, destino y producto. Manual o con plantilla."},
            {"t": "El modelo lo analiza", "p": "Lo compara con 180,519 entregas anteriores de DataCo."},
            {"t": "Recibes una probabilidad", "p": "Un valor de 0 % a 100 % de que llegue tarde."},
            {"t": "Decides", "p": "Priorizas el pedido o pruebas otro modo de envío."},
        ],
        cols=4,
    )

    st.write("")
    c1, c2 = st.columns([1.5, 1], gap="large")
    with c1:
        with st.container(key="card_p3"):
            def fila_datos(t, items):
                return f'<div class="drow"><span>{t}</span>' + pills(items, "warm") + "</div>"

            H(
                titulo_card("Qué datos usa el modelo", "Veinte datos que ya existen al registrar un pedido.")
                + fila_datos("Envío", ["Modo de envío", "Días programados", "Fecha"])
                + fila_datos("Cliente", ["Segmento", "País", "Estado"])
                + fila_datos("Destino", ["Mercado", "Región", "País de destino"])
                + fila_datos("Producto", ["Departamento", "Categoría", "Precio", "Cantidad"])
                + fila_datos("Comercial", ["Tipo de pago", "Descuento", "Tasa de descuento", "Ratio de beneficio", "Beneficio"])
            )
    with c2:
        with st.container(key="card_p4"):
            H(
                titulo_card("Qué tener presente", "Es una guía, no una certeza.")
                + '<div class="dot-row sm"><div class="dot"></div><b>Acierta cerca de 2 de cada 3 pedidos</b></div>'
                '<div class="dot-row sm"><div class="dot"></div><b>Casi 3 de cada 10 alertas son falsas</b></div>'
                '<div class="dot-row sm"><div class="dot"></div><b>Aprende de pedidos de 2015 a 2018</b></div>'
                '<div class="dot-row sm"><div class="dot"></div><b>No ve clima, huelgas ni tráfico</b></div>'
                '<div class="dot-row sm"><div class="dot"></div><b>Se puede reentrenar con datos nuevos</b></div>'
            )

# ================================================================== ALGORITMOS
elif pagina == "Algoritmos":
    page_head("Algoritmos", "Siete modelos comparados, uno elegido", "Selecciona un algoritmo para ver cómo funciona y cómo rindió.")
    if "alg_sel" not in st.session_state:
        st.session_state["alg_sel"] = "adaboost_arbol_FINAL"
    sel = st.session_state["alg_sel"]

    def elegir(k):
        st.session_state["alg_sel"] = k

    for fila in (ORDEN[:4], ORDEN[4:]):
        cols = st.columns(4, gap="medium")
        for i, k in enumerate(fila):
            fam, nom, corta = DET[k][:3]
            with cols[i]:
                with st.container(key=("modsel_" if k == sel else "mod_") + k):
                    H(f'<div class="mk"><span class="fam{" fin" if fam == "Modelo final" else ""}">{fam}</span><h4>{nom}</h4><p>{corta}</p></div>')
                    st.button("Seleccionado" if k == sel else "Ver detalle", key=f"alg_btn_{k}", type="primary" if k == sel else "secondary", on_click=elegir, args=(k,))
    st.write("")
    fam, nom, _, como, fuerte, limite = DET[sel]
    m = metricas_modelo(sel)
    c1, c2 = st.columns([1.2, 1], gap="large")
    with c1:
        with st.container(key="card_a1"):
            etiqueta = '<span class="pill lime">Modelo final</span>' if sel == "adaboost_arbol_FINAL" else f'<span class="pill warm">{fam}</span>'
            H(
                f'<div style="display:flex;justify-content:space-between;align-items:center;gap:1rem">{titulo_card(nom)}{etiqueta}</div>'
                f'<p class="lead">{como}</p>'
                f'<div class="flow"><div><span>Punto fuerte</span><b>{fuerte}</b></div><div><span>Limitación</span><b>{limite}</b></div></div>'
            )
    with c2:
        with st.container(key="dark_a2"):
            H(
                titulo_card("Cómo rindió con pedidos nuevos", "Datos de prueba, 36,104 pedidos.", True)
                + barras(
                    [("Exactitud", m["acc"]), ("Precisión", m["prec"]), ("Recall", m["rec"]), ("F1", m["f1"]), ("ROC-AUC", m["auc"])],
                    destacado="Recall", fmt="{:.0%}", escala=(0.4, 0.9), oscuro=True,
                )
            )

    sec("Cómo se eligió", "")
    tiles(
        [
            {"t": "Se separaron los datos", "p": "80 % para entrenar y 20 % (36,104 pedidos) para probar."},
            {"t": "Se comparó con validación cruzada", "p": "Cada modelo se evaluó varias veces con datos distintos."},
            {"t": "Se ajustó el finalista", "p": "AdaBoost con árboles de profundidad 12 y 50 árboles.", "meta": "Elegido por su recall"},
        ],
        cols=3,
    )

# ================================================================== MÉTRICAS
elif pagina == "Métricas":
    page_head("Resultados", "Qué tan bien funciona cada algoritmo", "Todos se probaron con los mismos 36,104 pedidos nuevos.")
    with st.container(key="card_c0"):
        k1, k2 = st.columns([1.4, 1.6], gap="large")
        with k1:
            clave = st.selectbox("Algoritmo", ORDEN[::-1], format_func=nombre_corto, key="met_modelo")
        with k2:
            H(
                '<div class="flow" style="margin:.1rem 0 0"><div><span>Estado</span><b>'
                + ("Modelo final elegido" if clave == "adaboost_arbol_FINAL" else "Modelo comparado")
                + '</b></div><div><span>Cifras</span><b>'
                + ("Del notebook del equipo" if clave == "adaboost_arbol_FINAL" else "Reentrenado para la app")
                + "</b></div></div>"
            )
    st.write("")
    m = metricas_modelo(clave)
    anillos(
        [
            ("Exactitud", m["acc"], f"{m['acc']:.0%}", "pedidos bien clasificados"),
            ("Precisión", m["prec"], f"{m['prec']:.0%}", "de las alertas eran reales"),
            ("Recall", m["rec"], f"{m['rec']:.0%}", "de los retrasos fueron detectados"),
            ("F1", m["f1"], f"{m['f1']:.0%}", "equilibrio entre precisión y recall"),
            ("ROC-AUC", m["auc"], f"{m['auc']:.2f}", "capacidad de separar casos", True),
        ]
    )
    st.write("")
    n_t, prev = 36104, 0.5483
    pos = n_t * prev
    tp = round(pos * m["rec"])
    fn = round(pos - tp)
    fp = round(tp / m["prec"] - tp)
    tn = n_t - tp - fn - fp
    c1, c2 = st.columns([1, 1.15], gap="large")
    with c1:
        with st.container(key="card_m1"):
            H(
                titulo_card(f"Qué pasó con los pedidos: {nombre_corto(clave)}", "Cifras aproximadas, reconstruidas a partir de las métricas.")
                + '<div class="cm"><div></div><div class="ch">Con alerta</div><div class="ch">Sin alerta</div>'
                f'<div class="rh">Llegó tarde</div><div class="c good">{tp:,}<small>retrasos detectados</small></div><div class="c bad">{fn:,}<small>retrasos no detectados</small></div>'
                f'<div class="rh">Llegó a tiempo</div><div class="c warn">{fp:,}<small>falsas alertas</small></div><div class="c info">{tn:,}<small>a tiempo confirmados</small></div></div>'
                f'<div class="tip"><b>En palabras simples:</b> de cada 10 pedidos que sí llegan tarde, detecta {m["rec"] * 10:.0f}. De cada 10 alertas, {m["prec"] * 10:.0f} son reales.</div>'
            )
    with c2:
        with st.container(key="card_m2"):
            H(titulo_card("Comparación entre algoritmos", "Elige la métrica. El algoritmo seleccionado va resaltado."))
            opciones = {"Exactitud": "acc", "Precisión": "prec", "Recall": "rec", "F1": "f1", "ROC-AUC": "auc"}
            try:
                metrica = st.segmented_control("Métrica", list(opciones), default="Recall", key="met_metrica", label_visibility="collapsed")
            except Exception:
                metrica = st.selectbox("Métrica", list(opciones), index=2, key="met_metrica", label_visibility="collapsed")
            metrica = metrica or "Recall"
            datos = sorted(((k, metricas_modelo(k)[opciones[metrica]]) for k in ORDEN), key=lambda t: t[1])
            fig = go.Figure(
                go.Bar(
                    x=[v for _, v in datos], y=[nombre_corto(k) for k, _ in datos], orientation="h",
                    marker_color=[VIOLET if k == clave else "#D3CEF7" for k, _ in datos],
                    text=[f"{v:.1%}" for _, v in datos], textposition="outside",
                )
            )
            estilo(fig, 270)
            fig.update_xaxes(range=[0.4, 1.0], visible=False)
            fig.update_yaxes(showgrid=False)
            mostrar(fig)

    sec("Sobre el modelo final", "")
    c3, c4 = st.columns([1.15, 1], gap="large")
    with c3:
        with st.container(key="card_m3"):
            H(titulo_card("Qué datos influyen más", "Importancia de cada dato en la decisión de AdaBoost."))
            imp = [
                ("Beneficio por pedido", 0.118460), ("Pago por transferencia", 0.072075), ("Descuento (monto)", 0.070539),
                ("Envío First Class", 0.068366), ("Ratio de beneficio", 0.056160), ("Mes del pedido", 0.050799),
            ]
            H(barras(imp, destacado="Beneficio por pedido", fmt="{:.1%}"))
    with c4:
        with st.container(key="dark_m4"):
            H(
                titulo_card("Una advertencia honesta", "ROC-AUC de AdaBoost: memoriza parte del entrenamiento.", True)
                + barras([("Entrenamiento", 0.9619), ("Validación cruzada", 0.7400), ("Prueba", 0.7416)], destacado="Entrenamiento", fmt="{:.2f}", escala=(0.5, 1.0), oscuro=True)
                +                 '<div class="tip dk"><b>Por eso se evaluó con pedidos nuevos.</b> La validación cruzada (0.7400) y la prueba (0.7416) coinciden, '
                "así que las cifras son confiables.</div>"
            )

# ================================================================== PREDICCIÓN
else:
    page_head("Predicción", "¿Llegará tarde este pedido?", "Ingresa un pedido o sube varios a la vez.")
    with st.container(key="card_c0"):
        k1, k2, k3 = st.columns([1.2, 1.2, 1], gap="large")
        with k1:
            clave = st.selectbox("Modelo", list(NOMBRES), format_func=lambda k: NOMBRES[k], index=0, key="p_modelo")
        with k2:
            nivel = st.select_slider("Sensibilidad de la alerta", options=list(NIVELES), value="Normal", key="p_nivel")
        umbral = NIVELES[nivel]
        with k3:
            H(f'<div class="flow" style="margin:.1rem 0 0"><div><span>Alerta desde</span><b>{umbral:.0%} de probabilidad</b></div></div>')
    modelo = cargar_modelo(clave)
    st.write("")

    def preparar(fila):
        X = pd.DataFrame([fila])[info["columnas"]]
        for c in info["cols_cat"]:
            X[c] = X[c].astype(str)
        return X

    tab1, tab2 = st.tabs(["Un pedido", "Varios pedidos"])

    # ---------------------------------------------------------------- un pedido
    with tab1:
        rg, cat = info["rangos"], info["categorias"]
        izq, der = st.columns([1.35, 1], gap="large")
        with izq:
            with st.container(key="card_f1"):
                H('<div class="grp">Envío</div>')
                a1, a2, a3 = st.columns(3)
                modo = a1.selectbox("Modo de envío", list(DIAS), index=3, key="p_modo")
                fecha = a2.date_input("Fecha del pedido", value=pd.Timestamp("2016-06-15").date(), min_value=pd.Timestamp("2015-01-01").date(), max_value=pd.Timestamp("2018-12-31").date(), key="p_fecha")
                tipo = a3.selectbox("Tipo de pago", cat["Type"], key="p_tipo")
                H('<div class="grp" style="margin-top:.8rem">Cliente y destino</div>')
                c1, c2, c3 = st.columns(3)
                mercado = c1.selectbox("Mercado", cat["Market"], key="p_mercado")
                region = c2.selectbox("Región", cat["Order Region"], key="p_region")
                pais_o = c3.selectbox("País de destino", cat["Order Country"], index=cat["Order Country"].index("Estados Unidos") if "Estados Unidos" in cat["Order Country"] else 0, key="p_pais_o")
                d1, d2, d3 = st.columns(3)
                seg = d1.selectbox("Segmento del cliente", cat["Customer Segment"], key="p_seg")
                pais_c = d2.selectbox("País del cliente", cat["Customer Country"], key="p_pais_c")
                estado_c = d3.selectbox("Estado del cliente", cat["Customer State"], index=cat["Customer State"].index("CA") if "CA" in cat["Customer State"] else 0, key="p_estado")
                H('<div class="grp" style="margin-top:.8rem">Producto y precio</div>')
                e1, e2, e3 = st.columns(3)
                depto = e1.selectbox("Departamento", cat["Department Name"], key="p_depto")
                categoria = e2.selectbox("Categoría", cat["Category Name"], key="p_cat")
                precio = e3.number_input("Precio del producto", rg["Product Price"]["min"], rg["Product Price"]["max"], rg["Product Price"]["mediana"], key="p_precio")
                f1, f2, f3 = st.columns(3)
                cant = f1.number_input("Cantidad", 1, 5, 1, 1, key="p_cant")
                desc = f2.number_input("Descuento (monto)", rg["Order Item Discount"]["min"], rg["Order Item Discount"]["max"], rg["Order Item Discount"]["mediana"], key="p_desc")
                tasa = f3.number_input("Tasa de descuento", 0.0, 0.25, 0.10, 0.01, key="p_tasa")
                g1, g2, _g3 = st.columns(3)
                ratio = g1.number_input("Ratio de beneficio", rg["Order Item Profit Ratio"]["min"], rg["Order Item Profit Ratio"]["max"], rg["Order Item Profit Ratio"]["mediana"], key="p_ratio")
                ben = g2.number_input("Beneficio por pedido", rg["Order Profit Per Order"]["min"], rg["Order Profit Per Order"]["max"], rg["Order Profit Per Order"]["mediana"], key="p_ben")

        f = pd.Timestamp(fecha)
        fila = {
            "Type": tipo, "Days for shipment (scheduled)": DIAS[modo], "Category Name": categoria,
            "Customer Country": pais_c, "Customer Segment": seg, "Customer State": estado_c,
            "Department Name": depto, "Market": mercado, "Order Country": pais_o,
            "Order Item Discount": float(desc), "Order Item Discount Rate": float(tasa),
            "Order Item Profit Ratio": float(ratio), "Order Item Quantity": int(cant),
            "Order Profit Per Order": float(ben), "Order Region": region,
            "Product Price": float(precio), "Shipping Mode": modo,
            "order_year": int(f.year), "order_month": int(f.month), "order_dayofweek": int(f.dayofweek),
        }
        p = float(modelo.predict_proba(preparar(fila))[0, 1])
        riesgo = p >= umbral
        probs_modo = {}
        for m_envio in DIAS:
            variante = dict(fila, **{"Shipping Mode": m_envio, "Days for shipment (scheduled)": DIAS[m_envio]})
            probs_modo[m_envio] = float(modelo.predict_proba(preparar(variante))[0, 1])
        mejor = min(probs_modo, key=probs_modo.get)

        with der:
            with st.container(key="card_f2"):
                H(titulo_card("Resultado del pedido", "Se actualiza al cambiar cualquier dato."))
                mostrar(gauge(p, umbral))
                if riesgo:
                    H('<div class="verdict risk">Riesgo de retraso<small>Conviene priorizar este pedido.</small></div>')
                else:
                    H('<div class="verdict ok">Llegará a tiempo<small>No requiere acción especial.</small></div>')
                H(titulo_card("Simulador de envío", "Probabilidad de retraso si el pedido se enviara de otra forma.").replace('class="ct"', 'class="ct" style="margin-top:1.1rem;font-size:1rem"'))
                nombres_m = list(probs_modo)
                vals = [probs_modo[k] * 100 for k in nombres_m]
                fig = go.Figure(go.Bar(x=[k.replace(" Class", "") for k in nombres_m], y=vals, marker_color=[VIOLET if k == modo else "#C9C1FF" for k in nombres_m], text=[f"{v:.0f} %" for v in vals], textposition="inside", insidetextanchor="end", textfont=dict(color=NAVY, size=13)))
                estilo(fig, 215)
                fig.update_xaxes(tickangle=0, tickfont=dict(size=12, color=INK))
                fig.add_hline(y=umbral * 100, line_color=NAVY, line_width=2, line_dash="dot")
                fig.update_yaxes(range=[0, 100], visible=False)
                mostrar(fig)
                if mejor != modo and probs_modo[modo] - probs_modo[mejor] >= 0.02:
                    H(f'<div class="tip"><b>Mejor opción: {esc(mejor)}.</b> Bajaría el riesgo de {probs_modo[modo]:.0%} a {probs_modo[mejor]:.0%}.</div>')
                else:
                    H(f'<div class="tip"><b>{esc(modo)} ya es la mejor opción</b> para este pedido.</div>')

    # ---------------------------------------------------------------- varios pedidos
    with tab2:
        s1, s2, s3 = st.columns(3, gap="large")
        with s1:
            with st.container(key="card_b1"):
                H('<div class="stepc"><div class="num">1</div><div><b>Descarga la plantilla</b><span>Ya incluye todas las columnas.</span></div></div>')
                d1, d2 = st.columns(2)
                d1.download_button("CSV", a_csv(plantilla_df()), "plantilla_pedidos.csv", "text/csv", key="dl_csv")
                try:
                    d2.download_button("Excel", plantilla_xlsx(), "plantilla_pedidos.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx")
                except Exception:
                    pass
        with s2:
            with st.container(key="card_b2a"):
                H('<div class="stepc"><div class="num">2</div><div><b>Complétala</b><span>Una fila por pedido. El Excel trae listas desplegables.</span></div></div>')
                if st.button("Probar con pedidos de ejemplo", type="secondary", key="btn_ej"):
                    st.session_state["lote"] = ejemplo_df()
                    st.session_state["lote_nombre"] = "Pedidos de ejemplo"
        with s3:
            with st.container(key="card_b3a"):
                H('<div class="stepc"><div class="num">3</div><div><b>Súbela aquí</b><span>Formato CSV o Excel.</span></div></div>')
                archivo = st.file_uploader("Archivo con pedidos", type=["csv", "xlsx"], key="up_lote", label_visibility="collapsed")
                if archivo is not None:
                    try:
                        st.session_state["lote"] = leer_archivo(archivo)
                        st.session_state["lote_nombre"] = archivo.name
                    except Exception:
                        st.error("No se pudo leer el archivo. Usa la plantilla CSV o Excel.")

        lote = st.session_state.get("lote")
        if lote is None:
            st.write("")
            with st.container(key="card_b5"):
                H(
                    titulo_card("Así luce la plantilla", "Estas son las 17 columnas que debes completar. Los días de envío se calculan solos a partir del modo de envío.")
                )
                df_mostrar(plantilla_df())
        else:
            X, validas = df_a_modelo(lote)
            if X is None:
                st.error("Faltan columnas en tu archivo: " + ", ".join(validas) + ". Descarga la plantilla y úsala tal cual.")
            elif len(X) == 0:
                st.error("Ninguna fila está completa. Revisa que no haya celdas vacías.")
            else:
                probs = modelo.predict_proba(X)[:, 1]
                res = pd.DataFrame(
                    {
                        "Fila": X.index + 2,
                        "Fecha": lote.loc[X.index, "Fecha del pedido"].astype(str).str[:10].values,
                        "Modo de envío": X["Shipping Mode"].values,
                        "País de destino": X["Order Country"].values,
                        "Probabilidad de retraso (%)": (probs * 100).round(1),
                        "Estado": ["Riesgo" if q >= umbral else "A tiempo" for q in probs],
                    }
                ).sort_values("Probabilidad de retraso (%)", ascending=False)
                n, n_r = len(res), int((res["Estado"] == "Riesgo").sum())
                omitidas = int((~validas).sum())
                st.write("")
                kpis(
                    [
                        ("Pedidos evaluados", f"{n}", f"{omitidas} filas incompletas omitidas" if omitidas else f"archivo: {esc(st.session_state.get('lote_nombre', ''))}"),
                        ("Con riesgo", f"{n_r}", f"{n_r / n:.0%} del total", True),
                        ("Probabilidad media", f"{probs.mean():.0%}", "de retraso"),
                    ]
                )
                st.write("")
                g1, g2 = st.columns(2, gap="large")
                with g1:
                    with st.container(key="card_b2"):
                        H(titulo_card("Reparto de pedidos", "Cuántos requieren atención."))
                        fig = go.Figure(go.Pie(labels=["Riesgo", "A tiempo"], values=[n_r, n - n_r], hole=0.66, marker=dict(colors=[CORAL, MINT], line=dict(color="#fff", width=3)), textinfo="percent", sort=False))
                        estilo(fig, 260)
                        fig.update_layout(legend=dict(orientation="h", y=-0.05, x=0.25))
                        mostrar(fig)
                with g2:
                    with st.container(key="card_b3"):
                        H(titulo_card("Riesgo por modo de envío", "Probabilidad media de retraso."))
                        por_modo = res.groupby("Modo de envío")["Probabilidad de retraso (%)"].mean().sort_values()
                        fig = go.Figure(go.Bar(x=por_modo.values, y=por_modo.index, orientation="h", marker_color=VIOLET, text=[f"{v:.0f} %" for v in por_modo.values], textposition="outside"))
                        estilo(fig, 260)
                        fig.update_xaxes(range=[0, 100], visible=False)
                        fig.update_yaxes(showgrid=False)
                        mostrar(fig)
                st.write("")
                with st.container(key="card_b4"):
                    H(titulo_card("Pedidos ordenados por riesgo", "Los primeros son los que conviene atender antes."))
                    tabla_resultados(res)
                    r1, r2, r3, _ = st.columns([1, 1, 1, 2])
                    r1.download_button("Resultados CSV", a_csv(res), "resultados_riesgo.csv", "text/csv", key="dl_res_csv")
                    try:
                        r2.download_button("Resultados Excel", a_xlsx(res), "resultados_riesgo.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_res_xlsx")
                    except Exception:
                        pass
                    if r3.button("Limpiar", type="secondary", key="btn_limpiar"):
                        st.session_state.pop("lote", None)
                        st.session_state.pop("lote_nombre", None)
                        st.rerun()
