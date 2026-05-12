# LLM Judgement Parallel Task Plan

## Goal

LLM을 단독 매매 결정자가 아니라 기존 룰 기반 전략의 후보 신호를 검수하는 판정 레이어로 추가한다.
초기 구현은 실제 LLM provider 호출을 붙이지 않고, 인터페이스와 mock client를 통해 request/response
계약과 안전 게이트를 먼저 검증한다.

## Operating Principles

- 수치 계산, 포지션 크기, 주문 실행은 기존 코드와 리스크 게이트가 담당한다.
- LLM은 후보 신호의 맥락 검수, 시장 국면 힌트, 리스크 플래그, 판단 근거 생성만 담당한다.
- LLM 응답 실패, schema 불일치, 낮은 confidence, 높은 risk는 모두 거래 금지 방향으로 처리한다.
- 초기 rollout은 backtest/sandbox/shadow mode 기준으로 제한한다.
- prompt, request, response, fallback 여부는 trace로 남겨 replay와 감사가 가능해야 한다.

## Parallel Work Streams

### A. Judgement Contract

Owner: domain/contract 작업자

Scope:

- LLM 판정 request DTO 정의
- LLM 판정 response DTO 정의
- decision, market regime, risk level, risk flag enum 정의
- request/response가 JSON schema로 안정적으로 직렬화될 수 있는지 확인

Expected outputs:

- `LlmJudgementRequest`
- `LlmJudgementResponse`
- `LlmJudgementDecision`
- `LlmMarketRegime`
- `LlmRiskLevel`
- `LlmRiskFlag`

Completion criteria:

- request에는 strategy 후보 신호, instrument, timestamp, market snapshot, selected features,
  current position state, rule rationale가 포함된다.
- response에는 최종 판정, confidence, market regime, risk level, risk flags, reasons,
  invalidation condition이 포함된다.
- provider별 필드는 domain model에 들어가지 않는다.

### B. LLM Port And Mock Client

Owner: adapter/interface 작업자

Scope:

- 실제 AI 호출부를 port/protocol 뒤로 숨긴다.
- mock client를 만들어 deterministic 테스트가 가능하게 한다.
- 응답 파싱 실패와 provider 실패 fallback을 정의한다.

Expected outputs:

- `LlmJudgementPort`
- `MockLlmJudgementClient`
- safe fallback response

Completion criteria:

- 실제 provider SDK 없이도 전략 평가가 실행된다.
- mock은 승인, 거절, 낮은 confidence, 높은 risk, malformed response 시나리오를 재현할 수 있다.
- 실패 fallback은 신규 진입을 승인하지 않는다.

### C. Strategy Integration

Owner: strategy/runtime 작업자

Scope:

- 기존 룰 기반 전략이 만든 후보 신호를 LLM judgement request로 변환한다.
- LLM response를 최종 signal에 반영한다.
- veto 정책을 코드로 강제한다.

Initial veto rules:

```text
candidate == HOLD -> LLM 호출 생략 가능
LLM decision == NO_TRADE -> HOLD
confidence < min_confidence -> HOLD
risk_level == high -> HOLD
risk_flags contains stale_data -> HOLD
candidate action과 LLM decision이 충돌 -> HOLD
response parse/schema 실패 -> HOLD
```

Expected outputs:

- LLM veto wrapper 또는 decision engine implementation
- threshold parameter
- trace에 candidate, request summary, response summary, veto reason 기록

Completion criteria:

- LLM이 단독으로 BUY/SELL을 생성하지 않는다.
- BUY/SELL 후보가 없으면 신규 주문 방향으로 승격되지 않는다.
- 기존 execution sizing과 guarded-live safety path를 우회하지 않는다.

### D. Tests

Owner: test 작업자

Scope:

- contract 직렬화 테스트
- mock client 테스트
- 승인/거절/veto/fallback 전략 테스트
- trace 보존 테스트

Minimum test cases:

- 후보 BUY + LLM 승인 -> BUY 유지
- 후보 BUY + LLM `NO_TRADE` -> HOLD
- 후보 BUY + confidence threshold 미달 -> HOLD
- 후보 BUY + `risk_level=high` -> HOLD
- 후보 BUY + `stale_data` flag -> HOLD
- 후보 BUY + malformed response/fallback -> HOLD
- 후보 HOLD -> 신규 BUY/SELL로 승격되지 않음
- trace에 request/response/fallback/veto reason이 남음

Completion criteria:

- provider SDK나 네트워크 없이 전체 테스트가 통과한다.
- 실패 케이스가 모두 safe behavior를 검증한다.

### E. Documentation And Rollout Guardrails

Owner: docs/operator 작업자

Scope:

- LLM judgement lane의 책임 경계 문서화
- shadow mode rollout 절차 문서화
- live promotion 금지 조건과 향후 승격 조건 문서화

Expected outputs:

- architecture 또는 roadmap 문서 업데이트
- operator runbook 항목 초안
- prompt/response trace retention 기준

Completion criteria:

- LLM이 단독 매매 결정자가 아니라는 원칙이 문서에 남는다.
- 실제 provider 연결 전 필요한 검증 항목이 명확하다.
- unattended live trading에는 사용하지 않는다는 제한이 명확하다.

## Dependency Map

```text
A. Judgement Contract
  -> B. LLM Port And Mock Client
  -> C. Strategy Integration
  -> D. Tests

E. Documentation And Rollout Guardrails
  can run in parallel after A draft is stable
```

The main blocking path is A -> B -> C. Tests can begin as soon as A and B expose stable names.
Documentation can proceed in parallel but should be reconciled after C finalizes trace fields.

## Suggested Implementation Order

1. Define request/response models and enums.
2. Add port and mock implementation.
3. Add a veto wrapper around an existing candidate-producing strategy or decision engine.
4. Add deterministic tests for approved, vetoed, and fallback paths.
5. Update rollout documentation with shadow-mode and live-promotion restrictions.

## Non-Goals

- Direct provider integration.
- Prompt optimization.
- Autonomous signal generation from LLM alone.
- Unattended live trading.
- Replacing deterministic sizing, stop, or order execution logic.
