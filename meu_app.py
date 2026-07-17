import itertools
import json
import math
from collections import Counter

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Lotofácil | Análises e Desdobramentos",
    page_icon="🍀",
    layout="wide"
)


# ============================================================
# ESTADO DA SESSÃO
# ============================================================

if "jogos_gerados" not in st.session_state:
    st.session_state["jogos_gerados"] = []

if "calib_volante" not in st.session_state:
    st.session_state["calib_volante"] = {
        "x1": 25.0,
        "y1": 42.0,
        "x2": 25.0,
        "y2": 150.0,
        "dx": 12.5,
        "dy": 8.0,
        "raio": 2.2
    }


# ============================================================
# CSS
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

h1, h2, h3, h4 {
    color: #ffffff;
    font-weight: 900;
}

.subtitulo {
    font-size: 22px;
    color: #ffffff;
    font-weight: 800;
    margin-bottom: 24px;
}

.section-divider {
    border-top: 1px solid #2d3b4f;
    margin: 30px 0;
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
}

.dezena-resultado,
.dezena-base,
.dezena-fixa-painel,
.dezena-fria,
.dezena-jogo,
.dezena-acerto {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    border-radius: 50%;
    color: white;
    font-weight: 900;
}

.dezena-resultado {
    width: 36px;
    height: 36px;
    background: radial-gradient(
        circle at 30% 30%,
        #5cff75,
        #16a34a 65%,
        #0f7a35
    );
    font-size: 13px;
    border: 2px solid rgba(255,255,255,0.18);
    box-shadow: 0 0 10px rgba(34,197,94,0.45);
}

.dezena-base {
    width: 38px;
    height: 38px;
    background: #1e88ff;
    margin: 4px;
    box-shadow: 0 0 8px rgba(30,136,255,0.45);
}

.dezena-fixa-painel {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    margin: 4px;
    border: 2px solid #818cf8;
    box-shadow: 0 0 12px rgba(99,102,241,0.7);
}

.dezena-fria {
    width: 38px;
    height: 38px;
    background: #ef4444;
    margin: 4px;
    box-shadow: 0 0 8px rgba(239,68,68,0.45);
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

.jogo-box {
    background: #111821;
    border: 1px solid #2d3b4f;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 10px;
}

.jogo-titulo {
    color: #93c5fd;
    font-weight: 800;
    margin-bottom: 8px;
}

.dezena-jogo,
.dezena-acerto {
    width: 32px;
    height: 32px;
    margin: 3px;
    font-size: 12px;
}

.dezena-jogo {
    background: #16a34a;
}

.dezena-acerto {
    background: radial-gradient(
        circle at 30% 30%,
        #facc15,
        #ca8a04 65%,
        #854d0e
    );
    box-shadow: 0 0 8px rgba(234,179,8,0.6);
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

.stDownloadButton button {
    background-color: #16a34a !important;
    color: white !important;
    border-radius: 8px;
    font-weight: 800;
}

.volante-grid-geral {
    display: flex;
    flex-wrap: wrap;
    gap: 26px;
    align-items: flex-start;
}

.volante-grupo {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #0d1420;
    border: 1px solid #2d3b4f;
    border-radius: 12px;
    padding: 12px;
}

.volante-grupo-titulo {
    color: #93c5fd;
    font-weight: 800;
    margin-bottom: 8px;
    font-size: 14px;
}

.volante-wrapper {
    display: flex;
    gap: 22px;
    flex-wrap: wrap;
}

.volante-caixa {
    background: #fdf6d8;
    border: 2px solid #c9a94f;
    border-radius: 10px;
    padding: 16px;
    max-width: 260px;
}

.volante-titulo {
    color: #5c4a1a;
    font-weight: 900;
    margin-bottom: 10px;
    text-align: center;
    font-size: 13px;
}

.volante-linha {
    display: flex;
    gap: 6px;
    margin-bottom: 6px;
    justify-content: center;
}

.volante-cel,
.volante-cel-marcada {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 12px;
}

.volante-cel {
    background: #fffbe8;
    border: 2px solid #c9a94f;
    color: #5c4a1a;
}

.volante-cel-marcada {
    background: radial-gradient(
        circle at 30% 30%,
        #5cff75,
        #16a34a 65%,
        #0f7a35
    );
    border: 2px solid #0f7a35;
    color: white;
    box-shadow: 0 0 8px rgba(34,197,94,0.55);
}
</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# CONSTANTES
# ============================================================

BASE_URL = (
    "https://servicebus2.caixa.gov.br/"
    "portaldeloterias/api/lotofacil"
)

UNIVERSO = [
    str(numero).zfill(2)
    for numero in range(1, 26)
]


# ============================================================
# FUNÇÕES DE API
# ============================================================

@st.cache_data(ttl=600)
def buscar_concurso(numero=None):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*"
    }

    url = BASE_URL

    if numero is not None:
        url = f"{BASE_URL}/{int(numero)}"

    resposta = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    resposta.raise_for_status()

    dados = resposta.json()

    dezenas = dados.get("listaDezenas", [])
    dezenas = [
        str(dezena).zfill(2)
        for dezena in dezenas
    ]

    return {
        "numero": dados.get("numero"),
        "data": dados.get("dataApuracao"),
        "dezenas": dezenas,
        "municipio": (
            dados.get("nomeMunicipioUFSorteio")
            or dados.get("nomeMunicipioSorteio")
            or ""
        ),
        "local": dados.get("localSorteio") or "",
        "raw": dados
    }


@st.cache_data(ttl=600)
def carregar_concursos(quantidade):
    ultimo = buscar_concurso()

    if not ultimo.get("numero"):
        return []

    ultimo_numero = int(ultimo["numero"])
    concursos = []

    for numero in range(
        ultimo_numero,
        ultimo_numero - int(quantidade),
        -1
    ):
        try:
            concurso = buscar_concurso(numero)

            if len(concurso["dezenas"]) == 15:
                concursos.append(concurso)

        except Exception:
            continue

    return concursos


# ============================================================
# FUNÇÕES ESTATÍSTICAS
# ============================================================

def analisar_concursos(concursos):
    todas = []

    for concurso in concursos:
        todas.extend(concurso["dezenas"])

    contador = Counter(todas)

    tabela = pd.DataFrame({
        "dezena": UNIVERSO,
        "frequencia": [
            contador.get(dezena, 0)
            for dezena in UNIVERSO
        ]
    })

    return tabela.sort_values(
        ["frequencia", "dezena"],
        ascending=[False, True]
    ).reset_index(drop=True)


def calcular_atrasos(concursos):
    atrasos = {}

    for dezena in UNIVERSO:
        atraso = 0

        for concurso in concursos:
            if dezena in concurso["dezenas"]:
                break

            atraso += 1

        atrasos[dezena] = atraso

    tabela = pd.DataFrame({
        "dezena": list(atrasos.keys()),
        "atraso": list(atrasos.values())
    })

    return tabela.sort_values(
        ["atraso", "dezena"],
        ascending=[False, True]
    ).reset_index(drop=True)


def estatisticas_jogo(jogo, ultimo_resultado):
    numeros = [int(dezena) for dezena in jogo]

    pares = sum(
        numero % 2 == 0
        for numero in numeros
    )

    repetidas = len(
        set(jogo).intersection(set(ultimo_resultado))
    )

    return {
        "pares": pares,
        "impares": 15 - pares,
        "soma": sum(numeros),
        "repetidas_ultimo": repetidas
    }


def pontuar_jogo(jogo, mapa_frequencia, mapa_atraso):
    pontos_frequencia = sum(
        mapa_frequencia.get(dezena, 0)
        for dezena in jogo
    )

    pontos_atraso = sum(
        mapa_atraso.get(dezena, 0)
        for dezena in jogo
    )

    return pontos_frequencia + pontos_atraso * 0.25


# ============================================================
# GERAÇÃO DOS JOGOS
# ============================================================

def gerar_desdobramento(
    base_variavel,
    fixas,
    quantidade_jogos,
    ultimo_resultado,
    mapa_frequencia,
    mapa_atraso,
    pares_min,
    pares_max,
    soma_min,
    soma_max,
    repetidas_min,
    repetidas_max,
    sobreposicao_max
):
    fixas = sorted(
        set(fixas),
        key=int
    )

    base_variavel = sorted(
        set(base_variavel) - set(fixas),
        key=int
    )

    vagas = 15 - len(fixas)

    if vagas <= 0:
        return []

    if len(base_variavel) < vagas:
        return []

    jogos_validos = []

    for combinacao in itertools.combinations(
        base_variavel,
        vagas
    ):
        jogo = sorted(
            fixas + list(combinacao),
            key=int
        )

        estatisticas = estatisticas_jogo(
            jogo,
            ultimo_resultado
        )

        if not (
            pares_min
            <= estatisticas["pares"]
            <= pares_max
        ):
            continue

        if not (
            soma_min
            <= estatisticas["soma"]
            <= soma_max
        ):
            continue

        if not (
            repetidas_min
            <= estatisticas["repetidas_ultimo"]
            <= repetidas_max
        ):
            continue

        score = pontuar_jogo(
            jogo,
            mapa_frequencia,
            mapa_atraso
        )

        jogos_validos.append({
            "jogo": jogo,
            "score": score,
            "pares": estatisticas["pares"],
            "impares": estatisticas["impares"],
            "soma": estatisticas["soma"],
            "repetidas_ultimo": (
                estatisticas["repetidas_ultimo"]
            )
        })

    jogos_validos.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    selecionados = []

    for candidato in jogos_validos:
        conjunto_atual = set(candidato["jogo"])
        aprovado = True

        for selecionado in selecionados:
            intersecao = len(
                conjunto_atual.intersection(
                    set(selecionado["jogo"])
                )
            )

            if intersecao > sobreposicao_max:
                aprovado = False
                break

        if aprovado:
            selecionados.append(candidato)

        if len(selecionados) >= quantidade_jogos:
            break

    # Completa a quantidade se o filtro de sobreposição for rígido
    if len(selecionados) < quantidade_jogos:
        for candidato in jogos_validos:
            if candidato not in selecionados:
                selecionados.append(candidato)

            if len(selecionados) >= quantidade_jogos:
                break

    return selecionados[:quantidade_jogos]


def jogos_para_csv(jogos):
    linhas = []

    for numero, item in enumerate(jogos, start=1):
        linha = {
            "Jogo": numero,
            "Dezenas": " ".join(item["jogo"]),
            "Pares": item["pares"],
            "Ímpares": item["impares"],
            "Soma": item["soma"],
            "Repetidas do último": (
                item["repetidas_ultimo"]
            ),
            "Score": round(item["score"], 2)
        }

        for posicao, dezena in enumerate(
            item["jogo"],
            start=1
        ):
            linha[f"D{posicao:02d}"] = dezena

        linhas.append(linha)

    return pd.DataFrame(linhas).to_csv(
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )


# ============================================================
# FUNÇÕES DO VOLANTE
# ============================================================

def numero_da_celula(linha, coluna):
    """
    O volante é organizado assim:

    21 16 11 06 01
    22 17 12 07 02
    23 18 13 08 03
    24 19 14 09 04
    25 20 15 10 05
    """
    return (4 - coluna) * 5 + (linha + 1)


def renderizar_volante_visual(jogo, titulo):
    jogo_set = set(jogo or [])
    linhas = ""

    for linha in range(5):
        celulas = ""

        for coluna in range(5):
            numero = numero_da_celula(
                linha,
                coluna
            )

            numero_texto = str(numero).zfill(2)

            classe = (
                "volante-cel-marcada"
                if numero_texto in jogo_set
                else "volante-cel"
            )

            celulas += (
                f'<div class="{classe}">'
                f'{numero_texto}'
                f'</div>'
            )

        linhas += (
            '<div class="volante-linha">'
            f'{celulas}'
            '</div>'
        )

    return (
        '<div class="volante-caixa">'
        f'<div class="volante-titulo">{titulo}</div>'
        f'{linhas}'
        '</div>'
    )


def calcular_posicoes_mm(x0, y0, dx, dy):
    posicoes = {}

    for coluna in range(5):
        for linha in range(5):
            numero = numero_da_celula(
                linha,
                coluna
            )

            posicoes[str(numero).zfill(2)] = (
                round(x0 + coluna * dx, 2),
                round(y0 + linha * dy, 2)
            )

    return posicoes


def montar_paginas_volante(jogos):
    paginas = []

    for inicio in range(0, len(jogos), 2):
        jogo1 = jogos[inicio]

        jogo2 = None

        if inicio + 1 < len(jogos):
            jogo2 = jogos[inicio + 1]

        paginas.append({
            "rotulo1": f"Jogo {inicio + 1}",
            "jogo1": jogo1["jogo"],
            "rotulo2": (
                f"Jogo {inicio + 2}"
                if jogo2
                else None
            ),
            "jogo2": (
                jogo2["jogo"]
                if jogo2
                else None
            )
        })

    return paginas


def gerar_html_impressao(paginas, calib):
    x1 = float(calib["x1"])
    y1 = float(calib["y1"])
    x2 = float(calib["x2"])
    y2 = float(calib["y2"])
    dx = float(calib["dx"])
    dy = float(calib["dy"])
    raio = float(calib["raio"])

    diametro = raio * 2
    margem_pagina = 10.0
    margem_bloco = 12.0

    esquerda = min(x1, x2) - margem_bloco
    topo = min(y1, y2) - margem_bloco

    direita = (
        max(x1, x2)
        + dx * 4
        + margem_bloco
    )

    base = (
        max(y1, y2)
        + dy * 4
        + margem_bloco
    )

    largura_bloco = direita - esquerda
    altura_bloco = base - topo

    largura_util = 210 - 2 * margem_pagina
    altura_util = 297 - 2 * margem_pagina

    colunas = max(
        1,
        int(largura_util // largura_bloco)
    )

    linhas = max(
        1,
        int(altura_util // altura_bloco)
    )

    por_folha = colunas * linhas

    rel_x1 = x1 - esquerda
    rel_y1 = y1 - topo
    rel_x2 = x2 - esquerda
    rel_y2 = y2 - topo

    total_folhas = max(
        1,
        math.ceil(len(paginas) / por_folha)
    )

    def marca_svg(x, y):
        return (
            '<svg class="marca" '
            f'style="left:{x - raio}mm;'
            f'top:{y - raio}mm;" '
            f'width="{diametro}mm" '
            f'height="{diametro}mm" '
            'viewBox="0 0 10 10">'
            '<circle cx="5" cy="5" r="5" '
            'fill="#000000"/>'
            '</svg>'
        )

    def guia(x, y, numero):
        return (
            '<div class="guia" '
            f'style="left:{x}mm;top:{y}mm;">'
            f'{numero}'
            '</div>'
        )

    folhas = ""

    for folha_numero in range(total_folhas):
        blocos = ""

        inicio = folha_numero * por_folha
        fim = min(
            inicio + por_folha,
            len(paginas)
        )

        for posicao, indice in enumerate(
            range(inicio, fim)
        ):
            pagina = paginas[indice]

            linha = posicao // colunas
            coluna = posicao % colunas

            origem_x = (
                margem_pagina
                + coluna * largura_bloco
            )

            origem_y = (
                margem_pagina
                + linha * altura_bloco
            )

            posicoes1 = calcular_posicoes_mm(
                origem_x + rel_x1,
                origem_y + rel_y1,
                dx,
                dy
            )

            posicoes2 = calcular_posicoes_mm(
                origem_x + rel_x2,
                origem_y + rel_y2,
                dx,
                dy
            )

            jogo1 = set(pagina["jogo1"] or [])
            jogo2 = set(pagina["jogo2"] or [])

            guias = ""
            marcas = ""

            for numero, coordenadas in posicoes1.items():
                x, y = coordenadas
                guias += guia(x, y, numero)

                if numero in jogo1:
                    marcas += marca_svg(x, y)

            for numero, coordenadas in posicoes2.items():
                x, y = coordenadas
                guias += guia(x, y, numero)

                if numero in jogo2:
                    marcas += marca_svg(x, y)

            rotulo = pagina["rotulo1"]

            if pagina["rotulo2"]:
                rotulo += f" e {pagina['rotulo2']}"

            blocos += (
                '<div class="rotulo no-print" '
                f'style="left:{origem_x}mm;'
                f'top:{origem_y - 6}mm;">'
                f'Volante {indice + 1} — {rotulo}'
                '</div>'
                f'{guias}'
                f'{marcas}'
            )

        quebra = (
            "always"
            if folha_numero < total_folhas - 1
            else "auto"
        )

        folhas += (
            '<div class="folha" '
            f'style="page-break-after:{quebra};">'
            f'{blocos}'
            '</div>'
        )

    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Volantes Lotofácil</title>

<style>
@page {{
    size: A4;
    margin: 0;
}}

html, body {{
    margin: 0;
    padding: 0;
    width: 210mm;
    background: white;
}}

.folha {{
    position: relative;
    width: 210mm;
    height: 297mm;
    background: white;
}}

.marca {{
    position: absolute;
}}

.guia {{
    position: absolute;
    width: 2mm;
    height: 2mm;
    font-size: 2mm;
    color: #bbbbbb;
    border: 0.15mm dashed #cccccc;
    border-radius: 50%;
    text-align: center;
    transform: translate(-50%, -50%);
}}

.rotulo {{
    position: absolute;
    color: #999999;
    font-size: 10px;
    font-family: Arial, sans-serif;
}}

.barra {{
    position: fixed;
    top: 8px;
    left: 8px;
    right: 8px;
    z-index: 10;
    background: #111827;
    padding: 10px;
    color: white;
    font-family: Arial, sans-serif;
    border-radius: 8px;
}}

.barra button {{
    padding: 8px 16px;
    font-weight: bold;
    cursor: pointer;
    border: none;
    border-radius: 6px;
    background: #16a34a;
    color: white;
}}

@media print {{
    .no-print,
    .barra,
    .guia {{
        display: none !important;
    }}
}}
</style>
</head>

<body>
<div class="barra no-print">
    <button onclick="window.print()">
        Imprimir agora
    </button>

    <span>
        {total_folhas} folha(s) A4 —
        {colunas}x{linhas} volante(s) por folha
    </span>
</div>

{folhas}
</body>
</html>
"""


# ============================================================
# CABEÇALHO E ÚLTIMO CONCURSO
# ============================================================

st.markdown("# 🍀 Lotofácil | Análises e Desdobramentos")

st.markdown(
    '<div class="subtitulo">'
    'Painel estatístico com base nos concursos analisados'
    '</div>',
    unsafe_allow_html=True
)

try:
    ultimo_concurso = buscar_concurso()

except Exception as erro:
    st.error(
        "Não foi possível carregar o último concurso "
        f"da Caixa: {erro}"
    )
    st.stop()

numero_ultimo = ultimo_concurso["numero"]
data_ultimo = ultimo_concurso["data"]
dezenas_ultimo = ultimo_concurso["dezenas"]

local_ultimo = (
    ultimo_concurso["municipio"]
    or ultimo_concurso["local"]
    or "Local não informado"
)

html_dezenas = "".join(
    f'<span class="dezena-resultado">{dezena}</span>'
    for dezena in dezenas_ultimo
)

st.markdown(
    f"""
<div class="ultimo-sorteio">
    <div class="ultimo-label">
        🍀 Último sorteio carregado da Caixa
    </div>

    <div class="ultimo-concurso">
        Concurso {numero_ultimo} — {data_ultimo}
    </div>

    <div class="ultimo-local">
        Sorteio realizado em:
        <strong>{local_ultimo}</strong>
    </div>

    <div class="dezenas-resultado-container">
        {html_dezenas}
    </div>
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Configurações")

quantidade_concursos = st.sidebar.number_input(
    "Quantidade de concursos para análise",
    min_value=5,
    max_value=100,
    value=11,
    step=1
)

tamanho_base = st.sidebar.number_input(
    "Tamanho da base sugerida",
    min_value=15,
    max_value=25,
    value=20,
    step=1
)

quantidade_jogos = st.sidebar.number_input(
    "Quantidade de jogos",
    min_value=1,
    max_value=100,
    value=12,
    step=1
)

st.sidebar.divider()

dezenas_fixas = st.sidebar.multiselect(
    "Dezenas FIXAS",
    options=UNIVERSO,
    default=[],
    max_selections=9,
    help=(
        "As dezenas selecionadas aparecerão "
        "em todos os jogos."
    )
)

opcoes_descartar = [
    dezena
    for dezena in UNIVERSO
    if dezena not in dezenas_fixas
]

dezenas_descartadas = st.sidebar.multiselect(
    "Dezenas temporariamente descartadas",
    options=opcoes_descartar,
    default=[]
)

st.sidebar.info(
    f"Fixas selecionadas: {len(dezenas_fixas)}/9"
)

st.sidebar.divider()

st.sidebar.subheader("Filtros combinatórios")

pares_min = st.sidebar.slider(
    "Mínimo de pares",
    0,
    15,
    6
)

pares_max = st.sidebar.slider(
    "Máximo de pares",
    0,
    15,
    9
)

soma_min = st.sidebar.number_input(
    "Soma mínima",
    min_value=120,
    max_value=300,
    value=170,
    step=1
)

soma_max = st.sidebar.number_input(
    "Soma máxima",
    min_value=120,
    max_value=300,
    value=220,
    step=1
)

repetidas_min = st.sidebar.slider(
    "Mínimo de repetidas do último concurso",
    0,
    15,
    8
)

repetidas_max = st.sidebar.slider(
    "Máximo de repetidas do último concurso",
    0,
    15,
    11
)

sobreposicao_max = st.sidebar.slider(
    "Sobreposição máxima entre jogos",
    8,
    15,
    13
)


# ============================================================
# CARREGAMENTO DOS CONCURSOS
# ============================================================

with st.spinner("Carregando concursos da Caixa..."):
    concursos = carregar_concursos(
        quantidade_concursos
    )

if not concursos:
    st.error("Nenhum concurso foi carregado.")
    st.stop()

df_frequencia = analisar_concursos(concursos)
df_atrasos = calcular_atrasos(concursos)

mapa_frequencia = dict(
    zip(
        df_frequencia["dezena"],
        df_frequencia["frequencia"]
    )
)

mapa_atraso = dict(
    zip(
        df_atrasos["dezena"],
        df_atrasos["atraso"]
    )
)


# ============================================================
# VISÃO GERAL
# ============================================================

st.markdown(
    '<div class="section-divider"></div>',
    unsafe_allow_html=True
)

st.markdown("## 📊 Visão geral")

coluna1, coluna2 = st.columns(2)

with coluna1:
    st.markdown("### 🔥 Dezenas mais fortes")

    fortes = df_frequencia.head(10)
    html_fortes = "".join(
        f'<span class="dezena-base">{row.dezena}</span>'
        for _, row in fortes.iterrows()
    )

    st.markdown(
        html_fortes,
        unsafe_allow_html=True
    )

    st.dataframe(
        fortes.rename(
            columns={
                "dezena": "Dezena",
                "frequencia": "Frequência"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

with coluna2:
    st.markdown(
        f"### 📈 Frequência nos últimos "
        f"{len(concursos)} concursos"
    )

    grafico = df_frequencia.sort_values("dezena")

    st.bar_chart(
        grafico,
        x="dezena",
        y="frequencia",
        use_container_width=True
    )


# ============================================================
# ATRASOS
# ============================================================

st.markdown(
    '<div class="section-divider"></div>',
    unsafe_allow_html=True
)

st.markdown("## 🧊 Dezenas em atraso")

coluna1, coluna2 = st.columns(2)

with coluna1:
    atrasadas = df_atrasos.head(10)

    html_atrasadas = "".join(
        f'<span class="dezena-fria">{row.dezena}</span>'
        for _, row in atrasadas.iterrows()
    )

    st.markdown(
        html_atrasadas,
        unsafe_allow_html=True
    )

    st.dataframe(
        atrasadas.rename(
            columns={
                "dezena": "Dezena",
                "atraso": "Concursos sem sair"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

with coluna2:
    grafico_atrasos = df_atrasos.sort_values("dezena")

    st.bar_chart(
        grafico_atrasos,
        x="dezena",
        y="atraso",
        use_container_width=True
    )


# ============================================================
# BASE SUGERIDA
# ============================================================

st.markdown(
    '<div class="section-divider"></div>',
    unsafe_allow_html=True
)

st.markdown("## 🎯 Base sugerida")

df_base = df_frequencia.copy()

excluir = set(
    dezenas_fixas + dezenas_descartadas
)

df_base = df_base[
    ~df_base["dezena"].isin(excluir)
]

vagas_variaveis = (
    int(tamanho_base) - len(dezenas_fixas)
)

if vagas_variaveis < 0:
    vagas_variaveis = 0

base_variavel = df_base.head(
    vagas_variaveis
)["dezena"].tolist()

base_completa = sorted(
    set(base_variavel + dezenas_fixas),
    key=int
)

html_base = ""

for dezena in base_completa:
    classe = (
        "dezena-fixa-painel"
        if dezena in dezenas_fixas
        else "dezena-base"
    )

    html_base += (
        f'<span class="{classe}">{dezena}</span>'
    )

st.markdown(
    html_base,
    unsafe_allow_html=True
)

if dezenas_fixas:
    st.info(
        f"{len(dezenas_fixas)} dezena(s) fixa(s) "
        f"em todos os jogos. "
        f"Cada jogo terá "
        f"{15 - len(dezenas_fixas)} "
        "dezenas variáveis."
    )

if dezenas_descartadas:
    st.warning(
        "Dezenas descartadas: "
        + ", ".join(dezenas_descartadas)
    )


# ============================================================
# GERAÇÃO
# ============================================================

st.markdown(
    '<div class="section-divider"></div>',
    unsafe_allow_html=True
)

st.markdown("## 🧩 Geração de jogos")

vagas_jogo = 15 - len(dezenas_fixas)

if vagas_jogo < 1:
    st.error(
        "É necessário deixar pelo menos uma vaga "
        "para uma dezena variável."
    )

elif len(base_completa) < 15:
    st.error(
        "A base total precisa possuir pelo menos "
        "15 dezenas."
    )

elif len(base_variavel) < vagas_jogo:
    st.error(
        "Não existem dezenas variáveis suficientes "
        "para completar os jogos."
    )

else:
    quantidade_combinacoes = math.comb(
        len(base_variavel),
        vagas_jogo
    )

    st.info(
        f"A base possui {len(base_completa)} dezenas. "
        f"Serão escolhidas {vagas_jogo} dezenas variáveis "
        f"por jogo. "
        f"Combinações possíveis: "
        f"{quantidade_combinacoes:,}".replace(",", ".")
    )

    if st.button(
        "🎲 Gerar novo desdobramento",
        use_container_width=True,
        type="primary"
    ):
        with st.spinner("Gerando jogos..."):
            st.session_state["jogos_gerados"] = (
                gerar_desdobramento(
                    base_variavel=base_variavel,
                    fixas=dezenas_fixas,
                    quantidade_jogos=quantidade_jogos,
                    ultimo_resultado=dezenas_ultimo,
                    mapa_frequencia=mapa_frequencia,
                    mapa_atraso=mapa_atraso,
                    pares_min=pares_min,
                    pares_max=pares_max,
                    soma_min=soma_min,
                    soma_max=soma_max,
                    repetidas_min=repetidas_min,
                    repetidas_max=repetidas_max,
                    sobreposicao_max=sobreposicao_max
                )
            )

        if st.session_state["jogos_gerados"]:
            st.success(
                f"{len(st.session_state['jogos_gerados'])} "
                "jogos gerados com sucesso."
            )
        else:
            st.warning(
                "Nenhum jogo foi encontrado. "
                "Flexibilize os filtros."
            )


# ============================================================
# CONFERÊNCIA DOS JOGOS
# ============================================================

jogos = st.session_state["jogos_gerados"]

if jogos:
    st.markdown(
        '<div class="section-divider"></div>',
        unsafe_allow_html=True
    )

    st.markdown("## 🎟️ Conferência de acertos")

    opcoes_conferencia = {}

    for concurso in concursos:
        nome = (
            f"Concurso {concurso['numero']} "
            f"({concurso['data']})"
        )

        opcoes_conferencia[nome] = concurso["dezenas"]

    opcoes_conferencia[
        "Inserir dezenas manualmente"
    ] = []

    selecao = st.selectbox(
        "Selecione o concurso:",
        list(opcoes_conferencia.keys())
    )

    dezenas_alvo = []

    if selecao == "Inserir dezenas manualmente":
        entrada = st.text_input(
            "Digite as 15 dezenas separadas por espaço:",
            placeholder="01 02 03 04 05 ..."
        )

        if entrada:
            valores = []

            for valor in entrada.split():
                if valor.isdigit():
                    numero = int(valor)

                    if 1 <= numero <= 25:
                        valores.append(
                            str(numero).zfill(2)
                        )

            dezenas_alvo = list(
                dict.fromkeys(valores)
            )[:15]

        if dezenas_alvo and len(dezenas_alvo) != 15:
            st.warning(
                "Informe exatamente 15 dezenas válidas."
            )
            dezenas_alvo = []

    else:
        dezenas_alvo = opcoes_conferencia[selecao]

    if dezenas_alvo:
        gabarito_html = "".join(
            f'<span class="dezena-resultado">{dezena}</span>'
            for dezena in dezenas_alvo
        )

        st.markdown(
            f"""
            <div style="margin:15px 0;">
                <strong>Gabarito:</strong><br>
                {gabarito_html}
            </div>
            """,
            unsafe_allow_html=True
        )

    conferir = st.button(
        "🔍 Rodar conferência",
        use_container_width=True
    )

    acertos_por_jogo = []
    contadores = {
        11: 0,
        12: 0,
        13: 0,
        14: 0,
        15: 0
    }

    for item in jogos:
        acertos = set(item["jogo"]).intersection(
            set(dezenas_alvo)
        )

        quantidade = len(acertos)
        acertos_por_jogo.append(acertos)

        if quantidade in contadores:
            contadores[quantidade] += 1

    if conferir and dezenas_alvo:
        st.markdown("### 🏆 Painel de premiações")

        colunas = st.columns(5)

        for coluna, quantidade in zip(
            colunas,
            [11, 12, 13, 14, 15]
        ):
            coluna.markdown(
                f"""
                <div class="premio-card">
                    <div class="premio-titulo">
                        {quantidade} acertos
                    </div>
                    <div class="premio-valor">
                        {contadores[quantidade]} jogos
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("### 📋 Jogos gerados")

    for indice, item in enumerate(jogos):
        acertos = (
            acertos_por_jogo[indice]
            if conferir and dezenas_alvo
            else set()
        )

        dezenas_html = ""

        for dezena in item["jogo"]:
            classe = (
                "dezena-acerto"
                if dezena in acertos
                else "dezena-jogo"
            )

            dezenas_html += (
                f'<span class="{classe}">{dezena}</span>'
            )

        texto_acertos = ""

        if conferir and dezenas_alvo:
            texto_acertos = (
                f' | <strong style="color:#facc15;">'
                f'{len(acertos)} ACERTOS</strong>'
            )

        st.markdown(
            f"""
            <div class="jogo-box">
                <div class="jogo-titulo">
                    Jogo {indice + 1}
                </div>

                <div>
                    {dezenas_html}
                </div>

                <div style="margin-top:10px;
                            color:#cbd5e1;
                            font-size:13px;">
                    Pares: <strong>{item["pares"]}</strong> |
                    Ímpares: <strong>{item["impares"]}</strong> |
                    Soma: <strong>{item["soma"]}</strong> |
                    Repetidas do último:
                    <strong>{item["repetidas_ultimo"]}</strong> |
                    Score: <strong>
                        {round(item["score"], 2)}
                    </strong>
                    {texto_acertos}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.download_button(
        "⬇️ Baixar desdobramento em CSV",
        data=jogos_para_csv(jogos),
        file_name="desdobramento_lotofacil.csv",
        mime="text/csv"
    )


# ============================================================
# VOLANTE
# ============================================================

if jogos:
    st.markdown(
        '<div class="section-divider"></div>',
        unsafe_allow_html=True
    )

    st.markdown("## 🎫 Volante — visualizar e imprimir")

    modo = st.radio(
        "Escolha o modo:",
        [
            "Todos os jogos gerados",
            "Escolher jogos específicos"
        ],
        horizontal=True,
        key="modo_volante"
    )

    paginas = []

    if modo == "Todos os jogos gerados":
        paginas = montar_paginas_volante(jogos)

        html_volantes = (
            '<div class="volante-grid-geral">'
        )

        for indice, pagina in enumerate(paginas):
            html_volantes += (
                '<div class="volante-grupo">'
                f'<div class="volante-grupo-titulo">'
                f'Volante {indice + 1}'
                '</div>'
                '<div class="volante-wrapper">'
            )

            html_volantes += renderizar_volante_visual(
                pagina["jogo1"],
                f"Caixa 1 — {pagina['rotulo1']}"
            )

            html_volantes += renderizar_volante_visual(
                pagina["jogo2"],
                (
                    f"Caixa 2 — {pagina['rotulo2']}"
                    if pagina["jogo2"]
                    else "Caixa 2 — vazia"
                )
            )

            html_volantes += (
                '</div>'
                '</div>'
            )

        html_volantes += '</div>'

        st.markdown(
            html_volantes,
            unsafe_allow_html=True
        )

    else:
        opcoes_jogos = ["Nenhum"] + [
            f"Jogo {indice + 1}"
            for indice in range(len(jogos))
        ]

        coluna1, coluna2 = st.columns(2)

        with coluna1:
            escolha1 = st.selectbox(
                "Jogo para a Caixa 1",
                opcoes_jogos,
                index=1,
                key="volante_caixa_1"
            )

        with coluna2:
            escolha2 = st.selectbox(
                "Jogo para a Caixa 2",
                opcoes_jogos,
                index=(
                    2
                    if len(opcoes_jogos) > 2
                    else 0
                ),
                key="volante_caixa_2"
            )

        jogo1 = None
        jogo2 = None

        if escolha1 != "Nenhum":
            indice1 = int(
                escolha1.replace("Jogo ", "")
            ) - 1
            jogo1 = jogos[indice1]["jogo"]

        if escolha2 != "Nenhum":
            indice2 = int(
                escolha2.replace("Jogo ", "")
            ) - 1
            jogo2 = jogos[indice2]["jogo"]

        html_especifico = (
            '<div class="volante-wrapper">'
            + renderizar_volante_visual(
                jogo1,
                f"Caixa 1 — {escolha1}"
            )
            + renderizar_volante_visual(
                jogo2,
                f"Caixa 2 — {escolha2}"
            )
            + '</div>'
        )

        st.markdown(
            html_especifico,
            unsafe_allow_html=True
        )

        if jogo1 or jogo2:
            paginas = [{
                "rotulo1": escolha1,
                "jogo1": jogo1,
                "rotulo2": (
                    escolha2
                    if jogo2
                    else None
                ),
                "jogo2": jogo2
            }]


# ============================================================
# CALIBRAÇÃO DO VOLANTE
# ============================================================

if jogos:
    with st.expander(
        "⚙️ Calibrar posição de impressão"
    ):
        st.caption(
            "Use milímetros. Ajuste o X e o Y do primeiro "
            "número de cada caixa e depois ajuste os "
            "espaçamentos entre colunas e linhas."
        )

        calib = st.session_state["calib_volante"]

        coluna1, coluna2, coluna3 = st.columns(3)

        with coluna1:
            calib["x1"] = st.number_input(
                "Caixa 1 — X do número 21",
                value=float(calib["x1"]),
                step=0.5,
                format="%.1f",
                key="calib_x1"
            )

            calib["y1"] = st.number_input(
                "Caixa 1 — Y do número 21",
                value=float(calib["y1"]),
                step=0.5,
                format="%.1f",
                key="calib_y1"
            )

        with coluna2:
            calib["x2"] = st.number_input(
                "Caixa 2 — X do número 21",
                value=float(calib["x2"]),
                step=0.5,
                format="%.1f",
                key="calib_x2"
            )

            calib["y2"] = st.number_input(
                "Caixa 2 — Y do número 21",
                value=float(calib["y2"]),
                step=0.5,
                format="%.1f",
                key="calib_y2"
            )

        with coluna3:
            calib["dx"] = st.number_input(
                "Espaçamento das colunas",
                value=float(calib["dx"]),
                step=0.1,
                format="%.1f",
                key="calib_dx"
            )

            calib["dy"] = st.number_input(
                "Espaçamento das linhas",
                value=float(calib["dy"]),
                step=0.1,
                format="%.1f",
                key="calib_dy"
            )

        calib["raio"] = st.slider(
            "Raio da marca",
            min_value=1.0,
            max_value=4.0,
            value=float(calib["raio"]),
            step=0.1,
            key="calib_raio"
        )

        st.session_state["calib_volante"] = calib


# ============================================================
# IMPRESSÃO
# ============================================================

if jogos and paginas:
    html_impressao = gerar_html_impressao(
        paginas,
        st.session_state["calib_volante"]
    )

    st.markdown("### 🖨️ Impressão")

    st.warning(
        "Na tela de impressão, deixe a escala em 100% "
        "e desative a opção 'ajustar à página'."
    )

    conteudo = json.dumps(html_impressao)

    html_botao = f"""
    <div>
        <button id="abrir-impressao"
            style="
                padding:12px 20px;
                font-weight:800;
                font-size:15px;
                cursor:pointer;
                border:none;
                border-radius:8px;
                background:#16a34a;
                color:white;
            ">
            🖨️ Abrir para imprimir
        </button>
    </div>

    <script>
        const conteudo = {conteudo};
        const botao = document.getElementById(
            "abrir-impressao"
        );

        botao.addEventListener("click", function() {{
            const blob = new Blob(
                [conteudo],
                {{ type: "text/html" }}
            );

            const url = URL.createObjectURL(blob);
            const janela = window.open(url, "_blank");

            if (!janela) {{
                botao.innerText =
                    "⚠️ Permita pop-ups no navegador";
            }}
        }});
    </script>
    """

    components.html(
        html_botao,
        height=70
    )

    st.download_button(
        "⬇️ Baixar página de impressão em HTML",
        data=html_impressao,
        file_name="volante_impressao.html",
        mime="text/html"
    )


# ============================================================
# LEITURA COMBINATÓRIA
# ============================================================

st.markdown(
    '<div class="section-divider"></div>',
    unsafe_allow_html=True
)

st.markdown("## 🧠 Leitura combinatória")

coluna1, coluna2, coluna3 = st.columns(3)

with coluna1:
    st.markdown("### Distribuição par/ímpar")

    if jogos:
        tabela = pd.DataFrame(jogos)

        st.dataframe(
            tabela[
                [
                    "pares",
                    "impares",
                    "soma",
                    "repetidas_ultimo"
                ]
            ].rename(
                columns={
                    "pares": "Pares",
                    "impares": "Ímpares",
                    "soma": "Soma",
                    "repetidas_ultimo": (
                        "Repetidas do último"
                    )
                }
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.caption("Gere os jogos para visualizar.")

with coluna2:
    st.markdown("### Repetição do último concurso")

    if jogos:
        repeticoes = pd.DataFrame({
            "Jogo": [
                f"Jogo {i + 1}"
                for i in range(len(jogos))
            ],
            "Repetidas": [
                item["repetidas_ultimo"]
                for item in jogos
            ]
        })

        st.bar_chart(
            repeticoes,
            x="Jogo",
            y="Repetidas",
            use_container_width=True
        )
    else:
        st.caption("Gere os jogos para visualizar.")

with coluna3:
    st.markdown("### Faixa de soma")

    if jogos:
        somas = [
            item["soma"]
            for item in jogos
        ]

        st.metric("Menor soma", min(somas))
        st.metric("Maior soma", max(somas))
        st.metric(
            "Média",
            round(sum(somas) / len(somas), 2)
        )
    else:
        st.caption("Gere os jogos para visualizar.")


# ============================================================
# HISTÓRICO
# ============================================================

st.markdown(
    '<div class="section-divider"></div>',
    unsafe_allow_html=True
)

with st.expander("📚 Ver concursos analisados"):
    historico = []

    for concurso in concursos:
        historico.append({
            "Concurso": concurso["numero"],
            "Data": concurso["data"],
            "Dezenas": " ".join(
                concurso["dezenas"]
            )
        })

    st.dataframe(
        pd.DataFrame(historico),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# RESUMO
# ============================================================

st.markdown(
    '<div class="section-divider"></div>',
    unsafe_allow_html=True
)

st.markdown("## 📌 Resumo do painel")

st.markdown(
    """
    <div class="info-box">
        Este painel reúne frequência das dezenas, análise de
        atrasos, seleção de base, dezenas fixas, descartes,
        geração de jogos, conferência de acertos, exportação
        para CSV e impressão dos volantes.
        <br><br>
        A análise é estatística e não garante premiação.
    </div>
    """,
    unsafe_allow_html=True
)

coluna1, coluna2, coluna3, coluna4 = st.columns(4)

with coluna1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                Concursos analisados
            </div>
            <div class="metric-value">
                {len(concursos)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with coluna2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                Combinações da Lotofácil
            </div>
            <div class="metric-value">
                {math.comb(25, 15):,}
            </div>
        </div>
        """.replace(",", "."),
        unsafe_allow_html=True
    )

with coluna3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                Tamanho da base
            </div>
            <div class="metric-value">
                {len(base_completa)} dezenas
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with coluna4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                Jogos gerados
            </div>
            <div class="metric-value">
                {len(jogos)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    """
    <br>
    <div style="
        color:#94a3b8;
        font-size:13px;
        text-align:center;
    ">
        Análise estatística e combinatória.
        Este painel não garante premiação.
    </div>
    """,
    unsafe_allow_html=True
)
