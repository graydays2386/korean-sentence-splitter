# -*- coding: utf-8 -*-
import re
from typing import List, Tuple

def _basic_sentence_split(text: str) -> List[Tuple[str, int, int]]:
    """
    1차: 문장부호(.?!), 줄바꿈 기준의 거친 분할
    returns: list of (span_text, start_idx, end_idx)
    """
    spans = []
    # 문장부호/개행을 분리 토큰으로 보존하지 않고 경계로 사용
    pattern = re.compile(r"([.?!]+|\n+)")
    last = 0
    for m in pattern.finditer(text):
        end = m.start()
        chunk = text[last:end].strip()
        if chunk:
            spans.append((chunk, last, end))
        last = m.end()
    tail = text[last:].strip()
    if tail:
        spans.append((tail, last, len(text)))
    return spans
