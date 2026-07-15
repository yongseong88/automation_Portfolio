import subprocess
import sys
import time
import httpx
import pytest
from pathlib import Path
from playwright.sync_api import expect
from utilities.File_read import Filereadutil

"""
하네스 핵심 픽스처. (conftest.py 는 프로젝트 루트 = app.py 와 같은 폴더에 위치)

- live_server: uvicorn 을 자동 기동/종료 (수동 실행 불필요)
- base_url:    page.goto("/") 가 붙을 기준 URL (session 스코프)
- api:         Playwright APIRequestContext (API 자동화용)
- reset:      각 테스트 시작 전 상태를 시드로 초기화 (테스트 격리)
"""

# HOST = "127.0.0.1"
# PORT = 8000
# BASE_URL = f"http://{HOST}:{PORT}"
BASE_URL = "http://127.0.0.1:8000"

# 경로 계산은 utilities 공통 유틸로 위임 (프로젝트 루트 기준 절대경로)
files = Filereadutil()
ROOT = Path(files.read_filepath("", ""))
LOG_PATH = Path(files.read_filepath("", "uvicorn_test.log"))


def server_up() -> bool:
    try:
        return httpx.get(f"{BASE_URL}/api/health", timeout=0.5).status_code == 200

    except httpx.HTTPError:
        return False


@pytest.fixture(scope="session")
def live_server():
    # 이미 떠 있는 서버가 있으면 그대로 재사용 → 포트 충돌 방지
    if server_up():
        yield BASE_URL
        return

    log = open(LOG_PATH, "w")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(8000)],
        cwd=ROOT,
        stdout=log,
        stderr=subprocess.STDOUT,
    )

    deadline = time.time() + 15
    while time.time() < deadline:
        if proc.poll() is not None:  # 프로세스가 바로 죽으면 더 기다리지 않음
            break
        if server_up():
            break
        time.sleep(0.3)

    if not server_up():
        proc.terminate()
        log.flush()
        log.close()
        detail = LOG_PATH.read_text()[-2000:] if LOG_PATH.exists() else "(로그 없음)"
        raise RuntimeError(
            f"서버 기동 실패 (ROOT={ROOT}).\n--- uvicorn log ---\n{detail}"
        )

    yield BASE_URL
    proc.terminate()
    proc.wait(timeout=5)
    log.close()


@pytest.fixture(scope="session")
def base_url(live_server):
    return live_server


@pytest.fixture(autouse=True)
def reset(live_server):
    # 각 테스트 전에 상태 초기화 → 순서/병렬에 안전
    httpx.post(f"{live_server}/api/reset", timeout=2)


@pytest.fixture
def api(playwright, live_server):
    ctx = playwright.request.new_context(base_url=live_server)
    yield ctx
    ctx.dispose()


@pytest.fixture(autouse=True)
def inject_class_fixtures(request):
    """
        클래스 기반 테스트에 self.page / self.api / self.base_url 을 주입.
        - 클래스 테스트일 때만 page/api 를 끌어오므로(getfixturevalue),
        함수형/순수 API 테스트는 불필요하게 브라우저를 띄우지 않는다.
    """
    if request.cls is not None:
        request.cls.page = request.getfixturevalue("page")
        request.cls.api = request.getfixturevalue("api")
        request.cls.base_url = request.getfixturevalue("base_url")

    yield

@pytest.fixture(autouse=True)
def auto_start_at_home(request):
    """@pytest.mark.ui_journey 를 붙인 클래스만 자동으로 홈에 진입시킨다.

    - UI 여정 테스트: 인자 없이도 홈에서 시작 (Selenium 의 driver.get 처럼).
    - API/그 외 테스트: 마커가 없으므로 홈 진입도, 브라우저도 뜨지 않는다.
    - 스피너가 사라지는 순간의 레이스를 피하려고 '상품 카드가 보일 때까지' 대기.
    """
    if request.node.get_closest_marker("ui_journey"):
        page = request.getfixturevalue("page")
        base_url = request.getfixturevalue("base_url")
        page.goto(base_url)  # 홈으로 진입 (= driver.get)

    yield


# 페이지 객체는 픽스처로 리턴하지 않는다.
# 테스트에서 `HomePage(page, base_url)` 처럼 직접 생성하고,
# 페이지 객체가 base_url 기준으로 직접 이동(open)한다.