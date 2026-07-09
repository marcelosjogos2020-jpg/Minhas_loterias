import streamlit as st
import pandas as pd
import plotly.express as px
from math import comb

st.set_page_config(
    page_title="Lotofácil | Análises e Desdobramentos",
    page_icon="🍀",
    layout="wide"
)

# =========================
# CSS PERSONALIZADO
# =========================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0d1117;
        color: #ffffff;
    }

    section[data-testid="stSidebar"] {
        background-color: #262730;
    }

    h1, h2, h3 {
        color: #ffffff;
    }

    .card {
        background-color: #161b22;
        padding: 22px;
        border-radius: 14px;
        border: 1px solid #30363d;
        box-shadow: 0px 0px 8px rgba(0,0,0,0.25);
        margin-bottom: 18px;
    }

    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
    }

    .metric-title {
        color: #8b949e;
        font-size: 14px;
        font-weight: 600;
    }

    .metric-value {
        color: #58a6ff;
        font-size: 28px;
        font-weight: 800;
        margin-top: 8px;
    }

    .dezena {
        display: inline-block;
        background: linear-gradient(135deg, #007bff, #00c6ff);
        color: white;
        font-weight: 800;
        width: 42px;
        height: 42px;
        line-height: 42px;
        text-align: center;
        border-radius: 50%;
        margin: 5px;
        font-size: 16px;
    }

    .dezena-hot {
        display: inline-block;
        background: linear-gradient(135deg, #ff4b4b, #ff9800);
        color: white;
        font-weight: 800;
        width: 42px;
        height: 42px;
        line-height: 42px;
        text-align: center;
        border-radius: 50%;
        margin: 5px;
        font-size: 16px;
    }

    .dezena-cold {
        display: inline-block;
        background: linear-gradient(135deg, #444c56, #6e7681);
        color: white;
        font-weight: 800;
        width: 42px;
        height: 42px;
        line-height: 42px;
        text-align: center;
        border-radius: 50%;
        margin: 5px;
        font-size: 16px;
    }

    .jogo-box {
        background-color: #111827;
        border: 1px solid #30363d;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 10px;
    }

    .alerta {
        background-color: #1f2937;
        border-left: 5px solid #58a6ff;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 16px;
    }

    .positivo {
        color: #00e676;
        font-weight: 800;
    }

    .negativo {
        color: #ff4b4b;
        font-weight: 800;
    }

    .neutro {
        color: #facc15;
        font-weight: 800;
    }

    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# DADOS DOS CONCURSOS
# =========================

concursos = {
    3730: [2, 3, 5, 6, 8, 11, 12, 13, 14, 15, 16, 19, 20, 21, 24],
    3729: [1, 2, 3, 5, 6, 11, 12, 13, 14, 15, 16, 18, 20, 21, 22],
    3728: [1, 2, 3, 6, 7, 8, 10, 11, 16, 17, 19, 21, 22, 23, 25],
    3727: [1, 2, 3, 4, 5, 9, 10, 11, 13, 14, 16, 18, 19, 22, 23],
    3726: [2, 5, 6, 7, 10, 13, 14, 17, 18, 19, 20, 21, 22, 24, 25],
    3725: [1, 2, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 24, 25],
    3724: [1, 2, 3, 5, 6, 7, 12, 15, 16, 17, 19, 21, 22, 24, 25],
    3723: [2, 4, 5, 6, 7, 10, 12, 15, 17, 18, 19, 20, 22, 23, 25],
    3722: [2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 17, 19, 20, 23],
    3721: [1, 3, 4, 5, 7, 8, 10, 11, 12, 14, 15, 20, 21, 23, 24],
    3720: [1, 5, 7, 8, 9, 10, 11, 13, 15, 16, 17, 18, 20, 22, 24],
}

frequencias = {
    1: 7, 2: 9, 3: 7, 4: 4, 5: 10,
    6: 8, 7: 6, 8: 5, 9: 3, 10: 7,
    11: 8, 12: 6, 13: 7, 14: 7, 15: 7,
    16: 7, 17: 7, 18: 5, 19: 8, 20: 7,
    21: 7, 22: 7, 23: 5, 24: 6, 25: 5
}

base_18 = [1, 2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, 22, 24]

dezenas_fora = [4, 8, 9, 12, 18, 23, 25]

mais_fortes = [2, 5, 6, 11, 19]

intermediarias = [1, 3, 10, 13, 14, 15, 16, 17, 20, 21, 22]

mais_fracas = [4, 8, 9, 18, 23, 25]

desdobramento_12 = {
    "Jogo 01": [3, 5, 6, 7, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, 22],
    "Jogo 02": [2, 5, 6, 7, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, 24],
    "Jogo 03": [1, 3, 6, 7, 10, 11, 13, 14, 15, 16, 17, 19, 20, 22, 24],
    "Jogo 04": [1, 2, 5, 7, 10, 11, 13, 14, 15, 16, 17, 19, 21, 22, 24],
    "Jogo 05": [1, 2, 3, 6, 10, 11, 13, 14, 15, 16, 17, 20, 21, 22, 24],
    "Jogo 06": [1, 2, 3, 5, 7, 11, 13, 14, 15, 16, 19, 20, 21, 22, 24],
    "Jogo 07": [1, 2, 3, 5, 6, 10, 13, 14, 15, 17, 19, 20, 21, 22, 24],
    "Jogo 08": [1, 2, 3, 5, 6, 7, 11, 15, 16, 17, 19, 20, 21, 22, 24],
    "Jogo 09": [1, 2, 3, 5, 6, 7, 10, 13, 14, 16, 19, 20, 21, 22, 24],
    "Jogo 10": [2, 3, 5, 6, 7, 10, 11, 13, 14, 16, 17, 19, 20, 21, 22],
    "Jogo 11": [1, 3, 5, 6, 7, 10, 11, 13, 15, 16, 17, 19, 20, 21, 22],
    "Jogo 12": [1, 2, 5, 6, 7, 10, 11, 13, 14, 16, 17, 19, 20, 21, 24],
}

# =========================
# FUNÇÕES
# =========================

def bolas_html(lista, tipo="normal"):
    classe = "dezena"

    if tipo == "hot":
        classe = "dezena-hot"
    elif tipo == "cold":
        classe = "dezena-cold"

    html = ""
    for n in lista:
        html += f'<span class="{classe}">{n:02d}</span>'
    return html


def contar_pares(lista):
    return len([n for n in lista if n % 2 == 0])


def contar_impares(lista):
    return len([n for n in lista if n % 2 != 0])


def contar_baixas(lista):
    return len([n for n in lista if n <= 13])


def contar_altas(lista):
    return len([n for n in lista if n >= 14])


def soma_dezenas(lista):
    return sum(lista)


def chance_lotofacil(qtd_jogos):
    total = comb(25, 15)
    chance = total / qtd_jogos
    return total, chance


# =========================
# SIDEBAR
# =========================

st.sidebar.markdown("# 🍀 Menu Principal")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Escolha uma seção:",
    [
        "📊 Dashboard",
        "1️⃣ Últimos concursos",
        "2️⃣ Frequência das dezenas",
        "3️⃣ Leitura estatística",
        "4️⃣ Estratégia próximo sorteio",
        "5️⃣ Base de 18 dezenas",
        "6️⃣ Dezenas fora",
        "7️⃣ Desdobramento 12 jogos",
        "8️⃣ Chance matemática",
        "✅ Resumo final"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🎯 Filtros rápidos")

qtd_jogos_simulados = st.sidebar.number_input(
    "Quantidade de jogos para simular chance",
    min_value=1,
    max_value=1000,
    value=12,
    step=1
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Análise baseada nos concursos 3720 a 3730 da Lotofácil. "
    "Uso estatístico e combinatório, sem garantia de premiação."
)

# =========================
# CABEÇALHO
# =========================

st.markdown("# 🍀 Lotofácil | Análises e Desdobramentos")
st.markdown("### Painel estatístico com base nos últimos concursos analisados")

st.markdown(
    """
    <div class="alerta">
    Este painel reúne a análise estatística feita para a Lotofácil, incluindo frequência das dezenas,
    seleção de base com 18 números, dezenas descartadas temporariamente, desdobramento reduzido
    e cálculo matemático de probabilidade.
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-title">Concursos analisados</div>
            <div class="metric-value">11</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-title">Total de combinações</div>
            <div class="metric-value">3.268.760</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-title">Base sugerida</div>
            <div class="metric-value">18 dezenas</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-title">Desdobramento</div>
            <div class="metric-value">12 jogos</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# =========================
# DASHBOARD
# =========================

if menu == "📊 Dashboard":
    st.markdown("## 📊 Visão Geral da Análise")

    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        st.markdown("### 🔥 Dezenas mais fortes")
        st.markdown(bolas_html(mais_fortes, "hot"), unsafe_allow_html=True)

        st.markdown("### ⚖️ Grupo intermediário")
        st.markdown(bolas_html(intermediarias, "normal"), unsafe_allow_html=True)

        st.markdown("### ❄️ Dezenas mais fracas no recorte")
        st.markdown(bolas_html(mais_fracas, "cold"), unsafe_allow_html=True)

    with col_b:
        df_freq = pd.DataFrame({
            "Dezena": [f"{n:02d}" for n in frequencias.keys()],
            "Frequência": list(frequencias.values())
        })

        fig = px.bar(
            df_freq,
            x="Dezena",
            y="Frequência",
            title="Frequência das dezenas nos últimos 11 concursos",
            text="Frequência",
            color="Frequência",
            color_continuous_scale="Blues"
        )

        fig.update_layout(
            paper_bgcolor="#0d1117",
            plot_bgcolor="#161b22",
            font_color="white",
            title_font_color="white"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("## 🎯 Base principal sugerida")
    st.markdown(bolas_html(base_18, "normal"), unsafe_allow_html=True)

    st.markdown("## ✅ Recomendação")
    st.success(
        "Usar a base de 18 dezenas para gerar jogos de 15 dezenas, mantendo equilíbrio entre "
        "pares/ímpares, altas/baixas e repetição controlada do último concurso."
    )

# =========================
# 1. ÚLTIMOS CONCURSOS
# =========================

elif menu == "1️⃣ Últimos concursos":
    st.markdown("## 1️⃣ Últimos 11 concursos analisados")

    st.markdown(
        """
        Foram analisados os concursos de **3720 a 3730**, com destaque para o último concurso:
        """
    )

    st.markdown("### Último concurso encontrado: 3730")
    st.markdown(bolas_html(concursos[3730], "hot"), unsafe_allow_html=True)

    linhas = []

    for concurso, dezenas in concursos.items():
        linhas.append({
            "Concurso": concurso,
            "Dezenas": " ".join([f"{n:02d}" for n in dezenas]),
            "Pares": contar_pares(dezenas),
            "Ímpares": contar_impares(dezenas),
            "Baixas 01-13": contar_baixas(dezenas),
            "Altas 14-25": contar_altas(dezenas),
            "Soma": soma_dezenas(dezenas)
        })

    df_concursos = pd.DataFrame(linhas)

    st.dataframe(df_concursos, use_container_width=True, hide_index=True)

    st.markdown("### Visualização por concurso")

    for concurso, dezenas in concursos.items():
        st.markdown(f"#### Concurso {concurso}")
        st.markdown(bolas_html(dezenas), unsafe_allow_html=True)

# =========================
# 2. FREQUÊNCIA
# =========================

elif menu == "2️⃣ Frequência das dezenas":
    st.markdown("## 2️⃣ Frequência das dezenas nos últimos 11 concursos")

    df_freq = pd.DataFrame({
        "Dezena": list(frequencias.keys()),
        "Frequência": list(frequencias.values())
    }).sort_values(by="Frequência", ascending=False)

    col1, col2 = st.columns([1, 1.3])

    with col1:
        st.dataframe(df_freq, use_container_width=True, hide_index=True)

    with col2:
        fig = px.bar(
            df_freq,
            x=df_freq["Dezena"].astype(str).str.zfill(2),
            y="Frequência",
            title="Ranking de frequência",
            text="Frequência",
            color="Frequência",
            color_continuous_scale="Turbo"
        )

        fig.update_layout(
            paper_bgcolor="#0d1117",
            plot_bgcolor="#161b22",
            font_color="white",
            xaxis_title="Dezena",
            yaxis_title="Quantidade de vezes"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Destaques")
    st.markdown(
        """
        - A dezena **05** foi a mais frequente, aparecendo **10 vezes** em 11 concursos.
        - As dezenas **02**, **06**, **11** e **19** também tiveram forte presença.
        - A dezena **09** foi a menos frequente, aparecendo apenas **3 vezes**.
        """
    )

# =========================
# 3. LEITURA ESTATÍSTICA
# =========================

elif menu == "3️⃣ Leitura estatística":
    st.markdown("## 3️⃣ Leitura estatística")

    st.markdown("### 🔥 Dezenas mais fortes no período")
    st.markdown(bolas_html(mais_fortes, "hot"), unsafe_allow_html=True)

    st.markdown(
        """
        Essas dezenas foram as mais presentes no recorte analisado:

        - **05** saiu em 10 dos 11 concursos.
        - **02** saiu 9 vezes.
        - **06, 11 e 19** saíram 8 vezes cada.
        """
    )

    st.markdown("### ⚖️ Grupo intermediário muito consistente")
    st.markdown(bolas_html(intermediarias, "normal"), unsafe_allow_html=True)

    st.markdown(
        """
        Esse grupo apareceu com frequência equilibrada e pode ser usado como sustentação da montagem dos jogos.
        """
    )

    st.markdown("### ❄️ Dezenas mais fracas ou atrasadas")
    st.markdown(bolas_html(mais_fracas, "cold"), unsafe_allow_html=True)

    st.markdown(
        """
        Essas dezenas tiveram menor presença no período analisado.  
        Isso não significa que não possam sair, mas estatisticamente ficaram mais fracas neste recorte.
        """
    )

# =========================
# 4. ESTRATÉGIA
# =========================

elif menu == "4️⃣ Estratégia próximo sorteio":
    st.markdown("## 4️⃣ Estratégia para o próximo sorteio")

    ultimo = concursos[3730]

    st.markdown("### Último resultado usado como referência")
    st.markdown(bolas_html(ultimo, "hot"), unsafe_allow_html=True)

    st.markdown(
        """
        Estratégia recomendada:

        - Usar entre **9 e 11 dezenas repetidas** do último concurso;
        - Usar entre **4 e 6 dezenas ausentes** do último concurso;
        - Buscar soma entre **180 e 205**;
        - Trabalhar com equilíbrio entre **pares e ímpares**;
        - Preferir formações **7/8 ou 8/7** entre pares e ímpares;
        - Evitar sequências muito longas;
        - Não usar somente dezenas quentes;
        - Não abandonar totalmente dezenas atrasadas.
        """
    )

    pares = contar_pares(ultimo)
    impares = contar_impares(ultimo)
    baixas = contar_baixas(ultimo)
    altas = contar_altas(ultimo)
    soma = soma_dezenas(ultimo)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Pares", pares)
    col2.metric("Ímpares", impares)
    col3.metric("Baixas", baixas)
    col4.metric("Altas", altas)
    col5.metric("Soma", soma)

    st.info(
        "O objetivo não é prever o sorteio, mas montar jogos mais equilibrados estatisticamente."
    )

# =========================
# 5. BASE 18
# =========================

elif menu == "5️⃣ Base de 18 dezenas":
    st.markdown("## 5️⃣ Base principal sugerida com 18 dezenas")

    st.markdown(bolas_html(base_18, "normal"), unsafe_allow_html=True)

    st.markdown("### Por que essa base?")

    st.markdown(
        """
        A base de 18 dezenas foi montada com:

        - As dezenas mais fortes: **02, 05, 06, 11, 19**;
        - As dezenas intermediárias e consistentes;
        - Boa distribuição entre dezenas baixas e altas;
        - Boa presença de dezenas repetidas do último concurso;
        - Redução de risco em relação a escolher apenas 15 dezenas fixas.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Quantidade", len(base_18))
    col2.metric("Pares", contar_pares(base_18))
    col3.metric("Ímpares", contar_impares(base_18))
    col4.metric("Soma", soma_dezenas(base_18))

    st.markdown("### Conferência da base")

    df_base = pd.DataFrame({
        "Dezena": [f"{n:02d}" for n in base_18],
        "Frequência": [frequencias[n] for n in base_18]
    })

    st.dataframe(df_base, use_container_width=True, hide_index=True)

# =========================
# 6. DEZENAS FORA
# =========================

elif menu == "6️⃣ Dezenas fora":
    st.markdown("## 6️⃣ Dezenas que ficariam fora no primeiro filtro")

    st.markdown(bolas_html(dezenas_fora, "cold"), unsafe_allow_html=True)

    st.markdown(
        """
        Essas dezenas foram deixadas fora da primeira base estatística:

        **04, 08, 09, 12, 18, 23 e 25**

        Motivo:

        - Menor força no recorte analisado;
        - Algumas apresentaram frequência baixa;
        - Outras foram retiradas para manter a base com 18 dezenas mais enxuta;
        - A retirada ajuda a gerar um desdobramento mais focado.
        """
    )

    df_fora = pd.DataFrame({
        "Dezena": [f"{n:02d}" for n in dezenas_fora],
        "Frequência": [frequencias[n] for n in dezenas_fora]
    })

    st.dataframe(df_fora, use_container_width=True, hide_index=True)

    st.warning(
        "Importante: deixar uma dezena fora não significa que ela não será sorteada. "
        "É apenas um filtro estatístico para reduzir combinações."
    )

# =========================
# 7. DESDOBRAMENTO
# =========================

elif menu == "7️⃣ Desdobramento 12 jogos":
    st.markdown("## 7️⃣ Desdobramento reduzido — 12 jogos")

    st.markdown(
        """
        Abaixo estão 12 jogos de 15 dezenas criados a partir da base principal de 18 dezenas.
        """
    )

    for nome, jogo in desdobramento_12.items():
        pares = contar_pares(jogo)
        impares = contar_impares(jogo)
        soma = soma_dezenas(jogo)

        st.markdown(
            f"""
            <div class="jogo-box">
                <h4>{nome}</h4>
                {bolas_html(jogo)}
                <p>
                    <b>Pares:</b> {pares} |
                    <b>Ímpares:</b> {impares} |
                    <b>Soma:</b> {soma}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### Tabela dos jogos")

    linhas = []

    for nome, jogo in desdobramento_12.items():
        linhas.append({
            "Jogo": nome,
            "Dezenas": " ".join([f"{n:02d}" for n in jogo]),
            "Pares": contar_pares(jogo),
            "Ímpares": contar_impares(jogo),
            "Baixas": contar_baixas(jogo),
            "Altas": contar_altas(jogo),
            "Soma": soma_dezenas(jogo)
        })

    df_jogos = pd.DataFrame(linhas)

    st.dataframe(df_jogos, use_container_width=True, hide_index=True)

# =========================
# 8. CHANCE MATEMÁTICA
# =========================

elif menu == "8️⃣ Chance matemática":
    st.markdown("## 8️⃣ Chance matemática dos jogos")

    total_combinacoes, chance_12 = chance_lotofacil(12)
    _, chance_simulada = chance_lotofacil(qtd_jogos_simulados)

    st.markdown(
        """
        Na Lotofácil, uma aposta simples de 15 dezenas possui:
        """
    )

    st.latex(r"\frac{1}{3.268.760}")

    st.markdown("Com **12 jogos diferentes**, a chance aproximada fica:")

    st.latex(r"\frac{12}{3.268.760}")

    st.markdown("Ou seja, aproximadamente:")

    st.latex(r"1 \text{ em } 272.397")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total de combinações", f"{total_combinacoes:,.0f}".replace(",", "."))
    col2.metric("Jogos usados", "12")
    col3.metric("Chance aproximada", f"1 em {chance_12:,.0f}".replace(",", "."))

    st.markdown("---")

    st.markdown("## Simulador simples de probabilidade")

    st.markdown(
        f"""
        Com **{qtd_jogos_simulados} jogo(s)**, a chance aproximada de 15 pontos fica:
        """
    )

    st.latex(
        rf"1 \text{{ em }} {chance_simulada:,.0f}".replace(",", ".")
    )

    st.warning(
        "A probabilidade melhora com mais jogos, mas a Lotofácil continua sendo um jogo de alto risco. "
        "Nenhuma estratégia garante premiação."
    )

# =========================
# RESUMO FINAL
# =========================

elif menu == "✅ Resumo final":
    st.markdown("## ✅ Minha recomendação final")

    st.markdown("### Base principal recomendada")
    st.markdown(bolas_html(base_18, "normal"), unsafe_allow_html=True)

    st.markdown(
        """
        Esta é a base que eu usaria para montar desdobramentos de 15 dezenas.
        """
    )

    st.markdown("### Se for jogar poucos bilhetes, priorizar estes 5 jogos")

    jogos_prioritarios = list(desdobramento_12.items())[:5]

    for nome, jogo in jogos_prioritarios:
        st.markdown(
            f"""
            <div class="jogo-box">
                <h4>{nome}</h4>
                {bolas_html(jogo)}
                <p>
                    <b>Pares:</b> {contar_pares(jogo)} |
                    <b>Ímpares:</b> {contar_impares(jogo)} |
                    <b>Soma:</b> {soma_dezenas(jogo)}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### Estratégia resumida")

    st.markdown(
        """
        - Trabalhar com **18 dezenas base**;
        - Gerar jogos de **15 dezenas**;
        - Evitar jogos muito parecidos;
        - Manter equilíbrio entre pares e ímpares;
        - Buscar soma entre **180 e 205**;
        - Repetir de **9 a 11 dezenas** do último concurso;
        - Usar algumas dezenas ausentes como compensação;
        - Não depender apenas de dezenas quentes.
        """
    )

    st.success(
        "Painel finalizado com todos os tópicos da análise de 1 a 8."
    )

# =========================
# RODAPÉ
# =========================

st.markdown("---")
st.caption(
    "Desenvolvido para análise estatística da Lotofácil. "
    "As informações são educativas e não garantem premiação."
)
