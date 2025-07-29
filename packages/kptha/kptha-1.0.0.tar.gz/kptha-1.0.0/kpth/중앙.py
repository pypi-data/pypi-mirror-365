import sys
import os
import traceback
from typing import Optional
from .번역기 import 코드_번역

class 실행오류정보:
    """한국어 코드 실행 시 발생한 오류의 정보를 관리"""
    
    def __init__(self, 원본코드: str, 번역된코드: str):
        self.원본코드_줄들 = 원본코드.splitlines()
        self.번역된코드_줄들 = 번역된코드.splitlines()
    
    def 오류위치_변환(self, 파이썬_줄번호: int) -> int:
        """파이썬 오류 줄번호를 원본 한국어 코드 줄번호로 변환"""
        return 파이썬_줄번호
    
    def 친화적_오류메시지(self, 오류: Exception, 줄번호: Optional[int] = None) -> str:
        """사용자 친화적인 한국어 오류 메시지 생성"""
        오류타입 = type(오류).__name__
        오류메시지 = str(오류)
        
        # 일반적인 오류 메시지를 한국어로 번역
        한국어_오류타입 = self._오류타입_번역(오류타입)
        한국어_오류메시지 = self._오류메시지_번역(오류메시지)
        
        결과 = f"🚨 {한국어_오류타입}: {한국어_오류메시지}"
        
        if 줄번호 and 1 <= 줄번호 <= len(self.원본코드_줄들):
            문제줄 = self.원본코드_줄들[줄번호 - 1].strip()
            결과 += f"\n📍 {줄번호}번째 줄: {문제줄}"
        
        return 결과
    
    def _오류타입_번역(self, 오류타입: str) -> str:
        """오류 타입을 한국어로 번역"""
        번역맵 = {
            'SyntaxError': '문법 오류',
            'NameError': '이름 오류',
            'TypeError': '타입 오류', 
            'ValueError': '값 오류',
            'IndexError': '인덱스 오류',
            'KeyError': '키 오류',
            'AttributeError': '속성 오류',
            'ImportError': '임포트 오류',
            'ModuleNotFoundError': '모듈을 찾을 수 없음',
            'FileNotFoundError': '파일을 찾을 수 없음',
            'PermissionError': '권한 오류',
            'ZeroDivisionError': '0으로 나누기 오류',
            'IndentationError': '들여쓰기 오류',
            'TabError': '탭 오류',
            'RuntimeError': '런타임 오류',
            'RecursionError': '재귀 오류',
            'MemoryError': '메모리 오류',
            'OverflowError': '오버플로우 오류',
            'UnboundLocalError': '지역 변수 바인딩 오류',
        }
        return 번역맵.get(오류타입, 오류타입)
    
    def _오류메시지_번역(self, 메시지: str) -> str:
        """기본 오류 메시지를 한국어로 번역"""
        번역맵 = {
            "name '{}' is not defined": "이름 '{}'가 정의되지 않았습니다",
            "invalid syntax": "잘못된 문법입니다",
            "unexpected EOF while parsing": "구문 분석 중 예상치 못한 파일 끝",
            "list index out of range": "리스트 인덱스가 범위를 벗어났습니다",
            "division by zero": "0으로 나눌 수 없습니다",
            "unsupported operand type(s)": "지원되지 않는 연산자 타입",
            "can't assign to literal": "리터럴에 할당할 수 없습니다",
            "No module named": "모듈을 찾을 수 없습니다:",
        }
        
        for 영어, 한국어 in 번역맵.items():
            if 영어 in 메시지:
                return 메시지.replace(영어, 한국어)
        
        return 메시지


def 주_실행():
    """메인 실행 함수"""
    if len(sys.argv) < 2:
        print("⚠️  사용법: ㅋㅍ <파일명.kpy>")
        print("   예시: ㅋㅍ hello.kpy")
        print("   예시: ㅋㅍ --debug hello.kpy  (디버그 모드)")
        sys.exit(1)

    # 명령행 인수 파싱
    디버그_모드 = False
    파일_경로 = None
    
    for i, 인수 in enumerate(sys.argv[1:], 1):
        if 인수 == "--debug" or 인수 == "-d":
            디버그_모드 = True
        elif 인수 == "--help" or 인수 == "-h":
            도움말_출력()
            sys.exit(0)
        elif 인수 == "--version" or 인수 == "-v":
            버전_출력()
            sys.exit(0)
        elif not 인수.startswith("-"):
            파일_경로 = 인수
            break
    
    if not 파일_경로:
        print("⚠️  오류: 실행할 .kpy 파일을 지정해야 합니다.")
        print("   사용법: ㅋㅍ <파일명.kpy>")
        sys.exit(1)

    # 확장자 검사
    if not 파일_경로.endswith(".kpy"):
        print("⚠️  오류: .kpy 확장자를 가진 파일만 실행할 수 있습니다.")
        print(f"   제공된 파일: {파일_경로}")
        print(f"   올바른 예시: {파일_경로}.kpy")
        sys.exit(1)

    # 파일 존재 여부 검사
    if not os.path.exists(파일_경로):
        print("⚠️  오류: 파일을 찾을 수 없습니다.")
        print(f"   경로: {os.path.abspath(파일_경로)}")
        print("   현재 디렉터리에 있는 .kpy 파일들:")
        kpy_파일들 = [f for f in os.listdir('.') if f.endswith('.kpy')]
        if kpy_파일들:
            for 파일 in kpy_파일들:
                print(f"     - {파일}")
        else:
            print("     (없음)")
        sys.exit(1)

    # 파일 실행
    코드_실행(파일_경로, 디버그_모드)


def 도움말_출력():
    """도움말 메시지 출력"""
    print("""
🇰🇷 KPTH - 한국어 파이썬 번역기

사용법:
  ㅋㅍ <파일명.kpy>           # 한국어 파이썬 파일 실행
  ㅋㅍ --debug <파일명.kpy>   # 디버그 모드로 실행
  ㅋㅍ --help                # 이 도움말 출력  
  ㅋㅍ --version             # 버전 정보 출력

예시:
  ㅋㅍ hello.kpy
  ㅋㅍ -d complex_program.kpy

디버그 모드에서는 번역된 파이썬 코드와 자세한 오류 정보를 확인할 수 있습니다.
""")


def 버전_출력():
    """버전 정보 출력"""
    try:
        from . import __version__
        버전 = __version__
    except ImportError:
        버전 = "알 수 없음"
    
    print(f"""
🇰🇷 KPTH (Korean Python) v{버전}
한국어 파이썬 문법 번역기

GitHub: https://github.com/yhg4908/kpth
라이센스: MIT License
""")


def 코드_실행(파일_경로: str, 디버그_모드: bool = False):
    """한국어 파이썬 코드 파일을 실행"""
    try:
        # 파일 읽기
        with open(파일_경로, "r", encoding="utf-8") as 파일:
            원본_코드 = 파일.read()
            
        if not 원본_코드.strip():
            print("⚠️  경고: 파일이 비어있습니다.")
            return

        # 코드 번역
        try:
            번역된_코드 = 코드_번역(원본_코드)
        except Exception as 번역오류:
            print(f"⚠️  번역 오류: {번역오류}")
            if 디버그_모드:
                print("\n🔍 디버그 정보:")
                traceback.print_exc()
            sys.exit(1)

        # 디버그 모드일 때 번역된 코드 출력
        if 디버그_모드:
            print("🔍 번역된 파이썬 코드:")
            print("-" * 50)
            for i, 줄 in enumerate(번역된_코드.splitlines(), 1):
                print(f"{i:3d} | {줄}")
            print("-" * 50)
            print()

        # 실행 환경 설정
        실행_글로벌 = {
            '__name__': '__main__',
            '__file__': 파일_경로,
            '__builtins__': __builtins__,
        }
        
        # 오류 정보 관리자 생성
        오류정보 = 실행오류정보(원본_코드, 번역된_코드)

        # 코드 실행
        try:
            exec(번역된_코드, 실행_글로벌)
            
        except SyntaxError as 문법오류:
            # 문법 오류는 특별 처리
            줄번호 = getattr(문법오류, 'lineno', None)
            print(오류정보.친화적_오류메시지(문법오류, 줄번호))
            
            if 디버그_모드:
                print("\n🔍 원본 파이썬 오류:")
                print(f"   {type(문법오류).__name__}: {문법오류}")
                if 줄번호:
                    print(f"   줄 번호: {줄번호}")
                    
        except Exception as 실행오류:
            # 런타임 오류 처리
            tb = traceback.extract_tb(실행오류.__traceback__)
            
            # 마지막 트레이스백에서 줄 번호 추출
            줄번호 = None
            for frame in reversed(tb):
                if frame.filename == '<string>':  # exec로 실행된 코드
                    줄번호 = frame.lineno
                    break
            
            print(오류정보.친화적_오류메시지(실행오류, 줄번호))
            
            if 디버그_모드:
                print("\n🔍 상세 오류 정보:")
                traceback.print_exc()

    except UnicodeDecodeError as 인코딩오류:
        print(f"⚠️  파일 인코딩 오류: {파일_경로}")
        print("   파일이 UTF-8로 인코딩되어 있는지 확인하세요.")
        if 디버그_모드:
            print(f"   상세 오류: {인코딩오류}")
            
    except PermissionError:
        print("⚠️  권한 오류: 파일을 읽을 권한이 없습니다.")
        print(f"   파일: {파일_경로}")
        
    except FileNotFoundError:
        # 이미 위에서 처리했지만, 만약의 경우
        print(f"⚠️  파일을 찾을 수 없습니다: {파일_경로}")
        
    except Exception as 예상치못한오류:
        print("⚠️  예상치 못한 오류가 발생했습니다.")
        print(f"   오류 타입: {type(예상치못한오류).__name__}")
        print(f"   오류 메시지: {예상치못한오류}")
        
        if 디버그_모드:
            print("\n🔍 전체 스택 트레이스:")
            traceback.print_exc()
        else:
            print("   더 자세한 정보를 보려면 --debug 옵션을 사용하세요.")


if __name__ == "__main__":
    주_실행()