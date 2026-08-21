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


def invalid_format_cases(field: str) -> list:
    """형식 위반 케이스 (입력은 되지만 제출 시 에러가 노출되어야 하는 값)."""
    cases = signup_data.get_account_data("invalid_format").get(field)
    if not cases:
        raise KeyError(f"account.json 의 invalid_format 에 '{field}' 가 없습니다.")
    return [pytest.param(typed, id=case_id) for case_id, typed in cases.items()]