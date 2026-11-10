"""Testes de casos avançados, cenários reais e casos de borda da NBR 16820."""

import glob
import os
import unittest
from fractions import Fraction

from sinalizacao_nbr16820.calculator import (
    dimensionar_placa,
    dimensionar_projeto,
    dimensionar_trecho_rota,
    selecionar_dimensoes_padronizadas,
)
from sinalizacao_nbr16820.codecs import carregar_projeto_sinalizacao_json
from sinalizacao_nbr16820.models import (
    CategoriaFotoluminescente,
    DadosPlaca,
    DadosProjetoSinalizacao,
    DadosTrechoRota,
    FormaGeometrica,
    PosicaoInstalacao,
    TipoSinalizacao,
)


class TestCasosAvancados(unittest.TestCase):
    """Testes com cenários de alta complexidade, rotas extensas e casos de borda."""

    def test_todos_exemplos_carregam_e_dimensionam_com_sucesso(self) -> None:
        raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        arquivos = glob.glob(os.path.join(raiz, "examples", "*.json"))
        self.assertGreaterEqual(len(arquivos), 3)

        for arq in arquivos:
            with open(arq, "r", encoding="utf-8") as f:
                conteudo = f.read()
            proj = carregar_projeto_sinalizacao_json(conteudo)
            res = dimensionar_projeto(proj)
            self.assertGreater(res.total_placas_unidades, 0)
            self.assertTrue(res.conformidade_geral)
            self.assertGreater(len(res.placas), 0)

    def test_rota_extensa_100_metros(self) -> None:
        # Trecho de 100 metros com 4 mudanças de direção e 3 portas
        # vaos = ceil(100/15) = 7 vaos
        # placas intermediárias = 6
        # placas portas = 3
        # placas curvas = 4
        # Total = 13 placas
        trecho = DadosTrechoRota(
            id="ROTA-100M",
            descricao="Galpão Logístico Extenso",
            comprimento_m=Fraction(100, 1),
            mudancas_direcao=4,
            portas_saida=3,
        )
        res = dimensionar_trecho_rota(trecho)
        self.assertEqual(res.placas_intermediarias, 6)
        self.assertEqual(res.placas_mudanca_direcao, 4)
        self.assertEqual(res.placas_portas_saida, 3)
        self.assertEqual(res.placas_calculadas_total, 13)
        self.assertLessEqual(res.espacamento_maximo_adotado_m, Fraction(15, 1))

    def test_trecho_curto_menor_que_15m(self) -> None:
        # Trecho de 8 metros com 1 porta e 0 curvas
        # vaos = ceil(8/15) = 1 vao
        # intermediárias = 0
        trecho = DadosTrechoRota(
            id="ROTA-CURTA",
            descricao="Hall de Acesso",
            comprimento_m=Fraction(8, 1),
            mudancas_direcao=0,
            portas_saida=1,
        )
        res = dimensionar_trecho_rota(trecho)
        self.assertEqual(res.placas_intermediarias, 0)
        self.assertEqual(res.placas_portas_saida, 1)
        self.assertEqual(res.placas_calculadas_total, 1)
        self.assertEqual(res.espacamento_maximo_adotado_m, Fraction(8, 1))

    def test_alerta_distancia_elevada(self) -> None:
        # d = 35 metros (> 30 m) deve gerar observação/alerta
        placa = DadosPlaca(
            id="P-DIST",
            codigo="S-1",
            descricao="Saída Longa",
            tipo=TipoSinalizacao.ORIENTACAO_SALVAMENTO,
            distancia_visualizacao_m=Fraction(35, 1),
            forma=FormaGeometrica.RETANGULAR_2X1,
            posicao=PosicaoInstalacao.SUPERIOR,
            altura_instalacao_m=Fraction(21, 10),
            categoria_fotoluminescente=CategoriaFotoluminescente.CATEGORIA_W,
            quantidade=1,
        )
        res = dimensionar_placa(placa)
        self.assertTrue(any("Distância de visualização elevada" in obs for obs in res.observacoes))

    def test_alerta_fotoluminescencia_invalida_sem_luz_direta(self) -> None:
        # Placa sem luz direta e com fotoluminescência marcada como NAO_APLICAVEL
        placa = DadosPlaca(
            id="P-FOTO",
            codigo="S-1",
            descricao="Saída Sem Fotoluminescência",
            tipo=TipoSinalizacao.ORIENTACAO_SALVAMENTO,
            distancia_visualizacao_m=Fraction(10, 1),
            iluminacao_direta=False,
            forma=FormaGeometrica.RETANGULAR_2X1,
            categoria_fotoluminescente=CategoriaFotoluminescente.NAO_APLICAVEL,
            posicao=PosicaoInstalacao.SUPERIOR,
            altura_instalacao_m=Fraction(21, 10),
            quantidade=1,
        )
        res = dimensionar_placa(placa)
        self.assertTrue(any("fotoluminescente" in obs for obs in res.observacoes))

    def test_dimensoes_retangulares_grandes_fora_da_tabela(self) -> None:
        # Área mínima grande (ex: d = 50m, K = 2000 => A = 2500 / 2000 = 1.25 m²)
        # Deve calcular H e W múltiplos de 50mm sem falhar
        w, h, area = selecionar_dimensoes_padronizadas(
            area_minima_m2=Fraction(125, 100),
            forma=FormaGeometrica.RETANGULAR_2X1,
            tipo=TipoSinalizacao.ORIENTACAO_SALVAMENTO,
        )
        self.assertGreaterEqual(area, Fraction(125, 100))
        self.assertEqual(w, h * 2)

    def test_dimensoes_quadradas_grandes_fora_da_tabela(self) -> None:
        # Área mínima grande para placa quadrada (ex: 0.50 m²)
        w, h, area = selecionar_dimensoes_padronizadas(
            area_minima_m2=Fraction(50, 100),
            forma=FormaGeometrica.QUADRADA,
            tipo=TipoSinalizacao.COMBATE_INCENDIO,
        )
        self.assertGreaterEqual(area, Fraction(50, 100))
        self.assertEqual(w, h)
        self.assertEqual(w % 50, 0)

    def test_dimensoes_retangular_3x1(self) -> None:
        w, h, area = selecionar_dimensoes_padronizadas(
            area_minima_m2=Fraction(6, 100),
            forma=FormaGeometrica.RETANGULAR_3X1,
            tipo=TipoSinalizacao.ORIENTACAO_SALVAMENTO,
        )
        self.assertEqual(w, h * 3)
        self.assertGreaterEqual(area, Fraction(6, 100))


if __name__ == "__main__":
    unittest.main()
