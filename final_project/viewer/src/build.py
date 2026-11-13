"""Build the ALU4 design explorer page from Electric's dump (design.json).

Usage: python3 build.py design.json template.html out_artifact.html out_local.html
"""
import json
import sys

src, tpl, out_art, out_local = sys.argv[1:5]
d = json.load(open(src))
cells = d['cells']
CELLS = ['NOT', 'NAND', 'XOR', 'FA', 'TRI', 'ALU4']


def gate_and_diffs(dev):
    g, diffs = None, []
    for port, net in dev['ports'].items():
        if port in ('g',) or port.startswith('poly'):
            g = net
        elif port in ('s', 'd') or port.startswith('diff'):
            diffs.append(net)
    return g, diffs


equiv = {}
for cn in CELLS:
    e = d['equiv'][cn]
    netmap = {s: l for s, l in e['nets']}
    nodemap = {s: l for s, l in e['nodes']}
    sch_devs = {x['name']: x for x in cells[cn + '{sch}'].get('devs', [])}
    lay_devs = {x['name']: x for x in cells[cn + '{lay}'].get('devs', [])}
    # NCC merges series/parallel transistors into one part, so its part map is incomplete.
    # Match every transistor by type, gate net and diffusion nets, all through NCC's net
    # equivalence; NCC's own part match breaks ties.
    ncc_parts = dict(nodemap)
    nodemap = {k: v for k, v in nodemap.items() if k not in sch_devs}
    cands = []
    for name, sd in sch_devs.items():
        g, diffs = gate_and_diffs(sd)
        lg = netmap.get(g)
        ldiffs = {netmap.get(x) for x in diffs if netmap.get(x)}
        for lname, ld in lay_devs.items():
            if ld['p'] != sd['p']:
                continue
            g2, d2 = gate_and_diffs(ld)
            if g2 != lg:
                continue
            score = 10 * len(ldiffs & set(d2)) + (1 if ncc_parts.get(name) == lname else 0)
            cands.append((score, name, lname))
    taken = set()
    for score, name, lname in sorted(cands, reverse=True):
        if name in nodemap or lname in taken:
            continue
        nodemap[name] = lname
        taken.add(lname)
    equiv[cn] = {'match': e['match'], 'nets': netmap, 'nodes': nodemap}
    unmatched = [n for n in sch_devs if n not in nodemap]
    print(cn, 'NCC match' if e['match'] else 'MISMATCH', f"{len(netmap)} nets, {len(nodemap)} parts matched", 'unmatched:', unmatched)

# keep only what the page draws
slim = {}
for k, c in cells.items():
    slim[k] = {
        'bounds': c['bounds'],
        'shapes': [{kk: v for kk, v in s.items()} for s in c['shapes'] if s['l'] not in ('none',) and not s['s'].startswith('CROSS') and s['s'] != 'BIGCROSS'],
        'insts': c['insts'],
        'texts': c['texts'],
        'exports': c['exports'],
        'devs': [{'name': x['name'], 'p': x['p']} for x in c.get('devs', [])],
    }

payload = json.dumps({'cells': slim, 'equiv': equiv}, separators=(',', ':'))
html = open(tpl).read().replace('/*__DATA__*/null', payload)
open(out_art, 'w').write(html)
open(out_local, 'w').write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n</head>\n<body>\n' + html + '\n</body>\n</html>\n')
print('wrote', out_art, len(html) // 1024, 'KB')
