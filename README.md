# korean-sentence-splitter

Rule-based candidate splitter for Korean informal compound text.
This project is designed as an offset-preserving preprocessing step before LLM-based refinement.

## Overview
Korean informal text often contains ambiguous sentence boundaries that cannot be reliably detected by punctuation alone.
Instead of directly forcing a final segmentation, this project generates candidate spans that can later be merged or refined by an LLM or downstream rule layer.

## Problem Statement
In Korean informal or loosely structured text:
- sentence boundaries may appear without punctuation
- discourse markers may indicate semantic transitions
- connective endings may suggest clause boundaries
- comma usage may reflect either syntax or discourse, not always final sentence boundaries

Because of this, punctuation-only splitting is often insufficient.

## Design Principles
- Preserve substring offsets whenever possible
- Allow over-segmentation rather than miss potential boundaries
- Keep rules interpretable and easy to control
- Assume downstream LLM-based refinement

## Pipeline
1. **Normalize text**  
   - Normalizes whitespace and excessive line breaks before splitting.
2. **Initial coarse split**  
   - Performs a rough first-pass split on punctuation (`.?!`) and newlines while preserving original substrings and offsets.
3. **Marker-based split detection**  
   - Detects candidate boundaries around discourse markers inside each coarse span.
4. **Ending-based split detection**  
   - Detects additional boundaries from connective endings and nominal predicate patterns using morphological cues.
5. **Comma-based split detection**  
   - Uses comma patterns and post-comma discourse hints to find clause-like split candidates.
6. **Split by collected indices**  
   - Splits each span using the combined boundary indices gathered from the previous heuristics.
7. **Merge overly small chunks**  
   - Merges chunks that are too short to be useful as standalone candidates.
8. **Return candidate spans**  
   - Returns offset-preserving `CandidateSpan(text, reason, start, end)` objects for downstream refinement.

## Data Model
Each candidate span contains:
- `text`
- `reason`
- `start`
- `end`

## Example Usage
```python
from app.util.s_splitter.core import rule_based_candidate_split

text = "..."
result = rule_based_candidate_split(text)

for span in result:
    print(span.text, span.start, span.end)

## **Intended Use**
- Knowledge management pipelines
- Wiki / document preprocessing
- Korean NLP experiments
