# Backlog Map

## 목적

현재 backlog를 프로그램 기준으로 재정렬해, 구현 순서와 의존 관계가 한눈에 보이도록 합니다.

이 문서의 Program 번호는 `Platform Program`의 workstream을 실행 순서 관점에서 다시 묶은 번호입니다.

- Program 1 = `Data Trust` + `Experiment OS`
- Program 2 = `Runtime Ops` + operator trust surfaces
- Program 3 = `Guarded Execution`
- Program 4 = `Intelligence Research`
- Program 5 = cross-cutting documentation and operational discipline

## Program 1: Research Core (`Data Trust` + `Experiment OS`)

목표:

- 연구를 durable하고 rerunnable한 운영체계로 바꾼다

포함 epic:

- Epic 1: Reproducibility and Dataset Lineage Hardening
- Epic 2: Experiment Metadata Completion
- Epic 3: Durable Strategy Lifecycle and Registration

선행 순서:

1. dataset identity
2. experiment query/preset/tag
3. lifecycle and durable strategy registration

주요 산출물:

- stable dataset boundary
- preset/tag/filter model
- strategy promotion state model

## Program 2: Operations Core (`Runtime Ops` + operator trust surfaces)

목표:

- sandbox를 실제 운영 경로로 만든다

포함 epic:

- Epic 4: Continuous Sandbox Worker
- Epic 5: Alerts and Operator Events
- Epic 9: Control Room Operations Upgrade

선행 순서:

1. worker/session state model
2. heartbeat and recovery
3. alerts and operator event visibility
4. control room consolidation

주요 산출물:

- active worker model
- alert/event model
- operations UI

## Program 3: Safe Execution (`Guarded Execution`)

목표:

- live readiness를 기능보다 먼저 정의한다

포함 epic:

- Epic 6: Live Execution Guardrails
- Epic 7: Reconciliation and Audit Trail

선행 순서:

1. operator event and audit substrate
2. risk and kill-switch controls
3. reconciliation flow
4. live candidate gate

주요 산출물:

- kill switch
- audit log
- reconciliation drill

## Program 4: Intelligence Research (`Intelligence Research`)

목표:

- LLM decision lane을 연구 가능한 형태로 고립시킨다

포함 epic:

- Epic 8: LLM Decision Research Lane

파생 작업:

- prompt registry
- trace schema
- replay harness
- review/fallback policy

주요 산출물:

- valid LLM run definition
- replayable trace
- benchmarkable evaluation report

## Program 5: Documentation and Operational Discipline

목표:

- 구현과 운영 판단을 문서 체계로 고정한다
- 이 program은 다른 기능 program과 병행되는 cross-cutting discipline이다

포함 epic:

- Epic 10: Documentation and Runbooks

파생 작업:

- current-state maintenance rule
- incident runbook set
- promotion checklist
- release doc checklist

## 권장 실행 순서

### Wave 1

- Program 1 전부

이유:

- 연구 신뢰도 없이 이후 운영 기능을 올리면 판단 기준이 흔들린다

### Wave 2

- Program 2 핵심

이유:

- sandbox를 실제 운영 단계로 끌어올려야 Stage 3가 성립한다

### Wave 3

- Program 3 기초 + Program 4 foundation

이유:

- live readiness는 audit/reconciliation 없이 논의하지 않는다
- LLM lane도 trace foundation부터 시작해야 한다

### Wave 4

- Program 3 마무리 + Program 4 확장 + Program 5 정착

이유:

- 운영과 연구가 동시에 커지는 시점에 문서와 절차를 같이 묶어야 한다

## 프로그램 간 차단 관계

- Program 2는 Program 1이 만든 dataset identity와 experiment OS를 전제로 한다
- Program 3는 Program 2가 만든 worker/event 기반 없이는 성립하지 않는다
- Program 4는 Program 1의 reproducibility와 provenance가 없으면 의미가 약하다
- Program 5는 모든 wave에 병행되지만, 특히 Wave 2 이후 중요도가 커진다

## 구현 우선순위 결론

중장기 작업은 아래 한 줄로 정리합니다.

1. 신뢰 가능한 연구 기반을 먼저 만든다.
2. 그 위에 운영 가능한 sandbox를 만든다.
3. 그 다음에 live readiness를 만든다.
4. LLM은 항상 격리된 연구 레인으로 따라온다.
