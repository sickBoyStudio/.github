# sickBoyStudio / .github

조직 프로필, 공동 규칙, 템플릿, 자동 검사 도구가 있는 레포입니다. 조직 소개는 [조직 페이지](https://github.com/sickBoyStudio)에서 보세요.

## 구성

```
profile/README.md          조직 페이지에 보이는 소개
GOVERNANCE.md              운영 규칙
CONTRIBUTING.md            공동제작 참여 가이드 (PR로 기여자 등록)
CODE_OF_CONDUCT.md         행동강령
SUPPORT.md / SECURITY.md   도움 받기 / 보안 신고
policies/
  revenue-share.md           수익 분배 규칙
  contributor-agreement.md   기여자 약정
  copyright-and-licensing.md 저작권과 코드·에셋 사용 허가
  infringement-response.md   저작권 침해 대응
  legal-structure.md         법적 구조와 세금
guides/
  roblox-revenue.md          로블록스 수익구조 (2026년 10월 기준)
  getting-started.md         로블록스 처음 만들어 보기
templates/                   게임 레포에 복사해서 쓰는 파일
  CONTRIBUTORS.yml  LICENSE  CREDITS.md  workflows/contributors-check.yml
scripts/check_contributors.py  CONTRIBUTORS.yml 검사기
.github/
  ISSUE_TEMPLATE/            참여 신청 · 사용 허가 요청 · 침해 신고 (조직 기본 이슈 양식)
  PULL_REQUEST_TEMPLATE.md   조직 기본 PR 양식
  DISCUSSION_TEMPLATE/q-a.yml  소통창구 Q&A 질문 양식 (파일 이름 = 카테고리 slug.
                               GitHub는 한글 slug에 양식을 붙이지 못해서 Q&A만 영문 이름을 씀)
  workflows/contributors-check.yml   게임 레포에서 호출하는 재사용 워크플로
```

## 새 게임 레포에 적용하기

```sh
# 게임 레포 루트에서
base=https://raw.githubusercontent.com/sickBoyStudio/.github/main/templates
curl -fsSLO "$base/CONTRIBUTORS.yml"
curl -fsSLO "$base/LICENSE"
curl -fsSLO "$base/CREDITS.md"
mkdir -p .github/workflows
curl -fsSL "$base/workflows/contributors-check.yml" -o .github/workflows/contributors-check.yml
```

그 다음 `CONTRIBUTORS.yml`의 `project.name`과 `owner.github`, `LICENSE`의 연도와 이름을 채웁니다.

## 검사기 로컬 실행

```sh
pip install pyyaml
python3 scripts/check_contributors.py --file CONTRIBUTORS.yml
python3 -m unittest discover -s tests
```

## 규칙 바꾸기

이 레포에 PR을 보내고 멤버 과반의 Approve를 받습니다. 수익·저작권 규칙은 merge 전에 7일 동안 공지합니다. ([운영 규칙 6장](GOVERNANCE.md#6-의사결정))
