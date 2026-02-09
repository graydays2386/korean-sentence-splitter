import httpx
import json
import re  # 정규표현식 사용을 위해 추가 권장

async def get_iam_token(api_key):

    """API Key로 Access Token 발급 (비동기 변환)"""
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"apikey": api_key, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()["access_token"]
        except Exception as e:
            print(f"❌ 토큰 발급 실패: {e}")
            return None

async def call_agent(url: str, data: dict) -> dict:
    """
    Call external LLM agent asynchronously.
    """
    access_token = await get_iam_token(settings.API_KEY)
    
    if not access_token:
        raise ValueError("Failed to retrieve IAM token")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [{"role": "user", "content": data["content"]}]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=120.0)
        
        # [디버깅] 상태 코드 확인
        if response.status_code != 200:
            print(f"❌ Status Code: {response.status_code}")
            print(f"❌ Error Response: {response.text}")
        
        response.raise_for_status()
        res = response.json()
        
        # LLM의 텍스트 응답 추출
        content_text = res["choices"][0]["message"]["content"]
        print(f"🔍 Raw LLM Output: {content_text}")

        # === [안전장치 시작] ===
        
        # 1. 마크다운 코드 블록 제거 (```json ... ```)
        if "```" in content_text:
            content_text = content_text.replace("```json", "").replace("```", "").strip()

        # 2. JSON 파싱 및 예외 처리
        try:
            parsed_data = json.loads(content_text)
            return parsed_data
            
        except json.JSONDecodeError as e:
                        
            # [추가 안전장치] 단순 replace로 해결되지 않는 경우, 정규표현식으로 JSON 객체만 추출 시도
            try:
                match = re.search(r'\{.*', content_text, re.DOTALL)
                if match:
                    potential_json = match.group()
                    # 2. raw_decode를 사용하여 유효한 부분까지만 파싱
                    obj, index = json.JSONDecoder().raw_decode(potential_json)
                    return obj
            except Exception as e2:
                pass # 2차 시도도 실패하면 아래에서 빈 dict 리턴

            print("⚠️ 파싱 실패로 인해 빈 딕셔너리를 반환합니다.")
            return {} 
            
        # === [안전장치 끝] ===