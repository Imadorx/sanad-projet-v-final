#!/usr/bin/env python3
"""
Static checker for Odoo external-ID load-order bugs.

Odoo loads a module's `data` files in the EXACT order listed in the
manifest, resolving `ref="xml_id"` and `%(module.xml_id)d` at load
time. If a file references an ID not yet defined - either earlier in
the SAME file (document order matters), an earlier file in the same
module, or a dependency module - install fails with
`ValueError: External ID not found in the system`.

This script simulates that load order without a live Odoo instance.
Correctness notes vs. a naive version:
  - WITHIN a file, definitions and references are both processed in
    strict document order (a <record> can legally reference an earlier
    <record> in the same file - only forward references are bugs).
  - Every model's `_name` gets its auto-generated `model_<name>` XML ID
    registered BEFORE any data file is processed, because Odoo creates
    these automatically when models are loaded (prior to any data file),
    not from an XML <record>.
  - References whose module prefix is not one of our own custom-addons
    modules (e.g. `base.*`, `mail.*`) are NOT flagged - we can only
    audit our own code; those are assumed provided by their owning
    (already-installed) module, per normal Odoo dependency semantics.
"""
import ast
import os
import re
import sys
import xml.etree.ElementTree as ET

BASE = os.path.join(os.path.dirname(__file__), '..', 'custom-addons')
PERCENT_REF_RE = re.compile(r'%\((?:([\w]+)\.)?([\w]+)\)[ds]')


def load_manifest(module_dir):
    with open(os.path.join(module_dir, '__manifest__.py')) as f:
        return ast.literal_eval(f.read())


def get_all_modules():
    return sorted(
        d for d in os.listdir(BASE)
        if os.path.isdir(os.path.join(BASE, d)) and
        os.path.exists(os.path.join(BASE, d, '__manifest__.py'))
    )


def build_module_dependency_order(modules):
    manifests = {m: load_manifest(os.path.join(BASE, m)) for m in modules}
    resolved, seen = [], set()

    def visit(m):
        if m in seen or m not in manifests:
            return
        seen.add(m)
        for dep in manifests[m].get('depends', []):
            visit(dep)
        resolved.append(m)

    for m in modules:
        visit(m)
    return resolved, manifests


def extract_model_names(module_dir):
    names = []
    models_dir = os.path.join(module_dir, 'models')
    if not os.path.isdir(models_dir):
        return names
    name_re = re.compile(r"_name\s*=\s*['\"]([\w.]+)['\"]")
    for fname in os.listdir(models_dir):
        if fname.endswith('.py'):
            with open(os.path.join(models_dir, fname)) as f:
                names.extend(name_re.findall(f.read()))
    return names


def iter_refs_and_defs_in_order(elem):
    if elem.tag in ('record', 'menuitem', 'template') and 'id' in elem.attrib:
        for attr, val in elem.attrib.items():
            if attr == 'ref':
                yield ('ref', val)
            for mod, xid in PERCENT_REF_RE.findall(val):
                yield ('ref', f'{mod}.{xid}' if mod else xid)
        for child in elem:
            yield from iter_refs_and_defs_in_order(child)
        yield ('def', elem.attrib['id'])
        return
    for attr, val in elem.attrib.items():
        if attr == 'ref':
            yield ('ref', val)
        for mod, xid in PERCENT_REF_RE.findall(val):
            yield ('ref', f'{mod}.{xid}' if mod else xid)
    for child in elem:
        yield from iter_refs_and_defs_in_order(child)


def main():
    modules = get_all_modules()
    ordered_modules, manifests = build_module_dependency_order(modules)
    print(f'Module install order (topological, by depends): {ordered_modules}\n')

    globally_defined = set()
    errors = []

    for module in ordered_modules:
        for model_name in extract_model_names(os.path.join(BASE, module)):
            auto_id = 'model_' + model_name.replace('.', '_')
            globally_defined.add(f'{module}.{auto_id}')
            globally_defined.add(auto_id)

    for module in ordered_modules:
        manifest = manifests[module]
        data_files = manifest.get('data', []) + manifest.get('demo', [])
        module_dir = os.path.join(BASE, module)

        for data_file in data_files:
            if not data_file.endswith('.xml'):
                continue
            file_path = os.path.join(module_dir, data_file)
            if not os.path.exists(file_path):
                errors.append(f'[{module}] manifest references missing file: {data_file}')
                continue
            try:
                tree = ET.parse(file_path)
            except ET.ParseError as e:
                errors.append(f'[{module}] {data_file}: XML PARSE ERROR: {e}')
                continue

            for event, xid in iter_refs_and_defs_in_order(tree.getroot()):
                if event == 'ref':
                    if '.' in xid:
                        prefix = xid.split('.')[0]
                        if prefix not in ordered_modules:
                            continue
                        qualified, bare = xid, xid.split('.')[-1]
                    else:
                        qualified, bare = f'{module}.{xid}', xid
                    if qualified in globally_defined or bare in globally_defined:
                        continue
                    errors.append(
                        f'[{module}] {data_file}: reference "{xid}" not yet defined '
                        f'at this point in load order (forward reference)')
                else:
                    globally_defined.add(f'{module}.{xid}')
                    globally_defined.add(xid)

    print('=' * 70)
    if errors:
        print(f'FOUND {len(errors)} EXTERNAL-ID LOAD-ORDER ERROR(S):\n')
        for e in errors:
            print('  FAIL:', e)
    else:
        print('PASS: no external-ID forward references found across all modules.')
    print('=' * 70)
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
