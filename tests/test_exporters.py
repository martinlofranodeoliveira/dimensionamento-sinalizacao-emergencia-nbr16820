"""Testes unitários dos exportadores: memorial descritivo, CSV sanitizado e ZIP determinístico."""

import os
import tempfile
import unittest
import zipfile
from fractions import Fraction

from sinalizacao_nbr16820.calculator import dimensionar_projeto
from sinalizacao_nbr16820.exporters import (
    _fmt,
    _sanitizar_campo_csv,
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
    TipoSinalizacao,
)


class TestExporters(unittest.TestCase):
    """Valida a geração de relatórios técnicos, proteção de planilhas e determinismo ZIP."""

    def setUp(self) -> None:
        self.placa = DadosPlaca(
            id="P-01",
            codigo="S-1",
            descricao="Saída de Emergência Principal",
            tipo=TipoSinalizacao.ORIENTACAO_SALVAMENTO,
            distancia_visualizacao_m=Fraction(10, 1),
            forma=FormaGeometrica.RETANGULAR_2X1,
            posicao=PosicaoInstalacao.SUPERIOR,
            altura_instalacao_m=Fraction(21, 10),
            categoria_fotoluminescente=CategoriaFotoluminescente.CATEGORIA_W,
            quantidade=2,
        )
        self.trecho = DadosTrechoRota(
            id="T-01",
            descricao="Corredor Térreo",
            comprimento_m=Fraction(30, 1),
            mudancas_direcao=1,
            portas_saida=1,
        )
        self.proj = DadosProjetoSinalizacao(
            identificacao_edificio="Edifício Comercial Alpha",
            ocupacao="Comercial",
            responsavel_tecnico="Eng. Martin Lofrano",
            placas_individuais=[self.placa],
            trechos_rotas=[self.trecho],
        )
        self.resultado = dimensionar_projeto(self.proj)

    def test_fmt_fracao(self) -> None:
        self.assertEqual(_fmt(Fraction(10, 1), 2), "10.0")
        self.assertEqual(_fmt(Fraction(1, 2), 2), "0.50")
        self.assertEqual(_fmt(Fraction(1, 4), 2), "0.25")
        self.assertEqual(_fmt(Fraction(21, 10), 2), "2.10")

    def test_sanitizar_campo_csv(self) -> None:
        self.assertEqual(_sanitizar_campo_csv("=SOMA(A1:A10)"), "'=SOMA(A1:A10)")
        self.assertEqual(_sanitizar_campo_csv("+12345"), "'+12345")
        self.assertEqual(_sanitizar_campo_csv("-12345"), "'-12345")
        self.assertEqual(_sanitizar_campo_csv("@CMD"), "'@CMD")
        self.assertEqual(_sanitizar_campo_csv("Texto Normal"), "Texto Normal")

    def test_gerar_memorial_descritivo(self) -> None:
        rel = gerar_memorial_descritivo(self.resultado)
        self.assertIn("LOFRANO TECNOLOGIA", rel)
        self.assertIn("NBR 16820:2020", rel)
        self.assertIn("Edifício Comercial Alpha", rel)
        self.assertIn("A = d² / K", rel)
        self.assertIn("S-1", rel)
        self.assertIn("Corredor Térreo", rel)

    def test_gerar_csv_sanitizado(self) -> None:
        csv_texto = gerar_csv_sanitizado(self.resultado)
        linhas = csv_texto.strip().split("\n")
        self.assertGreaterEqual(len(linhas), 2)
        cabecalho = linhas[0].split(";")
        self.assertIn("codigo", cabecalho)
        self.assertIn("area_minima_m2", cabecalho)
        self.assertIn("conforme_nbr16820", cabecalho)

    def test_gerar_pacote_zip_determinismo_e_exclusividade(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_caminho = os.path.join(tmpdir, "pacote_sinalizacao.zip")
            gerar_pacote_zip(self.resultado, zip_caminho, svg_conteudo="<svg></svg>")

            self.assertTrue(os.path.exists(zip_caminho))

            with zipfile.ZipFile(zip_caminho, "r") as zf:
                nomes = zf.namelist()
                self.assertIn("memorial_descritivo.txt", nomes)
                self.assertIn("projeto_sinalizacao.json", nomes)
                self.assertIn("relatorio_placas.csv", nomes)
                self.assertIn("painel_sinalizacao.svg", nomes)

                # Verifica se o timestamp dos membros é determinístico (2026, 1, 1, 0, 0, 0)
                for info in zf.infolist():
                    self.assertEqual(info.date_time, (2026, 1, 1, 0, 0, 0))

            # Teste de colisão / O_EXCL: tentar gerar no mesmo arquivo existente deve falhar
            with self.assertRaises(FileExistsError):
                gerar_pacote_zip(self.resultado, zip_caminho)


if __name__ == "__main__":
    unittest.main()
