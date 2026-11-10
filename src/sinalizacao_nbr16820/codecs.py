"""Codec JSON canônico RFC 8259 para sinalização de emergência ABNT NBR 16820:2020.

Garante ausência estrita de números de ponto flutuante (float), rejeição de BOM,
rejeição de chaves duplicadas e limite de recursão.
"""

import json
from enum import Enum
from fractions import Fraction
from typing import Any

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


def _rejeitar_float(valor: str) -> None:
    raise ValueError(
        f"Ponto flutuante IEEE-754 ({valor}) não é permitido. "
        "Utilize inteiros ou strings numéricas fracionárias/decimais exatas."
    )


def _rejeitar_chaves_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    resultado: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError(f"Chave duplicada encontrada no JSON: '{chave}'")
        resultado[chave] = valor
    return resultado


def _verificar_profundidade(obj: Any, profundidade: int = 1, limite: int = 32) -> None:
    if profundidade > limite:
        raise ValueError(
            f"Profundidade da estrutura JSON ({profundidade}) excede o limite máximo permitido de {limite}."
        )
    if isinstance(obj, dict):
        for v in obj.values():
            _verificar_profundidade(v, profundidade + 1, limite)
    elif isinstance(obj, list):
        for elem in obj:
            _verificar_profundidade(elem, profundidade + 1, limite)


def _para_fracao(val: Any) -> Fraction:
    if isinstance(val, (int, str)):
        return Fraction(val)
    if isinstance(val, Fraction):
        return val
    raise ValueError(f"Tipo inválido para conversão fracionária: {type(val).__name__} ({val})")


def _serializar_valor(val: Any) -> Any:
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return val.numerator
        return f"{val.numerator}/{val.denominator}"
    if isinstance(val, Enum):
        return val.value
    if isinstance(val, tuple):
        return [_serializar_valor(x) for x in val]
    if isinstance(val, list):
        return [_serializar_valor(x) for x in val]
    if isinstance(val, dict):
        return {k: _serializar_valor(v) for k, v in val.items()}
    return val


def carregar_projeto_sinalizacao_json(conteudo: str) -> DadosProjetoSinalizacao:
    """Carrega e valida o projeto de sinalização a partir de string JSON canônica RFC 8259."""
    if conteudo.startswith(("\ufeff", "\xef\xbb\xbf")):
        raise ValueError("Byte Order Mark (BOM) detectado. O arquivo deve ser codificado em UTF-8 puro.")

    try:
        dados = json.loads(
            conteudo,
            object_pairs_hook=_rejeitar_chaves_duplicadas,
            parse_float=_rejeitar_float,
        )
    except json.JSONDecodeError as err:
        raise ValueError(f"Erro de decodificação JSON: {err}") from err

    _verificar_profundidade(dados)

    if not isinstance(dados, dict):
        raise ValueError("O JSON raiz do projeto deve ser um objeto dicionário.")

    edificio = str(dados.get("identificacao_edificio", "Edifício Sem Identificação"))
    ocupacao = str(dados.get("ocupacao", "Comercial / Administrativo"))
    responsavel = str(dados.get("responsavel_tecnico", "Engenharia Lofrano"))

    cat_padrao_str = str(dados.get("categoria_fotoluminescente_padrao", "CATEGORIA_W")).upper()
    try:
        cat_padrao = CategoriaFotoluminescente(cat_padrao_str)
    except ValueError:
        cat_padrao = CategoriaFotoluminescente.CATEGORIA_W

    # Placas individuais
    placas_raw = dados.get("placas_individuais", [])
    if not isinstance(placas_raw, list):
        raise ValueError("O campo 'placas_individuais' deve ser uma lista.")

    placas_parsed: list[DadosPlaca] = []
    for idx, p in enumerate(placas_raw):
        if not isinstance(p, dict):
            raise ValueError(f"Elemento da placa no índice {idx} deve ser um objeto JSON.")

        p_id = str(p.get("id", f"PLACA-{idx + 1:02d}"))
        codigo = str(p.get("codigo", "S-1"))
        descricao = str(p.get("descricao", "Sinalização de Emergência"))

        tipo_str = str(p.get("tipo", "ORIENTACAO_SALVAMENTO")).upper()
        try:
            tipo = TipoSinalizacao(tipo_str)
        except ValueError:
            tipo = TipoSinalizacao.ORIENTACAO_SALVAMENTO

        dist_raw = p.get("distancia_visualizacao_m", 10)
        dist_m = _para_fracao(dist_raw)

        ilum_direta = bool(p.get("iluminacao_direta", False))

        forma_str = str(p.get("forma", "RETANGULAR_2X1")).upper()
        try:
            forma = FormaGeometrica(forma_str)
        except ValueError:
            forma = FormaGeometrica.RETANGULAR_2X1

        cat_str = str(p.get("categoria_fotoluminescente", cat_padrao.value)).upper()
        try:
            cat_foto = CategoriaFotoluminescente(cat_str)
        except ValueError:
            cat_foto = cat_padrao

        pos_str = str(p.get("posicao", "SUPERIOR")).upper()
        try:
            posicao = PosicaoInstalacao(pos_str)
        except ValueError:
            posicao = PosicaoInstalacao.SUPERIOR

        alt_raw = p.get("altura_instalacao_m")
        altura_m = _para_fracao(alt_raw) if alt_raw is not None else None

        qtd = int(p.get("quantidade", 1))
        if qtd <= 0:
            qtd = 1

        placas_parsed.append(
            DadosPlaca(
                id=p_id,
                codigo=codigo,
                descricao=descricao,
                tipo=tipo,
                distancia_visualizacao_m=dist_m,
                iluminacao_direta=ilum_direta,
                forma=forma,
                categoria_fotoluminescente=cat_foto,
                posicao=posicao,
                altura_instalacao_m=altura_m,
                quantidade=qtd,
            )
        )

    # Trechos de rota
    trechos_raw = dados.get("trechos_rotas", [])
    if not isinstance(trechos_raw, list):
        raise ValueError("O campo 'trechos_rotas' deve ser uma lista.")

    trechos_parsed: list[DadosTrechoRota] = []
    for idx, t in enumerate(trechos_raw):
        if not isinstance(t, dict):
            raise ValueError(f"Elemento do trecho no índice {idx} deve ser um objeto JSON.")

        t_id = str(t.get("id", f"TRECHO-{idx + 1:02d}"))
        descricao = str(t.get("descricao", f"Trecho de Rota {idx + 1}"))

        comp_raw = t.get("comprimento_m", 15)
        comprimento_m = _para_fracao(comp_raw)

        mudancas = int(t.get("mudancas_direcao", 0))
        portas = int(t.get("portas_saida", 1))

        dist_desejada_raw = t.get("distancia_visualizacao_desejada_m")
        dist_desejada_m = (
            _para_fracao(dist_desejada_raw) if dist_desejada_raw is not None else None
        )

        ilum_direta_t = bool(t.get("iluminacao_direta", False))

        cat_t_str = str(t.get("categoria_fotoluminescente", cat_padrao.value)).upper()
        try:
            cat_t_foto = CategoriaFotoluminescente(cat_t_str)
        except ValueError:
            cat_t_foto = cat_padrao

        trechos_parsed.append(
            DadosTrechoRota(
                id=t_id,
                descricao=descricao,
                comprimento_m=comprimento_m,
                mudancas_direcao=mudancas,
                portas_saida=portas,
                distancia_visualizacao_desejada_m=dist_desejada_m,
                iluminacao_direta=ilum_direta_t,
                categoria_fotoluminescente=cat_t_foto,
            )
        )

    return DadosProjetoSinalizacao(
        identificacao_edificio=edificio,
        ocupacao=ocupacao,
        responsavel_tecnico=responsavel,
        categoria_fotoluminescente_padrao=cat_padrao,
        placas_individuais=placas_parsed,
        trechos_rotas=trechos_parsed,
    )


def exportar_resultado_json(resultado: ResultadoProjeto) -> str:
    """Serializa o resultado de dimensionamento em JSON canônico RFC 8259 determinístico."""
    dados: dict[str, Any] = {
        "norma": "ABNT NBR 16820:2020",
        "identificacao_edificio": resultado.identificacao_edificio,
        "ocupacao": resultado.ocupacao,
        "responsavel_tecnico": resultado.responsavel_tecnico,
        "total_placas_unidades": resultado.total_placas_unidades,
        "resumo_por_tipo": resultado.resumo_por_tipo,
        "conformidade_geral": resultado.conformidade_geral,
        "alertas": list(resultado.alertas),
        "placas": [
            {
                "placa_id": p.placa_id,
                "codigo": p.codigo,
                "descricao": p.descricao,
                "tipo": p.tipo.value,
                "distancia_visualizacao_m": _serializar_valor(p.distancia_visualizacao_m),
                "fator_k": p.fator_k,
                "area_minima_calculada_m2": _serializar_valor(p.area_minima_calculada_m2),
                "area_adotada_m2": _serializar_valor(p.area_adotada_m2),
                "largura_mm": p.largura_mm,
                "altura_mm": p.altura_mm,
                "forma": p.forma.value,
                "posicao": p.posicao.value,
                "altura_instalacao_m": _serializar_valor(p.altura_instalacao_m),
                "categoria_fotoluminescente": p.categoria_fotoluminescente.value,
                "quantidade": p.quantidade,
                "conforme_nbr16820": p.conforme_nbr16820,
                "observacoes": list(p.observacoes),
            }
            for p in resultado.placas
        ],
        "trechos": [
            {
                "trecho_id": t.trecho_id,
                "descricao": t.descricao,
                "comprimento_m": _serializar_valor(t.comprimento_m),
                "placas_calculadas_total": t.placas_calculadas_total,
                "espacamento_maximo_adotado_m": _serializar_valor(t.espacamento_maximo_adotado_m),
                "placas_intermediarias": t.placas_intermediarias,
                "placas_mudanca_direcao": t.placas_mudanca_direcao,
                "placas_portas_saida": t.placas_portas_saida,
                "placas_geradas": [
                    {
                        "placa_id": pg.placa_id,
                        "codigo": pg.codigo,
                        "descricao": pg.descricao,
                        "tipo": pg.tipo.value,
                        "largura_mm": pg.largura_mm,
                        "altura_mm": pg.altura_mm,
                        "altura_instalacao_m": _serializar_valor(pg.altura_instalacao_m),
                    }
                    for pg in t.placas_geradas
                ],
            }
            for t in resultado.trechos
        ],
    }

    return json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True)
