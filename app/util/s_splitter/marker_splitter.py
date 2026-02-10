# -*- coding: utf-8 -*-
import re
from typing import List
from .common.constants import DISCOURSE_SPLIT_MARKERS

def _find_marker_splits(span: str) -> List[int]:
    indices: List[int] = []
    for marker in DISCOURSE_SPLIT_MARKERS:
        for m in re.finditer(rf"(^|[\s,])({re.escape(marker)})(?=[\s,])", span):
            idx = m.start(2)
            if 0 < idx < len(span):
                indices.append(idx)
    return sorted(set(indices))
