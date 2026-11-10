"""Exportadores técnicos: memorial descritivo, CSV sanitizado e ZIP determinístico.

Atende rigorosamente aos padrões de qualidade da Lofrano Tecnologia e ABNT NBR 16820:2020.
"""

import csv
import io
import os
import zipfile
from fractions import Fraction
from typing import Optional

from sinalizacao_nbr16820.codecs import exportar_resultado_json
from sinalizacao_nbr16820.models import ResultadoProjeto


def _fmt(val: Fraction, casas: int = 2) -> str:
    """Formata fração para string decimal com número fixo de casas sem ponto flutuante IEEE-754."""
    num = val.numerator
    den = val.denominator
    if den == 1:
        return f"{num}.0" if casas > 0 else str(num)
    inteiro = num // den
    resto = abs(num % den)
    fator = 10**casas
    frac_parte = (resto * fator + den // 2) // den
    return f"{inteiro}.{frac_parte:0{casas}d}"


def _sanitizar_campo_csv(val: str) -> str:
    """Sanitiza strings contra injeção de fórmulas de planilhas eletrônicas."""
    if val and val[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val}"
    return val


def gerar_memorial_descritivo(res: ResultadoProjeto) -> str:
    """Gera memorial descritivo técnico detalhado de sinalização conforme ABNT NBR 16820:2020."""
    linhas: list[str] = []
    w = 82
    linhas.append("=" * w)
    linhas.append("        LOFRANO TECNOLOGIA - ENGENHARIA DE SEGURANÇA CONTRA INCÊNDIO")
    linhas.append("      PROJETO E DIMENSIONAMENTO DE SINALIZAÇÃO DE EMERGÊNCIA (NBR 16820:2020)")
    linhas.append("=" * w)
    linhas.append(f"Edificação:            {res.identificacao_edificio}")
    linhas.append(f"Ocupação / Uso:        {res.ocupacao}")
    linhas.append(f"Responsável Técnico:   {res.responsavel_tecnico}")
    linhas.append(f"Total de Placas (un):  {res.total_placas_unidades}")
    status_glo = "CONFORME" if res.conformidade_geral else "NÃO CONFORME / COM PENDÊNCIAS"
    linhas.append(f"Status Global NBR:     {status_glo}")
    linhas.append("-" * w)

    linhas.append("1. RESUMO QUANTITATIVO POR TIPO DE SINALIZAÇÃO")
    for tipo, qtd in sorted(res.resumo_por_tipo.items()):
        linhas.append(f"  * {tipo:<30}: {qtd:>4} unidade(s)")
    linhas.append("-" * w)

    linhas.append("2. MEMÓRIA DETALHADA DE DIMENSIONAMENTO DAS PLACAS")
    linhas.append("Fórmula de Dimensionamento: A = d² / K (Item 5.1.2 da NBR 16820:2020)")
    linhas.append("Onde: A = Área mínima (m²), d = Distância de visualização (m), K = Fator de visibilidade.")
    linhas.append("")

    for idx, p in enumerate(res.placas, start=1):
        status_p = "CONFORME" if p.conforme_nbr16820 else "NÃO CONFORME"
        linhas.append(f"  [{idx:02d}] {p.codigo} - {p.descricao} [{status_p}]")
        linhas.append(f"       Tipo: {p.tipo.value} | Formato: {p.forma.value}")
        linhas.append(
            f"       Distância Máx. (d): {_fmt(p.distancia_visualizacao_m, 2)} m | "
            f"Fator K: {p.fator_k} | "
            f"Área Mínima: {_fmt(p.area_minima_calculada_m2, 4)} m²"
        )
        linhas.append(
            f"       Dimensões Adotadas: {p.largura_mm} mm x {p.altura_mm} mm "
            f"(Área: {_fmt(p.area_adotada_m2, 4)} m²)"
        )
        linhas.append(
            f"       Instalação: {p.posicao.value} a {_fmt(p.altura_instalacao_m, 2)} m do piso | "
            f"Fotoluminescência: {p.categoria_fotoluminescente.value}"
        )
        linhas.append(f"       Quantidade: {p.quantidade} un.")

        if p.observacoes:
            for obs in p.observacoes:
                linhas.append(f"       [OBSERVAÇÃO] {obs}")
        linhas.append("  " + "." * (w - 4))

    if res.trechos:
        linhas.append("-" * w)
        linhas.append("3. AUDITORIA DE TRECHOS DE ROTAS DE FUGA (ESPAÇAMENTO MÁXIMO 15,0 m)")
        for t in res.trechos:
            linhas.append(f"  Trecho: {t.trecho_id} - {t.descricao}")
            linhas.append(
                f"    Comprimento: {_fmt(t.comprimento_m, 2)} m | "
                f"Espaçamento Efetivo: {_fmt(t.espacamento_maximo_adotado_m, 2)} m (Norma: <= 15,0 m)"
            )
            linhas.append(
                f"    Composição: {t.placas_portas_saida} porta(s) + "
                f"{t.placas_intermediarias} intermediária(s) + "
                f"{t.placas_mudanca_direcao} curva(s)/desvio(s) = "
                f"{t.placas_calculadas_total} placas geradas"
            )

    if res.alertas:
        linhas.append("-" * w)
        linhas.append("4. ALERTAS E REQUISITOS DE CONFORMIDADE NORMATIVA")
        for alerta in res.alertas:
            linhas.append(f"  [ALERTA] {alerta}")

    linhas.append("-" * w)
    linhas.append("5. DIRETRIZES DE INSTALAÇÃO, INSPEÇÃO E MANUTENÇÃO NORMATIVA")
    linhas.append("  * Fixação: As placas devem ser fixadas de forma indelével e resistente ao calor.")
    linhas.append("  * Limpeza: Não utilizar solventes agressivos que degradem a camada fotoluminescente.")
    linhas.append("  * Inspeção Semestral: Verificar integridade física e legibilidade visual de cada sinal.")
    linhas.append("  * Medição de Luminância: Aferição fotométrica a cada 24 meses conforme Anexo B da NBR 16820.")
    linhas.append("  * Desobstrução: É vedada a colocação de objetos ou elementos decorativos que obstruam a visão.")
    linhas.append("=" * w)
    linhas.append("Emitido via Lofrano Tecnologia - Conforme ABNT NBR 16820:2020")
    linhas.append("=" * w)

    return "\n".join(linhas)


def gerar_csv_sanitizado(res: ResultadoProjeto) -> str:
    """Gera resumo tabular estruturado em CSV sanitizado contra injeção de fórmulas."""
    saida = io.StringIO()
    writer = csv.writer(saida, delimiter=";", lineterminator="\n")

    writer.writerow([
        _sanitizar_campo_csv("placa_id"),
        _sanitizar_campo_csv("codigo"),
        _sanitizar_campo_csv("descricao"),
        _sanitizar_campo_csv("tipo"),
        _sanitizar_campo_csv("distancia_m"),
        _sanitizar_campo_csv("fator_k"),
        _sanitizar_campo_csv("area_minima_m2"),
        _sanitizar_campo_csv("largura_mm"),
        _sanitizar_campo_csv("altura_mm"),
        _sanitizar_campo_csv("area_adotada_m2"),
        _sanitizar_campo_csv("forma"),
        _sanitizar_campo_csv("posicao"),
        _sanitizar_campo_csv("altura_instalacao_m"),
        _sanitizar_campo_csv("categoria_fotoluminescente"),
        _sanitizar_campo_csv("quantidade"),
        _sanitizar_campo_csv("conforme_nbr16820"),
    ])

    for p in res.placas:
        writer.writerow([
            _sanitizar_campo_csv(p.placa_id),
            _sanitizar_campo_csv(p.codigo),
            _sanitizar_campo_csv(p.descricao),
            p.tipo.value,
            _fmt(p.distancia_visualizacao_m, 2),
            str(p.fator_k),
            _fmt(p.area_minima_calculada_m2, 4),
            str(p.largura_mm),
            str(p.altura_mm),
            _fmt(p.area_adotada_m2, 4),
            p.forma.value,
            p.posicao.value,
            _fmt(p.altura_instalacao_m, 2),
            p.categoria_fotoluminescente.value,
            str(p.quantidade),
            "SIM" if p.conforme_nbr16820 else "NAO",
        ])

    return saida.getvalue()


def gerar_pacote_zip(
    res: ResultadoProjeto,
    caminho_zip: str,
    svg_conteudo: Optional[str] = None,
) -> None:
    """Gera pacote determinístico ZIP com O_EXCL, evitando sobrescrita acidental."""
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0)
    fd = os.open(caminho_zip, flags, 0o644)
    fixed_time = (2026, 1, 1, 0, 0, 0)

    try:
        with open(fd, "wb", closefd=True) as f_out:
            with zipfile.ZipFile(f_out, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                # 1. Memorial descritivo em texto
                txt = gerar_memorial_descritivo(res).encode("utf-8")
                zi_txt = zipfile.ZipInfo(filename="memorial_descritivo.txt", date_time=fixed_time)
                zf.writestr(zi_txt, txt)

                # 2. Dados em JSON canônico
                js = exportar_resultado_json(res).encode("utf-8")
                zi_js = zipfile.ZipInfo(filename="projeto_sinalizacao.json", date_time=fixed_time)
                zf.writestr(zi_js, js)

                # 3. Resumo tabular em CSV sanitizado
                csv_data = gerar_csv_sanitizado(res).encode("utf-8")
                zi_csv = zipfile.ZipInfo(filename="relatorio_placas.csv", date_time=fixed_time)
                zf.writestr(zi_csv, csv_data)

                # 4. Diagrama vetorial SVG se fornecido
                if svg_conteudo is not None:
                    zi_svg = zipfile.ZipInfo(filename="painel_sinalizacao.svg", date_time=fixed_time)
                    zf.writestr(zi_svg, svg_conteudo.encode("utf-8"))
    except Exception:
        if os.path.exists(caminho_zip):
            try:
                os.remove(caminho_zip)
            except OSError:
                pass
        raise
