# 지침서: 테스트 코드 생성 가이드 (CREATE_CODE.md)

## 🏗️ 1. 디자인 패턴 및 아키텍처
- **POM(Page Object Model) 필수**: UI 테스트(Web/App)는 스크립트와 요소를 분리합니다.
  - Web 페이지 객체: `tests/web/pages/`
  - App 페이지 객체: `tests/app/pages/`
- **Fixture 기법 적용**: setup/teardown 로직은 개별 테스트 파일에 넣지 말고 `conftest.py`에 구현하여 주입받으세요.

## 🛠️ 2. 컴포넌트별 작성 규칙
### [Web UI - Playwright]
- 반드시 동기식 API(`from playwright.sync_api import Page`)를 사용하세요.
- Locator는 `page.get_by_test_id()`, `page.get_by_role()`을 최우선으로 사용하세요. (XPath 절대 자제)
- 하드코딩된 대기(`time.sleep()`)는 금지하며, Playwright의 자동 대기 기능을 신뢰하세요.

### [App UI - Appium]
- 모바일 환경은 `Accessibility ID`를 최우선 선택자로 지정하세요.
- 세션 릭(Leak) 방지를 위해 테스트 종료 시 반드시 `driver.quit()`이 호출되도록 fixture 구조를 잡으세요.

### [API - Requests]
- 세션 재사용을 위해 `requests.Session()` 객체를 fixture로 만들어 활용하세요.
- 응답 검증 시 상태 코드(`status_code == 200`)와 응답 바디의 필수 JSON 스키마 구조 검증을 동시에 작성하세요.

## 📝 3. 코드 출력 포맷
- 코드 생략(`// 기존 코드 동일` 등)을 하지 말고 **완전한 전체 소스 코드**를 제공하세요.
- 메서드나 함수 상단에는 이 테스트가 무엇을 검증하는지 한 줄 주석(Docstring)을 필수 기재하세요.
