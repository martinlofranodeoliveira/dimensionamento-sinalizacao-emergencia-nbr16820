"""Módulo de cálculo e dimensionamento de sinalização de emergência.

Executa dimensionamento rigoroso conforme ABNT NBR 16820:2020 utilizando exclusivamente
aritmética exata (fractions.Fraction e inteiros) sem nenhum uso de float IEEE-754.
"""

import math
from fractions import Fraction

from sinalizacao_nbr16820.constants import (
    ALTURA_FAIXA_MEDIA_MAXIMA_M,
    ALTURA_FAIXA_MEDIA_MINIMA_M,
    ALTURA_FAIXA_RODAPE_MAXIMA_M,
    ALTURA_FAIXA_RODAPE_MINIMA_M,
    ALTURA_MINIMA_INSTALACAO_SUPERIOR_M,
    ALTURA_PADRAO_SOBRE_PORTA_M,
    DIMENSOES_QUADRADAS_PADRAO_MM,
    DIMENSOES_RETANGULARES_PADRAO_MM,
    DISTANCIA_MAXIMA_ENTRE_PLACAS_FUGA_M,
    FATOR_VISUALIZACAO_ILUMINACAO_DIRETA_K,
    FATOR_VISUALIZACAO_PADRAO_K,
    LARGURA_PISO_EQUIPAMENTO_M,
)
from sinalizacao_nbr16820.models import (
    CategoriaFotoluminescente,
    DadosPlaca,
    DadosProjetoSinalizacao,
    DadosTrechoRota,
    FormaGeometrica,
    PosicaoInstalacao,
    ResultadoPlaca,
    ResultadoProjeto,
    ResultadoTrecho,
    TipoSinalizacao,
)


def isqrt_ceil(n: int) -> int:
    """Calcula o teto da raiz quadrada de um inteiro não-negativo."""
    if n <= 0:
        return 0
    s = math.isqrt(n)
    return s if s * s == n else s + 1


def arredondar_para_cima_multiplo(valor: int, multiplo: int) -> int:
    """Arredonda um inteiro para cima para o múltiplo especificado."""
    if multiplo <= 0:
        return valor
    resto = valor % multiplo
    if resto == 0:
        return valor
    return valor + (multiplo - resto)


def calcular_fator_k(iluminacao_direta: bool) -> int:
    """Retorna o fator de visualização K normativo (adimensional)."""
    return (
        FATOR_VISUALIZACAO_ILUMINACAO_DIRETA_K
        if iluminacao_direta
        else FATOR_VISUALIZACAO_PADRAO_K
    )


def calcular_area_minima(distancia_m: Fraction, fator_k: int) -> Fraction:
    """Calcula a área mínima teórica da placa conforme fórmula A = d² / K.
    
    Item 5.1.2 da ABNT NBR 16820:2020.
    """
    if distancia_m <= 0:
        raise ValueError("A distância de visualização deve ser estritamente positiva.")
    if fator_k <= 0:
        raise ValueError("O fator de visualização K deve ser positivo.")
    return (distancia_m * distancia_m) / Fraction(fator_k, 1)


def selecionar_dimensoes_padronizadas(
    area_minima_m2: Fraction,
    forma: FormaGeometrica,
    tipo: TipoSinalizacao,
) -> tuple[int, int, Fraction]:
    """Determina a largura e altura padronizadas em milímetros e a área adotada em m².
    
    Garante que a área adotada seja maior ou igual à área mínima exigida pela NBR 16820.
    """
    if tipo == TipoSinalizacao.COMPLEMENTAR_PISO:
        # Demarcação de solo padronizada de 1000 mm x 1000 mm (1 m²)
        largura = int(LARGURA_PISO_EQUIPAMENTO_M * 1000)
        altura = int(LARGURA_PISO_EQUIPAMENTO_M * 1000)
        area_adotada = Fraction(largura * altura, 1_000_000)
        return largura, altura, area_adotada

    # Converte área mínima para mm² (multiplicando por 1.000.000)
    area_min_mm2_frac = area_minima_m2 * Fraction(1_000_000, 1)
    # Teto inteiro de mm²
    area_min_mm2 = (
        area_min_mm2_frac.numerator // area_min_mm2_frac.denominator
        if area_min_mm2_frac.numerator % area_min_mm2_frac.denominator == 0
        else (area_min_mm2_frac.numerator // area_min_mm2_frac.denominator) + 1
    )

    if forma == FormaGeometrica.QUADRADA:
        lado_min_mm = isqrt_ceil(area_min_mm2)
        # Busca no catálogo padronizado
        lado_adotado = None
        for padrao in DIMENSOES_QUADRADAS_PADRAO_MM:
            if padrao >= lado_min_mm:
                lado_adotado = padrao
                break
        if lado_adotado is None:
            lado_adotado = max(100, arredondar_para_cima_multiplo(lado_min_mm, 50))
        area_adotada = Fraction(lado_adotado * lado_adotado, 1_000_000)
        return lado_adotado, lado_adotado, area_adotada

    elif forma == FormaGeometrica.RETANGULAR_2X1:
        # A = 2 * H²  => H² = A / 2
        # Busca nas dimensões retangulares padronizadas
        largura_adotada = None
        altura_adotada = None
        for w, h in DIMENSOES_RETANGULARES_PADRAO_MM:
            if w * h >= area_min_mm2:
                largura_adotada = w
                altura_adotada = h
                break
        if largura_adotada is None or altura_adotada is None:
            # Calcula H mínimo: H² = ceil(area / 2)
            h2 = (area_min_mm2 + 1) // 2
            h_min = isqrt_ceil(h2)
            altura_adotada = max(100, arredondar_para_cima_multiplo(h_min, 50))
            largura_adotada = altura_adotada * 2

        area_adotada = Fraction(largura_adotada * altura_adotada, 1_000_000)
        return largura_adotada, altura_adotada, area_adotada

    elif forma == FormaGeometrica.RETANGULAR_3X1:
        # A = 3 * H² => H² = ceil(area / 3)
        h2 = (area_min_mm2 + 2) // 3
        h_min = isqrt_ceil(h2)
        altura_adotada = max(100, arredondar_para_cima_multiplo(h_min, 50))
        largura_adotada = altura_adotada * 3
        area_adotada = Fraction(largura_adotada * altura_adotada, 1_000_000)
        return largura_adotada, altura_adotada, area_adotada

    elif forma == FormaGeometrica.CIRCULAR:
        # A = pi * D² / 4. Usando aproximação conservadora D² = ceil(4 * A / 3)
        d2 = (4 * area_min_mm2 + 2) // 3
        d_min = isqrt_ceil(d2)
        diametro = max(100, arredondar_para_cima_multiplo(d_min, 50))
        area_adotada = Fraction(diametro * diametro, 1_000_000)
        return diametro, diametro, area_adotada

    elif forma == FormaGeometrica.TRIANGULAR:
        # A = (sqrt(3)/4) * L² ≈ 0.433 * L². Usando conservadoramente L² = ceil(5 * A / 2) = 2.5 * A
        l2 = (5 * area_min_mm2 + 1) // 2
        l_min = isqrt_ceil(l2)
        lado = max(100, arredondar_para_cima_multiplo(l_min, 50))
        area_adotada = Fraction(lado * lado, 1_000_000)
        return lado, lado, area_adotada

    # Caso padrão de segurança
    lado_def = max(150, isqrt_ceil(area_min_mm2))
    return lado_def, lado_def, Fraction(lado_def * lado_def, 1_000_000)


def resolver_altura_instalacao(
    posicao: PosicaoInstalacao,
    altura_especificada: Fraction | None,
) -> tuple[Fraction, list[str]]:
    """Determina e audita a altura de instalação conforme a NBR 16820."""
    alertas: list[str] = []

    if altura_especificada is not None:
        altura = altura_especificada
    else:
        if posicao == PosicaoInstalacao.SUPERIOR:
            altura = ALTURA_PADRAO_SOBRE_PORTA_M  # 2.10 m
        elif posicao == PosicaoInstalacao.MEDIA:
            altura = Fraction(135, 100)           # 1.35 m (centro da faixa 1.20 - 1.50m)
        elif posicao == PosicaoInstalacao.RODAPE:
            altura = Fraction(25, 100)            # 0.25 m (centro da faixa 0.10 - 0.50m)
        elif posicao == PosicaoInstalacao.PISO:
            altura = Fraction(0, 1)               # 0.00 m
        else:
            altura = ALTURA_MINIMA_INSTALACAO_SUPERIOR_M

    # Validações normativas de altura
    if posicao == PosicaoInstalacao.SUPERIOR:
        if altura < ALTURA_MINIMA_INSTALACAO_SUPERIOR_M:
            alertas.append(
                f"Altura de instalação ({altura} m) inferior ao mínimo de "
                f"{ALTURA_MINIMA_INSTALACAO_SUPERIOR_M} m para sinalização superior."
            )
    elif posicao == PosicaoInstalacao.MEDIA:
        if altura < ALTURA_FAIXA_MEDIA_MINIMA_M or altura > ALTURA_FAIXA_MEDIA_MAXIMA_M:
            alertas.append(
                f"Altura de instalação ({altura} m) fora da faixa normativa "
                f"de {ALTURA_FAIXA_MEDIA_MINIMA_M} m a {ALTURA_FAIXA_MEDIA_MAXIMA_M} m."
            )
    elif posicao == PosicaoInstalacao.RODAPE:
        if altura < ALTURA_FAIXA_RODAPE_MINIMA_M or altura > ALTURA_FAIXA_RODAPE_MAXIMA_M:
            alertas.append(
                f"Altura de instalação rodapé ({altura} m) fora da faixa regulamentar "
                f"de {ALTURA_FAIXA_RODAPE_MINIMA_M} m a {ALTURA_FAIXA_RODAPE_MAXIMA_M} m."
            )

    return altura, alertas


def dimensionar_placa(placa: DadosPlaca) -> ResultadoPlaca:
    """Executa o dimensionamento normativo completo de uma placa individual."""
    fator_k = calcular_fator_k(placa.iluminacao_direta)
    area_minima_m2 = calcular_area_minima(placa.distancia_visualizacao_m, fator_k)

    largura_mm, altura_mm, area_adotada_m2 = selecionar_dimensoes_padronizadas(
        area_minima_m2=area_minima_m2,
        forma=placa.forma,
        tipo=placa.tipo,
    )

    altura_instalacao_m, alertas_altura = resolver_altura_instalacao(
        posicao=placa.posicao,
        altura_especificada=placa.altura_instalacao_m,
    )

    observacoes: list[str] = list(alertas_altura)

    # Verificação de visibilidade e escala
    if placa.distancia_visualizacao_m > Fraction(30, 1):
        observacoes.append(
            f"Distância de visualização elevada ({placa.distancia_visualizacao_m} m). "
            "Recomenda-se prever placas repetidoras intermediárias."
        )

    # Verificação de fotoluminescência
    if not placa.iluminacao_direta and placa.categoria_fotoluminescente == CategoriaFotoluminescente.NAO_APLICAVEL:
        observacoes.append(
            "Placa sem iluminação direta deve possuir pigmentação fotoluminescente Categoria W ou X."
        )

    conforme = len(alertas_altura) == 0 and area_adotada_m2 >= area_minima_m2

    return ResultadoPlaca(
        placa_id=placa.id,
        codigo=placa.codigo,
        descricao=placa.descricao,
        tipo=placa.tipo,
        distancia_visualizacao_m=placa.distancia_visualizacao_m,
        fator_k=fator_k,
        area_minima_calculada_m2=area_minima_m2,
        area_adotada_m2=area_adotada_m2,
        largura_mm=largura_mm,
        altura_mm=altura_mm,
        forma=placa.forma,
        posicao=placa.posicao,
        altura_instalacao_m=altura_instalacao_m,
        categoria_fotoluminescente=placa.categoria_fotoluminescente,
        quantidade=placa.quantidade,
        conforme_nbr16820=conforme,
        observacoes=observacoes,
    )


def dimensionar_trecho_rota(trecho: DadosTrechoRota) -> ResultadoTrecho:
    """Dimensiona a distribuição de placas de rota de fuga ao longo de um corredor ou trecho.
    
    Aplica o critério de espaçamento máximo de 15,0 m (item 5.2.1 da ABNT NBR 16820:2020),
    adiciona placas em todas as mudanças de direção e sobre cada porta de saída de emergência.
    """
    if trecho.comprimento_m <= 0:
        raise ValueError("O comprimento do trecho deve ser estritamente positivo.")
    if trecho.mudancas_direcao < 0:
        raise ValueError("O número de mudanças de direção não pode ser negativo.")
    if trecho.portas_saida < 0:
        raise ValueError("O número de portas de saída não pode ser negativo.")

    # Distância de visualização de referência para as placas do trecho
    if trecho.distancia_visualizacao_desejada_m is not None:
        dist_vis_m = trecho.distancia_visualizacao_desejada_m
    else:
        # Adota o mínimo entre o comprimento do trecho e o espaçamento máximo normativo (15 m)
        dist_vis_m = min(trecho.comprimento_m, DISTANCIA_MAXIMA_ENTRE_PLACAS_FUGA_M)

    # Cálculo do número de vãos e placas intermediárias
    # Para comprimento L, se L <= 15m, 0 placas intermediárias adicionais (apenas extremidades/portas)
    comprimento_inteiro = trecho.comprimento_m.numerator
    denominador = trecho.comprimento_m.denominator
    # Divisão inteira exata em fração: vaos = ceil(L / 15)
    limite_vao = Fraction(15, 1)
    razao = trecho.comprimento_m / limite_vao
    vaos = razao.numerator // razao.denominator
    if razao.numerator % razao.denominator != 0:
        vaos += 1
    if vaos == 0:
        vaos = 1

    espacamento_efetivo = trecho.comprimento_m / Fraction(vaos, 1)
    placas_intermediarias = max(0, vaos - 1)
    placas_mudanca = trecho.mudancas_direcao
    placas_portas = max(1, trecho.portas_saida)

    placas_geradas: list[ResultadoPlaca] = []

    # 1. Placas sobre as portas de saída (S-1 / S-2)
    for i in range(1, placas_portas + 1):
        p_porta = DadosPlaca(
            id=f"{trecho.id}-PORTA-{i}",
            codigo="S-1",
            descricao=f"Saída de Emergência - Porta {i} ({trecho.descricao})",
            tipo=TipoSinalizacao.ORIENTACAO_SALVAMENTO,
            distancia_visualizacao_m=dist_vis_m,
            iluminacao_direta=trecho.iluminacao_direta,
            forma=FormaGeometrica.RETANGULAR_2X1,
            categoria_fotoluminescente=trecho.categoria_fotoluminescente,
            posicao=PosicaoInstalacao.SUPERIOR,
            altura_instalacao_m=ALTURA_PADRAO_SOBRE_PORTA_M,
            quantidade=1,
        )
        placas_geradas.append(dimensionar_placa(p_porta))

    # 2. Placas intermediárias de sentido de fuga ao longo da rota (S-3)
    for i in range(1, placas_intermediarias + 1):
        p_inter = DadosPlaca(
            id=f"{trecho.id}-ROTA-{i}",
            codigo="S-3",
            descricao=f"Sentido de Fuga Intermediário {i} ({trecho.descricao})",
            tipo=TipoSinalizacao.ORIENTACAO_SALVAMENTO,
            distancia_visualizacao_m=espacamento_efetivo,
            iluminacao_direta=trecho.iluminacao_direta,
            forma=FormaGeometrica.RETANGULAR_2X1,
            categoria_fotoluminescente=trecho.categoria_fotoluminescente,
            posicao=PosicaoInstalacao.SUPERIOR,
            altura_instalacao_m=ALTURA_MINIMA_INSTALACAO_SUPERIOR_M,
            quantidade=1,
        )
        placas_geradas.append(dimensionar_placa(p_inter))

    # 3. Placas de mudança de direção (S-4 / S-5)
    for i in range(1, placas_mudanca + 1):
        p_curva = DadosPlaca(
            id=f"{trecho.id}-DESVIO-{i}",
            codigo="S-4",
            descricao=f"Mudança de Direção / Curva {i} ({trecho.descricao})",
            tipo=TipoSinalizacao.ORIENTACAO_SALVAMENTO,
            distancia_visualizacao_m=dist_vis_m,
            iluminacao_direta=trecho.iluminacao_direta,
            forma=FormaGeometrica.RETANGULAR_2X1,
            categoria_fotoluminescente=trecho.categoria_fotoluminescente,
            posicao=PosicaoInstalacao.SUPERIOR,
            altura_instalacao_m=ALTURA_MINIMA_INSTALACAO_SUPERIOR_M,
            quantidade=1,
        )
        placas_geradas.append(dimensionar_placa(p_curva))

    total_calculadas = placas_portas + placas_intermediarias + placas_mudanca

    return ResultadoTrecho(
        trecho_id=trecho.id,
        descricao=trecho.descricao,
        comprimento_m=trecho.comprimento_m,
        placas_calculadas_total=total_calculadas,
        espacamento_maximo_adotado_m=espacamento_efetivo,
        placas_intermediarias=placas_intermediarias,
        placas_mudanca_direcao=placas_mudanca,
        placas_portas_saida=placas_portas,
        placas_geradas=placas_geradas,
    )


def dimensionar_projeto(projeto: DadosProjetoSinalizacao) -> ResultadoProjeto:
    """Processa e consolida o dimensionamento global de sinalização do edifício.
    
    Dimensiona todas as placas individuais, todos os trechos de rota e gera resumo analítico
    com verificação global de conformidade com a ABNT NBR 16820:2020.
    """
    todas_placas: list[ResultadoPlaca] = []
    alertas_globais: list[str] = []

    # 1. Dimensionamento das placas individuais
    for placa in projeto.placas_individuais:
        res_placa = dimensionar_placa(placa)
        todas_placas.append(res_placa)
        if not res_placa.conforme_nbr16820:
            alertas_globais.append(
                f"Placa {res_placa.codigo} ({res_placa.descricao}) possui não-conformidade com a NBR 16820."
            )

    # 2. Dimensionamento dos trechos de rotas
    resultados_trechos: list[ResultadoTrecho] = []
    for trecho in projeto.trechos_rotas:
        res_trecho = dimensionar_trecho_rota(trecho)
        resultados_trechos.append(res_trecho)
        for p_rota in res_trecho.placas_geradas:
            todas_placas.append(p_rota)

    # 3. Consolidação quantitativa e resumo por tipo
    resumo_por_tipo: dict[str, int] = {}
    total_unidades = 0

    for p in todas_placas:
        tipo_str = p.tipo.value
        resumo_por_tipo[tipo_str] = resumo_por_tipo.get(tipo_str, 0) + p.quantidade
        total_unidades += p.quantidade

    conformidade = len(alertas_globais) == 0 and all(p.conforme_nbr16820 for p in todas_placas)

    return ResultadoProjeto(
        identificacao_edificio=projeto.identificacao_edificio,
        ocupacao=projeto.ocupacao,
        responsavel_tecnico=projeto.responsavel_tecnico,
        total_placas_unidades=total_unidades,
        resumo_por_tipo=resumo_por_tipo,
        placas=todas_placas,
        trechos=resultados_trechos,
        conformidade_geral=conformidade,
        alertas=alertas_globais,
    )
