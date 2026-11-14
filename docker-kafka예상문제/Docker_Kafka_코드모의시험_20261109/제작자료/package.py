from pathlib import Path
import ast, json, zipfile, hashlib
base=Path(__file__).resolve().parents[1]
report={}
for name in ['응시용','정답']:
    ps=list((base/name).rglob('*.py'))
    for p in ps:ast.parse(p.read_text(encoding='utf-8'))
    report[name+'_syntax_count']=len(ps)
def allowed(p):return p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name!='submission.zip'
for name,pdfname in [('응시용','01_모의시험_문제.pdf'),('정답','02_모의시험_정답해설.pdf')]:
    with zipfile.ZipFile(base/(name+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((base/name).rglob('*')):
            if allowed(p):z.write(p,p.relative_to(base))
        z.write(base/'output/pdf'/pdfname,Path(name)/pdfname)
    with zipfile.ZipFile(base/(name+'.zip')) as z:
        assert z.testzip() is None
        report[name+'_zip_files']=len(z.namelist())
        if name=='응시용':
            assert not any('정답' in n or '제작자료' in n for n in z.namelist())
            for n in z.namelist():
                if n.endswith('.py'):assert b'reference solution' not in z.read(n)
            report['student_answer_separation']='pass'
# No originals, installed dependencies, caches or QA images in the delivery bundle.
with zipfile.ZipFile(base/'전체결과물.zip','w',zipfile.ZIP_DEFLATED) as z:
    for folder in ['응시용','정답','output/pdf']:
        for p in sorted((base/folder).rglob('*')):
            if allowed(p):z.write(p,p.relative_to(base))
    for name in ['시작하세요.md','출처대응표.md','검증보고서.md',
                 '제작자료/verification.json','제작자료/pdf_checks.json','제작자료/test_정답.txt','제작자료/test_응시용.txt']:
        z.write(base/name,name)
with zipfile.ZipFile(base/'전체결과물.zip') as z:assert z.testzip() is None
for p in base.glob('*.zip'):
    report[p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(base/'제작자료/package_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True,indent=2))
