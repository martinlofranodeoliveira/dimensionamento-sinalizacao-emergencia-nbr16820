"""Testes unitários do gerador de painel técnico vetorial SVG."""

import unittest
from fractions import Fraction

from sinalizacao_nbr16820.calculator import dimensionar_projeto
from sinalizacao_nbr16820.models import (
    CategoriaFotoluminescente,
    DadosPlaca,
    DadosProjetoSinalizacao,
    DadosTrechoRota,
    FormaGeometrica,
    PosicaoInstalacao,
    TipoSinalizacao,
)
from sinalizacao_nbr16820.svg_generator import gerar_painel_svg


class TestSvgGenerator(unittest.TestCase):
    """Valida a conformidade visual e técnica do SVG gerado."""

    def test_gerar_painel_svg(self) -> None:
        placa = DadosPlaca(
            id="EXT-01",
            codigo="E-1",
            descricao="Extintor ABC",
            tipo=TipoSinalizacao.COMBATE_INCENDIO,
            distancia_visualizacao_m=Fraction(8, 1),
            forma=FormaGeometrica.QUADRADA,
            posicao=PosicaoInstalacao.SUPERIOR,
            altura_instalacao_m=Fraction(18, 10),
            categoria_fotoluminescente=CategoriaFotoluminescente.CATEGORIA_W,
            quantidade=2,
        )
        trecho = DadosTrechoRota(
            id="T-01",
            descricao="Corredor",
            comprimento_m=Fraction(30, 1),
            mudancas_direcao=1,
            portas_saida=1,
        )
        proj = DadosProjetoSinalizacao(
            identificacao_edificio="Edifício Teste SVG",
            ocupacao="Comercial",
            responsavel_tecnico="Eng. Lofrano",
            placas_individuais=[placa],
            trechos_rotas=[trecho],
        )
        res = dimensionar_projeto(proj)
        svg = gerar_painel_svg(res)

        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn('viewBox="0 0 1440 900"', svg)
        self.assertIn("LOFRANO TECNOLOGIA", svg)
        self.assertIn("ABNT NBR 16820:2020", svg)
        self.assertIn("A = d² / K", svg)
        self.assertIn("Edifício Teste SVG", svg)
        self.assertIn("#008751", svg)  # Verde segurança
        self.assertIn("#C8102E", svg)  # Vermelho segurança


if __name__ == "__main__":
    unittest.main()
