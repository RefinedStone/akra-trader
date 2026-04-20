# Blueprint

`akra-trader`의 중장기 청사진 문서군입니다.

이 문서군은 구현 현황 문서가 아니라 앞으로 6-9개월 동안 무엇을 어떤 순서와 기준으로
완성할지 정의하는 프로그램 문서입니다.

현재 구현 상태는 반드시 [Current State](../status/current-state.md)를 먼저 확인합니다.

## 기본 프레임

- 기간: 6-9개월
- 전략: research-first
- 운영 모델: single operator
- 시장 방향: crypto 운영 우선, stocks 확장 가능 구조 유지
- 문서 역할: 한국어 기획 청사진

## 이 문서군이 답하는 질문

- 이 플랫폼은 다음 단계에서 어떤 상태여야 하는가
- 무엇을 먼저 만들고 무엇을 의도적으로 미루는가
- 연구, sandbox, guarded-live, LLM 레인을 어떤 규칙으로 연결할 것인가
- 어떤 지표와 gate를 통과해야 다음 단계로 넘어가는가

## 읽는 순서

1. [North Star](north-star.md)
2. [Product Program](product-program.md)
3. [Platform Program](platform-program.md)
4. [Operating Model](operating-model.md)
5. [Metrics and Gates](metrics-and-gates.md)
6. [LLM Lane](llm-lane.md)
7. [Risk Register](risk-register.md)
8. [Backlog Map](backlog-map.md)

## 현재 문서 체계에서의 역할

- [Current State](../status/current-state.md)
  - 지금 실제로 구현된 상태의 기준 문서
- [Roadmap](../roadmap/README.md)
  - 현재 기준에서 남은 작업과 가까운 실행 순서를 다루는 문서
- `docs/blueprint/*`
  - 중장기 의도, 운영 원칙, gate, risk, 비범위를 다루는 문서

즉, blueprint는 구현 완료 여부를 판정하는 문서가 아니라 "어떤 완성 상태를 향해 갈지"를
고정하는 문서입니다.

## 청사진의 핵심 원칙

- 먼저 연구 신뢰도와 실험 운영체계를 완성한다.
- preview, worker, guarded-live를 같은 것으로 취급하지 않는다.
- live readiness는 기능 구현보다 safety, audit, reconciliation을 먼저 본다.
- LLM은 본선 실행 체계가 아니라 격리된 연구 레인으로 다룬다.
- single operator가 shell 없이도 판단할 수 있는 운영 표면을 만든다.

## 청사진 구조

청사진 문서는 두 개의 이름 체계를 함께 사용합니다.

- `Platform Program`과 `Metrics and Gates`는 기능 경계를 기준으로 한 workstream 이름을 사용합니다.
- `Backlog Map`은 실행 순서와 의존 관계를 드러내기 위해 workstream을 더 큰 execution program으로 다시 묶습니다.

### Workstreams

- Workstream A: Data Trust
- Workstream B: Experiment OS
- Workstream C: Runtime Ops
- Workstream D: Guarded Execution
- Workstream E: Intelligence Research

### Execution Programs

- Program 1: Research Core (`Data Trust` + `Experiment OS`)
- Program 2: Operations Core (`Runtime Ops` + control-room and operator-trust surfaces)
- Program 3: Safe Execution (`Guarded Execution` + audit/reconciliation gates)
- Program 4: Intelligence Research (`Intelligence Research`)
- Program 5: Documentation and Operational Discipline

## Directions Alignment

Internal planning directions live under `.codex-exec-loop/planning/directions/*.md`.

이 파일들도 blueprint와 같은 방향 문서이므로 `current-state` 및 `roadmap`과 어긋나면
함께 수정해야 합니다.
