#!/usr/bin/env python3
"""CONTRIBUTORS.yml 검사기 — sickBoyStudio 수익 분배 규칙 v1.0

형식 검사(항상)와 변경 검사(--base 를 줄 때)를 합니다.

  python3 check_contributors.py --file CONTRIBUTORS.yml
  python3 check_contributors.py --file CONTRIBUTORS.yml --base base.yml --actor 깃허브아이디

변경 검사 규칙 (PR 작성자가 오너가 아닐 때):
  - project / owner / version / policy 는 바꿀 수 없다.
  - 다른 사람 항목은 바꾸거나 지울 수 없다.
  - 자기 항목을 새로 추가할 때 share 는 5, status 는 active 여야 한다.
  - 자기 항목의 share 는 한 번에 최대 +5%p 까지만 올릴 수 있다.
  - 자기 항목을 지우는 대신 status: left 로 바꾼다.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys

import yaml

FILE_VERSION = 1
FIRST_SHARE = 5
MAX_STEP = 5
DEFAULT_CAP = 50
STATUSES = ("active", "inactive", "left", "revoked")


class Report:
    def __init__(self, path: str):
        self.path = path
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def emit(self) -> None:
        gha = os.environ.get("GITHUB_ACTIONS") == "true"
        for msg in self.warnings:
            print(f"::warning file={self.path}::{msg}" if gha else f"경고: {msg}")
        for msg in self.errors:
            print(f"::error file={self.path}::{msg}" if gha else f"오류: {msg}")


def load(path: str, report: Report):
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        report.error(f"{path} 파일이 없습니다.")
        return None
    except yaml.YAMLError as e:
        report.error(f"YAML 문법 오류: {e}")
        return None
    if not isinstance(data, dict):
        report.error("최상위는 키-값 형식이어야 합니다 (version, policy, project, owner, contributors).")
        return None
    return data


def is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def valid_date(v) -> bool:
    if isinstance(v, dt.date):
        return True
    if isinstance(v, str):
        try:
            dt.date.fromisoformat(v)
            return True
        except ValueError:
            return False
    return False


def login(v) -> str:
    return str(v or "").strip().lower()


def check_shape(data: dict, report: Report) -> None:
    if data.get("version") != FILE_VERSION:
        report.error(f"version 은 {FILE_VERSION} 이어야 합니다.")
    if not isinstance(data.get("policy"), str) or not data["policy"].strip():
        report.error("policy 에 적용하는 수익 분배 규칙 버전(예: v1.0)을 적으세요.")

    project = data.get("project")
    if not isinstance(project, dict):
        report.error("project 항목이 없습니다.")
        project = {}
    if not isinstance(project.get("name"), str) or not project["name"].strip():
        report.error("project.name 에 게임 이름을 적으세요.")
    cap = project.get("contributor_cap", DEFAULT_CAP)
    if not is_number(cap) or not 0 < cap <= 100:
        report.error("project.contributor_cap 은 0보다 크고 100 이하인 숫자여야 합니다.")
    released = project.get("released")
    if released is not None and not valid_date(released):
        report.error("project.released 는 YYYY-MM-DD 형식이거나 비어 있어야 합니다.")

    owner = data.get("owner")
    if not isinstance(owner, dict) or not login(owner.get("github")):
        report.error("owner.github 에 오너의 GitHub 아이디를 적으세요.")

    people = data.get("contributors")
    if people is None:
        data["contributors"] = people = []
    if not isinstance(people, list):
        report.error("contributors 는 목록이어야 합니다 (없으면 []).")
        return

    owner_login = login(owner.get("github")) if isinstance(owner, dict) else ""
    seen: set[str] = set()
    total = 0.0
    for i, p in enumerate(people):
        where = f"contributors[{i}]"
        if not isinstance(p, dict):
            report.error(f"{where} 형식이 잘못됐습니다.")
            continue
        who = login(p.get("github"))
        if not who:
            report.error(f"{where}.github 가 비어 있습니다.")
        else:
            where = f"기여자 {p['github']}"
            if who in seen:
                report.error(f"{where} 가 두 번 들어 있습니다.")
            seen.add(who)
            if who == owner_login:
                report.error(f"{where}: 오너는 기여자 목록에 넣지 않습니다 (오너 몫은 나머지 전부).")
        if not isinstance(p.get("role"), str) or not p["role"].strip():
            report.error(f"{where}.role 에 기여 분야를 적으세요.")
        share = p.get("share")
        if not is_number(share) or not 0 <= share <= 100:
            report.error(f"{where}.share 는 0~100 사이 숫자여야 합니다.")
            share = 0
        elif round(share, 2) != share:
            report.error(f"{where}.share 는 소수점 둘째 자리까지만 씁니다.")
        status = p.get("status")
        if status not in STATUSES:
            report.error(f"{where}.status 는 {' | '.join(STATUSES)} 중 하나여야 합니다.")
        if status == "revoked" and share != 0:
            report.error(f"{where}: 박탈(revoked)된 기여자의 share 는 0 이어야 합니다.")
        if not valid_date(p.get("recognized_at")):
            report.error(f"{where}.recognized_at 은 YYYY-MM-DD 형식이어야 합니다.")
        if not isinstance(p.get("agreement"), str) or not p["agreement"].strip():
            report.error(f"{where}.agreement 에 동의한 기여자 약정 버전(예: v1.0)을 적으세요.")
        rid = p.get("roblox_user_id")
        if rid is not None and not (isinstance(rid, int) and not isinstance(rid, bool) and rid > 0):
            report.error(f"{where}.roblox_user_id 는 양의 정수이거나 비어 있어야 합니다.")
        history = p.get("history")
        if history is not None:
            if not isinstance(history, list) or not history:
                report.error(f"{where}.history 는 비어 있지 않은 목록이어야 합니다.")
            else:
                for h in history:
                    if not (isinstance(h, dict) and valid_date(h.get("date")) and is_number(h.get("share"))
                            and isinstance(h.get("reason"), str)):
                        report.error(f"{where}.history 항목은 {{ date, share, reason }} 형식이어야 합니다.")
                        break
                else:
                    if history[-1]["share"] != share:
                        report.error(f"{where}: history 마지막 share({history[-1]['share']})가 "
                                     f"현재 share({share})와 다릅니다. 변경 이력을 추가하세요.")
        total += share

    if is_number(cap) and total > cap + 1e-9:
        report.error(f"기여자 지분 합계 {total:g}% 가 상한 {cap:g}% 를 넘습니다.")


def section(data: dict, key: str) -> dict:
    v = data.get(key)
    return v if isinstance(v, dict) else {}


def by_login(people) -> dict:
    if not isinstance(people, list):
        return {}
    return {login(p.get("github")): p for p in people if isinstance(p, dict) and login(p.get("github"))}


def check_change(base: dict, head: dict, actor: str, report: Report) -> None:
    base_owner = login(section(base, "owner").get("github"))
    old, new = by_login(base.get("contributors")), by_login(head.get("contributors"))

    if actor == base_owner:
        for who, p in old.items():
            q = new.get(who)
            if q is None:
                report.warn(f"기여자 {p.get('github')} 항목이 지워졌습니다. 기록을 남기려면 지우지 말고 "
                            f"status 를 left/revoked 로 바꾸세요.")
            elif is_number(p.get("share")) and is_number(q.get("share")) and q["share"] < p["share"]:
                report.warn(f"기여자 {p.get('github')} 의 지분이 {p['share']:g}% → {q['share']:g}% 로 "
                            f"내려갑니다. 수익 분배 규칙 6장 절차(본인 동의 또는 소명 7일)를 거쳤는지 확인하세요.")
        return

    for key in ("version", "policy", "project", "owner"):
        if base.get(key) != head.get(key):
            report.error(f"{key} 는 오너만 바꿀 수 있습니다.")

    for who, p in old.items():
        if who == actor:
            continue
        if who not in new:
            report.error(f"다른 사람({p.get('github')})의 항목을 지울 수 없습니다.")
        elif new[who] != p:
            report.error(f"다른 사람({p.get('github')})의 항목을 바꿀 수 없습니다.")
    for who, q in new.items():
        if who != actor and who not in old:
            report.error(f"다른 사람({q.get('github')})을 대신 등록할 수 없습니다. 본인이 직접 PR을 보내야 합니다.")

    mine_old, mine_new = old.get(actor), new.get(actor)
    if mine_old is None and mine_new is not None:
        if mine_new.get("share") != FIRST_SHARE:
            report.error(f"첫 기여자 등록의 share 는 {FIRST_SHARE} 입니다 (수익 분배 규칙 3장).")
        if mine_new.get("status") != "active":
            report.error("첫 기여자 등록의 status 는 active 입니다.")
        if mine_new.get("agreement") != head.get("policy"):
            report.warn(f"agreement({mine_new.get('agreement')})가 이 레포의 policy({head.get('policy')})와 다릅니다.")
    elif mine_old is not None and mine_new is None:
        report.error("자기 항목을 지우지 말고 status 를 left 로 바꾸세요 (기록 보존).")
    elif mine_old is not None and mine_new is not None:
        a, b = mine_old.get("share"), mine_new.get("share")
        if is_number(a) and is_number(b) and b - a > MAX_STEP + 1e-9:
            report.error(f"지분은 한 번에 최대 +{MAX_STEP}%p 까지만 올릴 수 있습니다 ({a:g}% → {b:g}%).")
        if mine_new.get("status") != mine_old.get("status") and mine_new.get("status") != "left":
            report.error("본인이 바꿀 수 있는 status 는 left(자발적 이탈)뿐입니다.")
        if mine_new.get("recognized_at") != mine_old.get("recognized_at"):
            report.error("recognized_at(첫 인정일)은 바꿀 수 없습니다.")


def summary(data: dict) -> str:
    people = data.get("contributors") or []
    owner = section(data, "owner").get("github", "?")
    rows = []
    total = 0.0
    for p in people:
        if not isinstance(p, dict):
            continue
        share = p.get("share") if is_number(p.get("share")) else 0
        total += share
        rows.append(f"| @{p.get('github')} | {p.get('role', '')} | {share:g}% | {p.get('status', '')} |")
    lines = [
        f"### {section(data, 'project').get('name', '')} 수익 지분",
        "",
        "| 사람 | 역할 | 지분 | 상태 |",
        "|---|---|---:|---|",
        f"| @{owner} | 오너 | {100 - total:g}% | owner |",
        *rows,
        "",
        f"기여자 합계 {total:g}% · 상한 {section(data, 'project').get('contributor_cap', DEFAULT_CAP)}%",
    ]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default="CONTRIBUTORS.yml")
    ap.add_argument("--base", help="PR 이전(base 브랜치) 버전의 파일 경로")
    ap.add_argument("--actor", default="", help="PR 작성자 GitHub 아이디")
    args = ap.parse_args(argv)

    report = Report(args.file)
    head = load(args.file, report)
    if head is not None:
        check_shape(head, report)
        if args.base:
            base_report = Report(args.base)
            base = load(args.base, base_report)
            if base is not None:
                check_change(base, head, login(args.actor), report)
        elif args.actor and login(args.actor) != login(section(head, "owner").get("github")):
            report.warn("오너가 아닌 사람이 이 파일을 처음 만들었습니다. 오너가 확인하세요.")

    report.emit()
    if head is not None and not report.errors:
        text = summary(head)
        print(text)
        out = os.environ.get("GITHUB_STEP_SUMMARY")
        if out:
            with open(out, "a", encoding="utf-8") as f:
                f.write(text)
    if report.errors:
        print(f"\n{len(report.errors)}개 오류 — 위 내용을 고친 뒤 다시 푸시하세요.")
        return 1
    print("기여자 설정 검사 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
