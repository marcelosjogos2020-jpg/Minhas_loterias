# ============================================================
# CONFERÊNCIA DOS JOGOS
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🔎 Conferência dos jogos")

if not jogos_gerados:
    st.info(
        "Primeiro gere um desdobramento para poder conferir os resultados."
    )
else:
    col_concurso, col_botao = st.columns([2, 1])

    with col_concurso:
        concurso_conferencia = st.number_input(
            "Informe o número do concurso para conferência",
            min_value=1,
            value=int(numero_ultimo),
            step=1
        )

    with col_botao:
        st.markdown("<br>", unsafe_allow_html=True)

        conferir = st.button(
            "🔎 Conferir jogos",
            use_container_width=True
        )

    if conferir:
        try:
            with st.spinner("Consultando resultado do concurso..."):
                resultado_conferencia = buscar_concurso(
                    int(concurso_conferencia)
                )

            dezenas_sorteadas = resultado_conferencia["dezenas"]
            dezenas_sorteadas_set = set(dezenas_sorteadas)

            linhas_conferencia = []

            for indice, item in enumerate(jogos_gerados, start=1):
                jogo = item["jogo"]
                acertos = sorted(
                    list(set(jogo).intersection(dezenas_sorteadas_set)),
                    key=lambda x: int(x)
                )

                linhas_conferencia.append({
                    "Jogo": indice,
                    "Acertos": len(acertos),
                    "Dezenas acertadas": " ".join(acertos),
                    "Dezenas do jogo": " ".join(jogo)
                })

            st.session_state.conferencia_resultado = {
                "numero": resultado_conferencia["numero"],
                "data": resultado_conferencia["data"],
                "dezenas": dezenas_sorteadas,
                "linhas": linhas_conferencia
            }

        except Exception:
            st.error(
                "Não foi possível carregar este concurso. "
                "Verifique o número informado e tente novamente."
            )

    if st.session_state.conferencia_resultado:
        conferencia = st.session_state.conferencia_resultado

        html_dezenas_conferencia = "".join(
            [
                f'<span class="dezena-resultado">{dezena}</span>'
                for dezena in conferencia["dezenas"]
            ]
        )

        st.markdown(
            f"""
<div class="ultimo-sorteio">
    <div class="ultimo-label">Resultado utilizado para conferência</div>
    <div class="ultimo-concurso">
        Concurso {conferencia["numero"]} — {conferencia["data"]}
    </div>
    <div class="dezenas-resultado-container">
        {html_dezenas_conferencia}
    </div>
</div>
            """,
            unsafe_allow_html=True
        )

        df_conferencia = pd.DataFrame(conferencia["linhas"])

        maior_acerto = df_conferencia["Acertos"].max()

        if maior_acerto >= 11:
            st.success(
                f"🏆 Maior pontuação encontrada: {maior_acerto} acertos."
            )
        else:
            st.info(
                f"Maior pontuação encontrada: {maior_acerto} acertos."
            )

        st.dataframe(
            df_conferencia.sort_values(
                by=["Acertos", "Jogo"],
                ascending=[False, True]
            ),
            use_container_width=True,
            hide_index=True
        )

        csv_conferencia = df_conferencia.to_csv(
            index=False,
            sep=";",
            encoding="utf-8-sig"
        )

        st.download_button(
            label="⬇️ Baixar conferência em CSV",
            data=csv_conferencia,
            file_name=f"conferencia_lotofacil_{conferencia['numero']}.csv",
            mime="text/csv"
        )
