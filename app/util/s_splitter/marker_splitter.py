# -*- coding: utf-8 -*-
import re
from typing import List
from .constants import DISCOURSE_SPLIT_MARKERS

def _find_marker_splits(span: str) -> List[int]:
    """
    담화 표지를 기준으로 split index 후보(문자 인덱스)를 찾음.
    """
    indices = []
    for marker in DISCOURSE_SPLIT_MARKERS:
        # 단어 경계 비슷하게: 앞은 공백/문장시작, 뒤는 공백/구두점
        for m in re.finditer(rf"(^|[\s,])({re.escape(marker)})([\s,])", span):
            idx = m.start(2)  # marker 시작 위치
            if 0 < idx < len(span) - 1:
                indices.append(idx)
    return sorted(set(indices))
