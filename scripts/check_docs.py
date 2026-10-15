"""Check local Markdown targets, YAML syntax and issue form structure."""
from pathlib import Path
from urllib.parse import unquote
import re
import sys
import xml.etree.ElementTree as ET
import yaml

ROOT = Path(__file__).resolve().parent.parent
errors = []
for path in ROOT.rglob('*.md'):
    if '.git' in path.parts:
        continue
    text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
    targets = re.findall(r'\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)', text)
    for target in targets:
        if target.startswith(('#', 'http:', 'https:', 'mailto:')):
            continue
        target = unquote(target.split('#')[0]).strip('<>')
        if target and not (path.parent / target).exists():
            errors.append(f'{path.relative_to(ROOT)}: missing target {target}')
for path in ROOT.rglob('*.yml'):
    if '.git' in path.parts:
        continue
    try:
        data = yaml.safe_load(path.read_text())
        if path.parent.name == 'ISSUE_TEMPLATE' and path.name != 'config.yml':
            assert isinstance(data, dict) and data.get('name') and data.get('description')
            assert isinstance(data.get('body'), list) and data['body']
            ids = [x['id'] for x in data['body'] if x['type'] != 'markdown']
            assert len(ids) == len(set(ids)), 'duplicate form IDs'
    except (yaml.YAMLError, AssertionError, KeyError, TypeError) as exc:
        errors.append(f'{path.relative_to(ROOT)}: {exc}')
for path in (ROOT / 'profile').glob('*.svg'):
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        errors.append(f'{path.name}: {exc}')
for error in errors:
    print(error)
print(f'Document checks: {len(errors)} error(s)')
sys.exit(bool(errors))
