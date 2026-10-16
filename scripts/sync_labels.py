#!/usr/bin/env python3
"""Preview or apply the studio label catalog; never delete or rename labels."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote
import yaml

ROOT = Path(__file__).resolve().parents[1]

def api(endpoint, method='GET', payload=None):
    args = ['gh', 'api', endpoint, '--method', method]
    if payload is not None:
        args += ['--input', '-']
    result = subprocess.run(args, input=json.dumps(payload) if payload is not None else None,
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout) if result.stdout.strip() else None

def plan(catalog, existing, community=False):
    current = {x['name'].casefold(): x for x in existing}
    changes = []
    for item in catalog:
        if item['scope'] == 'community' and not community:
            continue
        old = current.get(item['name'].casefold())
        if old is None:
            changes.append(('create', item))
        elif old['color'].lower() != item['color'].lower() or (old.get('description') or '') != item['description']:
            changes.append(('update', item))
    return changes

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, help='sickBoyStudio/repository')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default: preview only)')
    args = parser.parse_args()
    if not re.fullmatch(r'sickBoyStudio/[A-Za-z0-9_.-]+', args.repo):
        parser.error('Expected sickBoyStudio/repository')
    catalog = yaml.safe_load((ROOT / '.github/labels.yml').read_text())['labels']
    existing = []
    page = 1
    while True:
        batch = api(f'repos/{args.repo}/labels?per_page=100&page={page}')
        existing.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    changes = plan(catalog, existing, args.repo == 'sickBoyStudio/.github')
    print(f'{args.repo}: {len(changes)} changes ({"apply" if args.apply else "preview"})')
    for action, item in changes:
        print(f'  {action}: {item["name"]}')
        if args.apply:
            payload = {k: item[k] for k in ('name', 'color', 'description')}
            endpoint = f'repos/{args.repo}/labels'
            if action == 'update':
                endpoint += '/' + quote(item['name'], safe='')
                payload.pop('name')
            api(endpoint, 'POST' if action == 'create' else 'PATCH', payload)

if __name__ == '__main__':
    main()
