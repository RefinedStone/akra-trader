# North Star

## 비전

`akra-trader`는 1인 운영자가 연구, 검증, 운영 준비를 하나의 플랫폼 안에서 이어갈 수 있는 trading research workstation이 되는 것을 목표로 합니다.

핵심은 "전략을 빨리 만들기"가 아니라 다음 질문에 일관되게 답하는 것입니다.

- 어떤 데이터로 실험했는가
- 무엇이 바뀌어서 결과가 달라졌는가
- 지금 운영 중인 것은 무엇인가
- 언제 멈춰야 하는가
- live로 올려도 되는가

## 대상 사용자

기본 사용자는 single operator입니다.

이 사용자는 다음을 동시에 원합니다.

- 재현 가능한 연구
- 빠른 전략 반복
- benchmark와의 비교
- 장시간 sandbox 운영
- live 이전의 명확한 safety gate
- LLM 실험의 격리와 추적성

멀티유저 협업과 SaaS는 이번 청사진의 대상이 아닙니다.

## 6-9개월 뒤 도달해야 할 상태

6-9개월 뒤 플랫폼은 다음 상태를 만족해야 합니다.

- backtest는 durable하고 rerun 가능한 실험 기록으로 남는다
- reference 전략과 native 전략은 동일한 비교 프레임 안에서 해석된다
- sandbox는 replay preview가 아니라 continuous worker로 운영된다
- operator는 데이터 상태, run 상태, alert, drift를 control room에서 파악할 수 있다
- live는 guardrail, audit, reconciliation 없이는 열리지 않는다
- LLM 전략은 trace, replay, fallback이 있는 연구 레인으로만 동작한다

## 제품 논지

이 플랫폼의 가치는 "수익률이 높은 전략을 자동으로 찾는 것"이 아닙니다.

가치는 아래 네 가지를 동시에 제공하는 데 있습니다.

1. 신뢰 가능한 실험
2. 비교 가능한 전략 결과
3. 운영 가능한 sandbox
4. 승격 조건이 분명한 live 후보 파이프라인

## 핵심 원칙

### 1. 연구가 운영을 이끈다

운영 기능은 연구 결과를 검증하고 누적하는 수단이어야 합니다.

- 데이터 계보가 불명확한 상태에서 운영으로 가지 않는다
- benchmark 없이 전략 승격을 논의하지 않는다

### 2. 실행 모드는 하나의 계단이다

`backtest -> sandbox -> live`는 분리된 제품이 아니라 하나의 승격 사다리입니다.

- mode가 달라져도 전략 해석과 provenance 규칙은 유지된다
- 달라져야 하는 것은 adapter와 safety policy다

### 3. 운영 용어를 정확히 쓴다

- preview는 preview라고 부른다
- worker는 heartbeat와 restart semantics가 있을 때만 worker라고 부른다
- live는 실제 venue action과 reconciliation이 있을 때만 live라고 부른다

### 4. LLM은 격리된 연구 레인이다

- deterministic path를 약화시키지 않는다
- trace, replay, fallback이 없으면 유효한 연구로 보지 않는다
- unattended live 사용은 허용하지 않는다

### 5. single operator 우선

이번 청사진의 UX, 운영 모델, 기록 체계는 모두 1인 운영 기준으로 설계합니다.

- 멀티 승인 체계는 지금 넣지 않는다
- 대신 "한 사람이 실수하기 어렵게 만드는 구조"를 우선한다

## 시장 범위

### 운영 본선

- crypto 우선
- Binance 중심

### 구조적 확장성

- stocks를 나중에 추가할 수 있도록 market/data/strategy metadata는 특정 자산군에 과도하게 묶지 않는다
- 다만 6-9개월 본선 deliverable은 crypto 운영 완성도가 기준이다

## 하지 않을 것

이번 청사진에서 의도적으로 미루는 것:

- multi-user/RBAC
- SaaS/self-serve
- distributed execution cluster
- 여러 거래소 동시 운영
- broad public product polishing

## 성공 정의

이 청사진이 성공하려면 다음이 성립해야 합니다.

- 문서를 읽은 구현 담당자가 "무엇을 만들지"뿐 아니라 "왜 지금은 만들지 않는지"까지 이해할 수 있어야 한다
- 각 단계의 exit gate가 정성 문장이 아니라 운영 가능한 기준이어야 한다
- current-state 문서와 청사진이 충돌하지 않아야 한다
