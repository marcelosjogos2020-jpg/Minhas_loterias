import streamlit as st
import pandas as pd
import requests
import itertools
import math
from collections import Counter
from datetime import datetime
import json

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Lotofácil | Análises e Desdobramentos",
    page_icon="🍀",
    layout="wide"
)

# ============================================================
# ESTADO DA SESSÃO (SESSION STATE)
# ============================================================
if "jogos_gerados" not in st.session_state:
    st.session_state["jogos_gerados"] = []

# ============================================================
# CSS CUSTOMIZADO E REGRAS DE IMPRESSÃO A4
# ============================================================

st.markdown(
    """
<style>
    html, body, [class*="css"] {
        background-color: #0b111a;
        color: #ffffff;
    }

    .main {
        background-color: #0b111a;
    }

    h1, h2, h3 {
        color: #ffffff;
        font-weight: 900;
    }

    .subtitulo {
        font-size: 22px;
        color: #ffffff;
        font-weight: 800;
        margin-bottom: 24px;
    }

    .ultimo-sorteio {
        border: 2px solid #1e88ff;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0 26px 0;
        background: linear-gradient(90deg, #111827, #162033);
        box-shadow: 0 0 14px rgba(30,136,255,0.28);
    }

    .ultimo-label {
        font-size: 14px;
        color: #93c5fd;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .ultimo-concurso {
        font-size: 22px;
        color: #ffffff;
        font-weight: 900;
        margin-bottom: 16px;
    }

    .ultimo-local {
        color: #ffffff;
        font-size: 14px;
        margin-bottom: 20px;
    }

    .dezenas-resultado-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
        margin-top: 8px;
    }

    .dezena-resultado {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #5cff75, #16a34a 65%, #0f7a35);
        color: #ffffff;
        font-weight: 900;
        font-size: 13px;
        border: 2px solid rgba(255,255,255,0.18);
        box-shadow: 0 0 10px rgba(34,197,94,0.45);
    }

    .info-box {
        background: #1c2d45;
        border-left: 4px solid #1e88ff;
        color: #ffffff;
        padding: 16px 18px;
        border-radius: 8px;
        margin: 20px 0 14px 0;
        font-size: 14px;
        font-weight: 700;
    }

    .metric-card {
        background: #111821;
        border: 1px solid #2d3b4f;
        border-radius: 10px;
        padding: 22px 16px;
        text-align: center;
        min-height: 95px;
    }

    .metric-label {
        font-size: 13px;
        color: #9bd1ff;
        margin-bottom: 12px;
    }

    .metric-value {
        color: #2f83ff;
        font-size: 24px;
        font-weight: 900;
    }

    .section-divider {
        border-top: 1px solid #2d3b4f;
        margin: 30px 0;
    }

    .dezena-base {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #1e88ff;
        color: white;
        font-weight: 900;
        margin: 4px;
        box-shadow: 0 0 8px rgba(30,136,255,0.45);
    }

    .dezena-fixa-painel {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: white;
        font-weight: 900;
        margin: 4px;
        border: 2px solid #818cf8;
        box-shadow: 0 0 12px rgba(99, 102, 241, 0.7);
    }

    .dezena-fria {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #ef4444;
        color: white;
        font-weight: 900;
        margin: 4px;
        box-shadow: 0 0 8px rgba(239,68,68,0.45);
    }

    /* ============================================================
       ESTILIZAÇÃO DO VOLANTE OFICIAL (VISUALIZAÇÃO EM TELA)
       ============================================================ */
    .volante-wrapper {
        background-color: #fffde6;
        border: 2px solid #d946ef;
        border-radius: 12px;
        padding: 15px;
        max-width: 340px;
        margin: 15px auto;
        font-family: 'Arial', sans-serif;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }

    .volante-header {
        background-color: #c026d3;
        color: #ffffff;
        text-align: center;
        font-weight: 900;
        font-size: 20px;
        padding: 6px;
        border-radius: 6px;
        margin-bottom: 12px;
        letter-spacing: 2px;
    }

    .volante-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 8px;
        justify-items: center;
        background-color: #fffee6;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #fbcfe8;
    }

    .dezena-volante {
        width: 42px;
        height: 32px;
        border: 1.5px solid #c026d3;
        color: #c026d3;
        background-color: #ffffff;
        font-weight: bold;
        font-size: 14px;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 4px;
    }

    .dezena-volante.marcada {
        background: #111827 !important;
        color: #ffffff !important;
        border: 2px solid #111827 !important;
        position: relative;
    }

    .dezena-volante.marcada::after {
        content: "X";
        position: absolute;
        font-size: 16px;
        font-weight: 900;
        color: #ff4b4b;
    }

    .dezena-volante.acertada-gabarito {
        border: 2px solid #ca8a04 !important;
        background-color: #facc15 !important;
        color: #000000 !important;
    }

    .premio-card {
        background: #16222f;
        border: 1px solid #ca8a04;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .premio-titulo {
        font-size: 12px;
        color: #fef08a;
    }
    .premio-valor {
        font-size: 20px;
        font-weight: 900;
        color: #facc15;
    }

    /* ============================================================
       REGRAS ESTRITAS DE IMPRESSÃO (CONFIGURAÇÃO PARA FOLHA A4)
       ============================================================ */
    @media print {
        /* Oculta absolutamente tudo que é nativo do Streamlit e do layout */
        header, footer, [data-testid="stSidebar"], .stButton, .stDownloadButton, .section-divider, h1, h2, h3, p, span, div:not(.printable-print-area):not(.volante-wrapper):not(.volante-grid):not(.dezena-volante) {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Configura a página A4 */
        @page {
            size: A4 portrait;
            margin: 0;
        }

        body, .main {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        .printable-print-area {
            display: block !important;
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 210mm !important;
            height: 297mm !important;
            padding: 20mm !important;
            background-color: #ffffff !important;
        }

        /* O volante impresso vira uma guia perfeita com dimensões exatas */
        .volante-wrapper {
            display: inline-block !important;
            border: 0.5px dashed #777777 !important; /* Borda guia para colagem do papel */
            background-color: #ffffff !important;
            background: transparent !important;
            width: 84mm !important;
            height: 143mm !important;
            margin: 10mm !important;
            padding: 5mm !important;
            box-shadow: none !important;
            page-break-inside: avoid;
        }

        .volante-header {
            display: none !important; /* Some o logo rosa para não gastar tinta */
        }

        .volante-grid {
            background-color: transparent !important;
            border: none !important;
            gap: 4mm !important;
        }

        /* Remove o número e os contornos do quadrado na folha */
        .dezena-volante {
            border: none !important;
            background-color: transparent !important;
            color: transparent !important;
            width: 10mm !important;
            height: 8mm !important;
        }

        /* Pinta exclusivamente a marcação de preto para marcar o papel físico colado por cima */
        .dezena-volante.marcada {
            background-color: #000000 !important;
            background: #000000 !important;
            border-radius: 1px !important;
        }

        .dezena-volante.marcada::after {
            display: none !important; /* O X vermelho some, dando lugar ao preenchimento preto total */
        }
    }
</style>
""",
    unsafe_allow_html=True
)

# ============================================================
# FUNÇÕES DE BUSCA NA CAIXA
# ============================================================

BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"


@st.cache_data(ttl=600)
def buscar_concurso(numero=None):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*"
    }
    url = BASE_URL if numero is None else f"{BASE_URL}/{numero}"
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    dados = response.json()
    dezenas = [str(d).zfill(2) for d in dados.get("listaDezenas", [])]
    return {
        "numero": dados.get("numero"),
        "data": dados.get("dataApuracao"),
        "dezenas": dezenas,
        "municipio": dados.get("nomeMunicipioUFSorteio") or dados.get("nomeMunicipioSorteio"),
        "local": dados.get("localSorteio"),
        "raw": dados
    }


@st.cache_data(ttl=600)
def carregar_concursos(qtd):
    ultimo = buscar_concurso()
    numero_ultimo = int(ultimo["numero"])
    concursos = []
    for numero in range(numero_ultimo, numero_ultimo - qtd, -1):
        try:
            concurso = buscar_concurso(numero)
            if concurso["dezenas"]:
                concursos.append(concurso)
        except Exception:
            continue
    return concursos


# ============================================================
# FUNÇÕES DE ANÁLISE
# ============================================================

def analisar_concursos(concursos):
    todas_dezenas = []
    for concurso in concursos:
        todas_dezenas.extend(concurso["dezenas"])
    frequencia = Counter(todas_dezenas)
    universo = [str(i).zfill(2) for i in range(1, 26)]
    df_freq = pd.DataFrame({
        "dezena": universo,
        "frequencia": [frequencia.get(dezena, 0) for dezena in universo]
    })
    return df_freq.sort_values(by=["frequencia", "dezena"], ascending=[False, True]).reset_index(drop=True)


def calcular_atrasos(concursos):
    universo = [str(i).zfill(2) for i in range(1, 26)]
    atrasos = {}
    for dezena in universo:
        atraso = 0
        for concurso in concursos:
            if dezena in concurso["dezenas"]:
                break
            atraso += 1
        atrasos[dezena] = atraso
    df_atrasos = pd.DataFrame({
        "dezena": list(atrasos.keys()),
        "atraso": list(atrasos.values())
    })
    return df_atrasos.sort_values(by=["atraso", "dezena"], ascending=[False, True]).reset_index(drop=True)


def estatisticas_jogo(jogo, ultimo_resultado):
    numeros = [int(x) for x in jogo]
    pares = sum(1 for n in numeros if n % 2 == 0)
    impares = 15 - pares
    soma = sum(numeros)
    repetidas_ultimo = len(set(jogo).intersection(set(ultimo_resultado)))
    return {
        "pares": pares,
        "impares": impares,
        "soma": soma,
        "repetidas_ultimo": repetidas_ultimo
    }


def pontuar_jogo(jogo, mapa_freq, mapa_atraso):
    score_freq = sum(mapa_freq.get(d, 0) for d in jogo)
    score_atraso = sum(mapa_atraso.get(d, 0) for d in jogo)
    return score_freq + score_atraso * 0.25


def gerar_desdobramento_com_fixos(
    base_variavel, fixos, qtd_jogos, ultimo_resultado, mapa_freq, mapa_atraso,
    pares_min, pares_max, soma_min, soma_max, repetidas_min, repetidas_max, sobreposicao_max
):
    vagas_restantes = 15 - len(fixos)
    combinacoes_variaveis = list(itertools.combinations(base_variavel, vagas_restantes))
    jogos_validos = []

    for combo in combinacoes_variaveis:
        jogo = sorted(list(fixos) + list(combo), key=lambda x: int(x))
        stats = estatisticas_jogo(jogo, ultimo_resultado)

        if not (pares_min <= stats["pares"] <= pares_max): continue
        if not (soma_min <= stats["soma"] <= soma_max): continue
        if not (repetidas_min <= stats["repetidas_ultimo"] <= repetidas_max): continue

        pontos = pontuar_jogo(jogo, mapa_freq, mapa_atraso)
        jogos_validos.append({
            "jogo": jogo, "score": pontos, "pares": stats["pares"],
            "impares": stats["impares"], "soma": stats["soma"], "repetidas_ultimo": stats["repetidas_ultimo"]
        })

    jogos_validos = sorted(jogos_validos, key=lambda x: x["score"], reverse=True)
    selecionados = []

    for item in jogos_validos:
        jogo_atual = set(item["jogo"])
        if not selecionados:
            selecionados.append(item)
        else:
            aprovado = True
            for selecionado in selecionados:
                if len(jogo_atual.intersection(set(selecionado["jogo"]))) > sobreposicao_max:
                    aprovado = False
                    break
            if aprovado: selecionados.append(item)
        if len(selecionados) >= qtd_jogos: break

    if len(selecionados) < qtd_jogos:
        for item in jogos_validos:
            if item not in selecionados: selecionados.append(item)
            if len(selecionados) >= qtd_jogos: break

    return selecionados[:qtd_jogos]


def jogos_para_csv(jogos):
    linhas = []
    for idx, item in enumerate(jogos, start=1):
        linha = {
            "Jogo": idx, "Dezenas": " ".join(item["jogo"]), "Pares": item["pares"],
            "Ímpares": item["impares"], "Soma": item["soma"], "Repetidas do último": item["repetidas_ultimo"],
            "Score": round(item["score"], 2)
        }
        for pos, dezena in enumerate(item["jogo"], start=1):
            linha[f"D{pos:02d}"] = dezena
        linhas.append(linha)
    return pd.DataFrame(linhas).to_csv(index=False, sep=";", encoding="utf-8-sig")


# ============================================================
# PROCESSAMENTO DE DADOS INICIAIS
# ============================================================
st.markdown("# 🍀 Lotofácil | Análises e Desdobramentos")
st.markdown('<div class="subtitulo">Painel estatístico com base nos últimos concursos analisados</div>', unsafe_allow_html=True)

try:
    ultimo_concurso = buscar_concurso()
except Exception:
    st.error("Não foi possível carregar o último concurso automaticamente da Caixa.")
    st.stop()

numero_ultimo = ultimo_concurso["numero"]
data_ultimo = ultimo_concurso["data"]
dezenas_ultimo = ultimo_concurso["dezenas"]

html_dezenas_resultado = "".join([f'<span class="dezena-resultado">{dezena}</span>' for dezena in dezenas_ultimo])
st.markdown(
    f'<div class="ultimo-sorteio">'
    f'<div class="ultimo-label">🍀 Último sorteio carregado automaticamente da Caixa</div>'
    f'<div class="ultimo-concurso">Concurso {numero_ultimo} — {data_ultimo}</div>'
    f'<div class="dezenas-resultado-container">{html_dezenas_resultado}</div>'
    f'</div>',
    unsafe_allow_html=True
)

# ============================================================
# SIDEBAR CONFIGURAÇÕES
# ============================================================
st.sidebar.header("⚙️ Configurações")
qtd_concursos = st.sidebar.number_input("Quantidade de concursos para análise", min_value=5, max_value=100, value=11)
tamanho_base = st.sidebar.number_input("Tamanho da base sugerida", min_value=15, max_value=25, value=20)
qtd_jogos = st.sidebar.number_input("Quantidade de jogos no desdobramento", min_value=1, max_value=100, value=12)

st.sidebar.divider()
dezenas_fixas = st.sidebar.multiselect("Dezenas FIXAS (Máx 5)", options=[str(i).zfill(2) for i in range(1, 26)], max_selections=5)
dezenas_para_descartar = st.sidebar.multiselect("Dezenas descartadas", options=[str(i).zfill(2) for i in range(1, 26) if str(i).zfill(2) not in dezenas_fixas])

st.sidebar.divider()
st.sidebar.subheader("Filtros combinatórios")
pares_min = st.sidebar.slider("Mínimo de pares", 0, 15, 6)
pares_max = st.sidebar.slider("Máximo de pares", 0, 15, 9)
soma_min = st.sidebar.number_input("Soma mínima", 120, 300, 170)
soma_max = st.sidebar.number_input("Soma máxima", 120, 300, 220)
repetidas_min = st.sidebar.slider("Mínimo de repetidas", 0, 15, 8)
repetidas_max = st.sidebar.slider("Máximo de repetidas", 0, 15, 11)
sobreposicao_max = st.sidebar.slider("Sobreposição máxima", 8, 15, 13)

concursos = carregar_concursos(qtd_concursos)
if not concursos:
    st.error("Nenhum concurso carregado.")
    st.stop()

df_freq = analisar_concursos(concursos)
df_atrasos = calcular_atrasos(concursos)
mapa_freq = dict(zip(df_freq["dezena"], df_freq["frequencia"]))
mapa_atraso = dict(zip(df_atrasos["dezena"], df_atrasos["atraso"]))

opcoes_concurso = {f"Concurso {c['numero']} ({c['data']})": c['dezenas'] for c in concursos}
opcoes_concurso["Inserir Dezenas Manualmente"] = []

# ============================================================
# PAINÉIS DE ESTATÍSTICA
# ============================================================
st.markdown("## 📊 Visão Geral da Análise")
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🔥 Dezenas mais fortes")
    html_fortes = "".join([f'<span class="dezena-base">{r["dezena"]}</span>' for _, r in df_freq.head(10).iterrows()])
    st.markdown(html_fortes, unsafe_allow_html=True)
with col2:
    st.markdown("### 🧊 Dezenas em atraso")
    html_atrasadas = "".join([f'<span class="dezena-fria">{r["dezena"]}</span>' for _, r in df_atrasos.head(10).iterrows()])
    st.markdown(html_atrasadas, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🎯 Base sugerida")
df_base = df_freq[~df_freq["dezena"].isin(dezenas_para_descartar + dezenas_fixas)]
base_variavel = df_base.head(tamanho_base - len(dezenas_fixas))["dezena"].tolist()
base_sugerida_completa = sorted(list(set(base_variavel + dezenas_fixas)), key=lambda x: int(x))

html_base = "".join([f'<span class="{"dezena-fixa-painel" if d in dezenas_fixas else "dezena-base"}">{d}</span>' for d in base_sugerida_completa])
st.markdown(html_base, unsafe_allow_html=True)

# ============================================================
# ENGINE DE GERAÇÃO
# ============================================================
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🧩 Geração de jogos")

if len(base_sugerida_completa) < 15:
    st.error("A base selecionada precisa de ao menos 15 dezenas.")
else:
    if st.button("🎲 Gerar Novo Desdobramento", use_container_width=True, type="primary"):
        st.session_state["jogos_gerados"] = gerar_desdobramento_com_fixos(
            base_variavel, dezenas_fixas, qtd_jogos, dezenas_ultimo, mapa_freq, mapa_atraso,
            pares_min, pares_max, soma_min, soma_max, repetidas_min, repetidas_max, sobreposicao_max
        )
        st.success("Jogos gerados com sucesso!")

# ============================================================
# EXIBIÇÃO EM ABAS: VOLANTE DIGITAL VS LISTA TRADICIONAL & CONFERÊNCIA
# ============================================================
if st.session_state["jogos_gerados"]:
    jogos_ativos = st.session_state["jogos_gerados"]

    st.markdown("## 🎟️ Conferência & Gabarito de Resultados")
    col_sel, col_btn_action = st.columns([3, 1])
    with col_sel:
        selecao_concurso = st.selectbox("Escolha o concurso para conferência:", options=list(opcoes_concurso.keys()), label_visibility="collapsed")
    
    dezenas_alvo = []
    if selecao_concurso == "Inserir Dezenas Manualmente":
        dezenas_manuais = st.text_input("Insira as 15 dezenas separadas por espaço (Ex: 01 02 05...):")
        if dezenas_manuais: dezenas_alvo = [d.zfill(2) for d in dezenas_manuais.strip().split()][:15]
    else:
        dezenas_alvo = opcoes_concurso[selecao_concurso]

    rodar_conferencia = col_btn_action.button("🔍 Rodar Conferência", use_container_width=True)

    # Ordenação oficial exata das dezenas do volante conforme imagem do usuário
    # Linha 1: 21, 16, 11, 06, 01 | Linha 2: 22, 17, 12, 07, 02 ...
    ORDEM_VOLANTE_OFICIAL = [
        "21", "16", "11", "06", "01",
        "22", "17", "12", "07", "02",
        "23", "18", "13", "08", "03",
        "24", "19", "14", "09", "04",
        "25", "20", "15", "10", "05"
    ]

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Criamos um container invisível na tela que só o interpretador de impressão A4 do Windows/Chrome ativará
    st.markdown('<div class="printable-print-area">', unsafe_allow_html=True)

    st.markdown("### 📋 Painel de Cartões & Volantes Gerados")
    
    # Adicionamos um acionador JavaScript limpo para o usuário imprimir a folha diretamente
    if st.button("🖨️ Abrir Opções de Impressão (A4)", use_container_width=True):
        components.html("<script>window.print();</script>", height=0, width=0)
        st.info("Configuração Recomendada na janela de impressão: Desative cabeçalhos/rodapés e defina margens como 'Nenhuma' ou 'Padrão'.")

    # Renderização dinâmica dos blocos de volantes
    for idx, item in enumerate(jogos_ativos):
        jogo_set = set(item["jogo"])
        acertos_set = jogo_set.intersection(set(dezenas_alvo)) if dezenas_alvo else set()
        
        # Criação do HTML Estruturado do Volante Caixa
        html_volante = f'<div class="volante-wrapper">'
        html_volante += f'<div class="volante-header">JOGO {idx + 1}</div>'
        html_volante += f'<div class="volante-grid">'
        
        for dezena in ORDEM_VOLANTE_OFICIAL:
            classes = "dezena-volante"
            if dezena in jogo_set:
                classes += " marcada"
            if dezena in acertos_set and rodar_conferencia:
                classes += " acertada-gabarito"
            html_volante += f'<div class="{classes}">{dezena}</div>'
            
        html_volante += f'</div>' # fecha volante-grid
        if dezenas_alvo and rodar_conferencia:
            html_volante += f'<div style="text-align:center; color:#000; font-weight:bold; margin-top:5px; font-size:12px;">Acertos: {len(acertos_set)}</div>'
        html_volante += f'</div>' # fecha volante-wrapper
        
        st.markdown(html_volante, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # fecha printable-print-area

    csv = jogos_para_csv(jogos_ativos)
    st.download_button(label="Download da Lista em CSV", data=csv, file_name="jogos_lotofacil.csv", mime="text/csv", use_container_width=True)

# ============================================================
# ANÁLISE COMBINATÓRIA FINAL
# ============================================================
if st.session_state["jogos_gerados"]:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("<h2>📊 Leitura Combinatória do Fechamento</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    somas = [j["soma"] for j in st.session_state["jogos_gerados"]]
    c1.metric("Menor Soma", min(somas))
    c2.metric("Maior Soma", max(somas))
    c3.metric("Média das Somas", round(sum(somas)/len(somas), 2))
