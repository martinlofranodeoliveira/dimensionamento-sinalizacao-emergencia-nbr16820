"""Testes unitários das constantes e parâmetros normativos da ABNT NBR 16820:2020."""

import unittest
from fractions import Fraction

from sinalizacao_nbr16820.constants import (
    ALTURA_FAIXA_MEDIA_MAXIMA_M,
    ALTURA_FAIXA_MEDIA_MINIMA_M,
    ALTURA_FAIXA_RODAPE_MAXIMA_M,
    ALTURA_FAIXA_RODAPE_MINIMA_M,
    ALTURA_MINIMA_INSTALACAO_SUPERIOR_M,
    ALTURA_PADRAO_SOBRE_PORTA_M,
    COR_CONTRASTE_BRANCO_HEX,
    COR_CONTRASTE_PRETO_HEX,
    COR_FOTOLUMINESCENTE_HEX,
    COR_SEGURANCA_AMARELO_HEX,
    COR_SEGURANCA_VERDE_HEX,
    COR_SEGURANCA_VERMELHO_HEX,
    DIMENSOES_QUADRADAS_PADRAO_MM,
    DIMENSOES_RETANGULARES_PADRAO_MM,
    DISTANCIA_MAXIMA_ENTRE_PLACAS_FUGA_M,
    FATOR_VISUALIZACAO_ILUMINACAO_DIRETA_K,
    FATOR_VISUALIZACAO_PADRAO_K,
    LARGURA_BORDA_PISO_M,
    LARGURA_PISO_EQUIPAMENTO_M,
    LUMINANCIA_MIN_10MIN_CAT_W_MCD,
    LUMINANCIA_MIN_10MIN_CAT_X_MCD,
    LUMINANCIA_MIN_60MIN_CAT_W_MCD,
    LUMINANCIA_MIN_60MIN_CAT_X_MCD,
    TEMPO_ATENUACAO_MINIMO_MINUTOS,
)


class TestConstants(unittest.TestCase):
    """Verifica a consistência e conformidade das constantes regulamentares."""

    def test_fatores_visualizacao_k(self) -> None:
        self.assertEqual(FATOR_VISUALIZACAO_PADRAO_K, 2000)
        self.assertEqual(FATOR_VISUALIZACAO_ILUMINACAO_DIRETA_K, 1250)
        self.assertGreater(FATOR_VISUALIZACAO_PADRAO_K, FATOR_VISUALIZACAO_ILUMINACAO_DIRETA_K)

    def test_espacamento_maximo_rotas(self) -> None:
        self.assertEqual(DISTANCIA_MAXIMA_ENTRE_PLACAS_FUGA_M, Fraction(15, 1))

    def test_alturas_regulamentares(self) -> None:
        self.assertEqual(ALTURA_MINIMA_INSTALACAO_SUPERIOR_M, Fraction(18, 10))
        self.assertEqual(ALTURA_PADRAO_SOBRE_PORTA_M, Fraction(21, 10))
        self.assertEqual(ALTURA_FAIXA_MEDIA_MINIMA_M, Fraction(12, 10))
        self.assertEqual(ALTURA_FAIXA_MEDIA_MAXIMA_M, Fraction(15, 10))
        self.assertEqual(ALTURA_FAIXA_RODAPE_MINIMA_M, Fraction(1, 10))
        self.assertEqual(ALTURA_FAIXA_RODAPE_MAXIMA_M, Fraction(5, 10))
        self.assertLess(ALTURA_FAIXA_RODAPE_MAXIMA_M, ALTURA_FAIXA_MEDIA_MINIMA_M)
        self.assertLess(ALTURA_FAIXA_MEDIA_MAXIMA_M, ALTURA_MINIMA_INSTALACAO_SUPERIOR_M)

    def test_demarcacao_solo(self) -> None:
        self.assertEqual(LARGURA_PISO_EQUIPAMENTO_M, Fraction(1, 1))
        self.assertEqual(LARGURA_BORDA_PISO_M, Fraction(15, 100))

    def test_requisitos_fotoluminescencia(self) -> None:
        self.assertEqual(LUMINANCIA_MIN_10MIN_CAT_W_MCD, 140)
        self.assertEqual(LUMINANCIA_MIN_60MIN_CAT_W_MCD, 20)
        self.assertEqual(LUMINANCIA_MIN_10MIN_CAT_X_MCD, 210)
        self.assertEqual(LUMINANCIA_MIN_60MIN_CAT_X_MCD, 30)
        self.assertEqual(TEMPO_ATENUACAO_MINIMO_MINUTOS, 1800)
        self.assertGreater(LUMINANCIA_MIN_10MIN_CAT_X_MCD, LUMINANCIA_MIN_10MIN_CAT_W_MCD)
        self.assertGreater(LUMINANCIA_MIN_60MIN_CAT_X_MCD, LUMINANCIA_MIN_60MIN_CAT_W_MCD)

    def test_tabelas_dimensoes_padronizadas(self) -> None:
        self.assertIn(100, DIMENSOES_QUADRADAS_PADRAO_MM)
        self.assertIn(200, DIMENSOES_QUADRADAS_PADRAO_MM)
        self.assertIn((200, 100), DIMENSOES_RETANGULARES_PADRAO_MM)
        self.assertIn((400, 200), DIMENSOES_RETANGULARES_PADRAO_MM)

    def test_cores_normativas(self) -> None:
        self.assertTrue(COR_SEGURANCA_VERDE_HEX.startswith("#"))
        self.assertTrue(COR_SEGURANCA_VERMELHO_HEX.startswith("#"))
        self.assertTrue(COR_SEGURANCA_AMARELO_HEX.startswith("#"))
        self.assertTrue(COR_CONTRASTE_BRANCO_HEX.startswith("#"))
        self.assertTrue(COR_CONTRASTE_PRETO_HEX.startswith("#"))
        self.assertTrue(COR_FOTOLUMINESCENTE_HEX.startswith("#"))


if __name__ == "__main__":
    unittest.main()
