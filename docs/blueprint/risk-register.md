# Risk Register

## 목적

이 문서는 프로그램 진행 중 예상되는 제품, 기술, 운영 리스크를 관리하기 위한 기준 문서입니다.

## Risk 1: 데이터 신뢰도 부족

- 설명: dataset identity가 약하면 비교와 rerun이 모두 약해진다
- 트리거: 동일 입력 rerun mismatch, 반복 gap, stale data
- 영향: Stage 2와 Stage 3 전체 신뢰도 하락
- 대응: checkpoint identity, ingestion failure history, gap blocking rule
- 종료 조건: reproducibility gate 통과

## Risk 2: payload-centric storage 확장 한계

- 설명: 현재 저장 모델은 유연하지만 experiment query가 비싸고 운영성 확장이 어렵다
- 트리거: run 검색/비교/필터가 payload scan에 의존
- 영향: Stage 2 이후 성능과 설계 복잡도 증가
- 대응: 정규화된 query surface와 summary tables 도입
- 종료 조건: common query가 normalized path로 동작

## Risk 3: sandbox 용어와 실제 구현 불일치

- 설명: preview를 sandbox로 부르면 operator가 실제 운영 가능성으로 오해한다
- 트리거: restart/heartbeat 없는 상태에서 sandbox 명칭 유지
- 영향: 잘못된 기대와 위험한 운영 판단
- 대응: preview와 worker를 모델, API, UI, 문서에서 분리
- 종료 조건: continuous worker와 preview run이 명시적으로 구분

## Risk 4: 운영 표면 부족

- 설명: alert와 event가 없으면 operator는 shell로 돌아간다
- 트리거: stale data, worker crash, unexplained drift
- 영향: control room 가치 저하, incident 대응 실패
- 대응: operator event store, alert panel, incident taxonomy
- 종료 조건: 주요 incident가 UI에서 식별 가능

## Risk 5: live를 너무 빨리 열 가능성

- 설명: 기능 구현 압력으로 safety보다 execution이 먼저 들어갈 수 있다
- 트리거: audit/reconciliation 없이 live adapter 추진
- 영향: 실제 손실 및 설계 오염
- 대응: live readiness gate와 explicit prohibition 유지
- 종료 조건: kill switch, audit, reconciliation이 제품 기능으로 존재

## Risk 6: LLM 기대 과잉

- 설명: LLM lane이 차별화 포인트라는 이유로 본선 deterministic path를 침범할 수 있다
- 트리거: trace 없이 sandbox 사용, fallback 없는 승격 논의
- 영향: 실험과 운영 기준 붕괴
- 대응: LLM lane 별도 문서와 gate, unattended live 금지
- 종료 조건: trace/replay/fallback이 전부 구현됨

## Risk 7: market scope 확장으로 인한 분산

- 설명: crypto와 stocks를 동시에 깊게 가져가려 하면 둘 다 얕아질 수 있다
- 트리거: 초기에 stocks-specific 운영 기능까지 병행 추진
- 영향: 본선 완성도 저하
- 대응: crypto 운영 우선, stocks는 adapter-friendly structure로만 준비
- 종료 조건: crypto 운영 baseline 확보 후 stocks track 착수

## Risk 8: 1인 운영 과부하

- 설명: 관찰, 비교, incident 대응, 승격 판단이 모두 한 사람에게 몰린다
- 트리거: 알림 과다, manual checklist 과다, context switching 과다
- 영향: 운영 실수, 문서 미갱신, 판단 지연
- 대응: control room 집중, structured metadata, stop rules 명확화
- 종료 조건: daily workflow가 shell과 ad hoc note 없이 가능

## Risk 9: reference lane 의존 왜곡

- 설명: NFI reference를 benchmark가 아니라 사실상 주 실행 경로처럼 다루게 될 수 있다
- 트리거: reference-specific behavior가 native contract를 잠식
- 영향: 아키텍처 일관성 붕괴
- 대응: reference lane은 benchmark/external runtime lane으로 고정
- 종료 조건: native contract와 reference lane의 경계 유지

## Risk 10: 문서와 구현의 재분리

- 설명: 청사진 문서가 생긴 뒤 다시 구현과 어긋날 수 있다
- 트리거: 기능 추가 후 current-state/blueprint 미갱신
- 영향: 우선순위 왜곡, 잘못된 기대
- 대응: release/change 시 문서 갱신 체크 포함
- 종료 조건: current-state와 roadmap/blueprint drift가 관리됨
