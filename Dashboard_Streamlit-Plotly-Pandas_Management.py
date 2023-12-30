import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(layout="wide")

# Leitura dos dados
df = pd.read_csv("supermarket_sales.csv", sep=";", decimal=",")
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")

# Adição da coluna 'Month'
df["Month"] = df["Date"].apply(lambda x: f"{x.year}-{x.month}")
months = df["Month"].unique()

# Opção para avaliar o período total ou escolher um mês
period_option = st.sidebar.radio("Avaliar por:", ["Mês", "Período Total"])

if period_option == "Mês":
    # Seleção do mês via barra lateral
    selected_month = st.sidebar.selectbox("Mês", months)
    df_filtered = df[df["Month"] == selected_month]
else:
    # Avaliação para o período total
    df_filtered = df

# Opção para escolher a coluna para a frequência relativa e acumulada
selected_column = st.sidebar.selectbox("Selecione a coluna para o Diagrama de Pareto:", ["Selecione uma coluna"] + list(df_filtered.columns))

# Opção para escolher a coluna para o eixo das abscissas
x_axis_column = st.sidebar.selectbox("Selecione a coluna para o eixo das abscissas:", ["Selecione uma coluna"] + list(df_filtered.columns))

# Layout em colunas
col3 = st.columns(1)
col1, col2 = st.columns(2)
col4, col5, col6 = st.columns(3)

# Verificar se o DataFrame df_filtered contém dados antes de criar o gráfico do Pareto
if not df_filtered.empty and selected_column != "Selecione uma coluna" and x_axis_column != "Selecione uma coluna":
    # Gráfico de Pareto
    df_pareto = df_filtered.groupby(x_axis_column)[selected_column].sum().sort_values(ascending=False).reset_index()
    df_pareto["pareto_rel"] = (df_pareto[selected_column] / df_pareto[selected_column].sum()) * 100
    df_pareto["pareto_acum"] = df_pareto["pareto_rel"].cumsum()

    # Criando uma segunda escala para a curva de Pareto
    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(x=df_pareto[x_axis_column], y=df_pareto[selected_column], text=df_pareto["pareto_rel"], textposition="auto", name=selected_column))
    fig_pareto.add_trace(go.Scatter(x=df_pareto[x_axis_column], y=df_pareto["pareto_acum"], mode="lines", name="Curva de Pareto", yaxis="y2"))

    # Adicionando rótulos aos eixos
    fig_pareto.update_layout(
        xaxis=dict(title=x_axis_column),
        yaxis=dict(title=selected_column, side="left"),
        yaxis2=dict(title="Curva de Pareto", side="right", overlaying="y", showgrid=False),
        title="Diagrama de Pareto",
    )
    col3[0].plotly_chart(fig_pareto, use_container_width=True)

# Gráfico de barras para o faturamento por dia
fig_date = px.bar(df_filtered, x="Date", y="Total", color="City", title="Faturamento por dia")
col1.plotly_chart(fig_date, use_container_width=True)

# Gráfico de barras para o faturamento por tipo de produto
fig_prod = px.bar(df_filtered, x="Date", y="Product line", color="City", title="Faturamento por tipo de produto", orientation="h")
col2.plotly_chart(fig_prod, use_container_width=True)

# Faturamento por filial
city_total = df_filtered.groupby("City")[["Total"]].sum().reset_index()
fig_city = px.bar(city_total, x="City", y="Total", title="Faturamento por filial")
col4.plotly_chart(fig_city, use_container_width=True)

# Faturamento por tipo de pagamento (gráfico de pizza)
fig_kind = px.pie(df_filtered, values="Total", names="Payment", title="Faturamento por tipo de pagamento")
col5.plotly_chart(fig_kind, use_container_width=True)

# Avaliação por filial
city_total = df_filtered.groupby("City")[["Rating"]].mean().reset_index()
fig_rating = px.bar(df_filtered, y="Rating", x="City", title="Avaliação entre filiais")
col6.plotly_chart(fig_rating, use_container_width=True)

# Carrega automaticamente um arquivo CSV, desde que esteja na mesma pasta do arquivo .py;
# Permite avaliar o dashboard em meses e no período total;
# Implementado gráfico do Diagrama de Pareto na Primeira Linha e na Primeira Coluna;
# Permite selecionar os tipos de colunas com dados para o gráfico do Diagrama de Pareto;
# Primeira lista suspensa "Selecione a coluna para o Diagrama de Pareto:", refere-se aos dados absolutos, custos totais e etc.;
# Segunda lista suspensa "Selecione a coluna para o eixo das abscissas:", refere-se a identificação dos itens, produtos, etc.
