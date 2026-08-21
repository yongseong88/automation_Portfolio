"""
    회원가입 parametrize 케이스.
    parametrize 는 테스트 수집 시점에 평가되므로 인스턴스 메서드를 쓸 수 없다.
    이 모듈은 수집 시점에 호출되는 케이스 생성 함수만 모아둔다.
"""
import pytest
from pages.signup.signup_data import Signupdata




signup_data = Signupdata()          # 파일 읽기 전용 (캐시 공유)



def filter_cases(field: str) -> list:
    """입력 차단 케이스 (한글·공백 등 필드에 남지 않아야 하는 값)."""
    cases = signup_data.get_account_data("filter_cases").get(field)
    if not cases:
        raise KeyError(f"account.json 의 filter_cases 에 '{field}' 가 없습니다.")
    return [pytest.param(input_value, id=case_id) for case_id, input_value in cases.items()]


def allowed_special_chars() -> list:
    """아이디/비밀번호에 허용되는 특수문자 케이스 (문자별로 하나씩)."""
    chars = signup_data.allowed_special_chars()
    if not chars:
        raise KeyError("account.json 에 'allowed_special_chars' 데이터가 없습니다.")
    # 실패한 문자를 리포트에서 바로 알 수 있게 인덱스와 문자를 함께 id 로 쓴다
    return [pytest.param(char, id=f"special_{index}_{char}") for index, char in enumerate(chars)]


def invalid_format_cases(field: str) -> list:
    """형식 위반 케이스 (입력은 되지만 제출 시 에러가 노출되어야 하는 값)."""
    cases = signup_data.get_account_data("invalid_format").get(field)
    if not cases:
        raise KeyError(f"account.json 의 invalid_format 에 '{field}' 가 없습니다.")
    return [pytest.param(typed, id=case_id) for case_id, typed in cases.items()]