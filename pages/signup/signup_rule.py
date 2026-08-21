"""입력값 규칙 검증 (UI 무관, 페이지 무관 공통 함수)."""
import re



class Signuprule():
    # ── 패턴 ─────────────────────────────────────────────────────
    # 어떤 화면에서도 걸러져야 하는 문자: 완성형 한글 + 자모 단독 + 공백류
    DISALLOWED_PATTERN = r"[ㄱ-ㅎㅏ-ㅣ가-힣\s]"

    # 이메일: 아이디@도메인.최상위도메인
    EMAIL_PATTERN = r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"

    # 연락처: 3자리-4자리-4자리
    PHONE_PATTERN = r"^\d{3}-\d{4}-\d{4}$"

    # ── 정책 상수 ────────────────────────────────────────────────
    USERNAME_MIN, USERNAME_MAX = 4, 10  # 아이디 길이
    PASSWORD_MIN, PASSWORD_MAX = 8, 16  # 비밀번호 길이

    # ── 문자 필터 ────────────────────────────────────────────────
    def remove_disallowed(self, text: str) -> str:
        """차단 문자를 제거한 결과 (필드에 남아야 할 값)."""
        disallow_pattern = bool(re.search(self.DISALLOWED_PATTERN, text))
        if disallow_pattern:
            return re.sub(self.DISALLOWED_PATTERN, "", text)















    # def is_valid_username(self, text: str) -> bool:
    #     """아이디: 4~10자, 영문·숫자·특수문자만 (공백·한글 불가)."""
    #     return (
    #             self.USERNAME_MIN <= len(text) <= self.USERNAME_MAX
    #             and not bool(re.search(self.DISALLOWED_PATTERN, text))
    #     )









    # def has_disallowed(self, text: str) -> bool:
    #     """한글·공백 등 입력이 차단되어야 할 문자가 포함되어 있는지."""
    #     return bool(re.search(self.DISALLOWED_PATTERN, text))


    # # ── 형식 검증 ────────────────────────────────────────────────
    # def is_valid_email(text: str) -> bool:
    #     """이메일 형식이 올바른지 (@ 와 도메인 뒤 마침표 필수)."""
    #     return bool(re.fullmatch(EMAIL_PATTERN, text))
    #
    #
    # def is_valid_phone(text: str) -> bool:
    #     """연락처가 3-4-4 하이픈 형식인지."""
    #     return bool(re.fullmatch(PHONE_PATTERN, text))
    #
    #
    # def format_phone(text: str) -> str:
    #     """숫자만 남겨 3-4-4 하이픈 형식으로 변환 (11자리 초과분은 버림).
    #
    #     화면의 자동 하이픈 입력이 기대대로 동작하는지 비교할 때 사용한다.
    #     """
    #     digits = re.sub(r"\D", "", text)[:11]
    #     if len(digits) <= 3:
    #         return digits
    #     if len(digits) <= 7:
    #         return f"{digits[:3]}-{digits[3:]}"
    #     return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
