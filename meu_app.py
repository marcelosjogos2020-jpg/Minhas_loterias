import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import itertools
import math
import base64
from collections import Counter
from datetime import datetime

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

# Calibração da posição de impressão do volante (em milímetros)
# Esses valores representam o CENTRO do número 21 (canto sup. esquerdo)
# de cada caixa do volante físico já colado na folha A4.
if "calib_volante" not in st.session_state:
    st.session_state["calib_volante"] = {
        "x1": 25.0,   # Caixa 1 - posição X do número 21
        "y1": 42.0,   # Caixa 1 - posição Y do número 21
        "x2": 25.0,   # Caixa 2 - posição X do número 21
        "y2": 150.0,  # Caixa 2 - posição Y do número 21
        "dx": 12.5,   # espaçamento horizontal entre colunas
        "dy": 8.0,    # espaçamento vertical entre linhas
        "raio": 2.2   # raio da marca impressa
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

    .ultimo-local strong {
        color: #ffffff;
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
        box-shadow:
            0 0 10px rgba(34,197,94,0.45),
            inset 0 2px 5px rgba(255,255,255,0.25),
            inset 0 -4px 8px rgba(0,0,0,0.22);
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

    /* Estilo para destacar as dezenas fixas na base */
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

    .dezena-jogo {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #16a34a;
        color: white;
        font-weight: 800;
        margin: 3px;
        font-size: 12px;
    }

    .dezena-acerto {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #facc15, #ca8a04 65%, #854d0e);
        color: white;
        font-weight: 800;
        margin: 3px;
        font-size: 12px;
        box-shadow: 0 0 8px rgba(234, 179, 8, 0.6);
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

    /* ---------- VOLANTE VISUAL (pré-visualização na tela) ---------- */
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

    .volante-cel {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: #fffbe8;
        border: 2px solid #c9a94f;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 12px;
        color: #5c4a1a;
    }

    .volante-cel-marcada {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #5cff75, #16a34a 65%, #0f7a35);
        border: 2px solid #0f7a35;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 12px;
        color: white;
        box-shadow: 0 0 8px rgba(34,197,94,0.55);
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

    if numero is None:
        url = BASE_URL
    else:
        url = f"{BASE_URL}/{numero}"

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    dados = response.json()

    dezenas = dados.get("listaDezenas", [])
    dezenas = [str(d).zfill(2) for d in dezenas]

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

    df_freq = df_freq.sort_values(
        by=["frequencia", "dezena"],
        ascending=[False, True]
    ).reset_index(drop=True)

    return df_freq


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

    df_atrasos = df_atrasos.sort_values(
        by=["atraso", "dezena"],
        ascending=[False, True]
    ).reset_index(drop=True)

    return df_atrasos


def staticas_jogo(jogo, ultimo_resultado):
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


# 🚀 Motor de combinação adaptado para injetar dezenas fixas de forma limpa e performática
def gerar_desdobramento_com_fixos(
    base_variavel,
    fixos,
    qtd_jogos,
    ultimo_resultado,
    mapa_freq,
    mapa_atraso,
    pares_min,
    pares_max,
    soma_min,
    soma_max,
    repetidas_min,
    repetidas_max,
    sobreposicao_max
):
    vagas_restantes = 15 - len(fixos)
    combinacoes_variaveis = list(itertools.combinations(base_variavel, vagas_restantes))

    jogos_validos = []

    for combo in combinacoes_variaveis:
        jogo = sorted(list(fixos) + list(combo), key=lambda x: int(x))
        stats = staticas_jogo(jogo, ultimo_resultado)

        if not (pares_min <= stats["pares"] <= pares_max):
            continue

        if not (soma_min <= stats["soma"] <= soma_max):
            continue

        if not (repetidas_min <= stats["repetidas_ultimo"] <= repetidas_max):
            continue

        pontos = pontuar_jogo(jogo, mapa_freq, mapa_atraso)

        jogos_validos.append({
            "jogo": jogo,
            "score": pontos,
            "pares": stats["pares"],
            "impares": stats["impares"],
            "soma": stats["soma"],
            "repetidas_ultimo": stats["repetidas_ultimo"]
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
                intersecao = len(jogo_atual.intersection(set(selecionado["jogo"])))

                if intersecao > sobreposicao_max:
                    aprovado = False
                    break

            if aprovado:
                selecionados.append(item)

        if len(selecionados) >= qtd_jogos:
            break

    if len(selecionados) < qtd_jogos:
        for item in jogos_validos:
            if item not in selecionados:
                selecionados.append(item)

            if len(selecionados) >= qtd_jogos:
                break

    return selecionados[:qtd_jogos]


def jogos_para_csv(jogos):
    linhas = []

    for idx, item in enumerate(jogos, start=1):
        linha = {
            "Jogo": idx,
            "Dezenas": " ".join(item["jogo"]),
            "Pares": item["pares"],
            "Ímpares": item["impares"],
            "Soma": item["soma"],
            "Repetidas do último": item["repetidas_ultimo"],
            "Score": round(item["score"], 2)
        }

        for pos, dezena in enumerate(item["jogo"], start=1):
            linha[f"D{pos:02d}"] = dezena

        linhas.append(linha)

    return pd.DataFrame(linhas).to_csv(index=False, sep=";", encoding="utf-8-sig")


# ============================================================
# FUNÇÕES DO VOLANTE (visual em tela + impressão A4 só com as marcas)
# ============================================================

def numero_da_celula(linha, coluna):
    """
    Reproduz a disposição oficial do volante da Lotofácil:
    coluna 0 (esquerda) = 21..25 | coluna 4 (direita) = 01..05
    """
    return (4 - coluna) * 5 + (linha + 1)


def renderizar_volante_visual(jogo, titulo):
    """Gera o HTML de um volante (grade 5x5) com os números do jogo pintados."""
    jogo_set = set(jogo) if jogo else set()

    linhas_html = ""
    for r in range(5):
        celulas_html = ""
        for c in range(5):
            numero = numero_da_celula(r, c)
            num_str = str(numero).zfill(2)
            marcado = num_str in jogo_set
            classe = "volante-cel-marcada" if marcado else "volante-cel"
            celulas_html += f'<div class="{classe}">{num_str}</div>'
        linhas_html += f'<div class="volante-linha">{celulas_html}</div>'

    html = (
        f'<div class="volante-caixa">'
        f'<div class="volante-titulo">{titulo}</div>'
        f'<div>{linhas_html}</div>'
        f'</div>'
    )
    return html


def calcular_posicoes_mm(x0, y0, dx, dy):
    """Retorna {dezena: (x_mm, y_mm)} para uma das duas caixas do volante."""
    posicoes = {}
    for c in range(5):
        for r in range(5):
            numero = numero_da_celula(r, c)
            x = x0 + c * dx
            y = y0 + r * dy
            posicoes[str(numero).zfill(2)] = (round(x, 2), round(y, 2))
    return posicoes


def montar_paginas_volante(jogos):
    """
    Agrupa a lista de jogos em pares (Caixa 1 / Caixa 2), reproduzindo o
    padrão oficial do volante físico da Lotofácil (2 caixas por folha).
    Retorna uma lista de dicts: {"rotulo1", "jogo1", "rotulo2", "jogo2"}.
    """
    paginas = []
    total = len(jogos)
    i = 0
    numero_jogo = 1
    while i < total:
        jogo1 = jogos[i]["jogo"]
        rotulo1 = f"Jogo {numero_jogo}"
        jogo2 = None
        rotulo2 = None
        if i + 1 < total:
            jogo2 = jogos[i + 1]["jogo"]
            rotulo2 = f"Jogo {numero_jogo + 1}"
        paginas.append({
            "rotulo1": rotulo1, "jogo1": jogo1,
            "rotulo2": rotulo2, "jogo2": jogo2
        })
        i += 2
        numero_jogo += 2
    return paginas


def gerar_html_impressao_volante(paginas, calib):
    """
    Monta um HTML A4 contendo APENAS as marcas dos jogos (sem nenhum desenho
    do volante), para imprimir por cima do(s) volante(s) físico(s) já
    colado(s) na folha A4. Os volantes são organizados lado a lado
    (horizontal), o máximo que couber por folha, antes de pular para a
    próxima página.

    As marcas são desenhadas como SVG (círculo preenchido), não como
    background CSS — isso evita que a impressão saia em branco quando a
    opção "Gráficos de segundo plano" do navegador está desligada.
    """
    x1, y1 = calib["x1"], calib["y1"]
    x2, y2 = calib["x2"], calib["y2"]
    dx, dy = calib["dx"], calib["dy"]
    raio = calib["raio"]
    diametro = raio * 2

    margem_pagina = 10.0   # mm de margem externa da folha
    margem_bloco = 12.0    # mm de respiro ao redor de cada volante

    # Caixa delimitadora (bounding box) de UM volante (caixa1 + caixa2 juntas)
    esquerda = min(x1, x2) - margem_bloco
    topo = min(y1, y2) - margem_bloco
    direita = max(x1, x2) + dx * 4 + margem_bloco
    base = max(y1, y2) + dy * 4 + margem_bloco

    largura_bloco = direita - esquerda
    altura_bloco = base - topo

    largura_util = 210 - (2 * margem_pagina)
    altura_util = 297 - (2 * margem_pagina)

    colunas = max(1, int(largura_util // largura_bloco))
    linhas = max(1, int(altura_util // altura_bloco))
    por_pagina = colunas * linhas

    # Posição de cada caixa relativa ao canto superior-esquerdo do próprio bloco
    rel_x1, rel_y1 = x1 - esquerda, y1 - topo
    rel_x2, rel_y2 = x2 - esquerda, y2 - topo

    total_paginas_fisicas = math.ceil(len(paginas) / por_pagina)

    def svg_marca(x, y):
        return (
            f'<svg class="marca" style="left:{x - raio}mm; top:{y - raio}mm;" '
            f'width="{diametro}mm" height="{diametro}mm" viewBox="0 0 10 10">'
            f'<circle cx="5" cy="5" r="5" fill="#000000"/></svg>'
        )

    def guia_ponto(x, y, num):
        return f'<div class="guia" style="left:{x}mm; top:{y}mm;">{num}</div>'

    folhas_html = ""

    for pagina_idx in range(total_paginas_fisicas):
        blocos_html = ""
        inicio = pagina_idx * por_pagina
        fim = min(inicio + por_pagina, len(paginas))

        for pos, idx_volante in enumerate(range(inicio, fim)):
            pagina = paginas[idx_volante]
            linha = pos // colunas
            coluna = pos % colunas

            origem_x = margem_pagina + coluna * largura_bloco
            origem_y = margem_pagina + linha * altura_bloco

            fx1, fy1 = origem_x + rel_x1, origem_y + rel_y1
            fx2, fy2 = origem_x + rel_x2, origem_y + rel_y2

            pos1 = calcular_posicoes_mm(fx1, fy1, dx, dy)
            pos2 = calcular_posicoes_mm(fx2, fy2, dx, dy)

            jogo1_set = set(pagina["jogo1"]) if pagina["jogo1"] else set()
            jogo2_set = set(pagina["jogo2"]) if pagina["jogo2"] else set()

            marcas_html = ""
            guia_html = ""

            for num, (x, y) in pos1.items():
                guia_html += guia_ponto(x, y, num)
                if num in jogo1_set:
                    marcas_html += svg_marca(x, y)

            for num, (x, y) in pos2.items():
                guia_html += guia_ponto(x, y, num)
                if num in jogo2_set:
                    marcas_html += svg_marca(x, y)

            rotulo = pagina["rotulo1"]
            if pagina["rotulo2"]:
                rotulo += f" e {pagina['rotulo2']}"

            blocos_html += (
                f'<div class="no-print rotulo-folha" '
                f'style="left:{origem_x}mm; top:{origem_y - 6}mm;">'
                f'Volante {idx_volante + 1} — {rotulo}</div>'
                f'{guia_html}{marcas_html}'
            )

        quebra = "always" if pagina_idx < total_paginas_fisicas - 1 else "auto"
        folhas_html += f'<div class="folha" style="page-break-after:{quebra};">{blocos_html}</div>'

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Volante para impressão</title>
<style>
    @page {{ size: A4; margin: 0; }}
    html, body {{
        margin: 0;
        padding: 0;
        width: 210mm;
        background: white;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
        color-adjust: exact;
    }}
    .folha {{
        position: relative;
        width: 210mm;
        height: 297mm;
        background: white;
    }}
    .rotulo-folha {{
        position: absolute;
        font-size: 10px;
        color: #999;
        font-family: sans-serif;
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
    .barra-topo {{
        position: fixed;
        top: 8px;
        left: 8px;
        right: 8px;
        z-index: 10;
        background: #111827;
        padding: 10px 14px;
        border-radius: 8px;
        font-family: sans-serif;
        color: white;
    }}
    .barra-topo button {{
        padding: 8px 16px;
        font-weight: bold;
        cursor: pointer;
        border: none;
        border-radius: 6px;
        background: #16a34a;
        color: white;
        margin-right: 8px;
    }}
    @media print {{
        .no-print {{ display: none !important; }}
        .guia {{ display: none !important; }}
    }}
</style>
</head>
<body>
    <div class="barra-topo no-print">
        <button onclick="window.print()">🖨️ Imprimir agora ({total_paginas_fisicas} folha(s) A4 · {colunas}x{linhas} volante(s) por folha)</button>
        <span>Confira o alinhamento. As linhas pontilhadas e os rótulos somem na impressão.</span>
    </div>
    {folhas_html}
</body>
</html>"""
    return html


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown("# 🍀 Lotofácil | Análises e Desdobramentos")
st.markdown(
    '<div class="subtitulo">Painel estatístico com base nos últimos concursos analisados</div>',
    unsafe_allow_html=True
)

# ============================================================
# ÚLTIMO SORTEIO NO TOPO
# ============================================================

try:
    ultimo_concurso = buscar_concurso()
except Exception as erro:
    st.error("Não foi possível carregar o último concurso automaticamente da Caixa.")
    st.stop()

numero_ultimo = ultimo_concurso["numero"]
data_ultimo = ultimo_concurso["data"]
dezenas_ultimo = ultimo_concurso["dezenas"]

municipio_sorteio = ultimo_concurso["municipio"]
local_sorteio = ultimo_concurso["local"]

if municipio_sorteio:
    texto_local = municipio_sorteio
elif local_sorteio:
    texto_local = local_sorteio
else:
    texto_local = "Local não informado"

html_dezenas_resultado = "".join(
    [f'<span class="dezena-resultado">{dezena}</span>' for dezena in dezenas_ultimo]
)

html_ultimo_sorteio = (
    f'<div class="ultimo-sorteio">'
    f'<div class="ultimo-label">🍀 Último sorteio carregado automaticamente da Caixa</div>'
    f'<div class="ultimo-concurso">Concurso {numero_ultimo} — {data_ultimo}</div>'
    f'<div class="ultimo-local">Sorteio realizado em: <strong>{texto_local}</strong></div>'
    f'<div class="dezenas-resultado-container">{html_dezenas_resultado}</div>'
    f'</div>'
)

st.markdown(html_ultimo_sorteio, unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Configurações")

qtd_concursos = st.sidebar.number_input(
    "Quantidade de concursos para análise",
    min_value=5,
    max_value=100,
    value=11,
    step=1
)

tamanho_base = st.sidebar.number_input(
    "Tamanho da base sugerida (Total de números jogados)",
    min_value=15,
    max_value=25,
    value=20,
    step=1
)

qtd_jogos = st.sidebar.number_input(
    "Quantidade de jogos no desdobramento",
    min_value=1,
    max_value=100,
    value=12,
    step=1
)

st.sidebar.divider()

# 🚀 Seletor de 1 a 5 números fixos travados em todos os bilhetes.
# Cada dezena fixa ocupa 1 vaga do "tamanho_base", então o pool de
# números variáveis diminui automaticamente conforme você trava mais fixos.
dezenas_fixas = st.sidebar.multiselect(
    "Dezenas FIXAS (Presentes em todos os bilhetes - Máx 5)",
    options=[str(i).zfill(2) for i in range(1, 25 + 1)],
    default=[],
    max_selections=5
)

dezenas_para_descartar = st.sidebar.multiselect(
    "Dezenas temporariamente descartadas",
    options=[str(i).zfill(2) for i in range(1, 26) if str(i).zfill(2) not in dezenas_fixas],
    default=[]
)

st.sidebar.divider()

st.sidebar.subheader("Filtros combinatórios")

pares_min = st.sidebar.slider("Mínimo de pares", min_value=0, max_value=15, value=6)
pares_max = st.sidebar.slider("Máximo de pares", min_value=0, max_value=15, value=9)

soma_min = st.sidebar.number_input("Soma mínima", min_value=120, max_value=300, value=170, step=1)
soma_max = st.sidebar.number_input("Soma máxima", min_value=120, max_value=300, value=220, step=1)

repetidas_min = st.sidebar.slider("Mínimo de repetidas do último concurso", min_value=0, max_value=15, value=8)
repetidas_max = st.sidebar.slider("Máximo de repetidas do último concurso", min_value=0, max_value=15, value=11)

sobreposicao_max = st.sidebar.slider("Sobreposição máxima entre jogos", min_value=8, max_value=15, value=13)

# ============================================================
# CARREGAMENTO DOS CONCURSOS
# ============================================================

with st.spinner("Carregando concursos da Caixa..."):
    concursos = carregar_concursos(qtd_concursos)

if not concursos:
    st.error("Nenhum concurso foi carregado.")
    st.stop()

df_freq = analisar_concursos(concursos)
df_atrasos = calcular_atrasos(concursos)

mapa_freq = dict(zip(df_freq["dezena"], df_freq["frequencia"]))
mapa_atraso = dict(zip(df_atrasos["dezena"], df_atrasos["atraso"]))

opcoes_concurso = {}
for c in concursos:
    opcoes_concurso[f"Concurso {c['numero']} ({c['data']})"] = c['dezenas']
opcoes_concurso["Inserir Dezenas Manualmente"] = []

# ============================================================
# VISÃO GERAL DA ANÁLISE
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 📊 Visão Geral da Análise")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔥 Dezenas mais fortes")

    dezenas_fortes = df_freq.head(10)

    html_fortes = ""

    for _, row in dezenas_fortes.iterrows():
        html_fortes += f'<span class="dezena-base">{row["dezena"]}</span>'

    st.markdown(html_fortes, unsafe_allow_html=True)

    st.dataframe(
        dezenas_fortes.rename(
            columns={
                "dezena": "Dezena",
                "frequencia": "Frequência"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.markdown(f"### 📈 Frequência das dezenas nos últimos {len(concursos)} concursos")

    grafico_freq = df_freq.copy()
    grafico_freq = grafico_freq.sort_values("dezena")

    st.bar_chart(
        grafico_freq,
        x="dezena",
        y="frequencia",
        use_container_width=True
    )

# ============================================================
# ATRASOS
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🧊 Dezenas em atraso")

col1, col2 = st.columns(2)

with col1:
    dezenas_atrasadas = df_atrasos.head(10)

    html_atrasadas = ""

    for _, row in dezenas_atrasadas.iterrows():
        html_atrasadas += f'<span class="dezena-fria">{row["dezena"]}</span>'

    st.markdown(html_atrasadas, unsafe_allow_html=True)

    st.dataframe(
        dezenas_atrasadas.rename(
            columns={
                "dezena": "Dezena",
                "atraso": "Concursos sem sair"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

with col2:
    grafico_atrasos = df_atrasos.copy()
    grafico_atrasos = grafico_atrasos.sort_values("dezena")

    st.bar_chart(
        grafico_atrasos,
        x="dezena",
        y="atraso",
        use_container_width=True
    )

# ============================================================
# BASE SUGERIDA (ADAPTADA PARA NÚMEROS FIXOS)
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🎯 Base sugerida")

df_base = df_freq.copy()

# Remove descartadas e fixas para calcular o pool de variáveis puras
exclusoes_pool = dezenas_para_descartar + dezenas_fixas
if exclusoes_pool:
    df_base = df_base[~df_base["dezena"].isin(exclusoes_pool)]

# Vagas livres para números que vão variar no fechamento
vagas_variaveis = tamanho_base - len(dezenas_fixas)
base_variavel = df_base.head(vagas_variaveis)["dezena"].tolist()

# União montada e ordenada para exibição completa
base_sugerida_completa = sorted(list(set(base_variavel + dezenas_fixas)), key=lambda x: int(x))

html_base = ""
for dezena in base_sugerida_completa:
    if dezena in dezenas_fixas:
        html_base += f'<span class="dezena-fixa-painel">{dezena}</span>'
    else:
        html_base += f'<span class="dezena-base">{dezena}</span>'

st.markdown(html_base, unsafe_allow_html=True)

if dezenas_fixas:
    st.info(
        f"📌 As dezenas destacadas em **Roxo/Azul** são as suas fixas travadas em todos os jogos "
        f"({len(dezenas_fixas)}/5 usadas). Elas ocupam vagas do tamanho da base, então o pool de "
        f"números variáveis foi ajustado para {vagas_variaveis} dezenas."
    )
if dezenas_para_descartar:
    st.warning("Dezenas descartadas temporariamente: " + ", ".join(dezenas_para_descartar))

# ============================================================
# GERAÇÃO DO DESDOBRAMENTO
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🧩 Geração de jogos")

vagas_restantes_jogo = 15 - len(dezenas_fixas)

if len(base_sugerida_completa) < 15:
    st.error("A sua base sugerida total precisa atingir no mínimo 15 dezenas combinadas.")
elif len(base_variavel) < vagas_restantes_jogo:
    st.error(f"Você precisa de pelo menos {vagas_restantes_jogo} números variáveis disponíveis no pool para completar as vagas livres.")
else:
    total_combinacoes_base = math.comb(len(base_variavel), vagas_restantes_jogo)

    st.info(
        f"A sua estratégia atual fixa {len(dezenas_fixas)} números e combina as outras {vagas_restantes_jogo} vagas "
        f"em cima das {len(base_variavel)} dezenas variáveis da sua base. Total de caminhos no fechamento: "
        f"{total_combinacoes_base:,}".replace(",", ".") + " combinações."
    )

    if st.button("🎲 Gerar Novo Desdobramento", use_container_width=True, type="primary"):
        st.session_state["jogos_gerados"] = gerar_desdobramento_com_fixos(
            base_variavel=base_variavel,
            fixos=dezenas_fixas,
            qtd_jogos=qtd_jogos,
            ultimo_resultado=dezenas_ultimo,
            mapa_freq=mapa_freq,
            mapa_atraso=mapa_atraso,
            pares_min=pares_min,
            pares_max=pares_max,
            soma_min=soma_min,
            soma_max=soma_max,
            repetidas_min=repetidas_min,
            repetidas_max=repetidas_max,
            sobreposicao_max=sobreposicao_max
        )
        if not st.session_state["jogos_gerados"]:
            st.warning("Nenhum jogo foi encontrado com os filtros atuais. Tente flexibilizar os critérios na lateral.")
        else:
            st.success(f"{len(st.session_state['jogos_gerados'])} jogos gerados com sucesso travando as dezenas fixas!")

# ============================================================
# IMPRESSÃO E CENTRAL DE CONFERÊNCIA
# ============================================================

if st.session_state["jogos_gerados"]:
    jogos_para_exibir = st.session_state["jogos_gerados"]

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("## 🎟️ Conferência de Acertos")

    col_conf1, col_conferir_btn = st.columns([3, 1])
    with col_conf1:
        selecao_concurso = st.selectbox(
            "Selecione o concurso para conferir seus jogos atuais:",
            options=list(opcoes_concurso.keys()),
            label_visibility="collapsed"
        )

    dezenas_alvo = []
    if selecao_concurso == "Inserir Dezenas Manualmente":
        dezenas_manuais_input = st.text_input("Digite 15 dezenas separadas por espaço (ex: 01 02 03...):")
        if dezenas_manuais_input:
            dezenas_alvo = [d.zfill(2) for d in dezenas_manuais_input.strip().split() if d.isdigit()][:15]
    else:
        dezenas_alvo = opcoes_concurso[selecao_concurso]

    if dezenas_alvo:
        html_gabarito = "".join([f'<span class="dezena-resultado">{d}</span>' for d in dezenas_alvo])
        st.markdown(f"<div style='margin-bottom:15px;'><strong>Gabarito de Sorteio:</strong><br>{html_gabarito}</div>", unsafe_allow_html=True)

    rodar_conferencia = col_conferir_btn.button("🔍 Rodar Conferência", use_container_width=True)

    contadores_premios = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
    mapa_acertos_jogos = {}

    if dezenas_alvo:
        for idx, item in enumerate(jogos_para_exibir):
            acertos = set(item["jogo"]).intersection(set(dezenas_alvo))
            qtd_acertos = len(acertos)
            mapa_acertos_jogos[idx] = acertos
            if qtd_acertos in contadores_premios:
                contadores_premios[qtd_acertos] += 1

        if rodar_conferencia:
            st.markdown("### 🏆 Painel de Premiações")
            c_p1, c_p2, c_p3, c_p4, c_p5 = st.columns(5)
            c_p1.markdown(f'<div class="premio-card"><div class="premio-titulo">11 Acertos</div><div class="premio-valor">{contadores_premios[11]} jg</div></div>', unsafe_allow_html=True)
            c_p2.markdown(f'<div class="premio-card"><div class="premio-titulo">12 Acertos</div><div class="premio-valor">{contadores_premios[12]} jg</div></div>', unsafe_allow_html=True)
            c_p3.markdown(f'<div class="premio-card"><div class="premio-titulo">13 Acertos</div><div class="premio-valor">{contadores_premios[13]} jg</div></div>', unsafe_allow_html=True)
            c_p4.markdown(f'<div class="premio-card"><div class="premio-titulo">14 Acertos</div><div class="premio-valor">{contadores_premios[14]} jg</div></div>', unsafe_allow_html=True)
            c_p5.markdown(f'<div class="premio-card"><div class="premio-titulo">15 Acertos</div><div class="premio-valor">{contadores_premios[15]} jg</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📋 Seus Jogos Atuais")
    for idx, item in enumerate(jogos_para_exibir):
        html_jogo = ""
        acertos_desse_jogo = mapa_acertos_jogos.get(idx, set()) if dezenas_alvo else set()

        for dezena in item["jogo"]:
            if dezena in acertos_desse_jogo and rodar_conferencia:
                html_jogo += f'<span class="dezena-acerto">{dezena}</span>'
            else:
                html_jogo += f'<span class="dezena-jogo">{dezena}</span>'

        texto_conferencia_stats = ""
        if dezenas_alvo and rodar_conferencia:
            texto_conferencia_stats = f' | Premiação: <strong style="color:#facc15;font-size:14px;">{len(acertos_desse_jogo)} ACERTOS</strong>'

        st.markdown(
            f"""
<div class="jogo-box">
    <div class="jogo-titulo">Jogo {idx + 1} {"🌟 (Contém Fixos)" if dezenas_fixas else ""}</div>
    <div>{html_jogo}</div>
    <div style="margin-top:10px;color:#cbd5e1;font-size:13px;">
        Pares: <strong>{item["pares"]}</strong> |
        Ímpares: <strong>{item["impares"]}</strong> |
        Soma: <strong>{item["soma"]}</strong> |
        Repetidas do último: <strong>{item["repetidas_ultimo"]}</strong> |
        Score: <strong>{round(item["score"], 2)}</strong>{texto_conferencia_stats}
    </div>
</div>
            """,
            unsafe_allow_html=True
        )

    csv = jogos_para_csv(jogos_para_exibir)
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="⬇️ Baixar desdobramento ativo em CSV",
        data=csv,
        file_name="desdobramento_lotofacil.csv",
        mime="text/csv"
    )

    # ============================================================
    # VOLANTE VISUAL + IMPRESSÃO EM A4 (SÓ AS MARCAS)
    # ============================================================

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("## 🎫 Volante — Visualizar e Imprimir")
    st.markdown(
        '<div class="info-box">'
        'Escolha até 2 jogos para preencher as duas caixas do volante (igual ao cartão físico da Lotofácil). '
        'A pré-visualização abaixo mostra os números pintados. Na hora de imprimir, a folha A4 sai '
        '<strong>apenas com as bolinhas de marcação</strong> — sem o volante desenhado — para você imprimir '
        'por cima do volante físico que já está colado na folha A4.'
        '</div>',
        unsafe_allow_html=True
    )

    modo_volante = st.radio(
        "O que você quer ver/imprimir?",
        options=["Todos os jogos gerados (padrão volante da Caixa)", "Escolher jogos específicos"],
        horizontal=True,
        key="modo_volante_radio"
    )

    paginas_volante = []

    if modo_volante == "Todos os jogos gerados (padrão volante da Caixa)":
        # Cada folha do volante da Caixa tem 2 caixas -> agrupa os jogos 2 a 2
        paginas_volante = montar_paginas_volante(jogos_para_exibir)

        qtd_folhas = len(paginas_volante)
        st.caption(
            f"Você tem {len(jogos_para_exibir)} jogo(s), agrupados em {qtd_folhas} folha(s) A4 "
            f"(2 caixas por folha, igual ao volante físico da Lotofácil)."
        )

        st.markdown("#### 👀 Pré-visualização (na tela)")
        for idx, pagina in enumerate(paginas_volante):
            st.markdown(f"**Volante {idx + 1}**")
            html_bloco = '<div class="volante-wrapper">'
            html_bloco += renderizar_volante_visual(pagina["jogo1"], f"Caixa 1 — {pagina['rotulo1']}")
            if pagina["jogo2"]:
                html_bloco += renderizar_volante_visual(pagina["jogo2"], f"Caixa 2 — {pagina['rotulo2']}")
            else:
                html_bloco += renderizar_volante_visual(None, "Caixa 2 — (vazia)")
            html_bloco += '</div>'
            st.markdown(html_bloco, unsafe_allow_html=True)

    else:
        opcoes_jogos_volante = ["Nenhum"] + [f"Jogo {i + 1}" for i in range(len(jogos_para_exibir))]

        col_vol1, col_vol2 = st.columns(2)
        with col_vol1:
            escolha_caixa1 = st.selectbox("Jogo para a Caixa 1 do volante", options=opcoes_jogos_volante, index=1 if len(opcoes_jogos_volante) > 1 else 0, key="caixa1_select")
        with col_vol2:
            idx_default2 = 2 if len(opcoes_jogos_volante) > 2 else 0
            escolha_caixa2 = st.selectbox("Jogo para a Caixa 2 do volante", options=opcoes_jogos_volante, index=idx_default2, key="caixa2_select")

        jogo_caixa1 = None
        jogo_caixa2 = None
        if escolha_caixa1 != "Nenhum":
            jogo_caixa1 = jogos_para_exibir[int(escolha_caixa1.split(" ")[1]) - 1]["jogo"]
        if escolha_caixa2 != "Nenhum":
            jogo_caixa2 = jogos_para_exibir[int(escolha_caixa2.split(" ")[1]) - 1]["jogo"]

        st.markdown("#### 👀 Pré-visualização (na tela)")
        html_volante_preview = '<div class="volante-wrapper">'
        html_volante_preview += renderizar_volante_visual(jogo_caixa1, f"Caixa 1 — {escolha_caixa1}")
        html_volante_preview += renderizar_volante_visual(jogo_caixa2, f"Caixa 2 — {escolha_caixa2}")
        html_volante_preview += '</div>'
        st.markdown(html_volante_preview, unsafe_allow_html=True)

        if jogo_caixa1 or jogo_caixa2:
            paginas_volante = [{
                "rotulo1": escolha_caixa1, "jogo1": jogo_caixa1,
                "rotulo2": escolha_caixa2 if jogo_caixa2 else None, "jogo2": jogo_caixa2
            }]

    with st.expander("⚙️ Calibrar posição de impressão (ajuste fino em milímetros)"):
        st.caption(
            "Ajuste estes valores até as bolinhas caírem exatamente em cima dos números do seu volante físico "
            "colado na folha A4. A mesma calibração vale para todas as folhas. Faça um teste de impressão "
            "em papel comum antes de imprimir por cima do volante de verdade."
        )
        calib = st.session_state["calib_volante"]

        c1, c2, c3 = st.columns(3)
        with c1:
            calib["x1"] = st.number_input("Caixa 1 — X do número 21 (mm)", value=float(calib["x1"]), step=0.5, format="%.1f")
            calib["y1"] = st.number_input("Caixa 1 — Y do número 21 (mm)", value=float(calib["y1"]), step=0.5, format="%.1f")
        with c2:
            calib["x2"] = st.number_input("Caixa 2 — X do número 21 (mm)", value=float(calib["x2"]), step=0.5, format="%.1f")
            calib["y2"] = st.number_input("Caixa 2 — Y do número 21 (mm)", value=float(calib["y2"]), step=0.5, format="%.1f")
        with c3:
            calib["dx"] = st.number_input("Espaçamento entre colunas (mm)", value=float(calib["dx"]), step=0.1, format="%.1f")
            calib["dy"] = st.number_input("Espaçamento entre linhas (mm)", value=float(calib["dy"]), step=0.1, format="%.1f")

        calib["raio"] = st.slider("Raio da marca impressa (mm)", min_value=1.0, max_value=4.0, value=float(calib["raio"]), step=0.1)

        st.session_state["calib_volante"] = calib

    if paginas_volante:
        html_impressao = gerar_html_impressao_volante(
            paginas=paginas_volante,
            calib=st.session_state["calib_volante"]
        )

        st.markdown("#### 🖨️ Página(s) de impressão (A4)")
        st.markdown(
            '<div class="info-box">'
            'Os volantes são organizados <strong>lado a lado (na horizontal)</strong>, o máximo que couber '
            'em cada folha A4 de acordo com a calibração atual, antes de pular para a próxima página.'
            '</div>',
            unsafe_allow_html=True
        )
        st.warning(
            "⚠️ Clique em **'Abrir para imprimir'** abaixo — ele abre a folha em uma aba própria do navegador. "
            "É nessa aba (não dentro do app) que o Ctrl+P / botão 'Imprimir agora' funciona de verdade. "
            "Se mesmo assim sair em branco, verifique nas opções de impressão do navegador se "
            "**'Gráficos de segundo plano'** está marcado."
        )

        html_b64 = base64.b64encode(html_impressao.encode("utf-8")).decode()
        href_impressao = f"data:text/html;base64,{html_b64}"

        st.markdown(
            f'<a href="{href_impressao}" target="_blank" rel="noopener noreferrer">'
            f'<button style="padding:12px 20px;font-weight:800;font-size:15px;cursor:pointer;'
            f'border:none;border-radius:8px;background:#16a34a;color:white;margin:8px 0;">'
            f'🖨️ Abrir para imprimir ({len(paginas_volante)} volante(s))</button></a>',
            unsafe_allow_html=True
        )

        st.download_button(
            label=f"⬇️ Baixar página(s) de impressão em HTML ({len(paginas_volante)} volante(s))",
            data=html_impressao,
            file_name="volante_impressao.html",
            mime="text/html"
        )
    else:
        st.info("Selecione ao menos um jogo para gerar a página de impressão.")

else:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.info("💡 Alinhou a estratégia de fixos e filtros na barra esquerda? Clique em 'Gerar Novo Desdobramento' para processar os bilhetes.")

# ============================================================
# LEITURA COMBINATÓRIA
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🧠 Leitura combinatória")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Distribuição par/ímpar")
    if st.session_state["jogos_gerados"]:
        df_paridade = pd.DataFrame(st.session_state["jogos_gerados"])
        st.dataframe(
            df_paridade[["pares", "impares", "soma", "repetidas_ultimo"]].rename(
                columns={
                    "pares": "Pares",
                    "impares": "Ímpares",
                    "soma": "Soma",
                    "repetidas_ultimo": "Repetidas do último"
                }
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.caption("Gere jogos para visualizar esta leitura.")

with col2:
    st.markdown("### Repetição do último concurso")
    if st.session_state["jogos_gerados"]:
        repeticoes = [j["repetidas_ultimo"] for j in st.session_state["jogos_gerados"]]
        df_repeticoes = pd.DataFrame({"Repetidas": repeticoes})
        st.bar_chart(df_repeticoes, y="Repetidas", use_container_width=True)
    else:
        st.caption("Gere jogos para visualizar esta leitura.")

with col3:
    st.markdown("### Faixa de soma")
    if st.session_state["jogos_gerados"]:
        somas = [j["soma"] for j in st.session_state["jogos_gerados"]]
        st.metric("Menor soma", min(somas))
        st.metric("Maior soma", max(somas))
        st.metric("Média", round(sum(somas) / len(somas), 2))
    else:
        st.caption("Gere jogos para visualizar esta leitura.")

# ============================================================
# HISTÓRICO CARREGADO
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

with st.expander("📚 Ver concursos analisados"):
    linhas_historico = []

    for concurso in concursos:
        linhas_historico.append({
            "Concurso": concurso["numero"],
            "Data": concurso["data"],
            "Dezenas": " ".join(concurso["dezenas"])
        })

    st.dataframe(
        pd.DataFrame(linhas_historico),
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# RESUMO FINAL DA PÁGINA
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 📌 Resumo do painel")

st.markdown(
    """
<div class="info-box">
    Este painel reúne uma análise estatística feita para a Lotofácil, incluindo frequência das dezenas,
    seleção de base, dezenas fixas e móveis, descartes automáticos, geração controlada, conferência integrada de acertos
    e agora também visualização e impressão do volante.
</div>
    """,
    unsafe_allow_html=True
)

total_combinacoes_lotofacil = math.comb(25, 15)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Concursos analisados</div>
    <div class="metric-value">{len(concursos)}</div>
</div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Total de combinações da Lotofácil</div>
    <div class="metric-value">{total_combinacoes_lotofacil:,}</div>
</div>
        """.replace(",", ","),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Tamanho da sua base</div>
    <div class="metric-value">{len(base_sugerida_completa)} nros</div>
</div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">Desdobramento ativo</div>
    <div class="metric-value">{len(st.session_state["jogos_gerados"])} jogos</div>
</div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    """
<br>
<div style="color:#94a3b8;font-size:13px;text-align:center;">
    Análise estatística e combinatória. Este painel não garante premiação e não substitui a decisão pessoal de aposta.
</div>
    """,
    unsafe_allow_html=True
)
