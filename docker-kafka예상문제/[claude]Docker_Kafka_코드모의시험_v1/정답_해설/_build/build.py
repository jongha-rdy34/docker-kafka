"""templates/ 하나로 응시용(빈칸·버그 포함)과 정답_해설(정답 채움)을 동시에 생성한다.

표기법
  ⟪A:정답⟫        응시용에는 ______ , 정답에는 '정답'
  ⟪B:버그‖수정⟫   응시용에는 '버그'  , 정답에는 '수정'
  *.nb.py         '# %%' 셀 구분 → .ipynb 로 변환

실행: python build.py   (어느 위치에서 실행해도 됨)
"""
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "templates"
ROOT = HERE.parent.parent                 # [claude]Docker_Kafka_코드모의시험_v1
OUT_EXAM = ROOT / "응시용"
OUT_ANS = ROOT / "정답_해설"

BLANK = "______"
PAT_A = re.compile(r"⟪A:(.*?)⟫", re.S)
PAT_B = re.compile(r"⟪B:(.*?)‖(.*?)⟫", re.S)


def render(text: str, answer: bool) -> str:
    text = PAT_B.sub(lambda m: m.group(2) if answer else m.group(1), text)
    text = PAT_A.sub(lambda m: m.group(1) if answer else BLANK, text)
    assert "⟪" not in text and "⟫" not in text, "닫히지 않은 표기"
    return text


def to_ipynb(src: str) -> str:
    cells, cur, kind = [], [], None

    def flush():
        if kind is None:
            return
        lines = cur[:]
        while lines and not lines[-1].strip():
            lines.pop()
        while lines and not lines[0].strip():
            lines.pop(0)
        if kind == "markdown":
            lines = [l[2:] if l.startswith("# ") else l.lstrip("#") for l in lines]
            cells.append({"cell_type": "markdown", "metadata": {},
                          "source": [l + "\n" for l in lines[:-1]] + lines[-1:]})
        else:
            cells.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                          "outputs": [], "source": [l + "\n" for l in lines[:-1]] + lines[-1:]})

    for line in src.splitlines():
        if line.startswith("# %%"):
            flush()
            kind = "markdown" if "[markdown]" in line else "code"
            cur = []
        else:
            cur.append(line)
    flush()
    nb = {"cells": cells, "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
    return json.dumps(nb, ensure_ascii=False, indent=1) + "\n"


def large_messages() -> str:
    """hw3-2 large_message.txt 처럼 약 300바이트짜리 긴 메시지 20줄"""
    rows = []
    for i in range(1, 21):
        head = f"bulk-{i:02d} warehouse-sync "
        rows.append(head + ("x" if i % 2 else "y") * (300 - len(head)))
    return "\n".join(rows) + "\n"


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    if OUT_EXAM.exists():                  # 폴더 자체는 두고 내용만 지움(탐색기·셸이 열고 있어도 덜 실패)
        for sub in OUT_EXAM.iterdir():
            shutil.rmtree(sub) if sub.is_dir() else sub.unlink()
    for sub in OUT_ANS.iterdir():          # 정답_해설 안의 생성물만 지움(_build, 해설 문서 보존)
        if sub.is_dir() and (sub.name.startswith("q") or sub.name == "kafka-docker"):
            shutil.rmtree(sub)

    count = 0
    for src in sorted(TEMPLATES.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(TEMPLATES)
        text = src.read_text(encoding="utf-8")
        for out_root, is_ans in ((OUT_EXAM, False), (OUT_ANS, True)):
            body = render(text, is_ans)
            if src.name.endswith(".nb.py"):
                dst = out_root / rel.parent / src.name.replace(".nb.py", ".ipynb")
                write(dst, to_ipynb(body))
            else:
                write(out_root / rel, body)
        count += 1
    for out_root in (OUT_EXAM, OUT_ANS):
        write(out_root / "q07" / "large_messages.txt", large_messages())
    print(f"rendered {count} templates -> 응시용 / 정답_해설")


if __name__ == "__main__":
    main()
