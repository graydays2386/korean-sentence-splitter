# -*- coding: utf-8 -*-
# -----------------------------
# 1) 형태소 분석기 준비 (Mecab 우선, 없으면 Okt)
# -----------------------------
def get_tokenizer():
    """
    Returns a tokenizer-like object with a .pos(text) -> List[Tuple[str, str]] interface.
    Prefers Mecab (fast, good for Korean), falls back to Okt.
    """
    try:
        from konlpy.tag import Mecab  # type: ignore
        return Mecab()
    except Exception:
        try:
            from konlpy.tag import Okt  # type: ignore
            return Okt()
        except Exception:
            return None

TOKENIZER = get_tokenizer()
