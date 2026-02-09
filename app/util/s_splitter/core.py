# -*- coding: utf-8 -*-
from typing import List
from .data_model import CandidateSpan
from .normalizer import _normalize
from .basic_splitter import _basic_sentence_split
from .marker_splitter import _find_marker_splits
from .ending_splitter import _ending_based_splits
from .indices_splitter import _split_by_indices
from .chunk_merger import _merge_too_small

# -----------------------------
# 5) 메인: 규칙 기반 후보 분리
# -----------------------------
def rule_based_candidate_split(text: str) -> List[CandidateSpan]:
    """
    Step 1: rule-based candidate splitting for Korean informal compound text.
    Returns CandidateSpan list (over-splitting tendency, later to be refined by LLM).
    """
    original = text
    text = _normalize(text)

    candidates: List[CandidateSpan] = []

    # 1차 분할 (문장부호/개행)
    base_spans = _basic_sentence_split(text)

    for base_text, base_start, base_end in base_spans:
        # 2차 분할 후보: 담화 표지, 형태소 기반 연결어미/서술성 단서
        marker_idxs = _find_marker_splits(base_text)
        ending_idxs = _ending_based_splits(base_text)

        # 후보 index 합치기 (너무 촘촘하면 LLM 부담이 커지므로 간단한 downsample 가능)
        split_indices = sorted(set(marker_idxs + ending_idxs))

        pieces = _split_by_indices(base_text, split_indices)
        pieces = _merge_too_small(pieces)

        # CandidateSpan으로 반환 (reason은 디버그용)
        cursor_in_base = 0
        for piece in pieces:
            # 원본 위치 계산(대략): base_text 내 piece 검색
            found = base_text.find(piece, cursor_in_base)
            if found == -1:
                found = cursor_in_base
            start = base_start + found
            end = start + len(piece)
            cursor_in_base = found + len(piece)

            candidates.append(
                CandidateSpan(
                    text=piece,
                    reason="rule_based_candidate",
                    start=start,
                    end=end,
                )
            )

    return candidates
