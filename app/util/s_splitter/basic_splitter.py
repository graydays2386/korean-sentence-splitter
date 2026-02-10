# -*- coding: utf-8 -*-
import re
from typing import List, Tuple

def _basic_sentence_split(text: str) -> List[Tuple[str, int, int]]:
    """
    1차: 문장부호(.?!), 줄바꿈 기준의 거친 분할.
    *중요*: substring/offset 정확 보존을 위해 strip 하지 않음.
    returns: list of (span_text, start_idx, end_idx) where span_text == text[start:end]
    """
    spans: List[Tuple[str, int, int]] = []

    # 문장 경계로 쓰되, 구두점/개행은 '앞 조각'에 포함시켜 원문 재구성 용이하게
    pattern = re.compile(r"([.?!]+|\n+)")
    last = 0

    for m in pattern.finditer(text):
        end = m.end()  # 구두점/개행 포함
        chunk = text[last:end]
        if chunk:
            spans.append((chunk, last, end))
        last = end

    if last < len(text):
        tail = text[last:]
        if tail:
            spans.append((tail, last, len(text)))

    return spans