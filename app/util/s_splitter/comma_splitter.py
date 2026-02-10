# -*- coding: utf-8 -*-
import re
from typing import List

# “...었는데, ...” / “...인데, ...” / “...고, ...” / “...며, ...” / “...지만, ...”
# + “...수 있고, ...” 같이 ‘있고,’ 뒤 의미절 후보도 포착
_COMMA_ENDING_PAT = re.compile(
    r"(었는데|았는데|였는데|인데|는데|지만|고|며|면서|자|니)\s*,\s*"
)

# 쉼표 뒤가 새로운 의미절로 시작하는 “전환/첨가” 류 단서(너무 공격적이면 축소)
_AFTER_COMMA_HINT = re.compile(
    r"^\s*(당시|마침|그리고|또|또한|반면|하지만|다만|한편|그러나|그래서|따라서|즉)\b"
)

def _comma_based_splits(span: str) -> List[int]:
    """
    쉼표(,)를 의미절 경계 후보로 활용.
    반환값은 'span 내 char index' (split 시작점) 리스트.
    - split point는 '쉼표 다음(콤마+공백 뒤)' 위치로 둠.
    """
    idxs: List[int] = []

    for m in _COMMA_ENDING_PAT.finditer(span):
        cut = m.end()  # 콤마+공백까지 포함한 다음 위치
        if 0 < cut < len(span):
            idxs.append(cut)

    # 보강: 쉼표 뒤에 담화 전환/첨가 표지가 바로 나오면 경계 후보
    for cm in re.finditer(r",\s*", span):
        cut = cm.end()
        if 0 < cut < len(span):
            tail = span[cut:cut + 24]
            if _AFTER_COMMA_HINT.search(tail):
                idxs.append(cut)

    return sorted(set(idxs))