# -*- coding: utf-8 -*-
from .tokenizer import TOKENIZER

def _token_count(text: str) -> int:
    if TOKENIZER is None:
        # fallback: whitespace token
        return len(text.split())
    return len(TOKENIZER.pos(text))
