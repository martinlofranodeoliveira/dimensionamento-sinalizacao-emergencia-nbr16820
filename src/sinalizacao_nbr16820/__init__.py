"""Pacote dimensionamento-sinalizacao-emergencia-nbr16820.

Dimensionamento e Projeto de Sinalização de Emergência Contra Incêndio
conforme ABNT NBR 16820:2020.
Desenvolvido por Lofrano Tecnologia. Zero-Float Engine.
"""

from sinalizacao_nbr16820.calculator import (
    calcular_area_minima,
    calcular_fator_k,
    dimensionar_placa,
    dimensionar_projeto,
    dimensionar_trecho_rota,
    selecionar_dimensoes_padronizadas,
)
from sinalizacao_nbr16820.codecs import (
    carregar_projeto_sinalizacao_json,
    exportar_resultado_json,
)
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
    LUMINANCIA_MIN_10MIN_CAT_W_MCD,
    LUMINANCIA_MIN_10MIN_CAT_X_MCD,
    LUMINANCIA_MIN_60MIN_CAT_W_MCD,
    LUMINANCIA_MIN_60MIN_CAT_X_MCD,
    TEMPO_ATENUACAO_MINIMO_MINUTOS,
)
from sinalizacao_nbr16820.exporters import (
    gerar_csv_sanitizado,
    gerar_memorial_descritivo,
    gerar_pacote_zip,
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
from sinalizacao_nbr16820.svg_generator import gerar_painel_svg

__version__ = "1.0.0"
__author__ = "Lofrano Tecnologia"

__all__ = [
    "__version__",
    "__author__",
    "calcular_area_minima",
    "calcular_fator_k",
    "dimensionar_placa",
    "dimensionar_projeto",
    "dimensionar_trecho_rota",
    "selecionar_dimensoes_padronizadas",
    "carregar_projeto_sinalizacao_json",
    "exportar_resultado_json",
    "gerar_memorial_descritivo",
    "gerar_csv_sanitizado",
    "gerar_pacote_zip",
    "gerar_painel_svg",
    "CategoriaFotoluminescente",
    "DadosPlaca",
    "DadosProjetoSinalizacao",
    "DadosTrechoRota",
    "FormaGeometrica",
    "PosicaoInstalacao",
    "ResultadoPlaca",
    "ResultadoProjeto",
    "ResultadoTrecho",
    "TipoSinalizacao",
    "ALTURA_FAIXA_MEDIA_MAXIMA_M",
    "ALTURA_FAIXA_MEDIA_MINIMA_M",
    "ALTURA_FAIXA_RODAPE_MAXIMA_M",
    "ALTURA_FAIXA_RODAPE_MINIMA_M",
    "ALTURA_MINIMA_INSTALACAO_SUPERIOR_M",
    "ALTURA_PADRAO_SOBRE_PORTA_M",
    "DIMENSOES_QUADRADAS_PADRAO_MM",
    "DIMENSOES_RETANGULARES_PADRAO_MM",
    "DISTANCIA_MAXIMA_ENTRE_PLACAS_FUGA_M",
    "FATOR_VISUALIZACAO_ILUMINACAO_DIRETA_K",
    "FATOR_VISUALIZACAO_PADRAO_K",
    "LUMINANCIA_MIN_10MIN_CAT_W_MCD",
    "LUMINANCIA_MIN_10MIN_CAT_X_MCD",
    "LUMINANCIA_MIN_60MIN_CAT_W_MCD",
    "LUMINANCIA_MIN_60MIN_CAT_X_MCD",
    "TEMPO_ATENUACAO_MINIMO_MINUTOS",
]
