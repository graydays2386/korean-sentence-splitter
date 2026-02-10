# -*- coding: utf-8 -*-
from typing import List

def _split_by_indices(span: str, indices: List[int]) -> List[str]:
    """
    indices: span 내 char index (split 시작점).
    *중요*: 어떤 경우에도 원문 재구성을 깨는 strip 제거.
    """
    if not indices:
        return [span]

    cuts = [0] + [i for i in indices if 0 < i < len(span)] + [len(span)]
    cuts = sorted(set(cuts))

    raw_pieces = [span[a:b] for a, b in zip(cuts, cuts[1:])]

    # 공백만 있는 조각은 앞 조각에 붙여 재구성을 안정화
    out: List[str] = []
    for p in raw_pieces:
        if not out:
            out.append(p)
            continue
        if p.strip() == "":
            out[-1] = out[-1] + p
        else:
            out.append(p)

    return out