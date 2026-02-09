# -*- coding: utf-8 -*-
from dataclasses import dataclass

# -----------------------------
# 3) 데이터 구조
# -----------------------------
@dataclass
class CandidateSpan:
    text: str
    reason: str  # why we split here (debuggable)
    start: int   # char start in original (optional usage)
    end: int     # char end in original
