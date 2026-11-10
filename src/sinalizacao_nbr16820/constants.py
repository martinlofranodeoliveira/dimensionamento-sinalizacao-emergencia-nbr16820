"""Constantes e parâmetros normativos da ABNT NBR 16820:2020.

ABNT NBR 16820:2020 - Sistemas de sinalização de emergência e pânico contra incêndio.
Estabelece os requisitos para projeto, fabricação, dimensionamento e instalação de sinalização.
"""

from fractions import Fraction
from typing import Final

# Fatores de Visualização 'K' para cálculo da área mínima A = d² / K (adimensional)
# Item 5.1.2 da NBR 16820:2020
FATOR_VISUALIZACAO_PADRAO_K: Final[int] = 2000           # Iluminação externa ou fotoluminescente
FATOR_VISUALIZACAO_ILUMINACAO_DIRETA_K: Final[int] = 1250 # Sinalização com iluminação interna/direta

# Espaçamento Máximo entre Placas de Rota de Fuga em Linha Reta (metros)
# Item 5.2.1 da NBR 16820:2020
DISTANCIA_MAXIMA_ENTRE_PLACAS_FUGA_M: Final[Fraction] = Fraction(15, 1)  # 15.0 m

# Alturas de Instalação Regulamentares (metros)
# Conforme Item 5.3 e Anexo A da NBR 16820:2020
ALTURA_MINIMA_INSTALACAO_SUPERIOR_M: Final[Fraction] = Fraction(18, 10)  # 1.80 m (sobre portas e equipamentos)
ALTURA_PADRAO_SOBRE_PORTA_M: Final[Fraction] = Fraction(21, 10)          # 2.10 m (verga da porta)
ALTURA_FAIXA_MEDIA_MINIMA_M: Final[Fraction] = Fraction(12, 10)         # 1.20 m
ALTURA_FAIXA_MEDIA_MAXIMA_M: Final[Fraction] = Fraction(15, 10)         # 1.50 m
ALTURA_FAIXA_RODAPE_MINIMA_M: Final[Fraction] = Fraction(1, 10)         # 0.10 m (sinalização baixa de escape)
ALTURA_FAIXA_RODAPE_MAXIMA_M: Final[Fraction] = Fraction(5, 10)         # 0.50 m

# Demarcação de Piso para Equipamentos (metros)
LARGURA_PISO_EQUIPAMENTO_M: Final[Fraction] = Fraction(1, 1)            # 1.00 m
COMPRIMENTO_PISO_EQUIPAMENTO_M: Final[Fraction] = Fraction(1, 1)        # 1.00 m
LARGURA_BORDA_PISO_M: Final[Fraction] = Fraction(15, 100)               # 0.15 m (15 cm borda amarela)

# Requisitos Fotoluminescentes Mínimos (NBR 16820 item 6.1 e Anexo B)
LUMINANCIA_MIN_10MIN_CAT_W_MCD: Final[int] = 140   # Categoria W - 10 min (mcd/m²)
LUMINANCIA_MIN_60MIN_CAT_W_MCD: Final[int] = 20    # Categoria W - 60 min (mcd/m²)

LUMINANCIA_MIN_10MIN_CAT_X_MCD: Final[int] = 210   # Categoria X - 10 min (mcd/m²)
LUMINANCIA_MIN_60MIN_CAT_X_MCD: Final[int] = 30    # Categoria X - 60 min (mcd/m²)

TEMPO_ATENUACAO_MINIMO_MINUTOS: Final[int] = 1800  # 1800 minutos (30 horas até 0.3 mcd/m²)

# Dimensões e Áreas Mínimas de Referência Padronizadas (Tabela 1 NBR 16820)
AREA_MINIMA_TIPO_1_M2: Final[Fraction] = Fraction(1, 100)   # 0.01 m² (100x100mm) para d <= 4.0m
AREA_MINIMA_TIPO_2_M2: Final[Fraction] = Fraction(9, 400)   # 0.0225 m² (150x150mm) para d <= 6.7m
AREA_MINIMA_TIPO_3_M2: Final[Fraction] = Fraction(4, 100)   # 0.04 m² (200x200mm) para d <= 8.9m
AREA_MINIMA_TIPO_4_M2: Final[Fraction] = Fraction(1, 16)    # 0.0625 m² (250x250mm) para d <= 11.1m
AREA_MINIMA_TIPO_5_M2: Final[Fraction] = Fraction(9, 100)   # 0.09 m² (300x300mm) para d <= 13.4m
AREA_MINIMA_TIPO_6_M2: Final[Fraction] = Fraction(16, 100)  # 0.16 m² (400x400mm) para d <= 17.8m

# Dimensões Padronizadas de Placas Retangulares Proporção 2:1 (Largura x Altura em mm)
DIMENSOES_RETANGULARES_PADRAO_MM: Final[tuple[tuple[int, int], ...]] = (
    (200, 100),
    (300, 150),
    (400, 200),
    (500, 250),
    (600, 300),
    (800, 400),
)

# Dimensões Padronizadas de Placas Quadradas (Lado em mm)
DIMENSOES_QUADRADAS_PADRAO_MM: Final[tuple[int, ...]] = (
    100,
    150,
    200,
    250,
    300,
    400,
    500,
)

# Cores de Segurança da NBR 16820 / NBR 7195
COR_SEGURANCA_VERDE_HEX: Final[str] = "#008751"       # Orientação e salvamento
COR_SEGURANCA_VERMELHO_HEX: Final[str] = "#C8102E"    # Alarme e combate a incêndio
COR_SEGURANCA_AMARELO_HEX: Final[str] = "#FFC72C"     # Alerta contra riscos
COR_CONTRASTE_BRANCO_HEX: Final[str] = "#FFFFFF"      # Contraste / Símbolo
COR_CONTRASTE_PRETO_HEX: Final[str] = "#1A1A1A"       # Contraste para alerta e proibição
COR_FOTOLUMINESCENTE_HEX: Final[str] = "#D4ED91"      # Amarelo esverdeado fotoluminescente
