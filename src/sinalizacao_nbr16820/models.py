"""Modelos de dados e tipos para dimensionamento de sinalização de emergência.

Atende rigorosamente à ABNT NBR 16820:2020 com representação exata sem float.
"""

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction


class TipoSinalizacao(str, Enum):
    """Classificação normativa das placas de sinalização conforme ABNT NBR 16820."""
    ORIENTACAO_SALVAMENTO = "ORIENTACAO_SALVAMENTO"  # Verde: rotas, saídas, escadas
    COMBATE_INCENDIO = "COMBATE_INCENDIO"            # Vermelho: extintores, hidrantes
    ALARME = "ALARME"                                # Vermelho: botoeiras de alarme, sirenes
    PROIBICAO = "PROIBICAO"                          # Fundo branco/borda vermelha: não fumar, não usar elevador
    ALERTA = "ALERTA"                                # Amarelo/preto: alta tensão, inflamáveis, produtos químicos
    COMPLEMENTAR_PISO = "COMPLEMENTAR_PISO"          # Demarcação de solo para equipamentos
    COMPLEMENTAR_RODAPE = "COMPLEMENTAR_RODAPE"      # Sinalização baixa de corredor/rota


class CategoriaFotoluminescente(str, Enum):
    """Categorias fotoluminescentes da ABNT NBR 16820 (Tabela B.1)."""
    CATEGORIA_W = "CATEGORIA_W"  # Min 140 mcd/m² (10 min) e 20 mcd/m² (60 min)
    CATEGORIA_X = "CATEGORIA_X"  # Min 210 mcd/m² (10 min) e 30 mcd/m² (60 min)
    NAO_APLICAVEL = "NAO_APLICAVEL"  # Sinalização eletroluminescente / luz direta contínua


class FormaGeometrica(str, Enum):
    """Formatos geométricos padronizados da sinalização conforme NBR 16820."""
    QUADRADA = "QUADRADA"              # L x L (extintores, hidrantes, alerta)
    RETANGULAR_2X1 = "RETANGULAR_2X1"  # 2H x H (rotas de fuga, saída de emergência)
    RETANGULAR_3X1 = "RETANGULAR_3X1"  # 3H x H (painéis informativos longos)
    CIRCULAR = "CIRCULAR"              # Diâmetro D (proibições)
    TRIANGULAR = "TRIANGULAR"          # Triângulo equilátero de lado L (alerta de perigo)


class PosicaoInstalacao(str, Enum):
    """Faixas de altura de instalação regulamentares da NBR 16820."""
    SUPERIOR = "SUPERIOR"  # >= 1.80 m do piso acabado ou sobre portas
    MEDIA = "MEDIA"        # 1.20 m a 1.50 m do piso acabado
    RODAPE = "RODAPE"      # 0.10 m a 0.50 m do piso acabado
    PISO = "PISO"          # Pintura ou adesivo aplicado diretamente no solo


@dataclass(frozen=True)
class DadosPlaca:
    """Parâmetros de entrada para uma placa individual ou tipo de sinalização."""
    id: str
    codigo: str
    descricao: str
    tipo: TipoSinalizacao
    distancia_visualizacao_m: Fraction
    iluminacao_direta: bool = False
    forma: FormaGeometrica = FormaGeometrica.RETANGULAR_2X1
    categoria_fotoluminescente: CategoriaFotoluminescente = CategoriaFotoluminescente.CATEGORIA_W
    posicao: PosicaoInstalacao = PosicaoInstalacao.SUPERIOR
    altura_instalacao_m: Fraction | None = None
    quantidade: int = 1


@dataclass(frozen=True)
class DadosTrechoRota:
    """Parâmetros de entrada para dimensionamento automático de uma rota de fuga."""
    id: str
    descricao: str
    comprimento_m: Fraction
    mudancas_direcao: int = 0
    portas_saida: int = 1
    distancia_visualizacao_desejada_m: Fraction | None = None
    iluminacao_direta: bool = False
    categoria_fotoluminescente: CategoriaFotoluminescente = CategoriaFotoluminescente.CATEGORIA_W


@dataclass(frozen=True)
class DadosProjetoSinalizacao:
    """Conjunto completo de dados de um projeto de sinalização predial ou industrial."""
    identificacao_edificio: str
    ocupacao: str
    responsavel_tecnico: str
    categoria_fotoluminescente_padrao: CategoriaFotoluminescente = CategoriaFotoluminescente.CATEGORIA_W
    placas_individuais: list[DadosPlaca] = field(default_factory=list)
    trechos_rotas: list[DadosTrechoRota] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoPlaca:
    """Resultado técnico do dimensionamento de uma placa conforme a NBR 16820."""
    placa_id: str
    codigo: str
    descricao: str
    tipo: TipoSinalizacao
    distancia_visualizacao_m: Fraction
    fator_k: int
    area_minima_calculada_m2: Fraction
    area_adotada_m2: Fraction
    largura_mm: int
    altura_mm: int
    forma: FormaGeometrica
    posicao: PosicaoInstalacao
    altura_instalacao_m: Fraction
    categoria_fotoluminescente: CategoriaFotoluminescente
    quantidade: int
    conforme_nbr16820: bool
    observacoes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoTrecho:
    """Resultado do dimensionamento do trecho de rota com distribuição de placas."""
    trecho_id: str
    descricao: str
    comprimento_m: Fraction
    placas_calculadas_total: int
    espacamento_maximo_adotado_m: Fraction
    placas_intermediarias: int
    placas_mudanca_direcao: int
    placas_portas_saida: int
    placas_geradas: list[ResultadoPlaca] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoProjeto:
    """Resultado consolidado do projeto com auditoria de conformidade com a NBR 16820."""
    identificacao_edificio: str
    ocupacao: str
    responsavel_tecnico: str
    total_placas_unidades: int
    resumo_por_tipo: dict[str, int]
    placas: list[ResultadoPlaca]
    trechos: list[ResultadoTrecho]
    conformidade_geral: bool
    alertas: list[str] = field(default_factory=list)
