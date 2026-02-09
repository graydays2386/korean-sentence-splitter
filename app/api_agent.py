from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

import httpx
import json
import re
from app.config import settings
from app.util.s_splitter.common.data_model import CandidateSpan

# -----------------------------
# IAM Token
# -----------------------------
async def get_iam_token(api_key: str) -> Optional[str]:
    """
    IBM Cloud IAM: API Key -> Bearer access token
    """
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "apikey": api_key,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, data=data)
        resp.raise_for_status()
        return resp.json().get("access_token")


def _ensure_query_params(url: str, extra_params: Dict[str, str]) -> str:
    """
    url에 query param을 안전하게 병합.
    """
    parts = urlparse(url)
    q = dict(parse_qsl(parts.query, keep_blank_values=True))
    for k, v in extra_params.items():
        if k not in q and v is not None:
            q[k] = v
    new_query = urlencode(q)
    return urlunparse(parts._replace(query=new_query))


def _to_jsonable_candidates(candidates: List[Any]) -> List[Dict[str, Any]]:
    """
    CandidateSpan(list) -> JSON 직렬화 가능한 dict list로 변환
    """
    out: List[Dict[str, Any]] = []
    for c in candidates:
        if is_dataclass(c):
            out.append(asdict(c))
        elif isinstance(c, dict):
            out.append(c)
        else:
            # 최소 호환: text만이라도 보존
            out.append({"text": str(c)})
    return out


# -----------------------------
# watsonx 호출
# -----------------------------
async def call_agent(
    url: str,
    *,
    candidates: List[Union[CandidateSpan, Dict[str, Any]]],
    original_text: Optional[str] = None,
    system_hint: Optional[str] = None,
    model_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    watsonx 배포/Chat API로 'candidates'를 전송하고, JSON 응답(dict)을 반환.

    - url: settings.DEPLOYMENT_NEWWIKI_URL / settings.DEPLOYMENT_MERGEWIKI_URL 등
    - candidates: rule_based_candidate_split()의 결과
    - original_text: 원문(선택). LLM이 재병합/정렬 시 유용
    - system_hint: system role에 넣을 간단 힌트(선택)
    - model_params: temperature/top_p/max_tokens 등(엔드포인트 스키마에 맞게 조정)
    """
    access_token = await get_iam_token(settings.API_KEY)
    if not access_token:
        raise ValueError("Failed to retrieve IAM access token")

    # (환경에 따라) version / project_id가 query param으로 요구되는 경우가 많아 보강
    # version 값은 조직 표준에 맞게 고정하거나 설정으로 분리 권장
    url = _ensure_query_params(
        url,
        {
            "version": "2023-05-29",
            "project_id": getattr(settings, "PROJECT_ID", None),
        },
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        # 일부 환경에서는 header로 project id를 요구하기도 하므로 같이 싣는 편이 안전
        "X-Watson-Project-Id": getattr(settings, "PROJECT_ID", ""),
    }

    candidates_payload = _to_jsonable_candidates(candidates)

    # LLM 입력(content)은 "문자열"로 보내는 편이 파서/로그 관점에서 안정적
    user_content_obj: Dict[str, Any] = {"candidates": candidates_payload}
    if original_text is not None:
        user_content_obj["original_text"] = original_text

    user_content = json.dumps(user_content_obj, ensure_ascii=False)

    messages: List[Dict[str, str]] = []
    if system_hint:
        messages.append({"role": "system", "content": system_hint})
    messages.append({"role": "user", "content": user_content})

    payload: Dict[str, Any] = {"messages": messages}

    # (선택) 모델 파라미터를 엔드포인트 스키마에 맞춰 추가
    if model_params:
        payload["parameters"] = model_params

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        # 디버그 필요 시 resp.text 로깅
        resp.raise_for_status()
        res = resp.json()

    # ---------
    # 응답 파싱:
    # - watsonx chat 응답은 구현/라우팅에 따라 구조가 다를 수 있음.
    # - 기존 코드의 "choices[0].message.content" 패턴을 우선 지원. :contentReference[oaicite:3]{index=3}
    # ---------
    content_text: Optional[str] = None
    try:
        # 1. content 추출 (watsonx Chat API 응답 구조 고려)
        content_text = res["choices"][0]["message"]["content"]
    except Exception:
        # 대체 경로(배포/게이트웨이별 응답 차이 대응)
        # 예: {"results":[{"generated_text":"..."}]} 류가 있을 수 있어 방어적으로 처리
        if isinstance(res, dict):
            for k in ("generated_text", "output_text", "text"):
                if k in res and isinstance(res[k], str):
                    content_text = res[k]
                    break
            if content_text is None and "results" in res and isinstance(res["results"], list) and res["results"]:
                cand = res["results"][0]
                if isinstance(cand, dict):
                    content_text = cand.get("generated_text") or cand.get("text")

    if not content_text:
        # 원형 응답 반환(호출자는 여기서 스키마 확인 가능)
        return {"raw_response": res}

    # 코드블록 제거 (```json ... ```)
    if "```" in content_text:
        content_text = content_text.replace("```json", "").replace("```", "").strip()

    # JSON 파싱 1차
    try:
        return json.loads(content_text)
    except json.JSONDecodeError:
        # JSON 객체 시작점부터 복구 시도
        try:
            m = re.search(r"\{.*", content_text, re.DOTALL)
            if m:
                obj, _ = json.JSONDecoder().raw_decode(m.group())
                return obj
        except Exception:
            pass

    # 파싱 실패 시: 원문 텍스트/원형 응답을 함께 반환
    return {
        "raw_text": content_text,
        "raw_response": res,
        "warning": "Failed to parse model output as JSON",
    }
