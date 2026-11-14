from pathlib import Path
import ast, json, subprocess, sys, zipfile
base=Path(__file__).resolve().parents[1]
report={}
for area in ['응시용','정답']:
    paths=list((base/area).rglob('*.py'))
    for p in paths: ast.parse(p.read_text(encoding='utf-8'))
    report[area+'_python_syntax']=len(paths)
for p in (base/'정답'/'answers').glob('*.txt'):
    for line in p.read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.startswith('#'): assert line.startswith('docker '),(p,line)
report['answer_terminal_commands']='all start with docker'
q=json.loads((base/'제작자료/questions.json').read_text(encoding='utf-8'))
assert len(q)==12 and sum(i['points'] for i in q)==100 and sum(i['min'] for i in q)==110
report['question_count']=12;report['points']=100;report['minutes']=110
for area in ['정답','응시용']:
    cmd=[sys.executable,str(base/'응시용/tests/test_contracts.py'),str(base/area/'tasks')]
    r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
    (base/'제작자료'/('test_'+area+'.txt')).write_text(r.stdout+r.stderr,encoding='utf-8')
    report[area+'_test_exit']=r.returncode
assert report['정답_test_exit']==0
assert report['응시용_test_exit']!=0
for label,file in [('kafka',base/'응시용/docker-compose.yml'),('web_student',base/'응시용/tasks/q04/compose.yml'),('web_solution',base/'정답/tasks/q04/compose.yml')]:
    try:
        r=subprocess.run(['docker','compose','-f',str(file),'config','--format','json'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=40)
        report[label+'_compose_exit']=r.returncode
        if r.returncode==0:
            config=json.loads(r.stdout)
            if label=='kafka':
                assert list(config['services'])==['kafka']
                assert config['services']['kafka']['environment']['KAFKA_PROCESS_ROLES']=='broker,controller'
                assert not any('ZOOKEEPER' in k for k in config['services']['kafka']['environment'])
            (base/'제작자료'/('compose_'+label+'.json')).write_text(r.stdout,encoding='utf-8')
        else: report[label+'_error']=r.stderr
    except subprocess.TimeoutExpired: report[label+'_compose_exit']='timeout'
(base/'제작자료/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True,indent=2))
