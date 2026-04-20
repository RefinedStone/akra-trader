# Backlog Map

## 목적

현재 backlog를 프로그램 기준으로 재정렬해, 구현 순서와 의존 관계가 한눈에 보이도록 합니다.

이 문서의 Program 번호는 `Platform Program`의 workstream을 실행 순서 관점에서 다시 묶은 번호입니다.

- Program 1 = `Data Trust` + `Experiment OS`
- Program 2 = `Runtime Ops` + operator trust surfaces
- Program 3 = `Guarded Execution`
- Program 4 = `Intelligence Research`
- Program 5 = documentation and operational discipline

## Program 1: Research Core (`Data Trust` + `Experiment OS`)

목표:

- 연구를 defendable하고 rerunnable한 운영체계로 완성한다

현재 baseline:

- lineage, rerun boundary, presets, comparison이 이미 존재한다

다음 핵심 순서:

1. deterministic dataset boundary claim 강화
2. durable strategy registry와 promotion model
3. normalized experiment query, artifact, export posture

주요 산출물:

- stable dataset boundary
- durable strategy registry
- experiment summary and artifact model

## Program 2: Operations Core (`Runtime Ops` + operator trust surfaces)

목표:

- 이미 존재하는 runtime substrate를 operator-grade workflow로 만든다

현재 baseline:

- sandbox worker/session, heartbeat, recovery, alert surface가 이미 존재한다

다음 핵심 순서:

1. active session UX 정리
2. positions/fills/lag/recent-decision surface 강화
3. control room 구조 단순화
4. runbook-linked operator workflow 정착

주요 산출물:

- active runtime surface
- clearer alert and action model
- operations-oriented control room

## Program 3: Safe Execution (`Guarded Execution`)

목표:

- existing guarded-live control plane을 operational readiness 프로그램으로 완성한다

현재 baseline:

- kill switch, reconciliation, recovery, incidents, delivery history, venue-backed launch gate가 이미 있다

다음 핵심 순서:

1. venue lifecycle scope 정리
2. guarded-live drills와 operator discipline
3. broader order-management posture
4. explicit live candidacy gate

주요 산출물:

- reconciliation drill
- kill-switch drill
- live candidacy checklist

## Program 4: Intelligence Research (`Intelligence Research`)

목표:

- LLM decision lane을 연구 가능한 형태로 고립시킨다

현재 baseline:

- port와 template는 있으나 trace/replay/fallback은 없다

파생 작업:

- prompt registry
- trace schema
- replay harness
- review/fallback policy

주요 산출물:

- valid intelligence run definition
- replayable trace
- benchmarkable evaluation report

## Program 5: Documentation And Operational Discipline

목표:

- 구현과 운영 판단을 문서 체계로 고정한다

현재 baseline:

- 문서군은 충분히 많지만 drift가 생기기 쉬운 구조다

파생 작업:

- current-state maintenance rule
- operator runbook set
- release doc checklist
- directions alignment rule

## 권장 실행 순서

### Wave 1

- Program 1 마무리

이유:

- research trust와 experiment OS가 불안하면 이후 운영 판단 기준이 흔들린다

### Wave 2

- Program 2 핵심

이유:

- runtime substrate는 이미 있으므로, 이제 operator workflow를 완성해야 한다

### Wave 3

- Program 3 집중

이유:

- guarded-live는 기능보다 safety completion과 drill discipline이 더 중요하다

### Wave 4

- Program 4 foundation + Program 5 정착

이유:

- 운영과 연구가 동시에 커지는 시점에 문서와 절차를 같이 묶어야 한다

## 프로그램 간 차단 관계

- Program 2는 Program 1이 만든 deterministic experiment 기준 없이는 완성되지 않는다
- Program 3는 Program 2가 만든 operator workflow와 discipline 없이는 성립하지 않는다
- Program 4는 Program 1의 provenance와 reproducibility가 약하면 의미가 약하다
- Program 5는 모든 wave에 병행되지만 Wave 2 이후 중요도가 더 커진다
