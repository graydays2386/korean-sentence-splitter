import sys

def check_konlpy():
    print("=== 1. KoNLPy 설치 확인 ===")
    try:
        import konlpy
        print(f"KoNLPy 버전: {konlpy.__version__}")
    except ImportError:
        print("KoNLPy가 설치되지 않았습니다.")
        return

    print("\n=== 2. Okt (Java/JVM) 작동 확인 ===")
    try:
        from konlpy.tag import Okt
        okt = Okt()
        test_text = "테스트입니다"
        print(f"Okt 객체 생성 성공. 테스트 결과: {okt.pos(test_text)}")
    except Exception as e:
        print(f"Okt 실행 실패 (JDK 설치 또는 JAVA_HOME 설정을 확인하세요): {e}")

    print("\n=== 3. Mecab (C++ 라이브러리) 작동 확인 ===")
    print("사용자의 프로젝트는 Mecab을 우선적으로 사용하도록 설정되어 있습니다.")
    try:
        from konlpy.tag import Mecab
        mecab = Mecab()
        test_text = "아버지가방에들어가신다"
        print(f"Mecab 객체 생성 성공! 테스트 결과: {mecab.pos(test_text)}")
    except Exception as e:
        print("Mecab 실행 실패.")
        print(f"에러 메시지: {e}")
        print("-> 윈도우의 경우 'mecab-ko-msvc' 등을, 리눅스/맥은 'mecab-ko' 시스템 설치가 필요합니다.")

if __name__ == "__main__":
    check_konlpy()