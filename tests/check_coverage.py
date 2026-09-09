"""Guard rail: every endpoint Freshdesk documents must have a tool.

`freshdesk_endpoints.txt` was extracted from the curl examples on
https://developers.freshdesk.com/api/. Re-extract it when Freshdesk ships new
endpoints; this test then tells you what is unimplemented.

Run with: python tests/check_coverage.py
"""
import re, glob, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENDPOINTS = Path(__file__).resolve().parent / "freshdesk_endpoints.txt"

ARTIFACTS = {  # doc typos / example tokens, not real endpoints
    'api/v2/canned_responses/create_multiple',
    'canned_responses/{id}’',
    # The docs illustrate the export endpoint with a one-off download token;
    # the real endpoint is POST /contacts|companies/export.
    'contacts/export/{id}',
    'companies/export/{id}',
}

def _ph(p: str) -> str:
    """Collapse f-string placeholders, keeping language codes distinct from ids."""
    p = re.sub(r'\{(language|lang)\}', '{lang}', p)
    return re.sub(r'\{(?!lang\})[^}]+\}', '{id}', p)


def norm(p: str) -> str:
    p = p.strip().strip('/').rstrip("’'\"")
    p = re.sub(r'\[[^\]]*\]', '{id}', p)
    p = re.sub(r'\{(?!lang\})[a-z_-]+\}', '{id}', p)
    p = re.sub(r'(?<=/)(BKG-1|d809986[0-9a-f]+|[0-9A-Z]{18,})(?=/|$)', '{id}', p)
    p = re.sub(r'(?<=/)\d+(?=/|$)', '{id}', p)
    p = re.sub(r'\{id\}[0-9A-Z]{10,}', '{id}', p)
    # translation suffix: /es is a language code example, treat as /{lang}
    p = re.sub(r'/es$', '/{lang}', p)
    return p

doc = {}
for line in open(ENDPOINTS):
    m, raw = line.split(None, 1)
    raw = raw.strip()
    if not raw.startswith('/api/v2/'):
        continue
    p = norm(raw[len('/api/v2/'):])
    if p in ARTIFACTS or p.startswith('api/v2/'):
        continue
    doc[(m, p)] = raw.strip()

mine = set()
for f in glob.glob(str(ROOT / 'src/freshdesk_mcp/tools/*.py')):
    src = open(f).read()
    # literal calls
    for m in re.finditer(r'client\.(get|post|put|delete)\(\s*f?"([^"]+)"', src):
        mine.add((m.group(1).upper(), norm(_ph(m.group(2)))))
    for m in re.finditer(r'client\.request\(\s*"([A-Z]+)",\s*f?"([^"]+)"', src):
        mine.add((m.group(1), norm(_ph(m.group(2)))))
    # paths assembled into a `path` variable then passed to client.<verb>(path)
    paths = re.findall(r'path\s*=\s*f?"([^"]+)"', src)
    paths += re.findall(r'else\s+f?"([^"]+)"', src)
    extra = re.findall(r'f"\{path\}/\{(\w+)\}"', src)
    verbs = set(v.upper() for v in re.findall(r'client\.(get|post|put|delete)\(\s*(?:f?"\{path\}|path)', src))
    for raw in paths:
        base = norm(_ph(raw))
        for v in verbs:
            mine.add((v, base))
            if extra:
                mine.add((v, base + '/{lang}'))

missing = sorted(k for k in doc if k not in mine)
print(f"documented endpoints : {len(doc)}")
print(f"implemented paths    : {len(mine)}")
print(f"MISSING              : {len(missing)}\n")
for m, p in missing:
    print(f"  {m:7}{p}      (docs: {doc[(m,p)]})")
sys.exit(1 if missing else 0)
