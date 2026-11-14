from pathlib import Path
import subprocess,json
from PIL import Image,ImageOps,ImageDraw
from pypdf import PdfReader
base=Path(__file__).resolve().parents[1]
qa=base/'제작자료/pdf_qa';qa.mkdir(parents=True,exist_ok=True)
pop='C:/Users/82109/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
checks={}
for p in sorted((base/'output/pdf').glob('*.pdf')):
    key='exam' if p.name.startswith('01') else 'solution'
    subprocess.run([pop,'-scale-to','1400','-png',str(p),str(qa/key)],check=True)
    pages=sorted(qa.glob(key+'-*.png'))
    r=PdfReader(p);text='\n'.join(x.extract_text() or '' for x in r.pages)
    assert all('Q%02d.'%n in text for n in range(1,13))
    assert '\u25a0' not in text
    checks[key]={'pages':len(r.pages),'rendered':len(pages),'all_questions_present':True}
    for start in range(0,len(pages),6):
        batch=pages[start:start+6]; sheet=Image.new('RGB',(1000,740*((len(batch)+2)//3)),'#dde4ea')
        for i,imgpath in enumerate(batch):
            im=Image.open(imgpath).convert('RGB');im.thumbnail((320,700))
            x=(i%3)*333+6;y=(i//3)*740+22;sheet.paste(im,(x,y))
            ImageDraw.Draw(sheet).text((x,y-17),imgpath.stem,fill='black')
        sheet.save(qa/(key+'_contact_'+str(start//6+1)+'.jpg'))
(base/'제작자료/pdf_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks))
