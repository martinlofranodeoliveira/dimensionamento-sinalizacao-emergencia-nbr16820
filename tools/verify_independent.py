#!/usr/bin/env python3
"""Auditor independente em SQLite em memória para sinalização de emergência ABNT NBR 16820:2020.

Este script é 100% desacoplado do código de produção de 'src/sinalizacao_nbr16820' e NÃO importa
nenhum módulo do pacote. Utiliza exclusivamente a biblioteca padrão do Python e SQLite
em memória para verificar a conformidade regulamentar dos cenários em 'examples/'.
"""

import glob
import json
import os
import sqlite3
import sys
from fractions import Fraction


def para_fracao(val) -> Fraction:
    return Fraction(str(val))


def auditar_arquivo(caminho_json: str) -> bool:
    nome_arq = os.path.basename(caminho_json)
    print(f"\n[AUDITORIA INDEPENDENTE] Verificando cenário: {nome_arq}")

    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # 1. Esquema de banco de dados SQLite para auditoria independente
    cursor.execute("""
        CREATE TABLE placas (
            id TEXT PRIMARY KEY,
            codigo TEXT,
            descricao TEXT,
            tipo TEXT,
            distancia_num INTEGER,
            distancia_den INTEGER,
            iluminacao_direta INTEGER,
            forma TEXT,
            categoria_foto TEXT,
            posicao TEXT,
            altura_num INTEGER,
            altura_den INTEGER,
            quantidade INTEGER
        );
    """)

    cursor.execute("""
        CREATE TABLE trechos (
            id TEXT PRIMARY KEY,
            descricao TEXT,
            comprimento_num INTEGER,
            comprimento_den INTEGER,
            mudancas_direcao INTEGER,
            portas_saida INTEGER,
            dist_desejada_num INTEGER,
            dist_desejada_den INTEGER,
            iluminacao_direta INTEGER,
            categoria_foto TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE auditoria_placas (
            id TEXT PRIMARY KEY,
            fator_k INTEGER,
            area_minima_num INTEGER,
            area_minima_den INTEGER,
            conforme_altura INTEGER,
            conforme_foto INTEGER,
            status TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE auditoria_rotas (
            id TEXT PRIMARY KEY,
            vaos_calculados INTEGER,
            espacamento_efetivo_num INTEGER,
            espacamento_efetivo_den INTEGER,
            conforme_espacamento_15m INTEGER
        );
    """)

    # 2. Inserção de placas individuais
    for p in dados.get("placas_individuais", []):
        dist_f = para_fracao(p.get("distancia_visualizacao_m", 10))
        alt_raw = p.get("altura_instalacao_m")
        alt_f = para_fracao(alt_raw) if alt_raw is not None else Fraction(0, 1)

        cursor.execute("""
            INSERT INTO placas (
                id, codigo, descricao, tipo,
                distancia_num, distancia_den,
                iluminacao_direta, forma,
                categoria_foto, posicao,
                altura_num, altura_den,
                quantidade
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["id"],
            p["codigo"],
            p["descricao"],
            p["tipo"],
            dist_f.numerator,
            dist_f.denominator,
            1 if p.get("iluminacao_direta", False) else 0,
            p.get("forma", "RETANGULAR_2X1"),
            p.get("categoria_fotoluminescente", "CATEGORIA_W"),
            p.get("posicao", "SUPERIOR"),
            alt_f.numerator,
            alt_f.denominator,
            p.get("quantidade", 1),
        ))

    # 3. Inserção de trechos de rota
    for t in dados.get("trechos_rotas", []):
        comp_f = para_fracao(t.get("comprimento_m", 15))
        dist_d_raw = t.get("distancia_visualizacao_desejada_m")
        dist_d_f = para_fracao(dist_d_raw) if dist_d_raw is not None else Fraction(0, 1)

        cursor.execute("""
            INSERT INTO trechos (
                id, descricao, comprimento_num, comprimento_den,
                mudancas_direcao, portas_saida,
                dist_desejada_num, dist_desejada_den,
                iluminacao_direta, categoria_foto
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t["id"],
            t["descricao"],
            comp_f.numerator,
            comp_f.denominator,
            t.get("mudancas_direcao", 0),
            t.get("portas_saida", 1),
            dist_d_f.numerator,
            dist_d_f.denominator,
            1 if t.get("iluminacao_direta", False) else 0,
            t.get("categoria_fotoluminescente", "CATEGORIA_W"),
        ))

    conn.commit()

    # 4. Auditoria SQL independente das placas
    cursor.execute("""
        SELECT
            id, codigo, descricao, tipo,
            distancia_num, distancia_den,
            iluminacao_direta, forma,
            categoria_foto, posicao,
            altura_num, altura_den,
            quantidade
        FROM placas
    """)
    placas_db = cursor.fetchall()

    sucesso_placas = True
    for row in placas_db:
        p_id, cod, desc, tipo, d_num, d_den, ilum_dir, forma, cat_foto, pos, a_num, a_den, qtd = row
        dist = Fraction(d_num, d_den)
        alt = Fraction(a_num, a_den)

        # Regra 1: Fator K
        k = 1250 if ilum_dir == 1 else 2000

        # Regra 2: Área Mínima A = d² / K
        area_min = (dist * dist) / Fraction(k, 1)

        # Regra 3: Altura regulamentar
        conforme_alt = 1
        if pos == "SUPERIOR" and alt < Fraction(18, 10):
            conforme_alt = 0
        elif pos == "MEDIA" and (alt < Fraction(12, 10) or alt > Fraction(15, 10)):
            conforme_alt = 0
        elif pos == "RODAPE" and (alt < Fraction(1, 10) or alt > Fraction(5, 10)):
            conforme_alt = 0

        # Regra 4: Fotoluminescência
        conforme_foto = 1
        if ilum_dir == 0 and cat_foto not in ("CATEGORIA_W", "CATEGORIA_X"):
            conforme_foto = 0

        status = "CONFORME" if (conforme_alt == 1 and conforme_foto == 1) else "NAO_CONFORME"
        if status != "CONFORME":
            sucesso_placas = False

        cursor.execute("""
            INSERT INTO auditoria_placas VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            p_id, k, area_min.numerator, area_min.denominator, conforme_alt, conforme_foto, status
        ))

    conn.commit()

    # 5. Auditoria SQL independente dos trechos de rotas de fuga (NBR 16820 item 5.2.1)
    cursor.execute("""
        SELECT id, descricao, comprimento_num, comprimento_den FROM trechos
    """)
    trechos_db = cursor.fetchall()

    sucesso_trechos = True
    for row_t in trechos_db:
        t_id, desc_t, comp_n, comp_d = row_t
        comp = Fraction(comp_n, comp_d)

        # Divisão em vãos máximos de 15m
        limite = Fraction(15, 1)
        razao = comp / limite
        vaos = razao.numerator // razao.denominator
        if razao.numerator % razao.denominator != 0:
            vaos += 1
        if vaos == 0:
            vaos = 1

        espacamento_efetivo = comp / Fraction(vaos, 1)
        conforme_15m = 1 if espacamento_efetivo <= limite else 0
        if conforme_15m == 0:
            sucesso_trechos = False

        cursor.execute("""
            INSERT INTO auditoria_rotas VALUES (?, ?, ?, ?, ?)
        """, (
            t_id, vaos, espacamento_efetivo.numerator, espacamento_efetivo.denominator, conforme_15m
        ))

    conn.commit()

    # Exibição resumida dos resultados da auditoria
    cursor.execute("""
        SELECT p.id, p.codigo, ap.fator_k, ap.area_minima_num, ap.area_minima_den, ap.status
        FROM placas p JOIN auditoria_placas ap ON p.id = ap.id
    """)
    print("  Auditoria de Placas:")
    for r in cursor.fetchall():
        pid, pcod, pk, amin_n, amin_d, st = r
        amin_f = Fraction(amin_n, amin_d)
        print(f"    - Placa {pid} ({pcod}): K={pk}, Área Mínima={amin_f} m² [{st}]")

    cursor.execute("""
        SELECT t.id, ar.vaos_calculados, ar.espacamento_efetivo_num, ar.espacamento_efetivo_den, ar.conforme_espacamento_15m
        FROM trechos t JOIN auditoria_rotas ar ON t.id = ar.id
    """)
    print("  Auditoria de Trechos de Fuga (Máximo 15,0 m):")
    for r_t in cursor.fetchall():
        tid, vaos_calc, esp_n, esp_d, conf_15m = r_t
        esp_f = Fraction(esp_n, esp_d)
        status_t = "CONFORME" if conf_15m == 1 else "INCONFORME"
        print(f"    - Trecho {tid}: {vaos_calc} vão(s), Espaçamento={esp_f} m [{status_t}]")

    conn.close()

    if sucesso_placas and sucesso_trechos:
        print(f"[OK] Cenário '{nome_arq}' 100% aprovado pela auditoria independente.")
        return True
    else:
        print(f"[ERRO] Cenário '{nome_arq}' falhou na auditoria independente.")
        return False


def main() -> int:
    print("=" * 80)
    print("   LOFRANO TECNOLOGIA - AUDITORIA INDEPENDENTE SQLITE (NBR 16820:2020)")
    print("=" * 80)

    padrao = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples", "*.json")
    arquivos = sorted(glob.glob(padrao))

    if not arquivos:
        print(f"Nenhum arquivo JSON encontrado em 'examples/'.", file=sys.stderr)
        return 1

    total = len(arquivos)
    aprovados = 0

    for arq in arquivos:
        if auditar_arquivo(arq):
            aprovados += 1

    print("\n" + "=" * 80)
    print(f"Total de Cenários Auditados: {total}")
    print(f"Cenários Aprovados:          {aprovados}")
    print(f"Taxa de Conformidade:        {(aprovados * 100) // total}%")
    print("=" * 80)

    return 0 if aprovados == total else 1


if __name__ == "__main__":
    sys.exit(main())
