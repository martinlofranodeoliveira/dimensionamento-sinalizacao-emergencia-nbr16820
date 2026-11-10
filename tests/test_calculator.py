"""Testes unitários dos cálculos e regras de dimensionamento da NBR 16820."""

import unittest
from fractions import Fraction

from sinalizacao_nbr16820.calculator import (
    arredondar_para_cima_multiplo,
    calcular_area_minima,
    calcular_fator_k,
    dimensionar_placa,
    dimensionar_projeto,
    dimensionar_trecho_rota,
    isqrt_ceil,
    resolver_altura_instalacao,
    selecionar_dimensoes_padronizadas,
)
from sinalizacao_nbr16820.models import (
    CategoriaFotoluminescente,
    DadosPlaca,
    DadosProjetoSinalizacao,
    DadosTrechoRota,
    FormaGeometrica,
    PosicaoInstalacao,
    TipoSinalizacao,
)


class TestCalculator(unittest.TestCase):
    """Validação detalhada da matemática exata e conformidade técnica."""

    def test_isqrt_ceil(self) -> None:
        self.assertEqual(isqrt_ceil(0), 0)
        self.assertEqual(isqrt_ceil(-5), 0)
        self.assertEqual(isqrt_ceil(4), 2)
        self.assertEqual(isqrt_ceil(9), 3)
        self.assertEqual(isqrt_ceil(10), 4)
        self.assertEqual(isqrt_ceil(15), 4)
        self.assertEqual(isqrt_ceil(16), 4)
        self.assertEqual(isqrt_ceil(17), 5)

    def test_arredondar_para_cima_multiplo(self) -> None:
        self.assertEqual(arredondar_para_cima_multiplo(120, 50), 150)
        self.assertEqual(arredondar_para_cima_multiplo(150, 50), 150)
        self.assertEqual(arredondar_para_cima_multiplo(151, 50), 200)
        self.assertEqual(arredondar_para_cima_multiplo(80, 0), 80)

    def test_calcular_fator_k(self) -> None:
        self.assertEqual(calcular_fator_k(iluminacao_direta=False), 2000)
        self.assertEqual(calcular_fator_k(iluminacao_direta=True), 1250)

    def test_calcular_area_minima(self) -> None:
        # A = d² / K => para d = 10m e K = 2000: A = 100 / 2000 = 1/20 = 0.05 m²
        area = calcular_area_minima(Fraction(10, 1), 2000)
        self.assertEqual(area, Fraction(1, 20))

        # Para d = 4m e K = 2000: A = 16 / 2000 = 2 / 250 = 1 / 125 = 0.008 m²
        area_4 = calcular_area_minima(Fraction(4, 1), 2000)
        self.assertEqual(area_4, Fraction(2, 250))

        # Para d = 10m e K = 1250: A = 100 / 1250 = 2 / 25 = 0.08 m²
        area_luz = calcular_area_minima(Fraction(10, 1), 1250)
        self.assertEqual(area_luz, Fraction(2, 25))

    def test_calcular_area_minima_erros(self) -> None:
        with self.assertRaises(ValueError):
            calcular_area_minima(Fraction(0, 1), 2000)
        with self.assertRaises(ValueError):
            calcular_area_minima(Fraction(-5, 1), 2000)
        with self.assertRaises(ValueError):
            calcular_area_minima(Fraction(10, 1), 0)

    def test_selecionar_dimensoes_quadrada(self) -> None:
        # Área mínima 0.04 m² (40.000 mm²) => lado mínimo 200 mm
        w, h, area = selecionar_dimensoes_padronizadas(
            area_minima_m2=Fraction(4, 100),
            forma=FormaGeometrica.QUADRADA,
            tipo=TipoSinalizacao.COMBATE_INCENDIO,
        )
        self.assertEqual(w, 200)
        self.assertEqual(h, 200)
        self.assertEqual(area, Fraction(4, 100))

    def test_selecionar_dimensoes_retangular_2x1(self) -> None:
        # Área mínima 0.02 m² (20.000 mm²) => retangular 200x100mm = 20.000 mm²
        w, h, area = selecionar_dimensoes_padronizadas(
            area_minima_m2=Fraction(2, 100),
            forma=FormaGeometrica.RETANGULAR_2X1,
            tipo=TipoSinalizacao.ORIENTACAO_SALVAMENTO,
        )
        self.assertEqual(w, 200)
        self.assertEqual(h, 100)
        self.assertGreaterEqual(area, Fraction(2, 100))

    def test_selecionar_dimensoes_piso(self) -> None:
        w, h, area = selecionar_dimensoes_padronizadas(
            area_minima_m2=Fraction(1, 100),
            forma=FormaGeometrica.QUADRADA,
            tipo=TipoSinalizacao.COMPLEMENTAR_PISO,
        )
        self.assertEqual(w, 1000)
        self.assertEqual(h, 1000)
        self.assertEqual(area, Fraction(1, 1))

    def test_selecionar_dimensoes_circular_e_triangular(self) -> None:
        w_c, h_c, area_c = selecionar_dimensoes_padronizadas(
            area_minima_m2=Fraction(1, 50),
            forma=FormaGeometrica.CIRCULAR,
            tipo=TipoSinalizacao.PROIBICAO,
        )
        self.assertEqual(w_c, h_c)
        self.assertGreaterEqual(w_c, 100)

        w_t, h_t, area_t = selecionar_dimensoes_padronizadas(
            area_minima_m2=Fraction(1, 50),
            forma=FormaGeometrica.TRIANGULAR,
            tipo=TipoSinalizacao.ALERTA,
        )
        self.assertEqual(w_t, h_t)
        self.assertGreaterEqual(w_t, 100)

    def test_resolver_altura_instalacao(self) -> None:
        # Padrões
        alt_sup, alertas_sup = resolver_altura_instalacao(PosicaoInstalacao.SUPERIOR, None)
        self.assertEqual(alt_sup, Fraction(21, 10))
        self.assertEqual(len(alertas_sup), 0)

        alt_med, alertas_med = resolver_altura_instalacao(PosicaoInstalacao.MEDIA, None)
        self.assertEqual(alt_med, Fraction(135, 100))
        self.assertEqual(len(alertas_med), 0)

        alt_rod, alertas_rod = resolver_altura_instalacao(PosicaoInstalacao.RODAPE, None)
        self.assertEqual(alt_rod, Fraction(25, 100))
        self.assertEqual(len(alertas_rod), 0)

        # Inconformidades
        _, alertas_sup_err = resolver_altura_instalacao(PosicaoInstalacao.SUPERIOR, Fraction(15, 10))
        self.assertEqual(len(alertas_sup_err), 1)

        _, alertas_med_err = resolver_altura_instalacao(PosicaoInstalacao.MEDIA, Fraction(10, 10))
        self.assertEqual(len(alertas_med_err), 1)

        _, alertas_rod_err = resolver_altura_instalacao(PosicaoInstalacao.RODAPE, Fraction(6, 10))
        self.assertEqual(len(alertas_rod_err), 1)

    def test_dimensionar_placa(self) -> None:
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
        res = dimensionar_placa(placa)
        self.assertEqual(res.placa_id, "EXT-01")
        self.assertEqual(res.fator_k, 2000)
        self.assertEqual(res.area_minima_calculada_m2, Fraction(64, 2000))
        self.assertTrue(res.conforme_nbr16820)
        self.assertEqual(res.quantidade, 2)

    def test_dimensionar_trecho_rota(self) -> None:
        trecho = DadosTrechoRota(
            id="T-01",
            descricao="Corredor",
            comprimento_m=Fraction(35, 1),
            mudancas_direcao=1,
            portas_saida=2,
        )
        res = dimensionar_trecho_rota(trecho)
        # 35m com limite de 15m => ceil(35/15) = 3 vãos.
        # Espaçamento efetivo: 35/3 ≈ 11.67 m <= 15m
        self.assertEqual(res.espacamento_maximo_adotado_m, Fraction(35, 3))
        self.assertEqual(res.placas_intermediarias, 2)
        self.assertEqual(res.placas_mudanca_direcao, 1)
        self.assertEqual(res.placas_portas_saida, 2)
        self.assertEqual(res.placas_calculadas_total, 5)
        self.assertEqual(len(res.placas_geradas), 5)

    def test_dimensionar_trecho_rota_erros(self) -> None:
        with self.assertRaises(ValueError):
            dimensionar_trecho_rota(
                DadosTrechoRota(id="E-1", descricao="Err", comprimento_m=Fraction(0, 1))
            )
        with self.assertRaises(ValueError):
            dimensionar_trecho_rota(
                DadosTrechoRota(id="E-2", descricao="Err", comprimento_m=Fraction(10, 1), mudancas_direcao=-1)
            )

    def test_dimensionar_projeto(self) -> None:
        placa = DadosPlaca(
            id="P-01",
            codigo="E-1",
            descricao="Extintor",
            tipo=TipoSinalizacao.COMBATE_INCENDIO,
            distancia_visualizacao_m=Fraction(6, 1),
            forma=FormaGeometrica.QUADRADA,
            posicao=PosicaoInstalacao.SUPERIOR,
            altura_instalacao_m=Fraction(18, 10),
            categoria_fotoluminescente=CategoriaFotoluminescente.CATEGORIA_W,
            quantidade=3,
        )
        trecho = DadosTrechoRota(
            id="T-01",
            descricao="Rota",
            comprimento_m=Fraction(20, 1),
            mudancas_direcao=0,
            portas_saida=1,
        )
        proj = DadosProjetoSinalizacao(
            identificacao_edificio="Edifício Teste",
            ocupacao="Comercial",
            responsavel_tecnico="Engenharia Lofrano",
            placas_individuais=[placa],
            trechos_rotas=[trecho],
        )
        res = dimensionar_projeto(proj)
        self.assertEqual(res.identificacao_edificio, "Edifício Teste")
        self.assertTrue(res.conformidade_geral)
        self.assertIn("COMBATE_INCENDIO", res.resumo_por_tipo)
        self.assertEqual(res.resumo_por_tipo["COMBATE_INCENDIO"], 3)


if __name__ == "__main__":
    unittest.main()
