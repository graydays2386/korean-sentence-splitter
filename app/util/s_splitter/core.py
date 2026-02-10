# -*- coding: utf-8 -*-
from typing import List
from .common.data_model import CandidateSpan
from .normalizer import _normalize
from .basic_splitter import _basic_sentence_split
from .marker_splitter import _find_marker_splits
from .ending_splitter import _ending_based_splits
from .comma_splitter import _comma_based_splits
from .indices_splitter import _split_by_indices
from .chunk_merger import _merge_too_small

def rule_based_candidate_split(text: str) -> List[CandidateSpan]:
    """
    Step1: rule-based candidate splitting for Korean informal compound text.
    - 오프셋/substring 보존을 최우선.
    - 과분절 허용(LLM 후처리 전제) + 쉼표/서술어 기반 의미절 후보 포착 강화.
    """
    text = _normalize(text)

    candidates: List[CandidateSpan] = []

    base_spans = _basic_sentence_split(text)

    for base_text, base_start, base_end in base_spans:
        marker_idxs = _find_marker_splits(base_text)
        ending_idxs = _ending_based_splits(base_text)
        comma_idxs = _comma_based_splits(base_text)

        split_indices = sorted(set(marker_idxs + ending_idxs + comma_idxs))

        pieces = _split_by_indices(base_text, split_indices)
        pieces = _merge_too_small(pieces)

        # pieces는 base_text substring들의 순서열이어야 함
        cursor = 0
        for piece in pieces:
            found = base_text.find(piece, cursor)
            if found == -1:
                # fail-safe: 남은 구간을 그냥 던짐(오프셋 보존 우선)
                found = cursor
            start = base_start + found
            end = start + len(piece)
            cursor = found + len(piece)

            candidates.append(
                CandidateSpan(
                    text=piece,
                    reason="rule_based_candidate",
                    start=start,
                    end=end,
                )
            )
    print(candidates)

    return candidates
