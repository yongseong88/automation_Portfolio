# 지침서: 테스트 실행 및 옵션 가이드 (RUN_TEST.md)

## 🚀 1. 플랫폼 및 마커 조건별 통합 실행 규칙
클로드는 사용자의 실행 요청 문장을 분석하여 **[대상 플랫폼]**, **[테스트 마커(태그)]**, **[필수 실행 옵션]**을 자동 조합해 명령어를 실행해야 합니다.

### 📌 필수 자동화 옵션 매핑 규칙
사용자의 요청 문장에서 아래 키워드가 감지되면, 테스트 실행 전 반드시 해당 프로젝트 폴더로 이동(`cd`) 명령을 먼저 수행해야 합니다.
- **[web] 또는 [웹]** 키워드 포함 시 ➡️ `cd projects/ui_automation`으로 이동
- **[app] 또는 [앱]** 키워드 포함 시 ➡️ `cd projects/ui_automation`으로 이동
- **[api]** 키워드 포함 시 ➡️ `cd projects/api_automation`으로 이동
사용자가 **Regression, Smoke, Sanity** 키워드를 포함하여 요청하면, 명령어 뒤에 다음 옵션을 **무조건 자석처럼 함께 붙여서** 조합하세요.
- 기본 마커 지정: `-m [키워드]` (소문자로 변환: `regression`, `smoke`, `sanity`)
- 실시간 및 상세 로그: `-v -s`
- 상세 결과 보고 출력: `-rA`
- 웹 UI 브라우저 오픈 노출 (Web 한정): `--headed`
- 동작 속도 제어 인터벌 (Web 한정): `--slowmo 3000` (3초 대기)

---

## 💻 2. 요청 유형별 명령어 조합
테스트 실행 전 반드시 해당 프로젝트 폴더로 이동(`cd`)하는 로직을 결합하세요.

### ① "웹 Regression Test 실행 해줘"
- **적용 규칙**: 웹 폴더 진입 + regression 마커 + 웹 전용 옵션 풀세트 적용
- **실행 명령어**: 
  `cd projects/ui_automation && pytest -m regression --headed -rA -v -s --slowmo 3000`

### ② "웹 Smoke Test 실행 해줘"
- **적용 규칙**: 웹 폴더 진입 + smoke 마커 + 웹 전용 옵션 풀세트 적용
- **실행 명령어**: 
  `cd projects/ui_automation && pytest -m smoke --headed -rA -v -s --slowmo 3000`

### ③ "api Regression Test 실행 해줘"
- **적용 규칙**: API 폴더 진입 + regression 마커 + API 공통 옵션 적용 (※ API는 `--headed` 및 `--slowmo` 제외)
- **실행 명령어**: 
  `cd projects/api_automation && pytest -m regression -rA -v -s`

### ④ "앱 Sanity Test 실행 해줘"
- **적용 규칙**: 앱 폴더 진입 + sanity 마커 + 앱 공통 옵션 적용 (※ 앱은 `--headed` 및 `--slowmo` 제외)
- **실행 명령어**: 
  `cd projects/ui_automation && pytest tests/app/ -m sanity -rA -v -s`

---

## 🔄 3. 테스트 실패(FAILED) 발생 시 자동 대응 규칙
테스트 수행 중 단 하나의 테스트 케이스라도 **FAILED(실패)** 결과가 발생하면, 클로드는 즉시 인지하고 다음 단계를 안내하거나 실행해야 합니다.

1. **실패한 테스트만 타겟팅 재실행**: 사용자가 재시도를 원할 경우 `--lf` (Last Failed) 옵션을 붙여서 실패한 항목만 빠르게 다시 돌립니다.
   - 웹 재실행 예시: `cd projects/ui_automation && pytest --lf --headed -rA -v -s --slowmo 3000`
   - API 재실행 예시: `cd projects/api_automation && pytest --lf -rA -v -s`
2. **디버깅 가이드 연동**: 재실행 후에도 지속적으로 실패할 경우, 사용자의 추가 명령 없이도 `@DEBUG_CODE.md` 문서를 호출하여 에러 원인 분석 단계로 전환하세요.
