"""Testes unitários dos modelos e estruturas de dados da sinalização NBR 16820."""

import unittest
from fractions import Fraction

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


class TestModels(unittest.TestCase):
    """Testa inicialização, validação de campos e imutabilidade dos modelos de dados."""

    def test_enums_valores(self) -> None:
        self.assertEqual(TipoSinalizacao.ORIENTACAO_SALVAMENTO.value, "ORIENTACAO_SALVAMENTO")
        self.assertEqual(TipoSinalizacao.COMBATE_INCENDIO.value, "COMBATE_INCENDIO")
        self.assertEqual(TipoSinalizacao.ALARME.value, "ALARME")
        self.assertEqual(TipoSinalizacao.PROIBICAO.value, "PROIBICAO")
        self.assertEqual(TipoSinalizacao.ALERTA.value, "ALERTA")
        self.assertEqual(TipoSinalizacao.COMPLEMENTAR_PISO.value, "COMPLEMENTAR_PISO")
        self.assertEqual(TipoSinalizacao.COMPLEMENTAR_RODAPE.value, "COMPLEMENTAR_RODAPE")

        self.assertEqual(CategoriaFotoluminescente.CATEGORIA_W.value, "CATEGORIA_W")
        self.assertEqual(CategoriaFotoluminescente.CATEGORIA_X.value, "CATEGORIA_X")
        self.assertEqual(CategoriaFotoluminescente.NAO_APLICAVEL.value, "NAO_APLICAVEL")

        self.assertEqual(FormaGeometrica.QUADRADA.value, "QUADRADA")
        self.assertEqual(FormaGeometrica.RETANGULAR_2X1.value, "RETANGULAR_2X1")
        self.assertEqual(FormaGeometrica.CIRCULAR.value, "CIRCULAR")
        self.assertEqual(FormaGeometrica.TRIANGULAR.value, "TRIANGULAR")

        self.assertEqual(PosicaoInstalacao.SUPERIOR.value, "SUPERIOR")
        self.assertEqual(PosicaoInstalacao.MEDIA.value, "MEDIA")
        self.assertEqual(PosicaoInstalacao.RODAPE.value, "RODAPE")
        self.assertEqual(PosicaoInstalacao.PISO.value, "PISO")

    def test_dados_placa_criacao(self) -> None:
        placa = DadosPlaca(
            id="P-01",
            codigo="S-1",
            descricao="Saída de Emergência",
            tipo=TipoSinalizacao.ORIENTACAO_SALVAMENTO,
            distancia_visualizacao_m=Fraction(10, 1),
            iluminacao_direta=False,
            forma=FormaGeometrica.RETANGULAR_2X1,
            categoria_fotoluminescente=CategoriaFotoluminescente.CATEGORIA_W,
            posicao=PosicaoInstalacao.SUPERIOR,
            altura_instalacao_m=Fraction(21, 10),
            quantidade=2,
        )
        self.assertEqual(placa.id, "P-01")
        self.assertEqual(placa.codigo, "S-1")
        self.assertEqual(placa.distancia_visualizacao_m, 10)
        self.assertEqual(placa.quantidade, 2)

    def test_dados_trecho_rota_criacao(self) -> None:
        trecho = DadosTrechoRota(
            id="T-01",
            descricao="Corredor de Saída",
            comprimento_m=Fraction(30, 1),
            mudancas_direcao=1,
            portas_saida=2,
            distancia_visualizacao_desejada_m=Fraction(12, 1),
            iluminacao_direta=False,
            categoria_fotoluminescente=CategoriaFotoluminescente.CATEGORIA_W,
        )
        self.assertEqual(trecho.id, "T-01")
        self.assertEqual(trecho.comprimento_m, 30)
        self.assertEqual(trecho.mudancas_direcao, 1)
        self.assertEqual(trecho.portas_saida, 2)

    def test_dados_projeto_sinalizacao_criacao(self) -> None:
        proj = DadosProjetoSinalizacao(
            identificacao_edificio="Edifício Teste",
            ocupacao="Comercial",
            responsavel_tecnico="Eng. Martin",
        )
        self.assertEqual(proj.identificacao_edificio, "Edifício Teste")
        self.assertEqual(len(proj.placas_individuais), 0)
        self.assertEqual(len(proj.trechos_rotas), 0)

    def test_resultado_placa_imutabilidade(self) -> None:
        res = ResultadoPlaca(
            placa_id="P-01",
            codigo="S-1",
            descricao="Saída",
            tipo=TipoSinalizacao.ORIENTACAO_SALVAMENTO,
            distancia_visualizacao_m=Fraction(10, 1),
            fator_k=2000,
            area_minima_calculada_m2=Fraction(1, 20),
            area_adotada_m2=Fraction(3, 50),
            largura_mm=300,
            altura_mm=150,
            forma=FormaGeometrica.RETANGULAR_2X1,
            posicao=PosicaoInstalacao.SUPERIOR,
            altura_instalacao_m=Fraction(21, 10),
            categoria_fotoluminescente=CategoriaFotoluminescente.CATEGORIA_W,
            quantidade=1,
            conforme_nbr16820=True,
            observacoes=[],
        )
        with self.assertRaises(Exception):
            res.largura_mm = 400  # type: ignore

    def test_resultado_projeto_criacao(self) -> None:
        res_proj = ResultadoProjeto(
            identificacao_edificio="Edifício Teste",
            ocupacao="Comercial",
            responsavel_tecnico="Eng. Martin",
            total_placas_unidades=10,
            resumo_por_tipo={"ORIENTACAO_SALVAMENTO": 10},
            placas=[],
            trechos=[],
            conformidade_geral=True,
            alertas=[],
        )
        self.assertEqual(res_proj.total_placas_unidades, 10)
        self.assertTrue(res_proj.conformidade_geral)


if __name__ == "__main__":
    unittest.main()
