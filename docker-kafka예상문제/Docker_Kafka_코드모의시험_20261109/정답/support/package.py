from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path.cwd()
paths=[]
for folder in ('answers','tasks','evidence'):
    paths.extend(p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
for name in ('errors.txt','empty-errors.txt'):
    p=root/'data'/name
    if p.exists(): paths.append(p)
with ZipFile(root/'submission.zip','w',ZIP_DEFLATED) as z:
    for p in sorted(paths): z.write(p,p.relative_to(root))
print('submission.zip: '+str(len(paths))+' files')
