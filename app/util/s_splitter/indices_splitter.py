# -*- coding: utf-8 -*-
from typing import List

def _split_by_indices(span: str, indices: List[int]) -> List[str]:
    """
    indices는 span 내의 char index (split start positions).
    예: indices=[10, 25] -> [0:10], [10:25], [25:end]
    """
    if not indices:
        return [span.strip()]

    cuts = [0] + indices + [len(span)]
    out = []
    for a, b in zip(cuts, cuts[1:]):
        piece = span[a:b].strip(" ,")
        if piece:
            out.append(piece.strip())
    return out
