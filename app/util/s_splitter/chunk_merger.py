# -*- coding: utf-8 -*-
from typing import List
from .common.constants import MIN_CHUNK_CHARS, MIN_CHUNK_TOKENS
from .common.token_counter import _token_count

def _merge_too_small(chunks: List[str]) -> List[str]:
    """
    너무 작은 조각을 이웃과 병합해 과도 분절을 완화.
    """
    if not chunks:
        return chunks

    merged = []
    buf = chunks[0]
    for nxt in chunks[1:]:
        too_small = (len(buf) < MIN_CHUNK_CHARS) or (_token_count(buf) < MIN_CHUNK_TOKENS)
        if too_small:
            buf = f"{buf} {nxt}".strip()
        else:
            merged.append(buf)
            buf = nxt
    merged.append(buf)
    return merged
