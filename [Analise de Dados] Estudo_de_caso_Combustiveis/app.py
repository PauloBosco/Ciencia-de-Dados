import pandas as pd
import streamlit as st
import plotly.express as px
import kagglehub
import os

dataset_dir = kagglehub.dataset_download("paulobosco/dataset-combustiveis-2020-a-2025")
csv_path = os.path.join(dataset_dir, "consolidada_tratada.csv")

st.set_page_config(
    page_title="Dashboard de Combustíveis",
    page_icon="📊",
    layout="wide",
)

base = pd.read_csv(csv_path)

st.sidebar.header("🔍 Filtros")


def filtro_com_checkbox(nome, opcoes, chave_multiselect, default_selecionado=None, default_todos=False):
    if chave_multiselect not in st.session_state:
        st.session_state[chave_multiselect] = default_selecionado if default_selecionado else [opcoes[0]]
    chave_checkbox = f"{chave_multiselect}_todos"
    if chave_checkbox not in st.session_state:
        st.session_state[chave_checkbox] = default_todos

    def selecionar_todos():
        if st.session_state[chave_checkbox]:
            st.session_state[chave_multiselect] = opcoes
        else:
            st.session_state[chave_multiselect] = default_selecionado if default_selecionado else [opcoes[0]]

    # Multiselect
    st.sidebar.multiselect(nome, opcoes, key=chave_multiselect)

    # Checkbox abaixo
    st.sidebar.checkbox("Selecionar todos", key=chave_checkbox, on_change=selecionar_todos)

    return st.session_state[chave_multiselect]

# --- Filtros ---
anos_disponiveis = sorted(base['Ano'].unique())
ano = filtro_com_checkbox("Selecione o Ano", anos_disponiveis, "ano_sel", default_selecionado=[2025])

produtos_disponiveis = sorted(base['Produto'].unique())
produto = filtro_com_checkbox("Selecione o Produto", produtos_disponiveis, "produto_sel", default_selecionado=["GASOLINA"])

regioes_disponiveis = sorted(base['Regiao'].unique())
regiao = filtro_com_checkbox("Selecione a Região", regioes_disponiveis, "regiao_sel", default_selecionado=["SE"])

# Estado depende da Região selecionada
estados_disponiveis = sorted(base.loc[base['Regiao'].isin(regiao), 'Estado'].unique())
estado = filtro_com_checkbox("Selecione o(s) Estado(s)", estados_disponiveis, "estado_sel", default_selecionado=["MG"])

# Cidade depende do Estado selecionado
cidades_disponiveis = sorted(base.loc[base['Estado'].isin(estado), 'Municipio'].unique())
cidades = filtro_com_checkbox("Selecione a(s) Cidade(s)", cidades_disponiveis, "cidade_sel", default_selecionado=["JUIZ DE FORA"])


# --- Filtragem do DataFrame ---
# Aqui dataframe principal é filtrado com base nas seleções feitas na barra lateral.

base_filtrada = base[
    (base['Ano'].isin(ano)) &
    (base['Produto'].isin(produto)) &
    (base['Regiao'].isin(regiao)) &
    (base['Estado'].isin(estado)) &
    (base['Municipio'].isin(cidades))
]

# --- Conteúdo Principal ---
st.title("Análise de Dados de Combustíveis 2020 a 2025")
st.subheader("Dashboard de análise dos dados de combustíveis no Brasil segundo ANP")
st.write("Fonte: https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/serie-historica-de-precos-de-combustiveis")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais de combustíveis")

if not base_filtrada.empty:
    media_preco = base_filtrada['Valor de Venda'].mean()
    qtidade_registros = base_filtrada.shape[0]
    total_vendas = base_filtrada['Valor de Venda'].sum()
    produto_preco_medio_maior = base_filtrada.groupby('Produto')['Valor de Venda'].mean().idxmax().capitalize()
    preco_max = base_filtrada['Valor de Venda'].max()
    preco_min = base_filtrada['Valor de Venda'].min()
else:
    media_preco, qtidade_registros, total_vendas, produto_preco_medio_maior, preco_max, preco_min = 0, 0, 0, "", 0, 0


col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Média de Preço", f"R$ {media_preco:.2f}")
col2.metric("Preço Mínimo", f"R$ {preco_min:.2f}")
col3.metric("Preço Máximo", f"R$ {preco_max:.2f}")
col4.metric("Quantidade de Registros", qtidade_registros)
col5.metric("Produto Mais Caro", produto_preco_medio_maior if produto_preco_medio_maior else "N/A")




st.markdown("---")

st.subheader("📊 Gráficos")

col_graf1, col_graf2, col_graf3 = st.columns(3)

with col_graf1:
    st.subheader("Preços por Região")
    if not base_filtrada.empty:
        preco_medio_por_regiao = base_filtrada.groupby('Regiao')['Valor de Venda'].mean().reset_index().sort_values(by='Valor de Venda', ascending=False)
        fig = px.bar(
            preco_medio_por_regiao, 
            x='Regiao', 
            y='Valor de Venda', 
            orientation='v',
            title='Preços Médios por Região')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

with col_graf2:
    st.subheader("Preços por Estado")
    if not base_filtrada.empty:
        preco_medio_por_estado = base_filtrada.groupby('Estado')['Valor de Venda'].mean().reset_index().sort_values(by='Valor de Venda', ascending=False)
        fig = px.bar(
            preco_medio_por_estado, 
            x='Estado', 
            y='Valor de Venda', 
            orientation='v',
            title='Preços Médios por Estado')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

with col_graf3:
    st.subheader("Preços por Município")
    if not base_filtrada.empty:
        preco_medio_por_municipio = base_filtrada.groupby('Municipio')['Valor de Venda'].mean().reset_index().sort_values(by='Valor de Venda', ascending=False)
        fig = px.bar(
            preco_medio_por_municipio, 
            x='Municipio', 
            y='Valor de Venda',
            title='Preços Médios por Município')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")


col_graf4, col_graf5 = st.columns(2)



with col_graf4:
    st.subheader("Gráfico de Preços por Combustível ao Longo do Tempo")

    granularidade = st.selectbox("Visualizar por:", ["Dia", "Mês"])
    
    # Lista de cidades disponíveis
    cidades_disponiveis = sorted(base_filtrada['Municipio'].unique())
    cidade_selecionada = st.selectbox(
        "Selecione a Cidade",
        cidades_disponiveis,
        index=0
    )
    
    # Filtrar a base de acordo com a cidade selecionada
    base_cidade = base_filtrada[base_filtrada['Municipio'] == cidade_selecionada]

    if granularidade == "Dia":
        preco_medio = base_cidade.groupby(['Produto','Data da Coleta'])['Valor de Venda'].mean().reset_index()
        preco_medio = preco_medio.sort_values('Data da Coleta')
    elif granularidade == "Mês":
        preco_medio = base_cidade.groupby(['Produto','Mes'])['Valor de Venda'].mean().reset_index()
        preco_medio = preco_medio.sort_values('Mes')
    
    if not base_cidade.empty:
        fig = px.line(
            preco_medio,
            x='Mes' if granularidade == "Mês" else 'Data da Coleta',
            y='Valor de Venda',
            markers=True,
            color='Produto',
            title=f"Preço médio ao longo do tempo em {cidade_selecionada}"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

with col_graf5:
    st.subheader("Análise de Preços: Mediana e Outliers por Produto")
    
    if not base_filtrada.empty:
        fig = px.box(
            base_filtrada,
            x="Produto",
            y="Valor de Venda",
            title="Distribuição de preços por produto"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")


col_graf6, col_graf7 = st.columns(2)

with col_graf6:
    st.subheader("Top 5 Cidades com Maior Preço Médio por Combustível")

    combustiveis_disponiveis = sorted(base['Produto'].unique())
    combustivel_selecionado = st.selectbox(
        "Selecione o combustível",
        combustiveis_disponiveis
    )

    base_sem_filtro_produto = base[
        (base['Ano'].isin(ano)) &
        (base['Regiao'].isin(regiao)) &
        (base['Estado'].isin(estado)) &
        (base['Municipio'].isin(cidades))
    ]

    if not base_sem_filtro_produto.empty:
        df_combustivel = base_sem_filtro_produto[
            base_sem_filtro_produto['Produto'] == combustivel_selecionado
        ]

        top_cidades = df_combustivel.groupby('Municipio')['Valor de Venda'].mean().reset_index().sort_values(by='Valor de Venda', ascending=True).tail(5)

        fig = px.bar(
            top_cidades,
            y='Municipio',
            x='Valor de Venda',
            orientation='h',
            title=f"Top 5 Cidades com Maior Preço Médio - {combustivel_selecionado}"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

with col_graf7:
    st.subheader("Top 5 Bandeiras de Combustíveis")
    if not base_sem_filtro_produto.empty:
        bandeiras = base_sem_filtro_produto['Bandeira'].value_counts().reset_index().head(5)
        bandeiras.columns = ['Bandeira', 'Quantidade']
        
        fig = px.pie(
            bandeiras,
            names='Bandeira',
            values='Quantidade',
            title='Distribuição de Bandeiras de Combustíveis'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

col_graf8, col_graf9 = st.columns(2)

with col_graf8:
    st.subheader("Análise de Concorrência por Município")

    if not base_sem_filtro_produto.empty:
    # Contar quantos postos por município
        concorrencia = (
            base_filtrada.groupby(["Regiao","Municipio"])["Revenda"]
            .nunique()
            .reset_index()
            .rename(columns={"Revenda": "Qtd_Postos"})
        )

        # Média de preço por município
        preco_por_municipio = (
            base_filtrada.groupby("Municipio")["Valor de Venda"]
            .mean()
            .round(2)
            .reset_index()
            .rename(columns={"Valor de Venda": "Preco_Medio"})
        )

        concorrencia_preco = pd.merge(concorrencia, preco_por_municipio, on="Municipio")

        concorrencia_ordenada = concorrencia_preco.sort_values(by=["Qtd_Postos", "Preco_Medio"], ascending=[False, True]) 

        

        st.dataframe(concorrencia_ordenada,
            column_config={
                "Qtd_Postos": st.column_config.ProgressColumn(
                    "Qtd Postos",
                    format="localized",
                    width="small",
                    min_value=0,
                    max_value=int(concorrencia_ordenada['Qtd_Postos'].max()),
                    )}, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

with col_graf9:
    st.subheader("Maior e Menor Preço Médio dentre as Cidades Selecionadas")
    if not base_filtrada.empty:
        
        # Descobrindo onde é menor e o maior valor cobrado em gasolina em 2025
        dic_preco_medio = {}
        preco_medio_max = concorrencia_ordenada['Preco_Medio'].max()
        preco_medio_min = concorrencia_ordenada['Preco_Medio'].min()

        dic_preco_medio['max'] = preco_medio_max
        dic_preco_medio['min'] = preco_medio_min

        df_maior_menor_preco = concorrencia_ordenada.loc[
            (concorrencia_ordenada['Preco_Medio'] == dic_preco_medio['max']) |
            (concorrencia_ordenada['Preco_Medio'] == dic_preco_medio['min'])
        ]

        st.dataframe(df_maior_menor_preco, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")


st.subheader("Tabela de Dados Filtrados")
st.dataframe(base_filtrada, use_container_width=True)
