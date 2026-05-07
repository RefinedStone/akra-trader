# Risk Register

## 목적

이 문서는 프로그램 진행 중 예상되는 제품, 기술, 운영 리스크를 관리하기 위한 기준 문서입니다.

## Risk 1: 데이터 신뢰도 부족

- 설명: dataset identity와 mismatch 해석이 약하면 비교와 rerun 주장이 모두 약해진다
- 트리거: 동일 입력 rerun mismatch, 반복 gap, stale data
- 영향: Research Core와 Operations Core 전체 신뢰도 하락
- 대응: checkpoint identity, lineage mismatch classification, data-quality gate
- 종료 조건: deterministic research claim을 문서와 제품에서 함께 방어 가능

## Risk 2: payload-centric storage 확장 한계

- 설명: 현재 저장 모델은 유연하지만 experiment query와 artifact 관리가 비싸고 복잡해진다
- 트리거: run 검색, 비교, export가 payload scan에 과도하게 의존
- 영향: Experiment OS 확장과 운영성 저하
- 대응: normalized query surface와 artifact/export model 도입
- 종료 조건: common query와 artifact path가 구조화된 모델로 동작

## Risk 3: runtime 의미 혼선

- 설명: preview, sandbox worker, guarded-live의 경계가 문서나 UI에서 흔들리면 operator 판단이 왜곡된다
- 트리거: 동일 용어가 다른 실행 의미를 가리키거나 active runtime과 history가 섞여 보일 때
- 영향: 잘못된 기대와 위험한 운영 판단
- 대응: mode naming, UI separation, current-state discipline
- 종료 조건: preview/history, worker, guarded-live가 제품과 문서에서 명시적으로 구분

## Risk 4: 운영 표면은 있지만 운영 경험이 부족함

- 설명: 기능은 있어도 operator workflow가 명확하지 않으면 다시 shell과 ad hoc 판단으로 돌아간다
- 트리거: alert 과밀, monolithic UI, runbook 부재
- 영향: control room 가치 저하, incident 대응 실패
- 대응: active-session-first UX, operator runbooks, clearer action guidance
- 종료 조건: 주요 daily/incident workflow를 control room과 runbook만으로 수행 가능

## Risk 5: early guarded-live capability를 live-ready로 오해할 가능성

- 설명: guarded-live control plane이 존재한다는 이유로 safety completion이 끝났다고 오해할 수 있다
- 트리거: drill, deployment, venue lifecycle completion 없이 readiness를 주장할 때
- 영향: 실제 손실 및 설계 오염
- 대응: live readiness gate, drill discipline, explicit product-position wording
- 종료 조건: guarded-live scope와 live candidacy 기준이 문서와 제품에 함께 고정

## Risk 6: LLM 기대 과잉

- 설명: LLM lane이 차별화 포인트라는 이유로 deterministic path를 침범할 수 있다
- 트리거: trace 없이 사용, fallback 없는 승격 논의
- 영향: 연구와 운영 기준 붕괴
- 대응: LLM lane 별도 문서와 gate, unattended live 금지
- 종료 조건: trace, replay, fallback이 모두 구현됨

## Risk 7: market scope 확장으로 인한 분산

- 설명: crypto와 stocks를 동시에 깊게 가져가면 둘 다 얕아질 수 있다
- 트리거: early-stage에서 equities-specific 운영 기능을 병행 추진
- 영향: 본선 완성도 저하
- 대응: crypto 운영 우선, stocks는 extension path만 유지
- 종료 조건: crypto 운영 baseline 확보 후에만 확장 착수

## Risk 8: 1인 운영 과부하

- 설명: 관찰, 비교, incident 대응, 승격 판단이 모두 한 사람에게 몰린다
- 트리거: 알림 과다, manual checklist 과다, context switching 과다
- 영향: 운영 실수, 문서 미갱신, 판단 지연
- 대응: control room 집중, structured metadata, stop rules, runbooks
- 종료 조건: daily workflow가 shell과 ad hoc note 없이 가능

## Risk 9: 외부 전략 의존 왜곡

- 설명: 외부 전략을 사실상 주 실행 경로처럼 다루게 될 수 있다
- 트리거: 외부 전략 behavior가 native contract를 잠식
- 영향: 아키텍처 일관성 붕괴
- 대응: 외부 전략은 제품 런타임에 직접 포함하지 않고 별도 검토로 제한
- 종료 조건: native contract 경계 유지

## Risk 10: 문서와 구현의 재분리

- 설명: 현재 문서 정리 이후에도 다시 구현과 어긋날 수 있다
- 트리거: 기능 추가 후 current-state, roadmap, directions 미갱신
- 영향: 우선순위 왜곡과 잘못된 기대
- 대응: release/change 시 문서 갱신 체크 포함
- 종료 조건: current-state, roadmap, blueprint, directions drift가 관리됨
