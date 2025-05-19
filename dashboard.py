import streamlit as st
import pandas as pd
import plotly.express as px
import textwrap
from load_data import carregar_dados

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo customizado para layout, fundo e KPIs
st.markdown(
    """
    <style>
    html, body, [data-testid="stApp"] {
        background-color: #ffffff;
    }
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #121113;
        padding-top: 0rem !important;
        color: white;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6 {
        color: white !important;
    }
    section[data-testid="stSidebar"] img {
        margin-top: 0px !important;
        margin-bottom: 10px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        display: block;
    }
    section.main > div {
        padding-top: 0rem;
    }
    .block-container div[data-testid="column"] > div:first-child {
        margin-bottom: 0rem;
    }
    .block-container .element-container:has([data-testid="stPlotlyChart"]) {
        padding-top: 2rem;
        margin-top: 0rem;
    }
    .js-plotly-plot .plotly-title {
        margin-bottom: -20px !important;
        font-size: 16px !important;
    }
    .custom-kpi {
        background-color: #f0f2f6;
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #ddd;
        text-align: center;
        margin: 5px;
    }
    .custom-kpi-label {
        font-size: 14px;
        color: #333;
        font-weight: 500;
    }
    .custom-kpi-value {
        font-size: 22px;
        font-weight: 600;
        color: #000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Carregamento e preparo dos dados
df = carregar_dados()
df['OrderDate'] = pd.to_datetime(df['OrderDate'])
df['YearMonth'] = df['OrderDate'].dt.to_period('M').astype(str)

# Datas limites da base de dados
data_min = pd.to_datetime("2011-05-31").date()
data_max = pd.to_datetime("2014-06-30").date()

# Sidebar com filtros
with st.sidebar:
    st.image("logo.png", width=200)
    produtos = st.multiselect("Produto", df['ProductName'].unique())
    regioes = st.multiselect("Região", df['RegionName'].unique(), default=None)
    data_inicio = st.date_input("Data inicial", data_min, min_value=data_min, max_value=data_max, format="DD/MM/YYYY")
    data_fim = st.date_input("Data final", data_max, min_value=data_min, max_value=data_max, format="DD/MM/YYYY")

# Aplicação dos filtros
filtro = (
    (df['OrderDate'].dt.date >= data_inicio) &
    (df['OrderDate'].dt.date <= data_fim)
)
if produtos:
    filtro &= df['ProductName'].isin(produtos)
if regioes:
    filtro &= df['RegionName'].isin(regioes)

df_filtrado = df[filtro]

# Indicadores adicionais na sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### Produto Mais Vendido", unsafe_allow_html=True)
    if not df_filtrado.empty:
        produto_mais_vendido = (
            df_filtrado.groupby('ProductName')['TotalItemValue']
            .sum()
            .idxmax()
        )
        produto_exibido = '\n'.join(textwrap.wrap(produto_mais_vendido, width=20))
        st.markdown(f"<p style='color:white'>{produto_exibido}</p>", unsafe_allow_html=True)

        st.markdown("### Região com Maior Faturamento", unsafe_allow_html=True)
        regiao_mais_vendida = (
            df_filtrado.groupby('RegionName')['TotalItemValue']
            .sum()
            .idxmax()
        )
        st.markdown(f"<p style='color:white'>{regiao_mais_vendida}</p>", unsafe_allow_html=True)

        st.markdown("### Pico de Vendas", unsafe_allow_html=True)
        periodo_top = (
            df_filtrado.groupby('YearMonth')['TotalItemValue']
            .sum()
            .idxmax()
        )
        st.markdown(f"<p style='color:white'>{pd.to_datetime(periodo_top, format='%Y-%m').strftime('%m/%Y')}</p>", unsafe_allow_html=True)

# KPIs
total_vendas = df_filtrado['TotalItemValue'].sum()
total_pedidos = df_filtrado['SalesOrderID'].nunique()
total_itens = df_filtrado['OrderQty'].sum()
ticket_medio = total_vendas / total_pedidos if total_pedidos > 0 else 0

with st.container():
    st.markdown("""<div style='margin-top: -30px'></div>""", unsafe_allow_html=True)
    col1, spacer, col2, col3, col4 = st.columns([1.2, 0.3, 1, 1, 1])
    with col1:
        st.markdown(f"""
            <div class='custom-kpi'>
                <div class='custom-kpi-label'>Total de Vendas</div>
                <div class='custom-kpi-value'>R${total_vendas:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class='custom-kpi'>
                <div class='custom-kpi-label'>Total de Pedidos</div>
                <div class='custom-kpi-value'>{total_pedidos}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class='custom-kpi'>
                <div class='custom-kpi-label'>Total de Itens</div>
                <div class='custom-kpi-value'>{int(total_itens)}</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class='custom-kpi'>
                <div class='custom-kpi-label'>Valor Médio por Pedido</div>
                <div class='custom-kpi-value'>R${ticket_medio:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)


# Gráfico 1: Vendas por Produto
vendas_produto = (
    df_filtrado.groupby('ProductName')['TotalItemValue']
    .sum()
    .reset_index()
    .sort_values(by='TotalItemValue')
)
fig_prod = px.bar(
    vendas_produto,
    x='TotalItemValue',
    y='ProductName',
    orientation='h',
    template='plotly_dark',
    height=500,
    labels={
        "TotalItemValue": "Valor Total Vendido (R$)",
        "ProductName": "Produto"
    }
)
fig_prod.update_layout(
    title=dict(text="Vendas por Produto", x=0.5, font=dict(size=16), pad=dict(t=4, b=0))
)

# Gráfico 2: Mapa Choropleth
state_abbreviations = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI',
    'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY'
}

vendas_regiao = (
    df_filtrado.groupby('RegionName')['TotalItemValue']
    .sum()
    .reset_index()
)
vendas_regiao['StateCode'] = vendas_regiao['RegionName'].map(state_abbreviations)
vendas_regiao = vendas_regiao.dropna(subset=['StateCode'])
fig_choropleth = px.choropleth(
    vendas_regiao,
    locations='StateCode',
    locationmode="USA-states",
    color='TotalItemValue',
    scope="usa",
    color_continuous_scale="blues",
    template="plotly_dark",
    height=500,
    labels={
        "RegionName": "Estado",
        "TotalItemValue": "Valor Total Vendido (R$)"
    }
)
fig_choropleth.update_layout(
    title=dict(text="Distribuição de Vendas por Estado (EUA)", x=0.5, font=dict(size=16), pad=dict(t=4, b=0)),
    geo=dict(bgcolor='white')
)

# Gráfico 3: Evolução
vendas_tempo = df_filtrado.groupby('YearMonth')['TotalItemValue'].sum().reset_index()
fig_tempo = px.line(
    vendas_tempo,
    x='YearMonth',
    y='TotalItemValue',
    markers=True,
    template='plotly_dark',
    height=350,
    labels={
        "YearMonth": "Mês/Ano",
        "TotalItemValue": "Faturamento Total (R$)"
    }
)
fig_tempo.update_layout(
    title=dict(text="Faturamento ao Longo do Tempo", x=0.5, font=dict(size=16), pad=dict(t=4, b=0))
)

# Exibição
g1, g2 = st.columns(2)
with g1:
    st.plotly_chart(fig_prod, use_container_width=True)
with g2:
    st.plotly_chart(fig_choropleth, use_container_width=True)
with st.container():
    st.plotly_chart(fig_tempo, use_container_width=True)

