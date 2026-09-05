#!/usr/bin/env python3
"""Optional project audit (Python standard library only; PDF builds do not use Python)."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent.parent
CODE=re.compile(r'\\begin\{CodeBlock\}(?:\[([^\]\n]*)\])?\n(.*?)\n\\end\{CodeBlock\}',re.S)
def sha(value):return hashlib.sha256(value if isinstance(value,bytes) else value.encode()).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',action='store_true',help='Also verify migration content and original asset hashes.')
    parser.add_argument('--require-build',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    manifest=json.loads((ROOT/'migration/content-manifest.json').read_text())
    errors=[];stats=collections.Counter();languages=collections.Counter()
    labels=[];refs=[];graphics=[];code_verified=0;unchanged=0;corrected=0
    styles=(ROOT/'config/code-style.tex').read_text()
    supported=set(re.findall(r'\\lstdefinelanguage\{([^}]+)\}',styles))
    paths=re.findall(r'\\input\{(chapters/[^}]+)\}',(ROOT/'main.tex').read_text())
    for stem in paths:
        p=ROOT/(stem+'.tex')
        if not p.is_file():errors.append('Missing chapter: '+stem);continue
        text=p.read_text();blocks=CODE.findall(text);prose=CODE.sub('',text)
        counts={'chapters':1,'headings':len(re.findall(r'^\s*\\(?:chapter\*?|section\*?|subsection\*?|subsubsection\*?|paragraph\*?|subparagraph\*?)\{',prose,re.M)),
                'code_blocks':len(blocks),'figures':prose.count('\\begin{figure}'),'tables':prose.count('\\begin{longtable}')}
        stats.update(counts)
        labels.extend(re.findall(r'\\label\{([^}]+)\}',prose))
        refs.extend(re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}',prose))
        graphics.extend(re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',prose))
        if re.search(r'\\@ref|@\\ref|<br\s*/?>|\\(?:NormalTok|KeywordTok|pandocbounded|passthrough)|knitr::|bcnez.*111\}json',prose):errors.append('Unconverted or corrupted markup: '+stem)
        for i,(options,code) in enumerate(blocks,1):
            m=re.search(r'(?:^|,)\s*language\s*=\s*(\w+)\s*(?:,|$)',options)
            if not m:errors.append(f'Missing code language: {stem} block {i}')
            else:
                languages[m[1]]+=1
                if m[1] not in supported:errors.append('Unsupported code language: '+m[1])
        if args.baseline:
            base=next((c for c in manifest['chapters'] if c['target']==stem+'.tex'),None)
            if not base:errors.append('Chapter outside baseline: '+stem);continue
            for key in ['headings','figures','tables']:
                if counts[key]!=base[key]:errors.append(f'{stem}: {key} count changed')
            expected=base['source_code_blocks']
            if len(blocks)!=len(expected):errors.append('Code count changed: '+stem);continue
            for i,((options,code),record) in enumerate(zip(blocks,expected),1):
                if sha(code)!=record['sha256']:errors.append(f'Code differs from reviewed migration: {stem} block {i}');continue
                code_verified+=1
                if record['source_sha256']==record['sha256']:unchanged+=1
                else:
                    before=record['original_code']
                    if sha(before)!=record['source_sha256']:errors.append(f'Bad original code record: {stem} block {i}')
                    for edit in record['edits']:
                        if before.count(edit['old'])!=edit['occurrences']:errors.append(f'Code correction count mismatch: {stem} block {i}')
                        before=before.replace(edit['old'],edit['new'])
                    if before!=code:errors.append(f'Code correction ledger mismatch: {stem} block {i}')
                    corrected+=1
    duplicate=[k for k,n in collections.Counter(labels).items() if n>1]
    if duplicate:errors.append('Duplicate labels: '+', '.join(duplicate))
    if set(refs)-set(labels):errors.append('Unresolved references: '+', '.join(sorted(set(refs)-set(labels))))
    for name in graphics:
        p=(ROOT/name).resolve()
        if ROOT not in p.parents or not p.is_file():errors.append('Missing or external image: '+name)
    for p in ROOT.rglob('*'):
        if p.is_symlink():errors.append('Unexpected symbolic link: '+str(p.relative_to(ROOT)))
    assets_verified=0
    if args.baseline:
        if paths!=[x['target'][:-4] for x in manifest['chapters']]:errors.append('Chapter order differs from baseline')
        for name,expected in manifest['assets'].items():
            p=ROOT/name
            if not p.is_file() or sha(p.read_bytes())!=expected:errors.append('Original asset changed or missing: '+name)
            else:assets_verified+=1
        for key in ['chapters','headings','figures','tables']:
            if stats[key]!=manifest['summary'][key]:errors.append('Baseline total differs: '+key)
        bibliography=(ROOT/'chapters/20-references.tex').read_text()
        if len(re.findall(r'^\{\[\}\d+\{\]\}',bibliography,re.M))!=manifest['summary']['manual_references']:errors.append('Manual bibliography count differs')
    logstats={}
    logpath=ROOT/'build/main.log'
    if logpath.is_file():
        log=logpath.read_text(errors='replace')
        logstats={'missing_characters':log.count('Missing character:'),'overfull_boxes':len(re.findall(r'Overfull \\[hv]box',log)),
                  'undefined_references':len(re.findall(r'LaTeX Warning: Reference .*?undefined',log)),
                  'latex_errors':len(re.findall(r'^!|LaTeX Error:|Package .*? Error:',log,re.M)),
                  'font_warnings':log.count('LaTeX Font Warning:'),'empty_link_warnings':log.count('Suppressing link with empty target')}
        for key,n in logstats.items():
            if n:errors.append(f'Build log {key}: {n}')
    elif args.require_build:errors.append('Build log missing')
    if args.require_build and not (ROOT/'build/main.pdf').is_file():errors.append('Compiled PDF missing')
    inputs=set();oldroots=[Path(manifest['source_directory']),Path(manifest['source_directory']).parent/'designpracticelatex',Path(manifest['source_directory']).parent/'designpractice']
    recorder=ROOT/'build/main.fls'
    if recorder.is_file():
        for line in recorder.read_text(errors='replace').splitlines():
            if not line.startswith('INPUT '):continue
            p=Path(line[6:].strip('"'));p=(ROOT/p).resolve() if not p.is_absolute() else p.resolve()
            if any(r in p.parents for r in oldroots):errors.append('Build depends on another book: '+str(p))
            if ROOT in p.parents:inputs.add(str(p.relative_to(ROOT)))
    result={'project':str(ROOT),'baseline_checked':args.baseline,'counts':dict(stats),'labels':len(labels),'references':len(refs),
            'code_languages':dict(languages),'highlighted_code_blocks':sum(n for k,n in languages.items() if k!='BookText'),
            'plain_text_blocks':languages['BookText'],'code_hashes_verified':code_verified,'original_code_unchanged':unchanged,
            'code_with_verified_documented_corrections':corrected,'original_assets_hash_verified':assets_verified,
            'recorded_local_inputs':sorted(inputs),'log':logstats,'errors':errors,'passed':not errors}
    out=json.dumps(result,ensure_ascii=False,indent=2)+'\n';print(out,end='')
    if args.output:args.output.write_text(out)
    return int(bool(errors))
if __name__=='__main__':sys.exit(main())
