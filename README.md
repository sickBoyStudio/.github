# sickBoyStudio / Handbook

운영 기준과 프로젝트 공통 문서를 관리합니다. [Studio](https://github.com/sickBoyStudio) · [Discussions](https://github.com/sickBoyStudio/.github/discussions) · [Gallery](https://github.com/sickBoyStudio/gallery)

> 이 브랜치의 운영·권리 문서는 **v1.1 개정안**입니다. 현재 적용 중인 v1.0과 시행 절차는 [개정 기록](CHANGELOG.md)을 확인해 주세요.

## 시작하기

| 목적 | 읽을 문서 |
| :--- | :--- |
| 질문하거나 작업을 제안할 때 | [지원 안내](SUPPORT.md) · [참여 안내](CONTRIBUTING.md) |
| 프로젝트를 만들 때 | [프로젝트 개설](guides/project-setup.md) · [README 양식](templates/README.md) |
| 운영을 맡을 때 | [운영 규칙](GOVERNANCE.md) · [관리자 안내](guides/maintainer-handbook.md) |
| 보상과 권리를 정할 때 | [수익 배분](policies/revenue-share.md) · [기여자 약정](policies/contributor-agreement.md) |
| 문제가 생겼을 때 | [보안 신고](SECURITY.md) · [행동강령](CODE_OF_CONDUCT.md) · [권리 침해 대응](policies/infringement-response.md) |

## 정책

- [저작권과 사용 허가](policies/copyright-and-licensing.md)
- [계약과 세무 확인](policies/legal-structure.md)
- [개인정보와 기록 관리](policies/privacy.md)
- [이름·로고·공개 자료 사용](policies/brand.md)
- [문서 버전과 개정 절차](policies/document-control.md)

## 작업 양식

[프로젝트 계획](templates/PROJECT_BRIEF.md) · [작업 사전 합의](templates/WORK_AGREEMENT.md) · [기여자 장부](templates/CONTRIBUTORS.yml) · [정산서](templates/SETTLEMENT.md) · [크레딧](templates/CREDITS.md) · [결정 기록](templates/DECISION.md) · [출시 확인](templates/RELEASE_CHECKLIST.md) · [인수인계](templates/HANDOVER.md)

양식의 빈칸을 채우는 것만으로 계약·승인·지급이 완료되지는 않습니다. 권한이 있는 당사자의 확인과 실제 이행을 기록해 주세요. 민감한 자료는 공개 저장소에 넣지 않습니다.

## 개발 자료

[Studio 시작하기](guides/getting-started.md) · [Roblox 수익과 정산](guides/roblox-revenue.md)

## 검사 도구

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/check_contributors.py --file templates/CONTRIBUTORS.yml
python3 -m unittest discover -s tests
python3 scripts/check_docs.py
```

기여자 검사기는 비율과 파일 형식을 확인합니다. 당사자의 신원·동의·저작권·실제 지급은 사람이 확인합니다. 조직 공통 양식은 해당 저장소에 자체 양식이 없을 때 적용됩니다.
