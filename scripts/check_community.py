#!/usr/bin/env python3
"""Check local GitHub forms and their label references before publishing."""
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]

def check(root=ROOT):
    catalog = yaml.safe_load((root / '.github/labels.yml').read_text())['labels']
    names = {x['name'] for x in catalog}
    assert len(names) == len(catalog), 'Duplicate label names'
    for label in catalog:
        assert re.fullmatch(r'[0-9a-fA-F]{6}', label['color']), label
        assert 0 < len(label['name']) <= 50 and len(label['description']) <= 100, label
        assert label['scope'] in ('all', 'community'), label
    files = list((root / '.github/DISCUSSION_TEMPLATE').glob('*.yml'))
    files += [p for p in (root / '.github/ISSUE_TEMPLATE').glob('*.yml') if p.name != 'config.yml']
    for path in files:
        form = yaml.safe_load(path.read_text())
        discussion = path.parent.name == 'DISCUSSION_TEMPLATE'
        assert set(form) <= ({'title', 'labels', 'body'} if discussion else {'name', 'description', 'title', 'labels', 'assignees', 'body'}), path
        if not discussion:
            assert form.get('name') and form.get('description'), path
        for label in form.get('labels', []):
            assert label in names, (path, 'Unknown label', label)
            if not discussion:
                assert next(x for x in catalog if x['name'] == label)['scope'] == 'all', path
        ids = set()
        inputs = 0
        for field in form['body']:
            kind = field['type']; attrs = field['attributes']
            assert kind in ('markdown', 'input', 'textarea', 'dropdown', 'checkboxes'), path
            if kind == 'markdown':
                assert attrs.get('value'), path
                continue
            inputs += 1
            ident = field['id']
            assert re.fullmatch(r'[a-zA-Z0-9_-]+', ident) and ident not in ids, (path, ident)
            ids.add(ident)
            assert attrs.get('label'), path
            if kind in ('dropdown', 'checkboxes'):
                assert attrs.get('options'), path
            if kind == 'dropdown':
                assert all(isinstance(x, str) and x for x in attrs['options']), path
                assert len(set(attrs['options'])) == len(attrs['options']), path
        assert inputs > 0, path
    print(f'Validated {len(files)} forms and {len(catalog)} labels')

if __name__ == '__main__':
    check()
