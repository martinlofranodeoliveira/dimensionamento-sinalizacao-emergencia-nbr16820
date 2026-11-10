"""Gerador de painel técnico vetorial SVG para sinalização de emergência ABNT NBR 16820:2020."""

from sinalizacao_nbr16820.constants import (
    COR_CONTRASTE_BRANCO_HEX,
    COR_CONTRASTE_PRETO_HEX,
    COR_FOTOLUMINESCENTE_HEX,
    COR_SEGURANCA_AMARELO_HEX,
    COR_SEGURANCA_VERDE_HEX,
    COR_SEGURANCA_VERMELHO_HEX,
)
from sinalizacao_nbr16820.exporters import _fmt
from sinalizacao_nbr16820.models import ResultadoProjeto


def gerar_painel_svg(res: ResultadoProjeto) -> str:
    """Gera painel vetorial SVG de alta resolução (1440x900) com infográfico técnico da NBR 16820:2020."""
    largura = 1440
    altura = 900

    linhas: list[str] = []
    linhas.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" width="{largura}" height="{altura}">')
    linhas.append('  <defs>')
    linhas.append('    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">')
    linhas.append('      <stop offset="0%" stop-color="#0a0f1d" />')
    linhas.append('      <stop offset="100%" stop-color="#151e33" />')
    linhas.append('    </linearGradient>')
    linhas.append('    <linearGradient id="glowVerde" x1="0" y1="0" x2="0" y2="1">')
    linhas.append('      <stop offset="0%" stop-color="#059669" />')
    linhas.append('      <stop offset="100%" stop-color="#047857" />')
    linhas.append('    </linearGradient>')
    linhas.append('    <linearGradient id="glowVermelho" x1="0" y1="0" x2="0" y2="1">')
    linhas.append('      <stop offset="0%" stop-color="#e11d48" />')
    linhas.append('      <stop offset="100%" stop-color="#be123c" />')
    linhas.append('    </linearGradient>')
    linhas.append('    <filter id="luminescencia" x="-20%" y="-20%" width="140%" height="140%">')
    linhas.append('      <feGaussianBlur stdDeviation="3" result="blur" />')
    linhas.append('      <feComposite in="SourceGraphic" in2="blur" operator="over" />')
    linhas.append('    </filter>')
    linhas.append('  </defs>')

    # Fundo do canvas
    linhas.append(f'  <rect width="{largura}" height="{altura}" fill="url(#bgGrad)" />')

    # Cabeçalho Principal (y: 20..95)
    linhas.append('  <rect x="30" y="20" width="1380" height="75" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />')
    linhas.append('  <text x="55" y="52" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="bold">LOFRANO TECNOLOGIA — ENGENHARIA DE SEGURANÇA CONTRA INCÊNDIO</text>')
    linhas.append('  <text x="55" y="76" fill="#38bdf8" font-family="system-ui, -apple-system, sans-serif" font-size="14">SINALIZAÇÃO DE EMERGÊNCIA E ROTAS DE FUGA — ABNT NBR 16820:2020 (ZERO-FLOAT)</text>')

    status_txt = "CONFORME NBR 16820" if res.conformidade_geral else "PENDÊNCIAS NORMATIVAS"
    status_bg = "#065f46" if res.conformidade_geral else "#991b1b"
    status_stroke = "#10b981" if res.conformidade_geral else "#ef4444"
    status_cor = "#34d399" if res.conformidade_geral else "#f87171"

    linhas.append(f'  <rect x="1140" y="35" width="250" height="45" rx="6" fill="{status_bg}" stroke="{status_stroke}" stroke-width="1.5" />')
    linhas.append(f'  <text x="1265" y="63" text-anchor="middle" fill="{status_cor}" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">{status_txt}</text>')

    # PAINEL ESQUERDO: Catálogo Visual de Placas Normativas (x: 30, y: 110, w: 460, h: 760)
    linhas.append('  <g transform="translate(30, 110)">')
    linhas.append('    <rect width="460" height="760" rx="8" fill="#111827" stroke="#374151" stroke-width="1" />')
    linhas.append('    <text x="25" y="35" fill="#f9fafb" font-family="system-ui, sans-serif" font-size="16" font-weight="bold">SÍMBOLOS E PLACAS NORMATIVAS</text>')
    linhas.append('    <text x="25" y="55" fill="#9ca3af" font-family="system-ui, sans-serif" font-size="12">Cores, pictogramas e padrões conforme NBR 16820 / NBR 7195</text>')
    linhas.append('    <line x1="25" y1="68" x2="435" y2="68" stroke="#374151" stroke-width="1" />')

    # Placa 1: Saída de Emergência (Verde, 2:1)
    linhas.append('    <!-- Placa S-1: Saída de Emergência -->')
    linhas.append('    <rect x="25" y="85" width="410" height="95" rx="6" fill="#1f2937" stroke="#374151" stroke-width="1" />')
    linhas.append(f'    <rect x="40" y="100" width="130" height="65" rx="4" fill="{COR_SEGURANCA_VERDE_HEX}" stroke="#22c55e" stroke-width="2" />')
    # Pictograma de homem correndo e seta em branco
    linhas.append('    <circle cx="80" cy="120" r="5" fill="#ffffff" />')
    linhas.append('    <path d="M 75 128 L 85 128 L 88 140 L 80 148 L 73 148 L 79 138 Z" fill="#ffffff" />')
    linhas.append('    <path d="M 110 132 L 140 132 L 132 124 M 140 132 L 132 140" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none" />')
    linhas.append('    <text x="185" y="118" fill="#ffffff" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">S-1: SAÍDA DE EMERGÊNCIA</text>')
    linhas.append('    <text x="185" y="136" fill="#a7f3d0" font-family="system-ui, sans-serif" font-size="11">Orientação e Salvamento (200x100 mm)</text>')
    linhas.append('    <text x="185" y="152" fill="#9ca3af" font-family="system-ui, sans-serif" font-size="11">Verde segurança com símbolo fotoluminescente</text>')

    # Placa 2: Extintor de Incêndio (Vermelho, 1:1)
    linhas.append('    <!-- Placa E-1: Extintor de Incêndio -->')
    linhas.append('    <rect x="25" y="195" width="410" height="95" rx="6" fill="#1f2937" stroke="#374151" stroke-width="1" />')
    linhas.append(f'    <rect x="70" y="210" width="65" height="65" rx="4" fill="{COR_SEGURANCA_VERMELHO_HEX}" stroke="#f43f5e" stroke-width="2" />')
    # Pictograma de cilindro de extintor
    linhas.append('    <rect x="95" y="228" width="16" height="34" rx="3" fill="#ffffff" />')
    linhas.append('    <rect x="99" y="222" width="8" height="6" fill="#ffffff" />')
    linhas.append('    <path d="M 97 222 L 91 228 L 91 242" stroke="#ffffff" stroke-width="2" fill="none" />')
    linhas.append('    <text x="185" y="228" fill="#ffffff" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">E-1: EXTINTOR DE INCÊNDIO</text>')
    linhas.append('    <text x="185" y="246" fill="#fecdd3" font-family="system-ui, sans-serif" font-size="11">Alarme e Combate (200x200 mm)</text>')
    linhas.append('    <text x="185" y="262" fill="#9ca3af" font-family="system-ui, sans-serif" font-size="11">Instalação a 1,80 m do piso acabado</text>')

    # Placa 3: Acionador Manual de Alarme (Vermelho, 1:1)
    linhas.append('    <!-- Placa A-1: Acionador Manual de Alarme -->')
    linhas.append('    <rect x="25" y="305" width="410" height="95" rx="6" fill="#1f2937" stroke="#374151" stroke-width="1" />')
    linhas.append(f'    <rect x="70" y="320" width="65" height="65" rx="4" fill="{COR_SEGURANCA_VERMELHO_HEX}" stroke="#f43f5e" stroke-width="2" />')
    # Pictograma de campainha/alarme
    linhas.append('    <circle cx="102" cy="350" r="12" fill="#ffffff" />')
    linhas.append('    <circle cx="102" cy="350" r="6" fill="#be123c" />')
    linhas.append('    <path d="M 90 338 L 86 334 M 114 338 L 118 334" stroke="#ffffff" stroke-width="2" />')
    linhas.append('    <text x="185" y="338" fill="#ffffff" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">A-1: BOTOEIRA DE ALARME</text>')
    linhas.append('    <text x="185" y="356" fill="#fecdd3" font-family="system-ui, sans-serif" font-size="11">Alarme de Emergência (150x150 mm)</text>')
    linhas.append('    <text x="185" y="372" fill="#9ca3af" font-family="system-ui, sans-serif" font-size="11">Instalação a 1,20 m – 1,50 m do piso</text>')

    # Placa 4: Proibido Fumar (Circular)
    linhas.append('    <!-- Placa P-1: Proibido Fumar -->')
    linhas.append('    <rect x="25" y="415" width="410" height="95" rx="6" fill="#1f2937" stroke="#374151" stroke-width="1" />')
    linhas.append('    <circle cx="102" cy="462" r="32" fill="#ffffff" stroke="#be123c" stroke-width="6" />')
    linhas.append('    <line x1="80" y1="440" x2="124" y2="484" stroke="#be123c" stroke-width="6" />')
    linhas.append('    <rect x="86" y="459" width="30" height="6" fill="#1a1a1a" />')
    linhas.append('    <text x="185" y="448" fill="#ffffff" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">P-1: PROIBIDO FUMAR</text>')
    linhas.append('    <text x="185" y="466" fill="#fecdd3" font-family="system-ui, sans-serif" font-size="11">Sinalização de Proibição (Diâmetro 200 mm)</text>')
    linhas.append('    <text x="185" y="482" fill="#9ca3af" font-family="system-ui, sans-serif" font-size="11">Orla e barra diagonal vermelhas a 45°</text>')

    # Placa 5: Alerta Alta Tensão (Triangular)
    linhas.append('    <!-- Placa AL-1: Alerta Alta Tensão -->')
    linhas.append('    <rect x="25" y="525" width="410" height="95" rx="6" fill="#1f2937" stroke="#374151" stroke-width="1" />')
    linhas.append(f'    <polygon points="102,540 68,598 136,598" fill="{COR_SEGURANCA_AMARELO_HEX}" stroke="#1a1a1a" stroke-width="3" />')
    linhas.append('    <path d="M 104 554 L 96 572 L 103 572 L 99 588 L 110 568 L 103 568 Z" fill="#1a1a1a" />')
    linhas.append('    <text x="185" y="558" fill="#ffffff" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">AL-1: RISCO DE CHOQUE ELÉTRICO</text>')
    linhas.append('    <text x="185" y="576" fill="#fef08a" font-family="system-ui, sans-serif" font-size="11">Sinalização de Alerta (Lado 200 mm)</text>')
    linhas.append('    <text x="185" y="592" fill="#9ca3af" font-family="system-ui, sans-serif" font-size="11">Triângulo equilátero amarelo com símbolo preto</text>')

    # Demarcação de Solo de Extintor (Piso 1,00m x 1,00m)
    linhas.append('    <!-- Demarcação de Piso de Extintor -->')
    linhas.append('    <rect x="25" y="635" width="410" height="105" rx="6" fill="#1f2937" stroke="#374151" stroke-width="1" />')
    linhas.append(f'    <rect x="70" y="650" width="65" height="65" fill="{COR_SEGURANCA_AMARELO_HEX}" stroke="#ca8a04" stroke-width="1" />')
    linhas.append(f'    <rect x="80" y="660" width="45" height="45" fill="{COR_SEGURANCA_VERMELHO_HEX}" />')
    linhas.append('    <text x="185" y="665" fill="#ffffff" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">DEMARCAÇÃO DE SOLO (PISO)</text>')
    linhas.append('    <text x="185" y="683" fill="#fecdd3" font-family="system-ui, sans-serif" font-size="11">Quadrado 1,00 m x 1,00 m</text>')
    linhas.append('    <text x="185" y="700" fill="#9ca3af" font-family="system-ui, sans-serif" font-size="11">Pintura vermelha central com borda amarela de 15 cm</text>')
    linhas.append('    <text x="185" y="718" fill="#fca5a5" font-family="system-ui, sans-serif" font-size="10">Área mantida rigorosamente desobstruída</text>')

    linhas.append('  </g>')

    # PAINEL CENTRAL/DIREITO SUPERIOR: Corte Esquemático de Alturas de Instalação (x: 510, y: 110, w: 900, h: 420)
    linhas.append('  <g transform="translate(510, 110)">')
    linhas.append('    <rect width="900" height="420" rx="8" fill="#111827" stroke="#374151" stroke-width="1" />')
    linhas.append('    <text x="30" y="35" fill="#f9fafb" font-family="system-ui, sans-serif" font-size="16" font-weight="bold">CORTE ESQUEMÁTICO — ALTURAS DE INSTALAÇÃO REGULAMENTARES</text>')
    linhas.append('    <text x="30" y="55" fill="#9ca3af" font-family="system-ui, sans-serif" font-size="12">ABNT NBR 16820:2020 Item 5.3 e Anexo A — Posicionamento e faixas de visibilidade</text>')
    linhas.append('    <line x1="30" y1="68" x2="870" y2="68" stroke="#374151" stroke-width="1" />')

    # Desenho esquemático da parede e elementos
    # Nível do Piso (y = 350)
    # Laje / Teto (y = 90)
    linhas.append('    <!-- Teto / Laje -->')
    linhas.append('    <rect x="50" y="85" width="700" height="15" fill="#334155" />')
    linhas.append('    <text x="760" y="97" fill="#64748b" font-family="monospace" font-size="11">+3.00 m (Laje/Forro)</text>')

    # Parede de fundo
    linhas.append('    <rect x="50" y="100" width="700" height="250" fill="#1e293b" opacity="0.6" />')

    # Nível do Piso
    linhas.append('    <rect x="50" y="350" width="700" height="20" fill="#475569" />')
    linhas.append('    <text x="760" y="365" fill="#64748b" font-family="monospace" font-size="11">±0.00 m (Piso Acabado)</text>')

    # 1. Porta de Saída de Emergência (x: 100, y: 155, w: 100, h: 195) -> topo em 2.10m
    linhas.append('    <!-- Porta de Saída de Emergência -->')
    linhas.append('    <rect x="90" y="155" width="105" height="195" fill="#991b1b" stroke="#fca5a5" stroke-width="2" />')
    linhas.append('    <rect x="95" y="250" width="95" height="8" rx="2" fill="#e2e8f0" />')  # Barra antipânico a 1.00m
    linhas.append('    <!-- Placa S-1 sobre a porta (h >= 1.80m, tipicamente 2.10m) -->')
    linhas.append(f'    <rect x="105" y="125" width="75" height="25" rx="3" fill="{COR_SEGURANCA_VERDE_HEX}" stroke="#22c55e" stroke-width="1.5" />')
    linhas.append('    <text x="142" y="141" text-anchor="middle" fill="#ffffff" font-family="system-ui, sans-serif" font-size="8" font-weight="bold">SAÍDA</text>')

    # 2. Extintor de Incêndio de Parede (x: 320)
    linhas.append('    <!-- Placa de Extintor a 1.80m -->')
    linhas.append(f'    <rect x="305" y="170" width="40" height="40" rx="3" fill="{COR_SEGURANCA_VERMELHO_HEX}" stroke="#f43f5e" stroke-width="1.5" />')
    linhas.append('    <text x="325" y="195" text-anchor="middle" fill="#ffffff" font-family="system-ui, sans-serif" font-size="10" font-weight="bold">E</text>')
    # Cilindro de extintor suspenso
    linhas.append('    <rect x="313" y="240" width="24" height="60" rx="6" fill="#be123c" stroke="#f87171" stroke-width="1" />')
    # Demarcação de solo no piso
    linhas.append(f'    <rect x="290" y="345" width="70" height="10" fill="{COR_SEGURANCA_AMARELO_HEX}" />')
    linhas.append(f'    <rect x="300" y="347" width="50" height="6" fill="{COR_SEGURANCA_VERMELHO_HEX}" />')

    # 3. Botoeira de Alarme / Acionador Manual (x: 500)
    linhas.append('    <!-- Botoeira de Alarme na Faixa Média (1.20 - 1.50m) -->')
    linhas.append(f'    <rect x="485" y="215" width="35" height="35" rx="3" fill="{COR_SEGURANCA_VERMELHO_HEX}" stroke="#f43f5e" stroke-width="1.5" />')
    linhas.append('    <text x="502" y="237" text-anchor="middle" fill="#ffffff" font-family="system-ui, sans-serif" font-size="9" font-weight="bold">A</text>')

    # 4. Sinalização Baixa / Rodapé de Fuga (x: 600..740)
    linhas.append('    <!-- Sinalização de Rodapé (0.10 - 0.50m) -->')
    linhas.append(f'    <rect x="590" y="315" width="120" height="18" rx="2" fill="{COR_SEGURANCA_VERDE_HEX}" stroke="#22c55e" stroke-width="1" filter="url(#luminescencia)" />')
    linhas.append('    <text x="650" y="328" text-anchor="middle" fill="#ffffff" font-family="system-ui, sans-serif" font-size="8" font-weight="bold">ROTA DE FUGA &gt;&gt;&gt;</text>')

    # Linhas de Cota e Alturas
    # Faixa Superior >= 1.80m (y <= 200)
    linhas.append('    <line x1="20" y1="137" x2="85" y2="137" stroke="#38bdf8" stroke-dasharray="3,3" />')
    linhas.append('    <text x="15" y="133" text-anchor="end" fill="#38bdf8" font-family="monospace" font-size="10">2.10 m (Verga)</text>')

    linhas.append('    <line x1="20" y1="190" x2="300" y2="190" stroke="#38bdf8" stroke-dasharray="3,3" />')
    linhas.append('    <text x="15" y="186" text-anchor="end" fill="#38bdf8" font-family="monospace" font-size="10">≥ 1.80 m (Superior)</text>')

    # Faixa Média 1.20m - 1.50m (y: 220..245)
    linhas.append('    <rect x="450" y="210" width="280" height="45" fill="#38bdf8" opacity="0.1" />')
    linhas.append('    <line x1="20" y1="232" x2="480" y2="232" stroke="#fbbf24" stroke-dasharray="3,3" />')
    linhas.append('    <text x="15" y="228" text-anchor="end" fill="#fbbf24" font-family="monospace" font-size="10">1.20 a 1.50 m (Média)</text>')

    # Faixa Baixa 0.10m - 0.50m (y: 310..340)
    linhas.append('    <rect x="580" y="310" width="140" height="35" fill="#34d399" opacity="0.1" />')
    linhas.append('    <line x1="20" y1="324" x2="585" y2="324" stroke="#34d399" stroke-dasharray="3,3" />')
    linhas.append('    <text x="15" y="320" text-anchor="end" fill="#34d399" font-family="monospace" font-size="10">0.10 a 0.50 m (Baixa)</text>')

    linhas.append('  </g>')

    # PAINEL CENTRAL/DIREITO INFERIOR: Critérios de Dimensionamento e Fotoluminescência (x: 510, y: 550, w: 900, h: 320)
    linhas.append('  <g transform="translate(510, 550)">')
    linhas.append('    <rect width="900" height="320" rx="8" fill="#111827" stroke="#374151" stroke-width="1" />')
    linhas.append('    <text x="30" y="35" fill="#f9fafb" font-family="system-ui, sans-serif" font-size="16" font-weight="bold">CRITÉRIOS DE CÁLCULO E FOTOLUMINESCÊNCIA (NBR 16820:2020)</text>')
    linhas.append('    <line x1="30" y1="48" x2="870" y2="48" stroke="#374151" stroke-width="1" />')

    # Coluna 1: Fórmula Fundamental A = d² / K (x: 30..300)
    linhas.append('    <rect x="30" y="65" width="260" height="235" rx="6" fill="#1f2937" stroke="#374151" stroke-width="1" />')
    linhas.append('    <text x="45" y="92" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">FÓRMULA FUNDAMENTAL</text>')
    linhas.append('    <rect x="45" y="105" width="230" height="50" rx="4" fill="#0f172a" stroke="#0284c7" stroke-width="1" />')
    linhas.append('    <text x="160" y="138" text-anchor="middle" fill="#38bdf8" font-family="monospace" font-size="18" font-weight="bold">A = d² / K</text>')
    linhas.append('    <text x="45" y="180" fill="#e2e8f0" font-family="system-ui, sans-serif" font-size="11">A = Área mínima da placa (m²)</text>')
    linhas.append('    <text x="45" y="200" fill="#e2e8f0" font-family="system-ui, sans-serif" font-size="11">d = Distância máxima de visão (m)</text>')
    linhas.append('    <text x="45" y="220" fill="#a7f3d0" font-family="system-ui, sans-serif" font-size="11">K = 2000 (Fotoluminescente / Luz ext.)</text>')
    linhas.append('    <text x="45" y="240" fill="#fde047" font-family="system-ui, sans-serif" font-size="11">K = 1250 (Iluminação interna direta)</text>')
    linhas.append('    <text x="45" y="270" fill="#fca5a5" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">Espaçamento Rota: ≤ 15,0 m</text>')

    # Coluna 2: Tabela de Áreas e Dimensões Padronizadas (x: 310..590)
    linhas.append('    <rect x="310" y="65" width="270" height="235" rx="6" fill="#1f2937" stroke="#374151" stroke-width="1" />')
    linhas.append('    <text x="325" y="92" fill="#34d399" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">TABELA DE DIMENSÕES (K = 2000)</text>')
    linhas.append('    <!-- Cabeçalho Tabela -->')
    linhas.append('    <rect x="325" y="105" width="240" height="25" fill="#334155" />')
    linhas.append('    <text x="335" y="122" fill="#f8fafc" font-family="monospace" font-size="10" font-weight="bold">Dist (d)</text>')
    linhas.append('    <text x="405" y="122" fill="#f8fafc" font-family="monospace" font-size="10" font-weight="bold">Área Mín.</text>')
    linhas.append('    <text x="495" y="122" fill="#f8fafc" font-family="monospace" font-size="10" font-weight="bold">Padrão</text>')

    linhas.append('    <text x="335" y="148" fill="#e2e8f0" font-family="monospace" font-size="10">≤ 4,0 m</text>')
    linhas.append('    <text x="405" y="148" fill="#e2e8f0" font-family="monospace" font-size="10">0,008 m²</text>')
    linhas.append('    <text x="495" y="148" fill="#a7f3d0" font-family="monospace" font-size="10">100x100</text>')

    linhas.append('    <text x="335" y="174" fill="#e2e8f0" font-family="monospace" font-size="10">≤ 6,7 m</text>')
    linhas.append('    <text x="405" y="174" fill="#e2e8f0" font-family="monospace" font-size="10">0,022 m²</text>')
    linhas.append('    <text x="495" y="174" fill="#a7f3d0" font-family="monospace" font-size="10">150x150</text>')

    linhas.append('    <text x="335" y="200" fill="#e2e8f0" font-family="monospace" font-size="10">≤ 8,9 m</text>')
    linhas.append('    <text x="405" y="200" fill="#e2e8f0" font-family="monospace" font-size="10">0,040 m²</text>')
    linhas.append('    <text x="495" y="200" fill="#a7f3d0" font-family="monospace" font-size="10">200x200</text>')

    linhas.append('    <text x="335" y="226" fill="#e2e8f0" font-family="monospace" font-size="10">≤ 11,1 m</text>')
    linhas.append('    <text x="405" y="226" fill="#e2e8f0" font-family="monospace" font-size="10">0,062 m²</text>')
    linhas.append('    <text x="495" y="226" fill="#a7f3d0" font-family="monospace" font-size="10">250x250</text>')

    linhas.append('    <text x="335" y="252" fill="#e2e8f0" font-family="monospace" font-size="10">≤ 13,4 m</text>')
    linhas.append('    <text x="405" y="252" fill="#e2e8f0" font-family="monospace" font-size="10">0,090 m²</text>')
    linhas.append('    <text x="495" y="252" fill="#a7f3d0" font-family="monospace" font-size="10">300x300</text>')

    linhas.append('    <text x="335" y="278" fill="#e2e8f0" font-family="monospace" font-size="10">≤ 17,8 m</text>')
    linhas.append('    <text x="405" y="278" fill="#e2e8f0" font-family="monospace" font-size="10">0,160 m²</text>')
    linhas.append('    <text x="495" y="278" fill="#a7f3d0" font-family="monospace" font-size="10">400x400</text>')

    # Coluna 3: Requisitos Fotoluminescentes (x: 600..870)
    linhas.append('    <rect x="600" y="65" width="270" height="235" rx="6" fill="#1f2937" stroke="#374151" stroke-width="1" />')
    linhas.append('    <text x="615" y="92" fill="#f59e0b" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">DESEMPENHO FOTOLUMINESCENTE</text>')
    linhas.append('    <!-- Categoria W -->')
    linhas.append('    <rect x="615" y="105" width="240" height="75" rx="4" fill="#0f172a" stroke="#d97706" stroke-width="1" />')
    linhas.append('    <text x="625" y="125" fill="#fde047" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">CATEGORIA W (Padrão)</text>')
    linhas.append('    <text x="625" y="143" fill="#e2e8f0" font-family="monospace" font-size="10">10 min: ≥ 140 mcd/m²</text>')
    linhas.append('    <text x="625" y="160" fill="#e2e8f0" font-family="monospace" font-size="10">60 min: ≥ 20 mcd/m²</text>')
    linhas.append('    <text x="625" y="174" fill="#9ca3af" font-family="system-ui, sans-serif" font-size="9">Atenuação mínima: 1800 min (30h)</text>')

    # Categoria X
    linhas.append('    <rect x="615" y="190" width="240" height="75" rx="4" fill="#0f172a" stroke="#ea580c" stroke-width="1" />')
    linhas.append('    <text x="625" y="210" fill="#fdba74" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">CATEGORIA X (Alta Performance)</text>')
    linhas.append('    <text x="625" y="228" fill="#e2e8f0" font-family="monospace" font-size="10">10 min: ≥ 210 mcd/m²</text>')
    linhas.append('    <text x="625" y="245" fill="#e2e8f0" font-family="monospace" font-size="10">60 min: ≥ 30 mcd/m²</text>')
    linhas.append('    <text x="625" y="259" fill="#9ca3af" font-family="system-ui, sans-serif" font-size="9">Recomendado para hospitais e subsolos</text>')

    linhas.append('    <text x="615" y="288" fill="#64748b" font-family="system-ui, sans-serif" font-size="10">Ensaios conforme Anexo B da NBR 16820</text>')

    linhas.append('  </g>')

    # Rodapé Técnico
    linhas.append('  <text x="55" y="885" fill="#64748b" font-family="monospace" font-size="11">Lofrano Tecnologia • Zero-Float Engine • ABNT NBR 16820:2020 • Relatório Oficial</text>')
    linhas.append(f'  <text x="1385" y="885" text-anchor="end" fill="#64748b" font-family="monospace" font-size="11">Edificação: {res.identificacao_edificio} | Placas: {res.total_placas_unidades} un.</text>')

    linhas.append('</svg>')
    return "\n".join(linhas)
