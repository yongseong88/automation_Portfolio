"""회원가입 테스트 데이터.

현재 서버(`app.py`) 가 적용 중인 가입 규칙 기준의 유효/무효 값을 한 곳에 모은다.
- 아이디  : 영문/숫자/특수문자 4~10자 (한글·공백 불가)
- 비밀번호: 영문/숫자/특수문자 8~16자, 허용 특수문자 1개 이상 (한글·공백 불가)
- 비밀번호 확인: 비밀번호와 일치
- 이름    : 1~40자 (문자 제한 없음)
- 연락처  : 3자리-4자리-4자리 (숫자와 하이픈만, 예: 010-1234-5678)
- 이메일  : 아이디@도메인.최상위도메인(2자 이상), 공백 불가, 100자 이하
- 주소    : 1~200자 (문자 제한 없음)

아이디/이메일/연락처는 이미 사용 중이면 중복(409)으로 차단된다.
"""
import pytest

from utilities.File_read import Filereadutil
from utilities.logger import get_logger

logger = get_logger(__name__)

# 요구사항에 명시된 허용 특수문자 (app.py SPECIAL_CHARS 와 동일 집합)
ALLOWED_SPECIAL_CHARS = [
    "!", "@", "#", "$", "%", "^", "&", "*", "(", ")",
    "_", "+", "-", "=", "[", "]", "{", "}", ";", "'",
    ":", '"', "\\", "|", ",", ".", "<", ">", "/", "?", "~", "`",
]

# 앱에 미리 존재하는 데모 계정 (중복 가입 검증용 · app.py SEED_USERS 와 동일)
EXISTING_USER = {
    "username": "demo",
    "phone": "010-1111-2222",
    "email": "demo@marketfresh.com",
}


class Signupdata():
    def __init__(self):
    # def __init__(self, base_url: str):
        # self.base_url = base_url
        self.read_util = Filereadutil()
        self.account_cache = None  # account.json 을 한 번만 읽어 재사용
        self.ui_cache = None  # ui.json 을 한 번만 읽어 재사용


    # ── 파일 로딩 ────────────────────────────────────────────
    def get_account_data(self, key: str):
        """account.json 의 특정 키를 읽는다. 없으면 즉시 실패시킨다."""
        try:
            if self.account_cache is None:
                path = self.read_util.read_filepath("config", "account.json")
                self.account_cache = self.read_util.read_file(path)

            value = self.account_cache.get(key)
            if not value:
                raise KeyError(f"account.json 에 '{key}' 데이터가 없습니다.")

            return value

        except Exception:
            # 경로 계산 실패, 권한 문제, 키 누락 등
            logger.exception("회원가입 계정 데이터 읽기 실패: config/account.json (key=%s)", key)
            raise

    def get_ui_data(self, screen: str) -> dict:
        """ui.json 에서 특정 화면의 문구 묶음을 읽는다."""
        try:
            if self.ui_cache is None:
                path = self.read_util.read_filepath("config", "ui.json")
                self.ui_cache = self.read_util.read_file(path)

            value = self.ui_cache.get(screen)
            if not value:
                raise KeyError(f"ui.json 에 '{screen}' 데이터가 없습니다.")

            return value

        except Exception:
            logger.exception("회원가입 문구 데이터 읽기 실패: config/ui.json (screen=%s)", screen)
            raise

    def valid_account(self) -> dict:
        """
            모든 규칙을 만족하는 기본 가입 정보.
            conftest 의 reset 픽스처가 매 테스트마다 회원을 초기화하므로
            같은 아이디를 계속 써도 중복 충돌이 나지 않는다.
            (아이디/이메일/연락처 모두 시드 계정과 겹치지 않는 값이어야 한다)
        """
        try:
            return self.get_account_data("valid_user")

        except Exception:
            # 경로 계산 실패, 권한 문제 등 예상 못 한 읽기 오류
            logger.exception("valid_user 데이터 파일 읽기 실패: config/account.json")
            raise

    def existing_account(self) -> dict:
        """이미 가입된 계정 (중복 검증용)."""

        try:
            return self.get_account_data("existing_user")

        except Exception:
            # 경로 계산 실패, 권한 문제 등 예상 못 한 읽기 오류
            logger.exception("existing_user 데이터 파일 읽기 실패: config/account.json")
            raise

    def allowed_special_chars(self) -> list:
        """아이디/비밀번호에 허용되는 특수문자 목록."""
        try:
            return self.get_account_data("allowed_special_chars")

        except Exception:
            # 경로 계산 실패, 권한 문제 등 예상 못 한 읽기 오류
            logger.exception("existing_user 데이터 파일 읽기 실패: config/account.json")
            raise


    # ── 화면 데이터 ──────────────────────────────────────────
    def field_data(self) -> list:
        try:
            """회원가입 폼의 입력 필드 목록."""
            return list(self.valid_account().keys())

        except Exception:
            # 경로 계산 실패, 권한 문제 등 예상 못 한 읽기 오류
            logger.exception("field_data 데이터 파일 읽기 실패")
            raise

    def msg_value(self) -> dict:
        """화면에 노출되는 회원가입 관련 문구."""
        return self.get_ui_data("signup")

    def account_with(self, **overrides) -> dict:
        """
            기본 가입 정보에서 일부 필드만 바꾼 사본을 만든다.

            한 필드만 무효값으로 두고 나머지는 유효하게 유지할 때 사용한다
            (형식 위반·중복 검증 시나리오).

            password 만 바꾸면 password_confirm 도 같이 맞춰준다.
            확인값 불일치를 만들려면 password_confirm 을 직접 지정한다.
        """
        account = dict(self.valid_account())  # 복사본 (캐시된 원본 보호)

        if "password" in overrides and "password_confirm" not in overrides:
            overrides["password_confirm"] = overrides["password"]

        account.update(overrides)

        return account


        # return {
        #     "username": "qauser01",                     # 8자, 영문+숫자
        #     "password": "Passw0rd!",                    # 9자, 영문+숫자+특수문자
        #     "password_confirm": "Passw0rd!",
        #     "name": "박테스터",
        #     "phone": "010-1234-5678",                   # 3-4-4 하이픈 형식
        #     "email": "qauser01@test.com",
        #     "address": "서울시 강남구 테헤란로 1",
        # }

