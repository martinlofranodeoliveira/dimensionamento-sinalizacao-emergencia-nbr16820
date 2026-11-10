"""Interface de Linha de Comando (CLI) para dimensionamento de sinalização NBR 16820:2020."""

import argparse
import sys
from typing import Sequence

from sinalizacao_nbr16820 import __version__
from sinalizacao_nbr16820.calculator import dimensionar_projeto
from sinalizacao_nbr16820.codecs import carregar_projeto_sinalizacao_json, exportar_resultado_json
from sinalizacao_nbr16820.exporters import gerar_csv_sanitizado, gerar_memorial_descritivo, gerar_pacote_zip
from sinalizacao_nbr16820.svg_generator import gerar_painel_svg


def _comando_calcular(args: argparse.Namespace) -> int:
    try:
        with open(args.arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except Exception as err:
        print(f"Erro ao ler arquivo de entrada: {err}", file=sys.stderr)
        return 1

    try:
        dados = carregar_projeto_sinalizacao_json(conteudo)
    except Exception as err:
        print(f"Erro ao processar JSON: {err}", file=sys.stderr)
        return 1

    resultado = dimensionar_projeto(dados)

    # Geração do pacote ZIP determinístico se solicitado
    if args.pacote_zip:
        try:
            svg_conteudo = gerar_painel_svg(resultado)
            gerar_pacote_zip(resultado, args.pacote_zip, svg_conteudo)
            print(f"[ZIP] Pacote determinístico gerado com sucesso em '{args.pacote_zip}'")
        except Exception as err:
            print(f"Erro ao gerar pacote ZIP: {err}", file=sys.stderr)
            return 1

    # Formatação da saída solicitada
    formato = args.formato.lower()
    if formato == "json":
        saida_str = exportar_resultado_json(resultado)
    elif formato == "csv":
        saida_str = gerar_csv_sanitizado(resultado)
    elif formato == "svg":
        saida_str = gerar_painel_svg(resultado)
    else:
        saida_str = gerar_memorial_descritivo(resultado)

    if args.saida:
        try:
            with open(args.saida, "w", encoding="utf-8") as f:
                f.write(saida_str)
            print(f"[OK] Saída ({formato}) salva com sucesso em '{args.saida}'")
        except Exception as err:
            print(f"Erro ao salvar arquivo de saída: {err}", file=sys.stderr)
            return 1
    else:
        print(saida_str)

    return 0


def _comando_catalogo(args: argparse.Namespace) -> int:
    print("=" * 82)
    print("    LOFRANO TECNOLOGIA - PARÂMETROS NORMATIVOS DA ABNT NBR 16820:2020")
    print("    Sistemas de Sinalização de Emergência e Pânico Contra Incêndio")
    print("=" * 82)
    print("1. FÓRMULA DE DIMENSIONAMENTO DA ÁREA MÍNIMA (Item 5.1.2)")
    print("  A = d² / K")
    print("  - K = 2000 : Sinalização fotoluminescente ou com iluminação externa")
    print("  - K = 1250 : Sinalização iluminada internamente (luz direta transmitida)")
    print("-" * 82)
    print("2. REQUISITOS DE ESPAÇAMENTO E ROTAS DE FUGA (Item 5.2)")
    print("  - Distância máxima entre placas consecutivas de rota em linha reta: 15,0 m")
    print("  - Mudanças de direção: placa indicativa obrigatória em cada curva ou desvio")
    print("  - Portas de saída de emergência: placa indicativa no eixo sobre a porta")
    print("-" * 82)
    print("3. FAIXAS DE ALTURA REGULAMENTARES DE INSTALAÇÃO (Item 5.3 e Anexo A)")
    print("  - Faixa Superior:  h >= 1,80 m do piso (portas e equipamentos de combate)")
    print("  - Faixa Média:     1,20 m <= h <= 1,50 m (acionadores manuais de alarme)")
    print("  - Faixa Rodapé:    0,10 m <= h <= 0,50 m (guias baixas contínuas de escape)")
    print("  - Solo / Piso:     Pintura 1,00 m x 1,00 m (vermelha com borda amarela 15 cm)")
    print("-" * 82)
    print("4. DESEMPENHO FOTOLUMINESCENTE MÍNIMO (Item 6.1 e Anexo B)")
    print("  - Categoria W : >= 140 mcd/m² (10 min) e >= 20 mcd/m² (60 min) | Atenuação >= 1800 min")
    print("  - Categoria X : >= 210 mcd/m² (10 min) e >= 30 mcd/m² (60 min) | Atenuação >= 1800 min")
    print("  (Atenuação medida até o limite de visibilidade de 0,3 mcd/m²)")
    print("-" * 82)
    print("5. DIMENSÕES E ÁREAS PADRONIZADAS (Tabela 1)")
    print("  - d <= 4,0 m  :  Área >= 0,008 m²  -> 100 x 100 mm  (Quadrada) / 200 x 100 mm (2:1)")
    print("  - d <= 6,7 m  :  Área >= 0,022 m²  -> 150 x 150 mm  (Quadrada) / 300 x 150 mm (2:1)")
    print("  - d <= 8,9 m  :  Área >= 0,040 m²  -> 200 x 200 mm  (Quadrada) / 400 x 200 mm (2:1)")
    print("  - d <= 11,1 m :  Área >= 0,062 m²  -> 250 x 250 mm  (Quadrada) / 500 x 250 mm (2:1)")
    print("  - d <= 13,4 m :  Área >= 0,090 m²  -> 300 x 300 mm  (Quadrada) / 600 x 300 mm (2:1)")
    print("  - d <= 17,8 m :  Área >= 0,160 m²  -> 400 x 400 mm  (Quadrada) / 800 x 400 mm (2:1)")
    print("=" * 82)
    return 0


def _comando_gerar_exemplo(args: argparse.Namespace) -> int:
    exemplo_json = """{
  "identificacao_edificio": "Torre Empresarial Lofrano",
  "ocupacao": "Serviços Profissionais / Escritórios Administrativos",
  "responsavel_tecnico": "Eng. Martin Lofrano de Oliveira - CREA/SP",
  "categoria_fotoluminescente_padrao": "CATEGORIA_W",
  "placas_individuais": [
    {
      "id": "EXT-01",
      "codigo": "E-1",
      "descricao": "Extintor de Incêndio Pó ABC 6kg - Hall Térreo",
      "tipo": "COMBATE_INCENDIO",
      "distancia_visualizacao_m": 8,
      "forma": "QUADRADA",
      "posicao": "SUPERIOR",
      "altura_instalacao_m": "1.80",
      "categoria_fotoluminescente": "CATEGORIA_W",
      "quantidade": 2
    },
    {
      "id": "HID-01",
      "codigo": "H-1",
      "descricao": "Abrigo de Mangueira de Hidrante - Pavimento 1",
      "tipo": "COMBATE_INCENDIO",
      "distancia_visualizacao_m": 10,
      "forma": "QUADRADA",
      "posicao": "SUPERIOR",
      "altura_instalacao_m": "1.80",
      "categoria_fotoluminescente": "CATEGORIA_W",
      "quantidade": 1
    },
    {
      "id": "ALM-01",
      "codigo": "A-1",
      "descricao": "Acionador Manual de Alarme de Incêndio",
      "tipo": "ALARME",
      "distancia_visualizacao_m": 6,
      "forma": "QUADRADA",
      "posicao": "MEDIA",
      "altura_instalacao_m": "1.35",
      "categoria_fotoluminescente": "CATEGORIA_W",
      "quantidade": 2
    },
    {
      "id": "PRO-01",
      "codigo": "P-1",
      "descricao": "Proibido Fumar no Interior do Edifício",
      "tipo": "PROIBICAO",
      "distancia_visualizacao_m": 6,
      "forma": "CIRCULAR",
      "posicao": "SUPERIOR",
      "altura_instalacao_m": "1.80",
      "categoria_fotoluminescente": "CATEGORIA_W",
      "quantidade": 4
    },
    {
      "id": "ALT-01",
      "codigo": "AL-1",
      "descricao": "Perigo: Risco de Alta Tensão - Cabine Primária",
      "tipo": "ALERTA",
      "distancia_visualizacao_m": 8,
      "forma": "TRIANGULAR",
      "posicao": "SUPERIOR",
      "altura_instalacao_m": "1.80",
      "categoria_fotoluminescente": "CATEGORIA_W",
      "quantidade": 2
    },
    {
      "id": "PISO-01",
      "codigo": "CP-1",
      "descricao": "Demarcação de Solo de Extintor (1,00m x 1,00m)",
      "tipo": "COMPLEMENTAR_PISO",
      "distancia_visualizacao_m": 5,
      "forma": "QUADRADA",
      "posicao": "PISO",
      "altura_instalacao_m": 0,
      "categoria_fotoluminescente": "CATEGORIA_W",
      "quantidade": 2
    }
  ],
  "trechos_rotas": [
    {
      "id": "ROTA-TERREO",
      "descricao": "Corredor Central de Acesso à Saída de Emergência - Térreo",
      "comprimento_m": 35,
      "mudancas_direcao": 1,
      "portas_saida": 2,
      "distancia_visualizacao_desejada_m": 12,
      "iluminacao_direta": false,
      "categoria_fotoluminescente": "CATEGORIA_W"
    },
    {
      "id": "ROTA-PAV1",
      "descricao": "Circulação Pavimento Tipo 1 até a Escada Enclausurada",
      "comprimento_m": 22,
      "mudancas_direcao": 1,
      "portas_saida": 1,
      "distancia_visualizacao_desejada_m": 10,
      "iluminacao_direta": false,
      "categoria_fotoluminescente": "CATEGORIA_W"
    }
  ]
}
"""
    if args.saida:
        try:
            with open(args.saida, "w", encoding="utf-8") as f:
                f.write(exemplo_json)
            print(f"[OK] Modelo de exemplo gravado em '{args.saida}'")
        except Exception as err:
            print(f"Erro ao gravar arquivo de exemplo: {err}", file=sys.stderr)
            return 1
    else:
        print(exemplo_json)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada principal da CLI de sinalização NBR 16820."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="sinalizacao-nbr16820",
        description="Dimensionamento e Projeto de Sinalização de Emergência Contra Incêndio (ABNT NBR 16820:2020) - Lofrano Tecnologia",
        add_help=False,
    )

    parser.add_argument("-h", "--help", "--ajuda", action="help", help="Exibe esta mensagem de ajuda e encerra.")
    parser.add_argument(
        "-v",
        "--version",
        "--versao",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Exibe a versão do programa.",
    )

    subparsers = parser.add_subparsers(dest="subcomando", title="Subcomandos Disponíveis")

    # Subcomando 'calcular'
    parser_calc = subparsers.add_parser("calcular", help="Dimensiona e audita o sistema de sinalização a partir de JSON.")
    parser_calc.add_argument("arquivo", help="Caminho do arquivo JSON de entrada do projeto.")
    parser_calc.add_argument(
        "-f",
        "--formato",
        choices=["texto", "json", "csv", "svg"],
        default="texto",
        help="Formato de saída dos resultados (padrão: texto).",
    )
    parser_calc.add_argument("-o", "--saida", help="Arquivo de destino para salvar a saída.")
    parser_calc.add_argument("-z", "--pacote-zip", help="Gera pacote ZIP determinístico completo no caminho especificado.")

    # Subcomando 'catalogo'
    subparsers.add_parser("catalogo", help="Exibe o catálogo de referências e critérios normativos da NBR 16820.")

    # Subcomando 'gerar-exemplo'
    parser_ex = subparsers.add_parser("gerar-exemplo", help="Gera arquivo JSON modelo de exemplo para preenchimento.")
    parser_ex.add_argument("-o", "--saida", help="Arquivo de destino para gravar o JSON de exemplo.")

    args = parser.parse_args(argv)

    if not args.subcomando:
        parser.print_help()
        return 0

    if args.subcomando == "calcular":
        return _comando_calcular(args)
    elif args.subcomando == "catalogo":
        return _comando_catalogo(args)
    elif args.subcomando == "gerar-exemplo":
        return _comando_gerar_exemplo(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
