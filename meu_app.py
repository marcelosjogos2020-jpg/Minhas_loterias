import streamlit as st
import requests
import itertools
import random
from collections import Counter
from datetime import datetime


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Loterias - Desdobramentos",
    page_icon="🍀",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
        .main {
            background-color: #020617;
        }

        section[data-testid="stSidebar"] {
            background-color: #0f172a;
        }

        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3, h4, h5, h6, p, div, span, label {
            color: #ffffff;
        }

        .titulo-principal {
            font-size: 30px;
            font-weight: 900;
            margin-bottom: 4px;
            color: #ffffff;
        }

        .subtitulo {
            color: #cbd5e1;
            font-size: 14px;
            margin-bottom: 18px;
        }

        .divisor {
            border-top: 1px solid #334155;
            margin: 24px 0 18px 0;
        }

        /* =====================================================
           CARD COMPACTO DO ÚLTIMO CONCURSO
        ===================================================== */

        .ultimo-sorteio {
            border: 1px solid #1e88ff;
            border-radius: 10px;
            padding: 10px 14px;
            margin: 8px 0 18px 0;
            background: linear-gradient(90deg, #101827, #111827);
            box-shadow: 0 0 8px rgba(30,136,255,0.18);
            max-width: 760px;
        }

        .ultimo-label {
            font-size: 12px;
            color: #93c5fd;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .ultimo-concurso {
            font-size: 17px;
            color: #ffffff;
            font-weight: 800;
            margin-bottom: 5px;
        }

        .ultimo-local {
            color: #cbd5e1;
            font-size: 12px;
            margin-bottom: 8px;
        }

        .dezena-mini {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            background: #22c55e;
            color: #ffffff;
            font-size: 11px;
            font-weight: 900;
            margin: 2px;
            box-shadow: 0 0 6px rgba(34,197,94,0.25);
        }

        /* =====================================================
           DEZENAS NORMAIS
        ===================================================== */

        .dezena-base {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 34px;
            height: 34px;
            border-radius: 50%;
            background: #22c55e;
            color: #ffffff;
            font-size: 13px;
            font-weight: 900;
            margin: 4px;
            box-shadow: 0 0 8px rgba(34,197,94,0.30);
        }

        .dezena-jogo {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 29px;
            height: 29px;
            border-radius: 50%;
            background: #1d4ed8;
            color: #ffffff;
            font-size: 12px;
            font-weight: 800;
            margin: 3px;
        }

        /* =====================================================
           PREMIAÇÃO ANTIGA
        ===================================================== */

        .premio-box {
            background: #111827;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 12px;
            min-height: 95px;
            color: #ffffff;
            font-size: 13px;
        }

        .premio-box strong {
            color: #ffffff;
            font-size: 13px;
        }

        /* =====================================================
           JOGOS
        ===================================================== */

        .jogo-card {
            background: #111827;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 12px;
        }

        .jogo-titulo {
            font-size: 13px;
            font-weight: 800;
            color: #93c5fd;
            margin-bottom: 8px;
        }

        .info-box {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 12px 14px;
            color: #cbd5e1;
            font-size: 13px;
            margin-bottom: 14px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def formatar_moeda(valor):
    try:
        valor = float(valor or 0)
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def formatar_data(data_texto):
    if not data_texto:
        return ""

    formatos = ["%d/%m/%Y", "%Y-%m-%d"]

    for formato in formatos:
        try:
            return datetime.strptime(data_texto[:10], formato).strftime("%d/%m/%Y")
        except Exception:
            pass

    return data_texto


def normalizar_dezenas(lista):
    dezenas = []

    for item in lista or []:
        try:
            dezenas.append(f"{int(item):02d}")
        except Exception:
            dezenas.append(str(item).zfill(2))

    return sorted(dezenas, key=lambda x: int(x))


def render_dezenas(dezenas, tipo="base"):
    if tipo == "jogo":
        classe = "dezena-jogo"
    else:
        classe = "dezena-base"

    html = ""

    for dezena in dezenas:
        html += f'<span class="{classe}">{dezena}</span>'

    st.markdown(html, unsafe_allow_html=True)


def render_dezenas_mini_html(dezenas):
    html = ""

    for dezena in dezenas:
        html += f'<span class="dezena-mini">{dezena}</span>'

    return html


def render_jogo_card(numero, dezenas):
    html_dezenas = ""

    for dezena in dezenas:
        html_dezenas += f'<span class="dezena-jogo">{dezena}</span>'

    st.markdown(
        f"""
        <div class="jogo-card">
            <div class="jogo-titulo">Jogo {numero}</div>
            <div>{html_dezenas}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# API CAIXA
# ============================================================

@st.cache_data(ttl=600)
def buscar_concurso_lotofacil(numero=None):
    base_url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"

    if numero:
        url = f"{base_url}/{numero}"
    else:
        url = base_url

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*"
    }

    resposta = requests.get(url, headers=headers, timeout=15)
    resposta.raise_for_status()

    return resposta.json()


@st.cache_data(ttl=900)
def buscar_historico_lotofacil(qtd_concursos=25):
    ultimo = buscar_concurso_lotofacil()
    numero_ultimo = int(ultimo.get("numero", 0))

    historico = []

    for numero in range(numero_ultimo, max(numero_ultimo - qtd_concursos, 0), -1):
        try:
            concurso = buscar_concurso_lotofacil(numero)
            dezenas = normalizar_dezenas(concurso.get("listaDezenas", []))

            if dezenas:
                historico.append({
                    "numero": concurso.get("numero"),
                    "data": formatar_data(concurso.get("dataApuracao")),
                    "dezenas": dezenas
                })

        except Exception:
            continue

    return historico


def extrair_ultimo_concurso(dados):
    dezenas = normalizar_dezenas(dados.get("listaDezenas", []))

    local = dados.get("localSorteio", "") or ""
    municipio = dados.get("nomeMunicipioUFSorteio", "") or ""

    rateio = dados.get("listaRateioPremio", []) or []

    return {
        "numero": dados.get("numero", ""),
        "data": formatar_data(dados.get("dataApuracao", "")),
        "dezenas": dezenas,
        "local": local,
        "municipio": municipio,
        "rateio": rateio,
        "valor_estimado_proximo": dados.get("valorEstimadoProximoConcurso", 0),
        "data_proximo": formatar_data(dados.get("dataProximoConcurso", ""))
    }


# ============================================================
# LÓGICA DA BASE E DOS JOGOS
# ============================================================

def gerar_base_18_por_frequencia(historico):
    contador = Counter()

    for concurso in historico:
        contador.update(concurso["dezenas"])

    todas_dezenas = [f"{i:02d}" for i in range(1, 26)]

    ranking = sorted(
        todas_dezenas,
        key=lambda dezena: (-contador[dezena], int(dezena))
    )

    base_18 = ranking[:18]

    return sorted(base_18, key=lambda x: int(x)), contador


def gerar_jogos_desdobramento(base_18, quantidade_jogos=20, dezenas_por_jogo=15, fixas=None):
    fixas = fixas or []
    fixas = normalizar_dezenas(fixas)

    base_18 = normalizar_dezenas(base_18)

    fixas_validas = [d for d in fixas if d in base_18]
    variaveis = [d for d in base_18 if d not in fixas_validas]

    quantidade_para_completar = dezenas_por_jogo - len(fixas_validas)

    if quantidade_para_completar < 0:
        return []

    if quantidade_para_completar > len(variaveis):
        return []

    combinacoes_possiveis = list(
        itertools.combinations(variaveis, quantidade_para_completar)
    )

    random.shuffle(combinacoes_possiveis)

    jogos = []

    for combinacao in combinacoes_possiveis[:quantidade_jogos]:
        jogo = sorted(fixas_validas + list(combinacao), key=lambda x: int(x))
        jogos.append(jogo)

    return jogos


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("## ⚙️ Configurações")

qtd_historico = st.sidebar.slider(
    "Concursos usados na análise",
    min_value=10,
    max_value=60,
    value=25,
    step=5
)

qtd_jogos = st.sidebar.slider(
    "Quantidade de jogos gerados",
    min_value=5,
    max_value=100,
    value=20,
    step=5
)

dezenas_por_jogo = st.sidebar.selectbox(
    "Dezenas por jogo",
    options=[15, 16, 17, 18],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔒 Dezenas fixas")

fixas_texto = st.sidebar.text_input(
    "Digite separadas por vírgula",
    value="",
    placeholder="Exemplo: 01, 02, 10"
)

fixas = []

if fixas_texto.strip():
    try:
        fixas = [
            f"{int(x.strip()):02d}"
            for x in fixas_texto.split(",")
            if x.strip()
        ]
    except Exception:
        st.sidebar.warning("Confira o formato das dezenas fixas.")


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="titulo-principal">🍀 Loterias - Desdobramentos Lotofácil</div>
    <div class="subtitulo">
        Análise automática com base nos concursos recentes, sugestão de base principal e geração de jogos.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

try:
    dados_ultimo = buscar_concurso_lotofacil()
    ultimo = extrair_ultimo_concurso(dados_ultimo)

    historico = buscar_historico_lotofacil(qtd_historico)
    base_18, contador_frequencia = gerar_base_18_por_frequencia(historico)

except Exception:
    st.error("Não foi possível carregar os dados da Caixa neste momento.")
    st.stop()


# ============================================================
# ÚLTIMO CONCURSO COM DEZENAS SORTEADAS
# ============================================================

numero_ultimo = ultimo["numero"]
data_ultimo = ultimo["data"]
dezenas_ultimo = ultimo["dezenas"]

local_sorteio = ultimo["local"]
municipio_sorteio = ultimo["municipio"]

if municipio_sorteio:
    texto_local = municipio_sorteio
elif local_sorteio:
    texto_local = local_sorteio
else:
    texto_local = "Local não informado"

bolinhas_dezenas = render_dezenas_mini_html(dezenas_ultimo)

st.markdown(
    f"""
    <div class="ultimo-sorteio">
        <div class="ultimo-label">🍀 Último sorteio da Caixa</div>
        <div class="ultimo-concurso">Concurso {numero_ultimo} — {data_ultimo}</div>
        <div class="ultimo-local">Local: <strong>{texto_local}</strong></div>
        <div style="margin-top:8px;">{bolinhas_dezenas}</div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# BASE PRINCIPAL SUGERIDA
# ============================================================

st.markdown("### 🎯 Base principal sugerida com 18 dezenas")
render_dezenas(base_18, "base")


# ============================================================
# PREMIAÇÃO DO ÚLTIMO CONCURSO - FORMATO ANTIGO
# ============================================================

st.markdown("## 🏆 Premiação do último concurso")

rateio = ultimo.get("rateio", [])

if rateio:
    cols = st.columns(min(len(rateio), 5))

    for i, faixa in enumerate(rateio[:5]):
        desc = faixa.get("descricaoFaixa", "")
        ganh = faixa.get("numeroDeGanhadores", 0)
        valor = faixa.get("valorPremio", 0)

        with cols[i]:
            st.markdown(
                f"""
                <div class="premio-box">
                    <strong>{desc}</strong><br>
                    {ganh} ganhador(es)<br>
                    <span style="color:#38bdf8;font-weight:800;">
                        {formatar_moeda(valor)}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.info("A Caixa não retornou dados de premiação para este concurso.")

valor_prox = ultimo.get("valor_estimado_proximo", 0)
data_prox = ultimo.get("data_proximo", "")

st.markdown(
    f"""
    <div class="premio-box">
        <strong>Estimativa do próximo concurso:</strong>
        <span style="color:#38bdf8;font-weight:900;">
            {formatar_moeda(valor_prox)}
        </span>
        &nbsp; | &nbsp;
        <strong>Data:</strong> {data_prox}
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# INFORMAÇÕES DA ANÁLISE
# ============================================================

st.markdown('<div class="divisor"></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="info-box">
            <strong>Concursos analisados:</strong><br>
            {len(historico)}
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="info-box">
            <strong>Base utilizada:</strong><br>
            18 dezenas
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="info-box">
            <strong>Jogos solicitados:</strong><br>
            {qtd_jogos}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# GERAÇÃO DOS JOGOS
# ============================================================

st.markdown("## 🧩 Jogos gerados a partir da base")

jogos = gerar_jogos_desdobramento(
    base_18=base_18,
    quantidade_jogos=qtd_jogos,
    dezenas_por_jogo=dezenas_por_jogo,
    fixas=fixas
)

if not jogos:
    st.warning("Não foi possível gerar jogos com as configurações atuais. Confira as dezenas fixas.")
else:
    cols = st.columns(2)

    for idx, jogo in enumerate(jogos, start=1):
        with cols[(idx - 1) % 2]:
            render_jogo_card(idx, jogo)


# ============================================================
# DOWNLOAD DOS JOGOS
# ============================================================

if jogos:
    texto_download = ""

    for idx, jogo in enumerate(jogos, start=1):
        texto_download += f"Jogo {idx}: {' '.join(jogo)}\n"

    st.download_button(
        label="📥 Baixar jogos em TXT",
        data=texto_download,
        file_name=f"jogos_lotofacil_concurso_{numero_ultimo}.txt",
        mime="text/plain"
    )


# ============================================================
# RODAPÉ
# ============================================================

st.markdown('<div class="divisor"></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div style="font-size:12px;color:#94a3b8;">
        Observação: este sistema apenas organiza dados estatísticos e gera combinações.
        Não há garantia de premiação.
    </div>
    """,
    unsafe_allow_html=True
)
