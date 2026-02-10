# -*- coding: utf-8 -*-
from typing import List
from .common.constants import MIN_CHUNK_CHARS, MIN_CHUNK_TOKENS
from .common.token_counter import _token_count

def _merge_too_small(chunks: List[str]) -> List[str]:
    if not chunks:
        return chunks

    merged: List[str] = []
    buf = chunks[0]
    for nxt in chunks[1:]:
        too_small = (len(buf.strip()) < MIN_CHUNK_CHARS) or (_token_count(buf) < MIN_CHUNK_TOKENS)
        if too_small:
            buf = buf + nxt  # 원문 보존 관점에서 공백을 “추가”하지 않음
        else:
            merged.append(buf)
            buf = nxt
    merged.append(buf)
    return merged
