# Platform Program

## 개요

플랫폼 청사진은 다섯 개의 workstream으로 고정합니다.

- Workstream A: Data Trust
- Workstream B: Experiment OS
- Workstream C: Runtime Ops
- Workstream D: Guarded Execution
- Workstream E: Intelligence Research

이 문서는 "무엇을 더 완성해야 하는가"를 정의합니다. 현재 구현 상태 판정은
`docs/status/current-state.md`를 따릅니다.

## Workstream A: Data Trust

목적:

- 모든 run이 설명 가능한 데이터 경계와 실패 해석을 갖게 만든다

현재 baseline:

- dataset fingerprint, sync-checkpoint linkage, rerun boundary가 이미 존재한다
- market-data status에 freshness, gap, backfill, failure history가 이미 드러난다

남은 핵심 공백:

- deterministic rerun claim을 더 강하게 증명하는 규약
- lineage mismatch를 제품 표면에서 해석하는 방식
- ingestion job history와 normalized lineage query

목표 상태:

- run이 stable dataset boundary를 가리킨다
- rerun mismatch가 generic drift가 아니라 분류된 원인으로 설명된다
- operator가 shell 없이도 데이터 경계 상태를 판단할 수 있다

필수 capability:

- dataset/checkpoint identity
- lineage mismatch classification
- ingestion job log
- symbol/timeframe별 data quality contract

## Workstream B: Experiment OS

목적:

- backtest와 비교를 실행 기록이 아니라 실험 운영체계로 승격한다

현재 baseline:

- presets, revisions, query/filter contracts, comparison, rerun boundary가 이미 있다
- native와 reference lane은 공통 비교 및 provenance 흐름을 공유한다

남은 핵심 공백:

- durable custom strategy registry
- promotion/lifecycle workflow의 영속화
- normalized experiment summaries, artifact registry, export posture

목표 상태:

- 전략, 시나리오, 데이터 기준, 결과 비교, 승격 판단이 하나의 실험 모델로 연결된다

필수 capability:

- durable strategy registration
- lifecycle and promotion model
- normalized experiment query surface
- artifact/export registry
- benchmark pack and review workflow

## Workstream C: Runtime Ops

목적:

- 현재 존재하는 sandbox worker 기반을 실제 운영 가능한 runtime 경험으로 완성한다

현재 baseline:

- sandbox worker/session model, heartbeat, restart recovery가 이미 존재한다
- stale runtime과 worker failure는 operator surface로 노출된다

남은 핵심 공백:

- active session 중심의 operator workflow
- lag, fills, positions, recent decisions에 대한 더 명확한 제품 표면
- control room 구조의 단순화와 운영성 강화

목표 상태:

- active sandbox session이 product-level workflow로 관찰, 중지, 해석, 복구될 수 있다

필수 capability:

- active session surface
- clearer health and lag model
- operator action guidance
- preview/history view와 active-runtime view의 명확한 분리

## Workstream D: Guarded Execution

목적:

- guarded-live를 "이미 가능한 기능"에서 "통제된 운영 readiness 프로그램"으로 완성한다

현재 baseline:

- kill switch, reconciliation, recovery, incidents, delivery history, live launch gate가 이미 있다
- venue-backed launch, cancel, replace, session ownership, open-order snapshot도 이미 있다

남은 핵심 공백:

- fuller venue-native lifecycle recovery
- broader order-management posture
- deployment, credential, and drill discipline
- 더 명확한 live candidacy 규약

목표 상태:

- live candidacy는 분명하되, 기준 미달 상태에서는 항상 차단된다

필수 capability:

- risk and operator confirmation path
- audit/event discipline
- reconciliation drill
- kill-switch drill
- venue lifecycle scope definition

## Workstream E: Intelligence Research

목적:

- decision-engine contract를 traceable research lane으로 승격한다

현재 baseline:

- `DecisionEnginePort`, template strategy, trace-capable envelope만 존재한다

남은 핵심 공백:

- prompt registry
- trace store
- replay harness
- fallback 또는 review enforcement
- provider adapter

목표 상태:

- LLM run은 deterministic lane과 분리되되, 비교 가능하고 재현 가능한 연구 기록으로 남는다

필수 capability:

- prompt version registry
- trace schema
- replay harness
- evaluation report
- fallback or review policy

## 공통 기술 원칙

- domain/application은 provider나 framework 세부 구현을 모르면 된다
- reference lane은 benchmark lane이며 native contract를 대체하지 않는다
- preview와 worker, worker와 guarded-live를 문서와 모델에서 명확히 분리한다
- audit와 alert는 운영 부가 기능이 아니라 제품 일부로 취급한다
