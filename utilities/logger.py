"""프로젝트 공통 로거.

페이지 객체 / 유틸 / 테스트 어디서든 같은 포맷·같은 파일로 로그를 남기기 위한 단일 진입점.
파일별로 logging.basicConfig 를 호출하면 핸들러가 중복되어 로그가 두 번씩 찍히므로,
핸들러 등록은 이 모듈에서 딱 한 번만 수행한다.

사용법:
    from utilities.logger import get_logger

    logger = get_logger(__name__)
    logger.info("특가 상품 클릭: id=%s", product_id)
    logger.exception("클릭 실패: %s", locator)   # except 블록 → 스택트레이스까지 기록

출력 위치:
    - 콘솔(stderr): pytest 의 -s / Captured log 에 그대로 노출
    - 파일: logs/ui_automation.log (5MB x 3개 로테이션, .gitignore 처리됨)

로그 레벨은 환경변수로 조절한다 (기본 INFO).
    LOG_LEVEL=DEBUG pytest tests/web/test_home.py
"""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from utilities.File_read import Filereadutil

# 프로젝트 로그의 최상위 이름. 모든 로거가 이 아래에 붙는다.
# → 서드파티(playwright/httpx 등) 로그와 섞이지 않고, 핸들러도 여기에만 달린다.
BASE_LOGGER_NAME = "ui_automation"
LOG_DIR_NAME = "logs"
LOG_FILE_NAME = "ui_automation.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_BYTES = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 3


def log_level() -> int:
    """환경변수 LOG_LEVEL 을 읽어 로그 레벨을 결정 (잘못된 값이면 INFO)."""
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_name, logging.INFO)


def log_file_path() -> str:
    """logs/ui_automation.log 절대경로. 폴더가 없으면 만든다."""
    files = Filereadutil()
    log_dir = files.read_filepath(LOG_DIR_NAME, "")
    os.makedirs(log_dir, exist_ok=True)

    return files.read_filepath(LOG_DIR_NAME, LOG_FILE_NAME)


def setup_logger() -> logging.Logger:
    """공통 로거에 콘솔/파일 핸들러를 1회만 등록하고 반환."""
    base_logger = logging.getLogger(BASE_LOGGER_NAME)
    base_logger.setLevel(log_level())

    if base_logger.handlers:  # 이미 설정됨 → 중복 등록 방지
        return base_logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    base_logger.addHandler(console_handler)

    try:
        file_handler = RotatingFileHandler(
            log_file_path(), maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        base_logger.addHandler(file_handler)

    except OSError:
        # 로그 파일을 못 만들어도(권한/경로 문제) 테스트 자체는 계속 진행해야 한다.
        base_logger.warning("로그 파일 생성 실패 → 콘솔 로그만 사용합니다.", exc_info=True)

    return base_logger


def get_logger(name: str | None = None) -> logging.Logger:
    """모듈 전용 로거 반환. 각 파일 최상단에서 `get_logger(__name__)` 로 사용한다."""
    setup_logger()

    if not name or name == BASE_LOGGER_NAME:
        return logging.getLogger(BASE_LOGGER_NAME)

    return logging.getLogger(f"{BASE_LOGGER_NAME}.{name}")
