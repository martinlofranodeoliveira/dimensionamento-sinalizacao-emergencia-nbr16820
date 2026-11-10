"""Testes unitários da Interface de Linha de Comando (CLI)."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from sinalizacao_nbr16820.cli import main


class TestCLI(unittest.TestCase):
    """Valida argumentos, subcomandos e saída da CLI."""

    def test_cli_ajuda(self) -> None:
        f = io.StringIO()
        with redirect_stdout(f):
            with self.assertRaises(SystemExit) as cm:
                main(["--ajuda"])
            self.assertEqual(cm.exception.code, 0)
        saida = f.getvalue()
        self.assertIn("sinalizacao-nbr16820", saida)
        self.assertIn("16820", saida)

    def test_cli_versao(self) -> None:
        f = io.StringIO()
        with redirect_stdout(f):
            with self.assertRaises(SystemExit) as cm:
                main(["--versao"])
            self.assertEqual(cm.exception.code, 0)
        self.assertIn("1.0.0", f.getvalue())

    def test_cli_catalogo(self) -> None:
        f = io.StringIO()
        with redirect_stdout(f):
            cod = main(["catalogo"])
            self.assertEqual(cod, 0)
        saida = f.getvalue()
        self.assertIn("LOFRANO TECNOLOGIA", saida)
        self.assertIn("A = d² / K", saida)
        self.assertIn("15,0 m", saida)
        self.assertIn("Categoria W", saida)

    def test_cli_gerar_exemplo_stdout(self) -> None:
        f = io.StringIO()
        with redirect_stdout(f):
            cod = main(["gerar-exemplo"])
            self.assertEqual(cod, 0)
        saida = f.getvalue()
        self.assertIn("identificacao_edificio", saida)
        self.assertIn("placas_individuais", saida)

    def test_cli_gerar_exemplo_arquivo(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = os.path.join(tmpdir, "exemplo_gerado.json")
            cod = main(["gerar-exemplo", "-o", caminho])
            self.assertEqual(cod, 0)
            self.assertTrue(os.path.exists(caminho))

    def test_cli_calcular_sucesso(self) -> None:
        raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        caminho_exemplo = os.path.join(raiz, "examples", "edificio_comercial_rotas_fuga.json")

        f = io.StringIO()
        with redirect_stdout(f):
            cod = main(["calcular", caminho_exemplo])
            self.assertEqual(cod, 0)
        saida = f.getvalue()
        self.assertIn("LOFRANO TECNOLOGIA", saida)
        self.assertIn("Torre Corporativa Faria Lima", saida)

    def test_cli_calcular_formatos(self) -> None:
        raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        caminho_exemplo = os.path.join(raiz, "examples", "edificio_comercial_rotas_fuga.json")

        for formato in ["json", "csv", "svg"]:
            f = io.StringIO()
            with redirect_stdout(f):
                cod = main(["calcular", caminho_exemplo, "-f", formato])
                self.assertEqual(cod, 0)
            saida = f.getvalue()
            if formato == "json":
                self.assertIn("ABNT NBR 16820:2020", saida)
            elif formato == "csv":
                self.assertIn("codigo;descricao", saida)
            elif formato == "svg":
                self.assertIn("<svg", saida)

    def test_cli_calcular_pacote_zip(self) -> None:
        raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        caminho_exemplo = os.path.join(raiz, "examples", "edificio_comercial_rotas_fuga.json")

        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_zip = os.path.join(tmpdir, "resultado.zip")
            f = io.StringIO()
            with redirect_stdout(f):
                cod = main(["calcular", caminho_exemplo, "-z", caminho_zip])
                self.assertEqual(cod, 0)
            self.assertTrue(os.path.exists(caminho_zip))

    def test_cli_arquivo_inexistente(self) -> None:
        f_err = io.StringIO()
        with redirect_stderr(f_err):
            cod = main(["calcular", "arquivo_fantasma.json"])
            self.assertEqual(cod, 1)
        self.assertIn("Erro ao ler arquivo", f_err.getvalue())


if __name__ == "__main__":
    unittest.main()
