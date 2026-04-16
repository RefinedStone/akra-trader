# Platform Program

## 개요

플랫폼 청사진은 다섯 개의 workstream으로 고정합니다.

- Workstream A: Data Trust
- Workstream B: Experiment OS
- Workstream C: Runtime Ops
- Workstream D: Guarded Execution
- Workstream E: Intelligence Research

각 workstream은 현재 구현을 확장하는 방식으로 설계합니다. 핵심은 기존 hexagonal boundary를 유지하면서 운영성과 재현성을 강화하는 것입니다.

## Workstream A: Data Trust

목적:

- 모든 run이 믿을 수 있는 데이터 경계를 갖게 만든다

현재 공백:

- lineage는 있으나 stable dataset identity가 부족하다
- ingestion job history와 failure retention이 약하다
- crypto 외 시장 확장 전략이 아직 문서 수준이다

목표 상태:

- run이 dataset id 또는 sync checkpoint id를 가진다
- data freshness, gap, failure가 제품 표면에 드러난다
- crypto 운영 본선을 유지하면서 stocks adapter를 위한 구조적 경계가 유지된다

필수 capability:

- dataset/checkpoint identity
- ingestion job log
- lag/failure summary
- symbol/timeframe별 data quality contract

필요한 인터페이스 방향:

- run metadata에 `dataset_identity` 또는 동등 개념 추가
- market-data status에 failure history와 checkpoint 정보 확장
- 읽기용 query와 쓰기용 sync control의 책임 분리

선행조건:

- 현재 Binance adapter 유지
- SQLite/Postgres 겸용 저장 구조 존중

미루는 것:

- 다중 거래소 동기 운영
- broad equities venue support

## Workstream B: Experiment OS

목적:

- backtest를 실행 기록이 아니라 실험 운영체계로 승격한다

현재 공백:

- strategy lifecycle이 metadata 수준에 머무른다
- run tags/presets가 없다
- payload-centric query 모델이라 실험 검색성과 확장성이 약하다

목표 상태:

- 전략, 시나리오, 데이터 기준, 결과 비교가 하나의 실험 모델로 연결된다

필수 capability:

- durable strategy registration
- lifecycle state machine
- run tags
- scenario presets
- benchmark pack
- export/artifact registry

필요한 인터페이스 방향:

- strategy metadata에 lifecycle/promotion status
- run metadata에 `tags`, `preset_id`, `benchmark_family`
- query model에 strategy/version/preset/tag/dataset 기준 필터

선행조건:

- dataset identity 정립
- reference/native provenance 공통 규약 유지

미루는 것:

- 대규모 optimization sweep orchestration
- collaborative annotation workflow

## Workstream C: Runtime Ops

목적:

- 현재 preview 중심 sandbox를 운영 가능한 runtime으로 바꾼다

현재 공백:

- sandbox가 replay preview에 가깝다
- worker/session 상태 모델이 없다
- restart recovery와 heartbeat가 없다

목표 상태:

- active sandbox session이 worker로 돌고 control room에서 관찰/중지/회복할 수 있다

필수 capability:

- worker session model
- heartbeat
- restart semantics
- runtime state persistence
- preview run과 worker run 분리

필요한 인터페이스 방향:

- run record와 별도로 worker/session state model 도입
- alert model과 worker health model 연결
- UI에 active session status, decision stream, lag surface 추가

선행조건:

- market-data freshness surface
- operator event model

미루는 것:

- 멀티노드 scheduler
- fully automated self-healing orchestration

## Workstream D: Guarded Execution

목적:

- live를 "기능"이 아니라 "통제된 승격 경로"로 만든다

현재 공백:

- live adapter 부재
- audit trail 부재
- reconciliation 부재
- kill switch 부재

목표 상태:

- live candidacy는 분명하되, 미달 상태에서는 실행이 차단된다

필수 capability:

- risk limits
- operator confirmation path
- kill switch
- audit event store
- reconciliation model

필요한 인터페이스 방향:

- operator event type
- alert type
- account/exposure state model
- reconciliation result model

선행조건:

- Runtime Ops 안정화
- alerts와 event logging 기초

미루는 것:

- 다중 계정 운영
- unattended autonomous live

## Workstream E: Intelligence Research

목적:

- decision-engine contract를 추적 가능한 연구 레인으로 승격한다

현재 공백:

- template strategy와 port는 있지만 trace/replay/fallback이 없다

목표 상태:

- LLM run은 deterministic run과 동일한 실행 계약을 따르되, 별도 연구 규칙으로 기록된다

필수 capability:

- prompt version registry
- trace store
- replay harness
- evaluation report
- human review 또는 fallback

필요한 인터페이스 방향:

- decision trace model
- prompt registry model
- fallback result and review status model

선행조건:

- Experiment OS 정립
- dataset identity 정립

미루는 것:

- unattended live promotion
- provider-specific deep optimization

## 공통 기술 원칙

- domain/application은 provider나 framework 세부 구현을 모르면 된다
- reference lane은 benchmark lane이며 native contract를 대체하지 않는다
- preview와 worker, worker와 live를 문서와 모델에서 명확히 분리한다
- audit와 alert는 운영 부가 기능이 아니라 제품 일부로 취급한다
