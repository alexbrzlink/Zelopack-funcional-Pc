from flask import render_template, request

from . import technical_bp

@technical_bp.route('/technical', methods=['GET', 'POST'])
def technical():
    results = {}
    if request.method == 'POST':
        # Parâmetros de entrada
        peso_liquido = float(request.form.get('peso_liquido', 0))
        perdas = float(request.form.get('perdas', 0))
        densidade = float(request.form.get('densidade', 1))
        brix_atual = float(request.form.get('brix_atual', 0))
        brix_desejado = float(request.form.get('brix_desejado', 0))
        volume_atual = float(request.form.get('volume_atual', 0))
        brix_medido = float(request.form.get('brix_medido', 0))
        temperatura = float(request.form.get('temperatura', 20))
        peso_embalagem = float(request.form.get('peso_embalagem', 0))
        volume = float(request.form.get('volume', 0))
        concentracao_desejada = float(request.form.get('concentracao_desejada', 0))
        concentracao_corante = float(request.form.get('concentracao_corante', 1))
        peso = float(request.form.get('peso', 0))
        acidez = float(request.form.get('acidez', 0))
        ratio = float(request.form.get('ratio', 0))
        volume_titulante = float(request.form.get('volume_titulante', 0))
        normalidade = float(request.form.get('normalidade', 0.1))
        volume_amostra = float(request.form.get('volume_amostra', 10))
        acidez_atual = float(request.form.get('acidez_atual', 0))
        concentracao_soda = float(request.form.get('concentracao_soda', 1))
        fator = float(request.form.get('fator', 1))
        volume_inicial = float(request.form.get('volume_inicial', 0))
        volume_final = float(request.form.get('volume_final', 0))
        brix1 = float(request.form.get('brix1', 0))
        vol1 = float(request.form.get('vol1', 0))
        brix2 = float(request.form.get('brix2', 0))
        vol2 = float(request.form.get('vol2', 0))
        acidez1 = float(request.form.get('acidez1', 0))
        acidez2 = float(request.form.get('acidez2', 0))
        vazao = float(request.form.get('vazao', 1))
        acidez_desejada = float(request.form.get('acidez_desejada', 0))
        brix_inicial = float(request.form.get('brix_inicial', 0))
        acucar_cristal = float(request.form.get('acucar_cristal', 0))
        volume_solucao = float(request.form.get('volume_solucao', 0))
        percentual_acucar = float(request.form.get('percentual_acucar', 0))
        peso_bruto = float(request.form.get('peso_bruto', 0))
        tara = float(request.form.get('tara', 0))
        peso_total = float(request.form.get('peso_total', 0))
        embalagem = float(request.form.get('embalagem', 0))

        # Cálculos
        # 1. Produção Final (200)
        producao_final = peso_liquido - perdas

        # 2. Produção (Litro)
        producao_l = peso_liquido / densidade if densidade != 0 else 0

        # 3. Abaixar Brix
        qtd_agua_l = ((brix_atual - brix_desejado) * volume_atual) / brix_desejado if brix_desejado != 0 else 0

        # 4. Brix Corrigido
        fator_correcao = 0.002 * (temperatura - 20)  # Fator típico baseado na temperatura
        brix_corrigido = brix_medido + fator_correcao

        # 5. Peso Bruto
        peso_bruto_calc = peso_liquido + peso_embalagem

        # 6. Corantes
        qtd_corante = (volume * concentracao_desejada) / concentracao_corante if concentracao_corante != 0 else 0

        # 7. Densidade
        densidade_calc = peso / volume if volume != 0 else 0

        # 8. Ratio
        ratio_calc = brix_atual / acidez if acidez != 0 else 0

        # 9. Ratio - Brix
        brix_from_ratio = ratio * acidez

        # 10. Ratio - Acidez
        acidez_from_ratio = brix_atual / ratio if ratio != 0 else 0

        # 11. Acidez (%)
        acidez_calc = (volume_titulante * normalidade * 0.064) / volume_amostra if volume_amostra != 0 else 0

        # 12. Cálculo de Soda
        qtd_soda = (volume * acidez_atual) / (concentracao_soda * 100) if concentracao_soda != 0 else 0

        # 13. Vitamina C
        vitamina_c = (volume_titulante * fator) / volume_amostra if volume_amostra != 0 else 0

        # 14. Soda-Antigo / Soda-Diversey (mesma fórmula, fatores distintos)
        qtd_soda_diversey = (volume * acidez_atual) / (concentracao_soda * 100) if concentracao_soda != 0 else 0

        # 15. Ácido-Diversey / Ácido-Antigo (mesma fórmula que Acidez, tabelas distintas)
        acidez_diversey = (volume_titulante * normalidade * 0.064) / volume_amostra if volume_amostra != 0 else 0

        # 16. Saber Perda de Base (%)
        perda = ((volume_inicial - volume_final) / volume_inicial) * 100 if volume_inicial != 0 else 0

        # 17. Quantidade de Açúcar a Puxar
        qtd_acucar_puxar = ((brix_desejado - brix_atual) * volume * densidade) / 100

        # 18. Aumentar Brix Açúcar Batido (mesma fórmula que Qtd Açúcar a Puxar)
        qtd_acucar_batido = ((brix_desejado - brix_atual) * volume * densidade) / 100

        # 19. Previsão Brix
        brix_previsto = (brix1 * vol1 + brix2 * vol2) / (vol1 + vol2) if (vol1 + vol2) != 0 else 0

        # 20. Previsão Acidez
        acidez_prevista = (acidez1 * vol1 + acidez2 * vol2) / (vol1 + vol2) if (vol1 + vol2) != 0 else 0

        # 21. Tempo de Finalização
        tempo_final = volume / vazao if vazao != 0 else 0

        # 22. Aumentar Acidez
        qtd_acido = (acidez_desejada - acidez_atual) * volume * fator

        # 23. Diminuir Acidez
        novo_volume_acidez = (volume_atual * acidez_atual) / acidez_desejada if acidez_desejada != 0 else 0

        # 24. Correção de Brix
        novo_volume_brix = (brix_inicial * volume_inicial) / brix_desejado if brix_desejado != 0 else 0

        # 25. Conversão Cristal Líquido
        volume_solucao_calc = acucar_cristal / densidade if densidade != 0 else 0

        # 26. Correção Açúcar Cristal
        qtd_acucar_cristal = (brix_desejado - brix_atual) * volume / 100

        # 27. Conversão Líquido - Cristal
        peso_cristal = volume_solucao * densidade * (percentual_acucar / 100)

        # 28. Peso Líquido 200
        peso_liquido_200 = peso_bruto - tara

        # 29. Peso Líquido Litro / Zeragem de Embalagem
        volume_liquido = peso_liquido / densidade if densidade != 0 else 0
        peso_liquido_zeragem = peso_total - embalagem

        results = {
            "Produção Final (kg)": producao_final,
            "Produção (Litro)": producao_l,
            "Abaixar Brix (L)": qtd_agua_l,
            "Brix Corrigido": brix_corrigido,
            "Peso Bruto (kg)": peso_bruto_calc,
            "Quantidade de Corante (L)": qtd_corante,
            "Densidade (g/mL)": densidade_calc,
            "Ratio": ratio_calc,
            "Brix (via Ratio)": brix_from_ratio,
            "Acidez (via Ratio)": acidez_from_ratio,
            "Acidez (%)": acidez_calc,
            "Quantidade de Soda (L)": qtd_soda,
            "Vitamina C (mg/L)": vitamina_c,
            "Quantidade de Soda Diversey (L)": qtd_soda_diversey,
            "Acidez Diversey (%)": acidez_diversey,
            "Perda de Base (%)": perda,
            "Quantidade de Açúcar a Puxar (kg)": qtd_acucar_puxar,
            "Quantidade de Açúcar Batido (kg)": qtd_acucar_batido,
            "Brix Previsto": brix_previsto,
            "Acidez Prevista (%)": acidez_prevista,
            "Tempo de Finalização (min)": tempo_final,
            "Quantidade de Ácido (L)": qtd_acido,
            "Novo Volume (Diminuir Acidez) (L)": novo_volume_acidez,
            "Novo Volume (Correção Brix) (L)": novo_volume_brix,
            "Volume Solução (Cristal Líquido) (L)": volume_solucao_calc,
            "Quantidade de Açúcar Cristal (kg)": qtd_acucar_cristal,
            "Peso Cristal (Líquido - Cristal) (kg)": peso_cristal,
            "Peso Líquido 200 (kg)": peso_liquido_200,
            "Volume Líquido (Peso Líquido Litro) (L)": volume_liquido,
            "Peso Líquido (Zeragem de Embalagem) (kg)": peso_liquido_zeragem,
        }

    return render_template('technical.html', results=results)