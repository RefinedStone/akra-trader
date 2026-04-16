# Metrics and Gates

## 목적

이 문서는 "좋아 보인다"가 아니라 "다음 단계로 넘어가도 된다"를 판단하는 기준을 정의합니다.

## Metric Group A: Data Trust

### Freshness

- 정의: tracked symbol/timeframe 기준 최신 데이터 지연
- 목표: 운영 대상 symbol의 지연이 95% 이상 구간에서 2 bar 이하
- blocking condition: 운영 대상 symbol이 3회 이상 연속 stale

### Gap-free Coverage

- 정의: 최근 운영 기준 구간에서 gap 없이 이어지는 캔들 비율
- 목표: sandbox 후보 구간 99% 이상
- blocking condition: 핵심 symbol/timeframe에서 반복 gap 발생

### Sync Failure Rate

- 정의: ingestion cycle 중 실패 비율
- 목표: 일 단위 1% 이하
- blocking condition: 동일 원인 실패가 24시간 내 반복

## Metric Group B: Experiment Quality

### Reproducibility Match Rate

- 정의: 동일 strategy/version/params/dataset checkpoint rerun 시 결과 일치 비율
- 목표: 연구 기준 100%
- blocking condition: 동일 checkpoint rerun mismatch 발생

### Comparison Completeness

- 정의: benchmark comparison에 필요한 metrics/artifacts가 모두 존재하는 run 비율
- 목표: benchmark 대상 run 100%
- blocking condition: 비교 대상 run에 필수 provenance 누락

### Preset Coverage

- 정의: 주요 전략이 표준 preset을 통해 재실행 가능한 비율
- 목표: active strategy 90% 이상

## Metric Group C: Runtime Reliability

### Worker Uptime

- 정의: sandbox worker 가용 시간 비율
- 목표: sandbox candidate 기준 7일 관찰 구간 95% 이상
- live readiness 목표: 99% 이상

### Heartbeat Miss Rate

- 정의: expected heartbeat 대비 miss 비율
- 목표: 1% 이하
- blocking condition: 연속 miss로 인해 worker state 불명확

### Recovery Success Rate

- 정의: restart 또는 transient failure 이후 자동/반자동 recovery 성공 비율
- 목표: 90% 이상

## Metric Group D: Safety Readiness

### Audit Coverage

- 정의: live-affecting action 중 structured event가 남는 비율
- 목표: 100%
- blocking condition: audit gap 한 건이라도 발생

### Reconciliation Success

- 정의: simulated or real account state와 내부 상태를 맞추는 절차의 성공 비율
- 목표: drill 기준 100%
- blocking condition: unresolved mismatch 존재

### Kill Switch Drill

- 정의: emergency stop 절차의 성공 여부
- 목표: 반복 drill 100% 성공

## Metric Group E: Intelligence Research

### Trace Capture Rate

- 정의: LLM run 중 필수 trace 필드가 모두 기록된 비율
- 목표: 100%

### Replay Coverage

- 정의: LLM run 중 replay 가능한 run 비율
- 목표: 100%

### Fallback Integrity

- 정의: fallback 또는 review path가 정책대로 작동한 비율
- 목표: 100%

## Gate 1: Research OS Gate

통과 조건:

- Reproducibility Match Rate 100%
- Comparison Completeness 100%
- standard preset 기반 rerun 가능
- strategy lifecycle 상태가 durable query로 조회 가능

실패 시 의미:

- 아직 플랫폼은 "실험 운영체계"가 아니라 "실행 기록 저장소"에 가깝다

## Gate 2: Sandbox Operations Gate

통과 조건:

- sandbox worker uptime 95% 이상
- heartbeat miss rate 1% 이하
- stale data alert와 worker failure alert 가시화
- preview와 worker state가 문서와 제품에서 분리됨

실패 시 의미:

- sandbox는 운영 모드가 아니라 여전히 preview 모드다

## Gate 3: Live Readiness Gate

통과 조건:

- audit coverage 100%
- reconciliation drill 100%
- kill switch drill 100%
- operator event visibility 확보

실패 시 의미:

- live는 구현되더라도 열면 안 된다

## Gate 4: LLM Research Gate

통과 조건:

- trace capture rate 100%
- replay coverage 100%
- fallback integrity 100%
- benchmark 대비 문서화된 평가 보고서 존재

실패 시 의미:

- LLM 레인은 데모일 뿐 연구 레인으로 인정할 수 없다

## 운영 원칙

- 한 단계 gate를 통과하지 못하면 다음 단계 capability를 확장하지 않는다
- 수익률이 좋아도 audit, reproducibility, trace gate를 대체하지 못한다
- gate는 문서 문구가 아니라 운영 가능한 수치와 drill로 검증한다
