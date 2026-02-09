# -*- coding: utf-8 -*-
from typing import List
from .tokenizer import TOKENIZER
from .constants import CONNECTIVE_ENDINGS, NOMINAL_PREDICATE_PATTERNS

def _ending_based_splits(span: str) -> List[int]:
    """
    형태소 분석이 가능할 때, 연결어미/서술성 패턴을 근거로 split 후보를 찾음.
    이 함수는 '정밀'보다 '후보 최대 포착'이 목표.
    """
    if TOKENIZER is None:
        return []

    # KoNLPy tagset은 분석기에 따라 다르므로, 여기선 "끝말" 중심 heuristics만 사용
    # Okt: ('...','Josa'/'Eomi' 등) / Mecab: 'EC','EF','ETM' 등
    pos = TOKENIZER.pos(span)

    split_char_indices = []
    cursor = 0

    # token -> char alignment (완전 일치가 아닐 수 있어 간단히 검색 기반으로 이동)
    for i, (tok, tag) in enumerate(pos):
        # 현재 cursor부터 tok를 찾음
        found = span.find(tok, cursor)
        if found == -1:
            continue
        tok_start = found
        tok_end = found + len(tok)
        cursor = tok_end

        # 1) 연결어미 단서: 토큰이 CONNECTIVE_ENDINGS에 포함되거나, tag가 연결 어미 계열이면 split 후보
        if tok in CONNECTIVE_ENDINGS:
            # 연결어미 뒤에 이어지는 내용을 새로운 후보로 볼 수 있음
            # split은 tok_end 위치(어미 뒤)로 둠
            if 0 < tok_end < len(span) - 1:
                split_char_indices.append(tok_end)

        if tag in ("EC", "EF"):  # Mecab 계열
            if 0 < tok_end < len(span) - 1:
                split_char_indices.append(tok_end)

        # 2) 서술성 명사 패턴: (전체 span 끝) 또는 중간 구간에 “...함” 등이 나오면 경계 후보
        # 여기서는 token이 '함'이고 앞 토큰이 의미 있는 경우를 후보로 둠
        if tok == "함":
            if 0 < tok_end < len(span) - 1:
                split_char_indices.append(tok_end)

    # 패턴 기반 보강: “…하는 것”, “…할 수” 등
    for pat in NOMINAL_PREDICATE_PATTERNS:
        for m in pat.finditer(span):
            end = m.end()
            if 0 < end < len(span) - 1:
                split_char_indices.append(end)

    # 정리
    split_char_indices = sorted(set(split_char_indices))
    return split_char_indices
