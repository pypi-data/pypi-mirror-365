import tokenize
import io
import re
from typing import Dict, List, Tuple, Set
from .예약어 import 한국어_파이썬_예약어

class 한국어번역기:
    def __init__(self):
        # 번역 맵을 키워드와 식별자로 분리
        self.키워드_맵: Dict[str, str] = {}
        self.식별자_맵: Dict[str, str] = {}  # 함수명, 내장함수 등
        
        # 파이썬 키워드 셋 (변수명으로 사용 불가)
        self.파이썬_키워드: Set[str] = {
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'try', 'while', 'with', 'yield', 'match', 'case'
        }
        
        self._분류_번역맵()
        self._컴파일_패턴()
    
    def _분류_번역맵(self):
        for 한국어, 파이썬 in 한국어_파이썬_예약어.items():
            if 파이썬 in self.파이썬_키워드:
                self.키워드_맵[한국어] = 파이썬
            else:
                self.식별자_맵[한국어] = 파이썬
    
    def _컴파일_패턴(self):
        self.키워드_패턴들: List[Tuple[re.Pattern, str]] = []
        self.식별자_패턴들: List[Tuple[re.Pattern, str]] = []
        
        for 한국어, 파이썬 in self.키워드_맵.items():
            패턴 = re.compile(r'\b' + re.escape(한국어) + r'\b')
            self.키워드_패턴들.append((패턴, 파이썬))
        
        for 한국어, 파이썬 in self.식별자_맵.items():
            패턴 = re.compile(r'\b' + re.escape(한국어) + r'\b')
            self.식별자_패턴들.append((패턴, 파이썬))

    def 코드_번역(self, 코드: str) -> str:
        try:
            return self._토큰_기반_번역(코드)
        except tokenize.TokenError as e:
            # 토큰화 실패 시 구버전 방식으로 폴백
            print(f"⚠️  토큰화 실패, 구버전 번역 방식 사용: {e}")
            return self._기본_번역(코드)
    
    def _토큰_기반_번역(self, 코드: str) -> str:
        결과_토큰들 = []
        
        # 코드를 바이트 스트림으로 변환
        코드_바이트 = io.BytesIO(코드.encode('utf-8'))
        
        try:
            토큰들 = tokenize.tokenize(코드_바이트.readline)
            
            for 토큰 in 토큰들:
                번역된_토큰 = self._토큰_번역(토큰)
                결과_토큰들.append(번역된_토큰)
                
        except tokenize.TokenError:
            return self._기본_번역(코드)
        
        return tokenize.untokenize(결과_토큰들).decode('utf-8')
    
    def _토큰_번역(self, 토큰: tokenize.TokenInfo) -> tokenize.TokenInfo:
        토큰_타입 = 토큰.type
        토큰_문자열 = 토큰.string
        
        # 문자열, 주석, 숫자는 번역하지 않음
        if 토큰_타입 in (tokenize.STRING, tokenize.COMMENT, tokenize.NUMBER):
            return 토큰
        
        # NAME 토큰만 번역 대상 (식별자, 키워드)
        if 토큰_타입 == tokenize.NAME:
            번역된_문자열 = self._이름_번역(토큰_문자열)
            if 번역된_문자열 != 토큰_문자열:
                return 토큰._replace(string=번역된_문자열)
        
        return 토큰
    
    def _이름_번역(self, 이름: str) -> str:
        """NAME 토큰(식별자)을 번역"""
        # 키워드 확인
        if 이름 in self.키워드_맵:
            return self.키워드_맵[이름]
        
        # 식별자(함수명 등) 확인
        if 이름 in self.식별자_맵:
            return self.식별자_맵[이름]
        
        return 이름
    
    def _기본_번역(self, 코드: str) -> str:
        줄들 = 코드.splitlines()
        번역된_줄들 = []
        
        for 줄 in 줄들:
            새_줄 = 줄
            
            # 키워드 번역
            for 패턴, 교체 in self.키워드_패턴들:
                새_줄 = 패턴.sub(교체, 새_줄)
            
            # 식별자 번역
            for 패턴, 교체 in self.식별자_패턴들:
                새_줄 = 패턴.sub(교체, 새_줄)
            
            번역된_줄들.append(새_줄)
        
        return "\n".join(번역된_줄들)


_번역기_인스턴스 = None

def 코드_번역(코드: str) -> str:
    global _번역기_인스턴스
    if _번역기_인스턴스 is None:
        _번역기_인스턴스 = 한국어번역기()
    
    return _번역기_인스턴스.코드_번역(코드)