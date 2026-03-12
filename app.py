"""
Mesa RV — Dashboard Real-Time
Netuno Investimentos | Grupo Netuno
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

# ─── Page Config ───
st.set_page_config(
    page_title="Mesa RV | Netuno Investimentos",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Colors ───
PRIMARY = "#004356"
ACCENT = "#00acad"
SECONDARY = "#191970"
GREEN = "#00c853"
RED = "#ff1744"
DARK_BG = "#0a1628"
CARD_BG = "#111d33"
ROW_BG = "#0f1a2e"
ROW_HOVER = "#162240"

# ─── CSS (dark theme) ───
st.markdown(f"""
<style>
    .stApp {{
        background-color: {DARK_BG};
        color: #e0e0e0;
    }}
    [data-testid="stSidebar"] {{
        background-color: {CARD_BG};
        border-right: 1px solid #1a2a45;
    }}
    [data-testid="stSidebar"] * {{
        color: #ccc !important;
    }}
    [data-testid="stSidebar"] .stTextArea textarea {{
        color: #ddd !important;
        background: {ROW_BG};
        border: 1px solid #1a2a45;
    }}
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb] {{
        background: {ROW_BG};
    }}
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb] {{
        background: {ROW_BG};
    }}
    .header-bar {{
        background: linear-gradient(135deg, {PRIMARY}, {SECONDARY});
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .header-title {{
        color: white;
        font-size: 22px;
        font-weight: 700;
        margin: 0;
    }}
    .header-info {{
        color: rgba(255,255,255,0.7);
        font-size: 13px;
        text-align: right;
    }}
    .market-badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }}
    .market-open {{ background: rgba(0,200,83,0.2); color: {GREEN}; }}
    .market-closed {{ background: rgba(255,23,68,0.2); color: {RED}; }}
    .stock-row {{
        display: flex;
        align-items: center;
        padding: 8px 16px;
        border-bottom: 1px solid #1a2a45;
        transition: background 0.15s;
    }}
    .stock-row:hover {{
        background: {ROW_HOVER};
    }}
    .stock-ticker {{
        font-weight: 700;
        font-size: 14px;
        color: white;
        width: 90px;
        flex-shrink: 0;
    }}
    .stock-price {{
        font-weight: 600;
        font-size: 14px;
        width: 100px;
        text-align: right;
        flex-shrink: 0;
    }}
    .stock-change {{
        font-weight: 600;
        font-size: 13px;
        width: 80px;
        text-align: right;
        flex-shrink: 0;
        padding: 2px 8px;
        border-radius: 6px;
        margin-left: 8px;
    }}
    .change-up {{
        color: {GREEN};
        background: rgba(0,200,83,0.12);
    }}
    .change-down {{
        color: {RED};
        background: rgba(255,23,68,0.12);
    }}
    .stock-vol {{
        color: #667;
        font-size: 12px;
        width: 100px;
        text-align: right;
        flex-shrink: 0;
        margin-left: 8px;
    }}
    .stock-range {{
        color: #556;
        font-size: 12px;
        flex: 1;
        text-align: right;
        margin-left: 8px;
    }}
    .stock-header {{
        display: flex;
        padding: 6px 16px;
        border-bottom: 2px solid #1a2a45;
        color: #556;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .stock-header span {{
        flex-shrink: 0;
    }}
    .stock-list {{
        background: {CARD_BG};
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #1a2a45;
    }}
    .stats-card {{
        background: {CARD_BG};
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #1a2a45;
        text-align: center;
    }}
    .stats-value {{
        font-size: 24px;
        font-weight: 700;
        color: white;
    }}
    .stats-label {{
        font-size: 12px;
        color: #667;
        margin-top: 4px;
    }}
</style>
""", unsafe_allow_html=True)

# ─── Auto-refresh ───
try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

# ─── Timezone ───
BRT = pytz.timezone("America/Sao_Paulo")


def is_market_open():
    now = datetime.now(BRT)
    return now.weekday() < 5 and 10 <= now.hour < 18


# ─── Tickers ───
ALL_B3_TICKERS = [
    "AALR3", "ABCB10", "ABCB4", "ABEV3", "ADMF3", "AERI3", "AFLT3", "AGRO3", "AGXY3", "AHEB3",
    "ALLD3", "ALOS3", "ALPA3", "ALPA4", "ALPK3", "ALUP11", "ALUP3", "ALUP4", "AMAR3", "AMBP3",
    "AMER3", "AMOB3", "ANIM3", "ARML3", "ARND3", "ASAI3", "ATED3", "AUAU3", "AURE3", "AVLL3",
    "AXIA3", "AXIA5", "AXIA6", "AZEV3", "AZEV4", "AZTE3", "AZZA3", "BALM4", "BAUH4", "BAZA3",
    "BBAS3", "BBDC3", "BBDC4", "BBSE3", "BDLL3", "BDLL4", "BEEF3", "BEES3", "BEES4", "BGIP3",
    "BGIP4", "BHIA3", "BIED3", "BIOM3", "BLAU3", "BMEB3", "BMEB4", "BMGB10", "BMGB4", "BMIN3",
    "BMIN4", "BMKS3", "BMOB3", "BNBR3", "BOBR4", "BPAC11", "BPAC3", "BPAC5", "BRAP3", "BRAP4",
    "BRAV3", "BRKM3", "BRKM5", "BRKM6", "BRSR3", "BRSR5", "BRSR6", "BRST3", "BSLI3", "BSLI4",
    "CAMB3", "CAML3", "CASH3", "CBAV3", "CBEE3", "CEAB3", "CEBR3", "CEBR5", "CEBR6", "CEDO4",
    "CEEB3", "CGAS3", "CGAS5", "CGRA3", "CGRA4", "CLSC3", "CLSC4", "CMIG3", "CMIG4", "CMIN3",
    "COCE5", "COGN3", "CPFE3", "CPLE3", "CRPG3", "CRPG5", "CRPG6", "CSAN3", "CSED3", "CSMG3",
    "CSNA3", "CSUD3", "CTAX3", "CTKA3", "CTKA4", "CTSA3", "CTSA4", "CURY3", "CVCB3", "CXSE3",
    "CYRE3", "CYRE4", "DASA3", "DESK3", "DEXP3", "DEXP4", "DIRR3", "DMVF3", "DOHL4", "DOTZ3",
    "DXCO3", "EALT3", "EALT4", "ECOR3", "EGIE3", "EKTR3", "EKTR4", "EMAE4", "EMBJ3", "ENEV3",
    "ENGI11", "ENGI3", "ENGI4", "ENJU3", "ENMT3", "ENMT4", "EPAR3", "EQPA3", "EQPA5", "EQTL3",
    "ESPA3", "ETER3", "EUCA3", "EUCA4", "EVEN3", "EZTC3", "FESA3", "FESA4", "FHER3", "FICT3",
    "FIGE3", "FIQE3", "FLRY3", "FRAS3", "GEPA3", "GEPA4", "GFSA3", "GGBR3", "GGBR4", "GGPS3",
    "GMAT3", "GOAU3", "GOAU4", "GRND3", "GSHP3", "HAGA3", "HAGA4", "HAPV3", "HBOR3", "HBRE3",
    "HBSA3", "HBTS5", "HOOT4", "HYPE3", "IFCM3", "IGTI11", "IGTI3", "IGTI4", "INEP3", "INEP4",
    "INTB3", "IRBR3", "ISAE3", "ISAE4", "ITSA3", "ITSA4", "ITUB3", "ITUB4", "JALL3", "JFEN3",
    "JHSF3", "JSLG3", "KEPL3", "KLBN11", "KLBN3", "KLBN4", "LAND3", "LAVV3", "LEVE3", "LIGT3",
    "LJQQ3", "LOGG3", "LOGN3", "LPSB3", "LREN3", "LUPA3", "LUXM4", "LWSA3", "MATD3", "MBRF3",
    "MDIA3", "MDNE3", "MEAL3", "MELK3", "MERC4", "MGEL4", "MGLU3", "MILS3", "MLAS3", "MNDL3",
    "MNPR3", "MOTV3", "MOVI3", "MRVE3", "MTRE3", "MTSA4", "MULT3", "MWET4", "MYPK3", "NATU3",
    "NEOE3", "NEXP3", "NGRD3", "NORD3", "NUTR3", "OBTC3", "ODPV3", "OFSA3", "OIBR3", "OIBR4",
    "ONCO3", "OPCT3", "ORVR3", "OSXB3", "PATI3", "PCAR3", "PDGR3", "PDTC3", "PEAB3", "PEAB4",
    "PETR3", "PETR4", "PFRM3", "PGMN3", "PINE10", "PINE3", "PINE4", "PLAS3", "PLPL3", "PMAM3",
    "PNVL3", "POMO3", "POMO4", "POSI3", "PRIO3", "PRNR3", "PSSA3", "PTBL3", "PTNT3", "PTNT4",
    "QUAL3", "RADL3", "RAIL3", "RAIZ4", "RANI3", "RAPT3", "RAPT4", "RCSL3", "RCSL4", "RDOR3",
    "RECV3", "REDE3", "RENT3", "RENT4", "RIAA3", "RNEW3", "RNEW4", "ROMI3", "RPAD3", "RPAD5",
    "RPAD6", "RPMG3", "RSID3", "RSUL4", "RVEE3", "SANB11", "SANB3", "SANB4", "SAPR11", "SAPR3",
    "SAPR4", "SBFG3", "SBSP3", "SCAR3", "SEER3", "SEQL3", "SHOW3", "SHUL4", "SIMH3", "SLCE3",
    "SMFT3", "SMTO3", "SNSY5", "SOJA3", "SOND5", "SOND6", "SUZB3", "SYNE3", "TAEE11", "TAEE3",
    "TAEE4", "TASA3", "TASA4", "TCSA3", "TECN3", "TELB3", "TELB4", "TEND3", "TFCO4", "TGMA3",
    "TIMS3", "TKNO3", "TKNO4", "TOKY3", "TOTS3", "TPIS3", "TRAD3", "TRIS3", "TTEN3", "TUPY3",
    "TXRX4", "UCAS3", "UGPA3", "UNIP3", "UNIP5", "UNIP6", "USIM3", "USIM5", "USIM6", "VALE3",
    "VAMO3", "VBBR3", "VITT3", "VIVA3", "VIVR3", "VIVT3", "VLID3", "VSTE3", "VTRU3", "VULC3",
    "VVEO3", "WDCN3", "WEGE3", "WEST3", "WHRL3", "WHRL4", "WIZC3", "WLMM3", "WLMM4", "YDUQ3",
]

# ─── Sidebar ───
st.sidebar.markdown("## 📈 Mesa RV")
st.sidebar.markdown("---")

# Refresh
refresh_options = {"5 seg": 5, "10 seg": 10, "30 seg": 30, "1 min": 60}
refresh_label = st.sidebar.selectbox("⏱️ Refresh", list(refresh_options.keys()), index=1)
refresh_sec = refresh_options[refresh_label]

if HAS_AUTOREFRESH:
    st_autorefresh(interval=refresh_sec * 1000, key="data_refresh")
else:
    if st.sidebar.button("🔄 Atualizar"):
        st.rerun()

st.sidebar.markdown("---")

# Charts in sidebar
chart_mode = st.sidebar.radio("📊 Gráfico", ["Individual", "Comparativo"], index=0)

st.sidebar.markdown("---")

# Tickers
default_tickers = "\n".join(ALL_B3_TICKERS)
tickers_text = st.sidebar.text_area("📋 Tickers", value=default_tickers, height=200)
tickers = [t.strip().upper() for t in tickers_text.split("\n") if t.strip() and len(t.strip()) >= 4]

st.sidebar.markdown("---")
st.sidebar.caption("Yahoo Finance | © Netuno Investimentos")


# ─── Data Fetching ───
@st.cache_data(ttl=15)
def fetch_all(tickers_tuple):
    """Fetch data for all tickers using batch download."""
    symbols = [f"{t}.SA" for t in tickers_tuple]
    results = {}

    try:
        df_intra = yf.download(
            symbols, period="1d", interval="1m",
            progress=False, threads=True, group_by="ticker",
        )
        df_daily = yf.download(
            symbols, period="5d", interval="1d",
            progress=False, threads=True, group_by="ticker",
        )
    except Exception:
        return results

    for t in tickers_tuple:
        sym = f"{t}.SA"
        try:
            if len(tickers_tuple) == 1:
                close_i = df_intra["Close"].dropna()
                vol_i = df_intra["Volume"].dropna()
                high_i = df_intra["High"].dropna()
                low_i = df_intra["Low"].dropna()
                open_i = df_intra["Open"].dropna()
                close_d = df_daily["Close"].dropna()
            else:
                close_i = df_intra[(sym, "Close")].dropna() if (sym, "Close") in df_intra.columns else df_intra[sym]["Close"].dropna()
                vol_i = df_intra[(sym, "Volume")].dropna() if (sym, "Volume") in df_intra.columns else df_intra[sym]["Volume"].dropna()
                high_i = df_intra[(sym, "High")].dropna() if (sym, "High") in df_intra.columns else df_intra[sym]["High"].dropna()
                low_i = df_intra[(sym, "Low")].dropna() if (sym, "Low") in df_intra.columns else df_intra[sym]["Low"].dropna()
                open_i = df_intra[(sym, "Open")].dropna() if (sym, "Open") in df_intra.columns else df_intra[sym]["Open"].dropna()
                close_d = df_daily[(sym, "Close")].dropna() if (sym, "Close") in df_daily.columns else df_daily[sym]["Close"].dropna()

            if close_i.empty or len(close_i) < 2:
                continue

            last_price = float(close_i.iloc[-1])
            prev_close = float(close_d.iloc[-2]) if len(close_d) >= 2 else float(open_i.iloc[0])
            change_pct = ((last_price / prev_close) - 1) * 100 if prev_close else 0

            results[t] = {
                "price": last_price,
                "prev_close": prev_close,
                "change_pct": change_pct,
                "volume": int(vol_i.sum()),
                "high": float(high_i.max()),
                "low": float(low_i.min()),
                "open": float(open_i.iloc[0]),
                "intraday": close_i.copy(),
            }
        except Exception:
            continue

    return results


# ─── Validation ───
if not tickers:
    st.warning("Adicione pelo menos 1 ticker na barra lateral.")
    st.stop()

# ─── Fetch ───
with st.spinner("Buscando cotações..."):
    data = fetch_all(tuple(tickers))

if not data:
    st.error("Não foi possível obter dados. Verifique os tickers ou aguarde o mercado abrir.")
    st.stop()

now = datetime.now(BRT)
market_open = is_market_open()
ticker_list = sorted(data.keys())

# ─── Header ───
status_class = "market-open" if market_open else "market-closed"
status_text = "🟢 Aberto" if market_open else "🔴 Fechado"
st.markdown(f"""
<div class="header-bar">
    <div>
        <p class="header-title">📈 Mesa RV — Real-Time</p>
    </div>
    <div class="header-info">
        <span class="market-badge {status_class}">{status_text}</span><br>
        {now.strftime("%d/%m/%Y %H:%M:%S")} &nbsp;|&nbsp; {len(data)} ativos
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Layout: Chart + List ───
col_chart, col_list = st.columns([2, 3])

# ─── Chart (left) ───
with col_chart:
    if chart_mode == "Individual":
        selected = st.selectbox("Ativo", list(data.keys()), label_visibility="collapsed")
        if selected and selected in data:
            d = data[selected]
            intra = d["intraday"]
            color = GREEN if d["change_pct"] >= 0 else RED
            fill_color = "rgba(0,200,83,0.1)" if d["change_pct"] >= 0 else "rgba(255,23,68,0.1)"

            fig = go.Figure()
            fig.add_hline(y=d["prev_close"], line_dash="dash", line_color="#334",
                          annotation_text=f"Fech: R$ {d['prev_close']:.2f}",
                          annotation_font_color="#667")
            fig.add_trace(go.Scatter(
                x=intra.index, y=intra.values, mode="lines",
                line=dict(color=color, width=2),
                fill="tozeroy", fillcolor=fill_color, name=selected,
            ))
            fig.update_layout(
                title=dict(text=f"{selected}  R$ {d['price']:.2f}  ({d['change_pct']:+.2f}%)", font=dict(color="white")),
                template="plotly_dark", height=400, showlegend=False,
                paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
                margin=dict(l=10, r=10, t=40, b=30),
                yaxis=dict(tickformat=",.2f", tickprefix="R$ ", gridcolor="#1a2a45"),
                xaxis=dict(gridcolor="#1a2a45"),
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        compare_tickers = st.multiselect("Comparar", list(data.keys()), default=list(data.keys())[:4],
                                         label_visibility="collapsed")
        if compare_tickers:
            fig_comp = go.Figure()
            colors = [ACCENT, "#4fc3f7", "#ff9800", GREEN, RED, "#ab47bc", "#ef5350", "#26a69a"]
            for i, t in enumerate(compare_tickers):
                if t in data:
                    intra = data[t]["intraday"]
                    base = float(intra.iloc[0])
                    if base > 0:
                        normalized = ((intra / base) - 1) * 100
                        fig_comp.add_trace(go.Scatter(
                            x=intra.index, y=normalized.values, mode="lines",
                            line=dict(color=colors[i % len(colors)], width=2), name=t,
                        ))
            fig_comp.add_hline(y=0, line_dash="dash", line_color="#334")
            fig_comp.update_layout(
                title=dict(text="Variação % desde abertura", font=dict(color="white")),
                template="plotly_dark", height=400,
                paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
                margin=dict(l=10, r=10, t=40, b=30),
                yaxis=dict(ticksuffix="%", gridcolor="#1a2a45"),
                xaxis=dict(gridcolor="#1a2a45"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                            font=dict(color="#ccc")),
            )
            st.plotly_chart(fig_comp, use_container_width=True)

    # Stats cards
    gainers = sum(1 for d in data.values() if d["change_pct"] > 0)
    losers = sum(1 for d in data.values() if d["change_pct"] < 0)
    top_gainer = max(data.items(), key=lambda x: x[1]["change_pct"])
    top_loser = min(data.items(), key=lambda x: x[1]["change_pct"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stats-card"><div class="stats-value" style="color:{GREEN}">▲ {gainers}</div><div class="stats-label">Em alta</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stats-card"><div class="stats-value" style="color:{RED}">▼ {losers}</div><div class="stats-label">Em baixa</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stats-card"><div class="stats-value" style="color:{GREEN};font-size:16px">{top_gainer[0]}<br>{top_gainer[1]["change_pct"]:+.2f}%</div><div class="stats-label">Maior alta</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stats-card"><div class="stats-value" style="color:{RED};font-size:16px">{top_loser[0]}<br>{top_loser[1]["change_pct"]:+.2f}%</div><div class="stats-label">Maior baixa</div></div>', unsafe_allow_html=True)

# ─── Stock List (right) ───
with col_list:
    # Filter + Sort
    col_filter, col_sort = st.columns([3, 1])
    with col_filter:
        filter_text = st.text_input("🔍 Filtrar ações", placeholder="Ex: PETR, VALE, ITUB...", label_visibility="collapsed")
    with col_sort:
        sort_col = st.selectbox("Ordenar por", ["Ticker", "Preço", "Var %", "Volume"], index=2, label_visibility="collapsed")

    # Apply filter
    if filter_text.strip():
        filter_terms = [f.strip().upper() for f in filter_text.split(",") if f.strip()]
        filtered_tickers = [t for t in ticker_list if any(term in t for term in filter_terms)]
    else:
        filtered_tickers = ticker_list

    sort_map = {"Ticker": "ticker", "Preço": "price", "Var %": "change_pct", "Volume": "volume"}
    reverse = sort_col != "Ticker"
    sorted_tickers = sorted(
        filtered_tickers,
        key=lambda t: data[t].get(sort_map[sort_col], t) if sort_col != "Ticker" else t,
        reverse=reverse,
    )

    # Header row
    st.markdown("""
    <div class="stock-list">
        <div class="stock-header">
            <span style="width:90px">Ticker</span>
            <span style="width:100px;text-align:right">Preço</span>
            <span style="width:80px;text-align:right;margin-left:8px">Var %</span>
            <span style="width:100px;text-align:right;margin-left:8px">Volume</span>
            <span style="flex:1;text-align:right;margin-left:8px">Mín / Máx</span>
        </div>
    """, unsafe_allow_html=True)

    # Data rows
    rows_html = ""
    for t in sorted_tickers:
        d = data[t]
        arrow = "▲" if d["change_pct"] >= 0 else "▼"
        change_cls = "change-up" if d["change_pct"] >= 0 else "change-down"
        price_color = GREEN if d["change_pct"] >= 0 else RED

        rows_html += f"""
        <div class="stock-row">
            <span class="stock-ticker">{t}</span>
            <span class="stock-price" style="color:{price_color}">R$ {d["price"]:.2f}</span>
            <span class="stock-change {change_cls}">{arrow} {d["change_pct"]:+.2f}%</span>
            <span class="stock-vol">{d["volume"]:,.0f}</span>
            <span class="stock-range">{d["low"]:.2f} / {d["high"]:.2f}</span>
        </div>"""

    rows_html += "</div>"
    st.markdown(rows_html, unsafe_allow_html=True)
