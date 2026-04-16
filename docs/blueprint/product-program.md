# Product Program

## 프로그램 요약

제품 프로그램은 `연구 완성 -> 운영형 sandbox -> guarded live 준비 -> LLM 연구 레인 정립` 순서로 진행합니다.

6-9개월 안에 모든 기능을 다 만드는 것이 목표가 아니라, 다음 단계로 올라도 되는 기준을 분명하게 만드는 것이 목표입니다.

## Program Phase 1: Research OS Completion

예상 기간:

- 0-8주

사용자 결과:

- 사용자가 실험을 다시 찾고, 다시 돌리고, benchmark와 비교할 수 있다

핵심 결과물:

- dataset identity와 run lineage 강화
- strategy lifecycle 기본 모델
- run tags와 scenario presets
- artifact/export 기준선
- comparison workflow 정리

릴리즈 게이트:

- run이 stable dataset boundary를 가리킨다
- 동일 입력 재실행 시 동일 checkpoint를 기준으로 비교 가능하다
- 전략과 run을 lifecycle과 preset 관점에서 찾을 수 있다

## Program Phase 2: Benchmark and Promotion Workflow

예상 기간:

- 6-14주

사용자 결과:

- operator가 전략을 draft에서 benchmark candidate로, 다시 sandbox candidate로 올리는 흐름을 플랫폼에서 관리할 수 있다

핵심 결과물:

- 전략 승격 상태 정의
- baseline benchmark pack
- comparison review template
- 승격/보류 판단 근거 문서화

릴리즈 게이트:

- native와 reference 전략을 공통 기준으로 비교할 수 있다
- 승격 판단에 필요한 artifact가 누락되지 않는다
- 전략 버전과 scenario가 durable하게 남는다

## Program Phase 3: Continuous Sandbox Operations

예상 기간:

- 12-24주

사용자 결과:

- operator가 shell 없이 sandbox 전략을 계속 돌리고 상태를 감시할 수 있다

핵심 결과물:

- continuous worker
- heartbeat와 restart behavior
- stale data / worker failure alert
- worker state와 preview state 분리
- control room operations surface 강화

릴리즈 게이트:

- sandbox는 더 이상 replay preview로 오해되지 않는다
- active worker의 상태와 최근 결정, 포지션, lag가 UI에 드러난다
- restart 이후에도 worker/session 상태를 추적할 수 있다

## Program Phase 4: Guarded Live Readiness

예상 기간:

- 20-32주

사용자 결과:

- live를 바로 열지 않더라도, 언제 열 수 있고 언제 못 여는지 기준이 명확하다

핵심 결과물:

- risk controls
- kill switch
- operator event log
- audit trail
- reconciliation flow

릴리즈 게이트:

- audit 없이 live action은 불가능하다
- reconciliation drill이 통과되지 않으면 live candidacy를 부여하지 않는다
- emergency stop은 문서가 아니라 제품 기능으로 존재한다

## Program Phase 5: LLM Research Lane

예상 기간:

- 24-36주 병행

사용자 결과:

- LLM-assisted 전략을 deterministic lane과 섞지 않고 연구할 수 있다

핵심 결과물:

- prompt version registry
- raw trace storage
- replay harness
- evaluation report
- human review / fallback policy

릴리즈 게이트:

- trace 없는 LLM run은 invalid하다
- replay 불가한 LLM strategy는 승격 대상이 아니다
- unattended live promotion은 금지된다

## 제품 사용자 여정

### 전략 연구

1. 전략 초안 생성
2. dataset/preset 선택
3. backtest 실행
4. benchmark 비교
5. 결과와 artifact 보존

### 전략 승격

1. draft
2. benchmark candidate
3. sandbox candidate
4. live candidate

각 단계는 수익률만이 아니라 데이터 신뢰도, 비교 품질, failure mode 해석 가능성을 포함해 판단합니다.

### 운영

1. 데이터 상태 확인
2. active sandbox 확인
3. alert 검토
4. drift 확인
5. stop/hold/promote 판단

## 이번 청사진의 제품적 비범위

- social/sharing 기능
- 팀 단위 승인 플로우
- 퍼블릭 전략 마켓플레이스
- 최적화 파라미터 탐색 대시보드의 대규모 자동화

## 제품 성공 상태

다음 질문에 UI와 기록만으로 답할 수 있어야 합니다.

- 지금 어떤 전략이 어떤 데이터 기준으로 돌고 있는가
- 최근 비교에서 무엇이 좋아졌고 무엇이 나빠졌는가
- 지금 멈춰야 하는가
- live candidacy가 있는가
- LLM 결과는 연구 가치가 있는가
