# LLM Lane

## 역할 정의

LLM lane은 `akra-trader`의 본선 실행 경로가 아니라, deterministic strategy와 동일한 실행 계약을 유지한 상태에서 decision quality를 연구하는 격리 레인입니다.

이 레인의 목적은 다음입니다.

- LLM이 어떤 맥락에서 유의미한 판단을 하는지 검증
- deterministic baseline과 비교 가능한 실험 생성
- human review 또는 fallback 없는 자동 승격을 막는 규칙 정립

## 현재 상태

현재 구현된 것은 아래 수준입니다.

- `DecisionEnginePort`
- template external decision strategy
- decision envelope에 trace를 담을 수 있는 구조

아직 없는 것은 아래입니다.

- provider adapter
- prompt versioning
- raw trace storage
- replay harness
- evaluation workflow
- fallback policy

## 운영 원칙

### 1. deterministic lane을 대체하지 않는다

- native와 reference lane이 본선 기준이다
- LLM lane은 비교 대상이자 연구 대상이다

### 2. trace 없는 run은 invalid다

최소 trace 항목:

- prompt version
- input context identity
- raw response
- normalized decision
- post-risk reviewed decision

### 3. replay 불가능한 전략은 승격 대상이 아니다

- 동일 context에서 replay 가능한 형태로 기록돼야 한다
- provider nondeterminism은 숨기지 않고 기록해야 한다

### 4. fallback 또는 review가 필수다

- fallback deterministic policy 또는 human review path가 없으면 sandbox 승격도 제한한다

### 5. unattended live는 금지한다

- 이 청사진 기간 동안 LLM lane의 unattended live promotion은 허용하지 않는다

## 평가 축

LLM 전략 평가는 수익률 하나로 하지 않습니다.

- decision consistency
- benchmark delta explainability
- replay stability
- fallback activation quality
- trace completeness
- operator review burden

## 단계별 구축 순서

### Phase A: Trace Foundation

- prompt registry
- trace schema
- raw response persistence
- run linkage

### Phase B: Replay and Evaluation

- historical context replay
- comparison report
- failure case labeling

### Phase C: Guarded Sandbox Research

- review queue
- fallback policy enforcement
- sandbox-only activation

## 최소 문서화 산출물

각 LLM 연구 run은 다음을 남겨야 합니다.

- 사용 모델/adapter
- prompt version
- context summary
- raw response
- normalized action
- fallback 여부
- operator review 결과

## 허용되는 사용

이번 청사진 기간에 허용되는 사용:

- backtest research
- replay evaluation
- guarded sandbox experiments

허용되지 않는 사용:

- trace 없는 sandbox usage
- fallback 없는 자동 의사결정
- unattended live

## exit criteria

LLM lane이 다음 단계로 넘어가려면 아래를 만족해야 합니다.

- trace capture rate 100%
- replay 가능한 run 비율 100%
- fallback 또는 review 없이 진행되는 path 0%
- benchmark 대비 장단점이 문서화된 strategy report 존재
