"""Regenerate the Mermaid diagram in causal-loop-diagram.md from source-code.dyn.

Every arrow comes from parsing the DYNAMO equations: a variable used on the right
side of an equation gets an arrow into the variable on the left. The + / - sign
of each arrow comes from a hand-written map (SIGN below), checked against the
equation algebra and the slope of each table. The script stops with an error if
the parsed arrows and the sign map do not match exactly.

Run from the repository root:  python tools/make_causal_loop_diagram.py
It replaces the mermaid code block in causal-loop-diagram.md and leaves the
legend around it untouched.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "source-code.dyn"
OUT = ROOT / "causal-loop-diagram.md"

# ---------- parse DYNAMO listing ----------
cards = []
for line in SRC.read_text(encoding="utf-8").splitlines():
    num, typ, text = line[:8].strip(), line[8:16].strip(), line[16:].rstrip()
    if typ == 'X':
        cards[-1] = (cards[-1][0], cards[-1][1], cards[-1][2] + text)
    else:
        cards.append((num, typ, text))

tables = {t.split('=')[0] for _, ty, t in cards if ty == 'T'}
eqnum = {}
SKIP = {'K', 'J', 'JK', 'KL', 'DT', 'TIME', 'CLIP', 'TABLE', 'TABHL'} | tables
# CLIP alternates and switch times collapse onto the base constant
ALIAS = {'BRN1': 'BRN', 'SWT1': 'BRN', 'NRUN1': 'NRUN', 'SWT2': 'NRUN',
         'DRN1': 'DRN', 'SWT3': 'DRN', 'CIGN1': 'CIGN', 'SWT4': 'CIGN',
         'CIDN1': 'CIDN', 'SWT5': 'CIDN', 'POLN1': 'POLN', 'SWT6': 'POLN',
         'FC1': 'FC', 'SWT7': 'FC'}
PLOT_ONLY = {'PRTPER', 'PLTPER'}

flows = []          # (rate, level, 'in'|'out')
info = set()        # (src, dst)
kinds = {}
for num, ty, text in cards:
    if ty not in ('L', 'A', 'R', 'S'):
        continue
    lhs, rhs = text.split('=', 1)
    var = lhs.split('.')[0]
    if var in PLOT_ONLY:
        continue
    kinds[var] = ty
    eqnum[var] = num
    if ty == 'L':
        for m in re.finditer(r'([-+(]?)([A-Z][A-Z0-9]*)\.JK', rhs):
            flows.append((m.group(2), var, 'out' if m.group(1) == '-' else 'in'))
        rhs = re.sub(r'[A-Z][A-Z0-9]*\.JK', '', rhs)
    for name in re.findall(r'[A-Z][A-Z0-9]*', rhs):
        if name in SKIP or name == var:
            continue
        info.add((ALIAS.get(name, name), var))

# ---------- signs (from equation algebra and table slopes) ----------
SIGN = {
    # population sector
    ('P', 'BR'): '+', ('BRN', 'BR'): '+', ('BRFM', 'BR'): '+', ('BRMM', 'BR'): '+',
    ('BRCM', 'BR'): '+', ('BRPM', 'BR'): '+',
    ('P', 'DR'): '+', ('DRN', 'DR'): '+', ('DRMM', 'DR'): '+', ('DRPM', 'DR'): '+',
    ('DRFM', 'DR'): '+', ('DRCM', 'DR'): '+',
    ('MSL', 'BRMM'): '-', ('MSL', 'DRMM'): '-',
    ('POLR', 'DRPM'): '+', ('POLR', 'BRPM'): '-',
    ('FR', 'DRFM'): '-', ('FR', 'BRFM'): '+',
    ('CR', 'DRCM'): '+', ('CR', 'BRCM'): '-',
    ('P', 'CR'): '+', ('LA', 'CR'): '-', ('PDN', 'CR'): '-',
    # natural resources
    ('NR', 'NRFR'): '+', ('NRI', 'NRFR'): '-', ('NRFR', 'NREM'): '+',
    ('P', 'NRUR'): '+', ('NRUN', 'NRUR'): '+', ('NRMM', 'NRUR'): '+',
    ('MSL', 'NRMM'): '+',
    # capital / material standard of living
    ('ECIR', 'MSL'): '+', ('ECIRN', 'MSL'): '-',
    ('CIR', 'ECIR'): '+', ('CIAF', 'ECIR'): '-', ('NREM', 'ECIR'): '+', ('CIAFN', 'ECIR'): '+',
    ('CI', 'CIR'): '+', ('P', 'CIR'): '-',
    ('P', 'CIG'): '+', ('CIM', 'CIG'): '+', ('CIGN', 'CIG'): '+', ('MSL', 'CIM'): '+',
    ('CI', 'CID'): '+', ('CIDN', 'CID'): '+',
    # agriculture / food
    ('FPCI', 'FR'): '+', ('FCM', 'FR'): '+', ('FPM', 'FR'): '+', ('FC', 'FR'): '+', ('FN', 'FR'): '-',
    ('CR', 'FCM'): '-', ('CIRA', 'FPCI'): '+', ('POLR', 'FPM'): '-',
    ('CIR', 'CIRA'): '+', ('CIAF', 'CIRA'): '+', ('CIAFN', 'CIRA'): '-',
    ('CFIFR', 'CIAF'): '+', ('CIQR', 'CIAF'): '+', ('CIAFT', 'CIAF'): 'time',
    ('FR', 'CFIFR'): '-', ('QLM', 'CIQR'): '+', ('QLF', 'CIQR'): '-',
    # pollution
    ('POL', 'POLR'): '+', ('POLS', 'POLR'): '-',
    ('P', 'POLG'): '+', ('POLN', 'POLG'): '+', ('POLCM', 'POLG'): '+', ('CIR', 'POLCM'): '+',
    ('POL', 'POLA'): '+', ('POLAT', 'POLA'): '-', ('POLR', 'POLAT'): '+',
    # quality of life
    ('QLS', 'QL'): '+', ('QLM', 'QL'): '+', ('QLC', 'QL'): '+', ('QLF', 'QL'): '+', ('QLP', 'QL'): '+',
    ('MSL', 'QLM'): '+', ('CR', 'QLC'): '-', ('FR', 'QLF'): '+', ('POLR', 'QLP'): '-',
}
missing = info - SIGN.keys()
extra = SIGN.keys() - info
assert not missing and not extra, f'missing signs: {missing}\nunparsed signs: {extra}'

# ---------- node metadata ----------
NAME = {
    'P': 'Population', 'BR': 'Birth rate', 'DR': 'Death rate',
    'BRMM': 'Birth-rate-from-material multiplier', 'BRCM': 'Birth-rate-from-crowding multiplier',
    'BRFM': 'Birth-rate-from-food multiplier', 'BRPM': 'Birth-rate-from-pollution multiplier',
    'DRMM': 'Death-rate-from-material multiplier', 'DRCM': 'Death-rate-from-crowding multiplier',
    'DRFM': 'Death-rate-from-food multiplier', 'DRPM': 'Death-rate-from-pollution multiplier',
    'CR': 'Crowding ratio',
    'NR': 'Natural resources', 'NRUR': 'Natural-resource-usage rate',
    'NRFR': 'Natural-resource fraction remaining', 'NREM': 'Natural-resource-extraction multiplier',
    'NRMM': 'Natural-resource-from-material multiplier',
    'CI': 'Capital investment', 'CIG': 'Capital-investment generation', 'CID': 'Capital-investment discard',
    'CIM': 'Capital-investment multiplier', 'CIR': 'Capital-investment ratio',
    'ECIR': 'Effective-capital-investment ratio', 'MSL': 'Material standard of living',
    'CIAF': 'Capital-investment-in-agriculture fraction', 'CIRA': 'Capital-investment ratio in agriculture',
    'FR': 'Food ratio', 'FPCI': 'Food potential from capital investment',
    'FCM': 'Food-from-crowding multiplier', 'FPM': 'Food-from-pollution multiplier',
    'CFIFR': 'Capital fraction indicated by food ratio', 'CIQR': 'Capital-investment-from-quality ratio',
    'POL': 'Pollution', 'POLG': 'Pollution generation', 'POLA': 'Pollution absorption',
    'POLR': 'Pollution ratio', 'POLCM': 'Pollution-from-capital multiplier', 'POLAT': 'Pollution-absorption time',
    'QL': 'Quality of life', 'QLM': 'Quality of life from material', 'QLC': 'Quality of life from crowding',
    'QLF': 'Quality of life from food', 'QLP': 'Quality of life from pollution',
}
CONST = {
    'BRN': ('Birth rate normal', '0.04, switch to BRN1 at SWT1'),
    'DRN': ('Death rate normal', '0.028, switch to DRN1 at SWT3'),
    'NRUN': ('Natural-resource usage normal', '1, switch to NRUN1 at SWT2'),
    'CIGN': ('Capital-investment generation normal', '0.05, switch to CIGN1 at SWT4'),
    'CIDN': ('Capital-investment discard normal', '0.025, switch to CIDN1 at SWT5'),
    'POLN': ('Pollution normal', '1, switch to POLN1 at SWT6'),
    'FC': ('Food coefficient', '1, switch to FC1 at SWT7'),
    'LA': ('Land area', '135E6'), 'PDN': ('Population density normal', '26.5'),
    'NRI': ('Natural resources initial', '900E9'), 'ECIRN': ('Effective-capital-investment ratio normal', '1'),
    'CIAFN': ('Capital-investment-in-agriculture fraction normal', '0.3'),
    'CIAFT': ('Capital-investment-in-agriculture-fraction adjustment time', '15 years'),
    'FN': ('Food normal', '1'), 'POLS': ('Pollution standard', '3.6E9'), 'QLS': ('Quality-of-life standard', '1'),
}
TABLEOF = {}
for _, ty, text in cards:
    if ty == 'A':
        m = re.match(r'(\w+)\.K=TAB(?:LE|HL)\((\w+),', text)
        if m:
            TABLEOF[m.group(1)] = m.group(2)

SECTORS = [
    ('POPULATION', 'Population sector', ['P', 'BR', 'DR', 'SRC_BR', 'SNK_DR', 'BRN', 'DRN', 'BRMM', 'BRCM', 'BRFM', 'BRPM',
                                         'DRMM', 'DRCM', 'DRFM', 'DRPM', 'CR', 'LA', 'PDN']),
    ('RESOURCES', 'Natural-resource sector', ['NR', 'NRUR', 'SNK_NRUR', 'NRUN', 'NRMM', 'NRFR', 'NRI', 'NREM']),
    ('CAPITAL', 'Capital sector', ['CI', 'CIG', 'CID', 'SRC_CIG', 'SNK_CID', 'CIGN', 'CIDN', 'CIM', 'CIR', 'ECIR', 'ECIRN', 'MSL']),
    ('AGRICULTURE', 'Agriculture sector', ['CIAF', 'CIAFT', 'CIAFN', 'CFIFR', 'CIQR', 'CIRA', 'FPCI', 'FCM', 'FPM', 'FR', 'FC', 'FN']),
    ('POLLUTION', 'Pollution sector', ['POL', 'POLG', 'POLA', 'SRC_POLG', 'SNK_POLA', 'POLN', 'POLCM', 'POLR', 'POLS', 'POLAT']),
    ('QUALITY', 'Quality-of-life sector', ['QL', 'QLS', 'QLM', 'QLC', 'QLF', 'QLP']),
]

def node(n):
    if n.startswith('SRC_') or n.startswith('SNK_'):
        word = 'source' if n.startswith('SRC_') else 'sink'
        return f'{n}(["{word}"]):::cloud'
    if n in CONST:
        name, val = CONST[n]
        return f'{n}[/"{n}<br/>{name}<br/>= {val}"/]:::const'
    eq = eqnum[n]
    label = f'{n}<br/>{NAME[n]}'
    if n in TABLEOF:
        label += f'<br/>table {TABLEOF[n]}'
    label += f'<br/>eq {eq}'
    k = kinds[n]
    if k == 'L':
        return f'{n}["{label}"]:::level'
    if k == 'R':
        return f'{n}{{{{"{label}"}}}}:::rate'
    if k == 'S':
        return f'{n}((("{label}"))):::supp'
    return f'{n}(("{label}")):::aux'

# sanity: every node placed in exactly one sector
placed = [n for _, _, ns in SECTORS for n in ns]
allnodes = {a for e in info for a in e} | {r for r, _, _ in flows} | {l for _, l, _ in flows}
srcsnk = {('SRC_' if d == 'in' else 'SNK_') + r for r, _, d in flows}
assert len(placed) == len(set(placed)), 'duplicate placement'
assert set(placed) == allnodes | srcsnk, f'placement mismatch: {set(placed) ^ (allnodes | srcsnk)}'

L = []
L.append('%%{init: {"themeCSS": ".edgeLabel, .edgeLabel p, .edgeLabel span { font-size: 22px; font-weight: bold; }"}}%%')
L.append('flowchart TB')
L.append('  classDef level fill:#cfe2ff,stroke:#084298,stroke-width:2px,color:#000')
L.append('  classDef rate fill:#fff3cd,stroke:#997404,stroke-width:2px,color:#000')
L.append('  classDef aux fill:#e2e3e5,stroke:#41464b,color:#000')
L.append('  classDef supp fill:#d1e7dd,stroke:#0f5132,color:#000')
L.append('  classDef const fill:#ffffff,stroke:#6c757d,stroke-dasharray:3 3,color:#000')
L.append('  classDef cloud fill:#f8f9fa,stroke:#adb5bd,stroke-dasharray:2 2,color:#6c757d')
L.append('')
for sid, title, ns in SECTORS:
    L.append(f'  subgraph {sid}["{title}"]')
    for n in ns:
        L.append(f'    {node(n)}')
    L.append('  end')
    L.append('')
L.append('  %% ===== Material flows (thick arrows): source -> rate -> level, or level -> rate -> sink =====')
for rate, level, d in flows:
    if d == 'in':
        L.append(f'  SRC_{rate} ==> {rate} ==>|"+ inflow"| {level}')
    else:
        L.append(f'  {level} ==>|"- outflow"| {rate} ==> SNK_{rate}')
L.append('')
L.append('  %% ===== Information links (dashed arrows), labeled with polarity =====')
order = [n for _, _, ns in SECTORS for n in ns]
for (s, d) in sorted(info, key=lambda e: (order.index(e[1]), order.index(e[0]))):
    sg = SIGN[(s, d)]
    L.append(f'  {s} -.->|"{sg}"| {d}')

fence = "```mermaid\n"
md = OUT.read_text(encoding="utf-8")
start = md.index(fence) + len(fence)
end = md.index("```", start)
OUT.write_text(md[:start] + "\n".join(L) + "\n" + md[end:], encoding="utf-8")
print(f"flows: {len(flows)}  info links: {len(info)}  nodes: {len(placed)}  -> {OUT.name} updated")
