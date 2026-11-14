from pathlib import Path
import json, re, html, textwrap
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
base=Path(__file__).resolve().parents[1]
pdfdir=base/'output/pdf'; pdfdir.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('KR','C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('KRB','C:/Windows/Fonts/malgunbd.ttf'))
styles={
 'title':ParagraphStyle('title',fontName='KRB',fontSize=25,leading=34,textColor=colors.HexColor('#102B46'),spaceAfter=18,wordWrap='CJK'),
 'h1':ParagraphStyle('h1',fontName='KRB',fontSize=15,leading=22,textColor=colors.HexColor('#114E67'),spaceAfter=10,wordWrap='CJK'),
 'body':ParagraphStyle('body',fontName='KR',fontSize=10,leading=16,spaceAfter=9,wordWrap='CJK'),
 'meta':ParagraphStyle('meta',fontName='KR',fontSize=8.5,leading=13,textColor=colors.HexColor('#526777'),spaceAfter=9,wordWrap='CJK'),
 'code':ParagraphStyle('code',fontName='KR',fontSize=8,leading=12,spaceAfter=3,wordWrap='CJK',backColor=colors.HexColor('#F0F4F7'),borderPadding=5),
 'cell':ParagraphStyle('cell',fontName='KR',fontSize=9,leading=14,wordWrap='CJK')}
def P(t,kind='body'): return Paragraph(html.escape(t).replace('\n','<br/>'),styles[kind])
def code(text):
    # Preserve indentation; wrap long command lines only for print display.
    return [Paragraph(html.escape(line).replace(' ','&#160;') or '&#160;',styles['code']) for line in text.splitlines()]
def foot(c,doc):
    c.setStrokeColor(colors.HexColor('#D8E2E9')); c.line(44,42,A4[0]-44,42)
    c.setFont('KR',8);c.setFillColor(colors.HexColor('#526777'))
    c.drawString(44,29,'SSAFY 학습용 창작 모의시험 | 2026-11-09 대비')
    c.drawRightString(A4[0]-44,29,str(doc.page))
def build(name,story):
    doc=SimpleDocTemplate(str(pdfdir/name),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=42,bottomMargin=56,
                          title=name[:-4],author='학습용 모의시험')
    doc.build(story,onFirstPage=foot,onLaterPages=foot)
q=json.loads((base/'제작자료/questions.json').read_text(encoding='utf-8'))
e=json.loads((base/'제작자료/explanations.json').read_text(encoding='utf-8'))
s=[P('Docker & Kafka\n코드 모의시험','title'),P('문제지 | 12문항 · 100점 · 권장 110분','h1'),
   P('택배 허브의 실행 환경과 이벤트 처리','h1'),
   P('Docker 이미지·컨테이너·Compose를 구성하고 Kafka 토픽과 메시지를 관리합니다. Python으로 Admin, Producer, Consumer와 간단한 변환 파이프라인을 완성합니다.'),
   P('이 시간·배점·제출 규칙은 이번 모의시험의 설계입니다. 실제 평가 공지로 해석하지 마세요.'),
   P('풀이 전 확인','h1'),
   P('응시용/README.md의 사전 준비를 마친 뒤 시간을 측정합니다. Kafka는 제공된 단일 브로커 KRaft Compose가 이미 실행된 것으로 가정합니다. 실제 Setup.exe에서 받은 파일은 아닙니다. 이 컴퓨터에 설치하거나 기동하지 않았습니다.'),
   P('터미널에서 실행하는 명령은 모두 docker로 시작해야 합니다. 메시지 본문 입력과 편집기에서의 코드 수정은 명령어가 아닙니다. Java·Kafka를 호스트에 설치하는 문제는 없습니다.'),
   P('정답은 별도 폴더·PDF에 있습니다. 문제지와 시작 파일의 이름·함수·입력 데이터를 유지하세요. 실제 실행을 하지 않았다면 실행 증거를 작성한 것으로 표시하지 마세요.'),
   P('구성과 제출','h1')]
rows=[[P('영역','cell'),P('문항','cell'),P('점수 / 권장 시간','cell')],
      [P('Docker·Compose','cell'),P('Q01~04','cell'),P('30점 / 33분','cell')],
      [P('Kafka CLI','cell'),P('Q05~07','cell'),P('25점 / 25분','cell')],
      [P('Python Kafka','cell'),P('Q08~11','cell'),P('35점 / 42분','cell')],
      [P('조건·결과 해석','cell'),P('Q12','cell'),P('10점 / 10분','cell')]]
t=Table(rows,colWidths=[180,100,220]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E2EDF3')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),0.4,colors.HexColor('#D8E2E9'))]));s+=[t,Spacer(1,12),P('수정 파일과 제출 방법은 README에 정리되어 있습니다. answers, tasks, evidence와 Q03 결과 파일을 submission.zip으로 제출합니다. 26개 함수 테스트는 실제 Docker·Kafka 실행 검증을 대신하지 않습니다.','meta')]
for idx,item in enumerate(q):
    if idx%2==0:s.append(PageBreak())
    else:s.append(Spacer(1,24))
    s.append(P('Q%02d. %s'%(item['n'],item['title']),'h1'))
    s.append(P('%s점 | 권장 %s분 | 수정: %s'%(item['points'],item['min'],item['file']),'meta'))
    for para in item['body'].split('\n'):s.append(P(para))
    s.append(P('배점: '+item['rubric'],'meta'))
build('01_모의시험_문제.pdf',s)
s=[P('Docker & Kafka\n정답·해설','title'),P('문제지와 분리된 채점·복습 자료','h1'),P('먼저 응시용 시작 파일로 시험을 풀어 보세요. 이 문서는 완성 코드와 명령을 포함합니다.'),
   P('정답 폴더는 공통 Compose, 입력 데이터, 실행기와 테스트를 포함한 완성본입니다. 응시용과 동시에 실행하지 말고 각각의 루트에서 사용하세요. 동일한 컨테이너 이름과 프로젝트 이름을 씁니다.'),
   P('검증 범위','h1'),P('Q08~11 정답의 오프라인 계약 테스트 26개가 통과했습니다. 빈 입력·한글·잘못된 UTF-8·전송 실패가 포함됩니다. 실제 Docker 이미지 빌드와 Kafka 송수신은 Docker 엔진 미실행으로 확인하지 못했습니다. 자세한 내용은 검증보고서.md를 보세요.'),
   P('채점 원칙','h1'),P('동치인 옵션·코드 표현은 인정하되 토픽명·컨테이너명·포트·함수 반환·경계조건을 지켜야 합니다. 명령 성공 여부와 요구한 결과를 함께 확인하세요. Q01~07과 Q12는 수동으로 채점합니다.'),
   P('PDF의 긴 명령은 지면상 줄바꿈될 수 있습니다. 복사해 실행할 때는 정답/answers의 한 줄 명령 또는 실행 안내 원문을 사용하세요.'),
   P('출처대응표.md에 문항별 실습·강의 페이지와 실제 시험에서 참고한 형식을 기록했습니다. 기존 시험의 배점이나 제출 규정을 이번 시험의 규정으로 단정하지 않았습니다.')]
for item,ex in zip(q,e):
    n=item['n'];s.append(PageBreak());s.append(P('Q%02d. %s'%(n,item['title']),'h1'));s.append(P(ex));s.append(P('배점: '+item['rubric'],'meta'))
    paths=['answers/q%02d.txt'%n] if n<=7 else ['answers/q12.md'] if n==12 else ['tasks/q%02d_%s.py'%(n,{8:'admin',9:'producer',10:'consumer',11:'pipeline'}[n])]
    if n==2:paths+=['tasks/q02/Dockerfile','tasks/q02/app.py']
    if n==4:paths+=['tasks/q04/compose.yml']
    for p in paths:
        s.append(P(p,'meta')); txt=(base/'정답'/p).read_text(encoding='utf-8')
        if n==12:
            for para in txt.split('\n\n')[1:]:s.append(P(para))
        else:s.extend(code(txt))
build('02_모의시험_정답해설.pdf',s)
print('PDFs created')
