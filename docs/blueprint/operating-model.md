# Operating Model

## 목적

이 문서는 single operator가 `akra-trader`를 어떻게 사용할지 정의합니다. 구현 목표는 기능 목록이 아니라 "한 사람이 안전하게 운영하는 습관"을 제품에 녹이는 것입니다.

## 운영 환경 계층

### Layer 1: Research

- backtest 중심
- dataset/preset/benchmark 비교
- 전략 초안과 실험 누적

### Layer 2: Sandbox

- continuous worker 기반 검증
- near-real-time 모니터링
- drift, stale data, failure 대응

### Layer 3: Live Candidate

- 실제 live 실행 이전의 마지막 검토 상태
- safety checklist와 reconciliation readiness 충족 필요

### Layer 4: Live

- 본 청사진에서는 readiness를 설계하되, 운영 개시는 엄격한 gate 이후에만 허용

## Daily Workflow

1. market-data freshness와 sync failure 확인
2. active sandbox worker 상태 확인
3. 최근 alert와 operator event 검토
4. benchmark 대비 drift/regression 확인
5. 필요한 stop, hold, rerun, compare 실행

## Weekly Workflow

1. 전략별 benchmark pack 갱신
2. draft 전략을 benchmark candidate로 승격할지 검토
3. sandbox candidate의 soak 결과 검토
4. 데이터 품질과 reproducibility 실패 사례 정리
5. 문서화되지 않은 운영 예외를 runbook 후보로 기록

## 전략 승격 모델

전략은 다음 상태를 거칩니다.

1. `draft`
2. `benchmark_candidate`
3. `sandbox_candidate`
4. `live_candidate`
5. `archived`

각 상태의 의미:

- `draft`
  - 아이디어 검증 전 단계
- `benchmark_candidate`
  - baseline 비교 대상으로 등록됨
- `sandbox_candidate`
  - continuous sandbox 검증 대상으로 승인됨
- `live_candidate`
  - safety와 reconciliation 준비가 완료된 상태
- `archived`
  - 유지하지 않거나 더 이상 승격하지 않는 전략

## 승격 기준

### Draft -> Benchmark Candidate

- dataset identity가 명확하다
- benchmark comparison이 가능하다
- 결과 artifact가 누락되지 않는다

### Benchmark Candidate -> Sandbox Candidate

- benchmark 대비 설명 가능한 우위 또는 용도 차이가 있다
- failure mode가 명시돼 있다
- operator가 stop 조건을 이해한다

### Sandbox Candidate -> Live Candidate

- soak 기간 동안 worker 안정성이 기준치 이상이다
- stale data와 runtime failure 대응이 검증됐다
- audit, alert, reconciliation readiness가 충족된다

## Stop Rules

다음 조건에서는 자동 또는 수동 stop을 우선합니다.

- data stale
- unexplained drift
- missing auditability
- worker heartbeat loss
- reconciliation mismatch
- LLM fallback failure

## 기록 원칙

operator는 최소한 다음을 항상 남겨야 합니다.

- 어떤 전략 버전을 왜 실행했는가
- 어떤 dataset/preset을 썼는가
- 무엇과 비교했는가
- stop/hold/promote를 왜 결정했는가

이 기록은 자유 텍스트가 아니라 가능한 한 structured metadata와 operator event로 남겨야 합니다.

## Incident Classes

### Data Incident

- sync failure
- stale data
- gap explosion

### Runtime Incident

- worker crash
- heartbeat miss
- restart failure

### Strategy Incident

- unexpected drift
- benchmark regression
- unexplained order behavior

### Safety Incident

- kill switch activation
- reconciliation mismatch
- audit gap

### Intelligence Incident

- missing trace
- replay mismatch
- fallback failure

## 운영 문서와의 연결

이 문서는 상위 운영 설계입니다. 이후 runbook는 다음 범주로 분화합니다.

- daily operations
- sandbox incident response
- data incident response
- reconciliation procedure
- live stop procedure
