"""Testes unitários dos codecs JSON canônicos RFC 8259 sem ponto flutuante."""

import json
import unittest
from fractions import Fraction

from sinalizacao_nbr16820.calculator import dimensionar_projeto
from sinalizacao_nbr16820.codecs import (
    carregar_projeto_sinalizacao_json,
    exportar_resultado_json,
)
from sinalizacao_nbr16820.models import (
    CategoriaFotoluminescente,
    DadosPlaca,
    DadosProjetoSinalizacao,
    FormaGeometrica,
    PosicaoInstalacao,
    TipoSinalizacao,
)


class TestCodecs(unittest.TestCase):
    """Garante conformidade estrita com RFC 8259, ausência de float e integridade estrutural."""

    def test_rejeicao_bom(self) -> None:
        conteudo_bom = "\ufeff{\"identificacao_edificio\": \"Teste\"}"
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_sinalizacao_json(conteudo_bom)
        self.assertIn("BOM", str(ctx.exception))

    def test_rejeicao_float(self) -> None:
        conteudo_float = """{
            "identificacao_edificio": "Teste",
            "placas_individuais": [
                {
                    "id": "P-01",
                    "distancia_visualizacao_m": 10.5
                }
            ]
        }"""
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_sinalizacao_json(conteudo_float)
        self.assertIn("Ponto flutuante", str(ctx.exception))

    def test_rejeicao_chave_duplicada(self) -> None:
        conteudo_dup = """{
            "identificacao_edificio": "Edificio 1",
            "identificacao_edificio": "Edificio 2"
        }"""
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_sinalizacao_json(conteudo_dup)
        self.assertIn("Chave duplicada", str(ctx.exception))

    def test_rejeicao_profundidade_excessiva(self) -> None:
        nested: dict = {}
        curr = nested
        for _ in range(35):
            curr["child"] = {}
            curr = curr["child"]
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_sinalizacao_json(json.dumps(nested))
        self.assertIn("Profundidade", str(ctx.exception))

    def test_carregamento_valido(self) -> None:
        json_valido = """{
            "identificacao_edificio": "Edifício Alfa",
            "ocupacao": "Escritórios",
            "responsavel_tecnico": "Eng. Lofrano",
            "categoria_fotoluminescente_padrao": "CATEGORIA_W",
            "placas_individuais": [
                {
                    "id": "P-01",
                    "codigo": "S-1",
                    "descricao": "Saída",
                    "tipo": "ORIENTACAO_SALVAMENTO",
                    "distancia_visualizacao_m": "10",
                    "iluminacao_direta": false,
                    "forma": "RETANGULAR_2X1",
                    "categoria_fotoluminescente": "CATEGORIA_W",
                    "posicao": "SUPERIOR",
                    "altura_instalacao_m": "2.10",
                    "quantidade": 2
                }
            ],
            "trechos_rotas": [
                {
                    "id": "T-01",
                    "descricao": "Corredor 1",
                    "comprimento_m": "25",
                    "mudancas_direcao": 1,
                    "portas_saida": 1
                }
            ]
        }"""
        proj = carregar_projeto_sinalizacao_json(json_valido)
        self.assertEqual(proj.identificacao_edificio, "Edifício Alfa")
        self.assertEqual(len(proj.placas_individuais), 1)
        self.assertEqual(proj.placas_individuais[0].distancia_visualizacao_m, 10)
        self.assertEqual(proj.placas_individuais[0].quantidade, 2)
        self.assertEqual(len(proj.trechos_rotas), 1)
        self.assertEqual(proj.trechos_rotas[0].comprimento_m, 25)

    def test_exportar_resultado_json(self) -> None:
        placa = DadosPlaca(
            id="P-01",
            codigo="S-1",
            descricao="Saída",
            tipo=TipoSinalizacao.ORIENTACAO_SALVAMENTO,
            distancia_visualizacao_m=Fraction(10, 1),
            forma=FormaGeometrica.RETANGULAR_2X1,
            posicao=PosicaoInstalacao.SUPERIOR,
            altura_instalacao_m=Fraction(21, 10),
            categoria_fotoluminescente=CategoriaFotoluminescente.CATEGORIA_W,
            quantidade=1,
        )
        proj = DadosProjetoSinalizacao(
            identificacao_edificio="Edifício Beta",
            ocupacao="Comercial",
            responsavel_tecnico="Eng. Lofrano",
            placas_individuais=[placa],
            trechos_rotas=[],
        )
        res = dimensionar_projeto(proj)
        json_str = exportar_resultado_json(res)
        self.assertIn("ABNT NBR 16820:2020", json_str)
        self.assertIn("Edifício Beta", json_str)
        self.assertIn("total_placas_unidades", json_str)

        # Decodifica de volta garantindo JSON válido
        decodificado = json.loads(json_str)
        self.assertEqual(decodificado["total_placas_unidades"], 1)
        self.assertTrue(decodificado["conformidade_geral"])


if __name__ == "__main__":
    unittest.main()
