"""로그인 페이지 ('/login')."""


from __future__ import annotations

import re
from playwright.sync_api import Page, Locator
from locators import LoginLocators
from pages.base_page import BasePage
from pages.login.login_page import LoginPage
from utilities.File_read import Filereadutil
from utilities.logger import get_logger

logger = get_logger(__name__)


class LoginAction(BasePage):
    # login_valid_check 의 분기 판별용 센티널.
    # 사용자명 대신 이 값을 넘기면 '로그인 실패' / '비로그인' 상태를 검증한다.
    LOGIN_FAILED = "아이디 또는 비밀번호가 올바르지 않습니다."
    GUEST = "로그인"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.login_page = LoginPage(self.page, base_url)
        self.File_read_util = Filereadutil()
        self.ll = LoginLocators()


    def msg_value(self):
        ui_json_path = self.File_read_util.read_filepath("config/", "ui.json")
        ui_data = self.File_read_util.read_file(ui_json_path)

        login_invalid_msg = ui_data.get('login', {}).get('error_invalid', "")
        login_btn_msg = ui_data.get('home', {}).get('login_btn', "")

        return {
            "header_login_btn" : login_btn_msg,
            "invalid_login_msg" : login_invalid_msg

        }


    def login_valid_check(self, value) -> bool:
        """로그인 성공 여부 검증 (홈으로 이동 + 헤더에 '{사용자}님' 노출)."""
        # check_url()/check_text() 는 bool 을 돌려주므로 assert 로 실패시키고,
        # 어느 조건이 깨졌는지는 except 에서 로그로 남긴다 (URL 문제 / 헤더 문제 구분)

        try:
            msg = self.msg_value()
            login_btn_msg = msg.get("header_login_btn", "")
            login_invalid_msg = msg.get("invalid_login_msg", "")

            if value == login_invalid_msg:
                assert self.check_url(re.compile(r"/login")), f"로그인 실패 후 로그인 페이지가 유지되지 않음: 현재={self.page.url}/"
                assert self.login_page.error_message(value), f"로그인 실패 에러 메시지 불일치: 기대='{login_invalid_msg}', locator={self.ll.error}"
                # assert self.check_text(self.login_page.error_message(), login_btn_txt), f"로그인 실패 에러 메시지 불일치: 기대='{self.LOGIN_FAILED}', locator={self.ll.error}"

            elif value == login_btn_msg:
                assert self.check_url(f"{self.base_url}/"), f"로그아웃 실패: 기대={self.base_url}/, 현재={self.page.url}"
                assert self.login_page.login_link(value), f"헤더 내 로그인 미노출: 기대='{login_btn_msg}', locator={self.ll.login_link}"
                # assert self.check_text(self.login_page.login_link(), login_link_txt), f"헤더 내 로그인 미노출: 기대='{self.GUEST}', locator={self.login_page.login_link()}"
                logger.info("로그아웃 완료")

            else:
                login_user = value + "님"
                assert self.check_url(f"{self.base_url}/"), f"로그인 후 홈 이동 실패: 기대={self.base_url}/, 현재={self.page.url}"
                assert self.login_page.auth_user(login_user), f"헤더 사용자명 불일치: 기대='{value}님', locator={self.ll.auth_user}"
                # assert self.check_text(self.login_page.auth_user(), login_id_txt), f"헤더 사용자명 불일치: 기대='{value}님', locator={self.ll.auth_user}"
                logger.info("로그인 완료: username=%s", value)

            return True

        except AssertionError:
            logger.exception("상태 검증 실패: username=%s", value)
            return False

        except Exception:
            # 요소 조회/페이지 접근 자체가 실패한 경우는 검증 결과로 볼 수 없으므로 재던짐
            logger.exception("로그인 상태 검증 중 오류: username=%s, url=%s", value, self.page.url)
            raise