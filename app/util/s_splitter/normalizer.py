# -*- coding: utf-8 -*-
import re

# -----------------------------
# 4) 유틸
# -----------------------------
def _normalize(text: str) -> str:
    # 공백/개행을 안정화
    text = text.replace("\u00A0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
