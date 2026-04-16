# Blueprint

`akra-trader`의 중장기 청사진 문서군입니다.

이 문서군은 구현 현황 문서가 아니라 앞으로 6-9개월 동안 무엇을 어떤 순서와 기준으로 만들지 정의하는 프로그램 문서입니다.

## 기본 프레임

- 기간: 6-9개월
- 전략: research-first
- 운영 모델: single operator
- 시장 방향: crypto 운영 우선, stocks 확장 가능 구조 유지
- 문서 역할: 한국어 기획 청사진

## 이 문서군이 답하는 질문

- 이 플랫폼은 6-9개월 뒤 어떤 상태여야 하는가
- 무엇을 먼저 만들고 무엇을 의도적으로 미루는가
- 연구, sandbox, live, LLM 레인을 어떤 규칙으로 연결할 것인가
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

## 기존 문서와의 관계

- [Current State](../status/current-state.md)
  - 지금 실제로 구현된 상태의 기준 문서
- [Roadmap](../roadmap/README.md)
  - 현재 기준에서 남은 작업을 요약한 실행 로드맵
- `docs/blueprint/*`
  - 중장기 의도, 단계, 운영 원칙, gate, 리스크를 담는 청사진 문서

## 청사진의 핵심 원칙

- 먼저 연구를 완성하고, 그 다음 운영을 만든다.
- replay preview와 continuous worker를 같은 것으로 취급하지 않는다.
- live는 안전장치, 감사 추적, reconciliation 없이 열지 않는다.
- LLM은 본선 실행 체계가 아니라 격리된 연구 레인으로 다룬다.
- single operator가 shell 없이도 판단할 수 있는 운영 표면을 만든다.

## 프로그램 축

- Program 1: Data Trust
- Program 2: Experiment OS
- Program 3: Runtime Ops
- Program 4: Guarded Execution
- Program 5: Intelligence Research

각 프로그램의 세부 내용은 [Platform Program](platform-program.md)과 [Backlog Map](backlog-map.md)에서 다룹니다.
