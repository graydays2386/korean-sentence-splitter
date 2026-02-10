# -*- coding: utf-8 -*-
from typing import List
from .common.tokenizer import TOKENIZER
from .common.constants import CONNECTIVE_ENDINGS, NOMINAL_PREDICATE_PATTERNS

def _ending_based_splits(span: str) -> List[int]:
    if TOKENIZER is None:
        return []

    pos = TOKENIZER.pos(span)
    split_char_indices: List[int] = []
    cursor = 0

    for tok, tag in pos:
        found = span.find(tok, cursor)
        if found == -1:
            continue
        tok_end = found + len(tok)
        cursor = tok_end

        # 1) 연결어미 단서
        if tok in CONNECTIVE_ENDINGS and 0 < tok_end < len(span):
            split_char_indices.append(tok_end)

        # Mecab 계열 태그 보강(있으면)
        if tag in ("EC", "EF") and 0 < tok_end < len(span):
            split_char_indices.append(tok_end)

        # 2) 서술성 명사 단서
        if tok == "함" and 0 < tok_end < len(span):
            split_char_indices.append(tok_end)

    for pat in NOMINAL_PREDICATE_PATTERNS:
        for m in pat.finditer(span):
            end = m.end()
            if 0 < end < len(span):
                split_char_indices.append(end)

    return sorted(set(split_char_indices))
