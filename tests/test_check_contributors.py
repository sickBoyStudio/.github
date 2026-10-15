"""check_contributors.py 테스트 — python3 -m unittest discover -s tests"""
import contextlib
import io
import os
import sys
import tempfile
import textwrap
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import check_contributors as cc  # noqa: E402

BASE = """
version: 1
policy: v1.0
project:
  name: TEST
  contributor_cap: 50
owner:
  github: owner-dev
contributors:
  - github: alice
    role: 맵
    share: 5
    status: active
    recognized_at: 2026-09-01
    agreement: v1.0
    history:
      - { date: 2026-09-01, share: 5, reason: 첫 기여자 인정 }
"""

BOB = """
  - github: bob
    role: 사운드
    share: {share}
    status: active
    recognized_at: 2026-10-15
    agreement: v1.0
    history:
      - {{ date: 2026-10-15, share: {share}, reason: 첫 기여자 인정 }}
"""


def run(head: str, base: str | None = None, actor: str = ""):
    with tempfile.TemporaryDirectory() as d:
        hp = os.path.join(d, "head.yml")
        with open(hp, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(head))
        args = ["--file", hp, "--actor", actor]
        if base is not None:
            bp = os.path.join(d, "base.yml")
            with open(bp, "w", encoding="utf-8") as f:
                f.write(textwrap.dedent(base))
            args += ["--base", bp]
        out = io.StringIO()
        env = os.environ.pop("GITHUB_ACTIONS", None), os.environ.pop("GITHUB_STEP_SUMMARY", None)
        try:
            with contextlib.redirect_stdout(out):
                code = cc.main(args)
        finally:
            if env[0] is not None:
                os.environ["GITHUB_ACTIONS"] = env[0]
            if env[1] is not None:
                os.environ["GITHUB_STEP_SUMMARY"] = env[1]
        return code, out.getvalue()


class Shape(unittest.TestCase):
    def test_template_with_owner_passes(self):
        with open(os.path.join(ROOT, "templates", "CONTRIBUTORS.yml"), encoding="utf-8") as f:
            code, out = run(f.read())
        self.assertEqual(code, 0, out)

    def test_base_passes_and_reports_owner_share(self):
        code, out = run(BASE)
        self.assertEqual(code, 0, out)
        self.assertIn("| @owner-dev | 오너 | 95% |", out)

    def test_over_cap_fails(self):
        head = BASE.replace("contributor_cap: 50", "contributor_cap: 8") + BOB.format(share=5)
        code, out = run(head)
        self.assertEqual(code, 1)
        self.assertIn("상한", out)

    def test_revoked_needs_zero_share(self):
        code, out = run(BASE.replace("status: active", "status: revoked"))
        self.assertEqual(code, 1)
        self.assertIn("revoked", out)

    def test_history_must_match_share(self):
        code, out = run(BASE.replace("    share: 5\n", "    share: 7.5\n"))
        self.assertEqual(code, 1)
        self.assertIn("history", out)

    def test_owner_not_listed_as_contributor(self):
        code, out = run(BASE.replace("github: alice", "github: Owner-Dev"))
        self.assertEqual(code, 1)


class Change(unittest.TestCase):
    def test_first_registration_at_five_passes(self):
        code, out = run(BASE + BOB.format(share=5), BASE, "bob")
        self.assertEqual(code, 0, out)

    def test_first_registration_above_five_fails(self):
        code, out = run(BASE + BOB.format(share=10), BASE, "bob")
        self.assertEqual(code, 1)
        self.assertIn("첫 기여자 등록", out)

    def test_cannot_register_someone_else(self):
        code, out = run(BASE + BOB.format(share=5), BASE, "carol")
        self.assertEqual(code, 1)
        self.assertIn("대신 등록", out)

    def test_cannot_touch_other_entry(self):
        head = BASE.replace("role: 맵", "role: 맵 전체") + BOB.format(share=5)
        code, out = run(head, BASE, "bob")
        self.assertEqual(code, 1)
        self.assertIn("alice", out)

    def test_cannot_change_owner(self):
        code, out = run(BASE.replace("github: owner-dev", "github: alice2"), BASE, "alice")
        self.assertEqual(code, 1)

    def test_step_up_by_five_passes(self):
        head = BASE.replace("    share: 5\n", "    share: 10\n").replace(
            "reason: 첫 기여자 인정 }", "reason: 첫 기여자 인정 }\n      - { date: 2026-12-01, share: 10, reason: 핵심 기여 }")
        code, out = run(head, BASE, "alice")
        self.assertEqual(code, 0, out)

    def test_step_up_above_five_fails(self):
        head = BASE.replace("    share: 5\n", "    share: 12.5\n").replace(
            "reason: 첫 기여자 인정 }", "reason: 첫 기여자 인정 }\n      - { date: 2026-12-01, share: 12.5, reason: 핵심 기여 }")
        code, out = run(head, BASE, "alice")
        self.assertEqual(code, 1)
        self.assertIn("+5%p", out)

    def test_self_leave_passes_but_delete_fails(self):
        code, out = run(BASE.replace("status: active", "status: left"), BASE, "alice")
        self.assertEqual(code, 0, out)
        head = BASE.split("contributors:")[0] + "contributors: []\n"
        code, out = run(head, BASE, "alice")
        self.assertEqual(code, 1)

    def test_owner_lowering_share_warns(self):
        head = BASE.replace("    share: 5\n", "    share: 2.5\n").replace(
            "reason: 첫 기여자 인정 }", "reason: 첫 기여자 인정 }\n      - { date: 2026-12-01, share: 2.5, reason: 출시 전 이탈 }")
        code, out = run(head, BASE, "owner-dev")
        self.assertEqual(code, 0, out)
        self.assertIn("내려갑니다", out)


class Integrity(unittest.TestCase):
    def test_invalid_base_fails_closed(self):
        for base in ("invalid: [", "[]", "owner: {}"):
            with self.subTest(base=base):
                code, out = run(BASE, base, "owner-dev")
                self.assertEqual(code, 1, out)
                self.assertIn("기준 파일", out)

    def test_missing_base_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            head = os.path.join(d, "head.yml")
            with open(head, "w") as f:
                f.write(BASE)
            with contextlib.redirect_stdout(io.StringIO()):
                code = cc.main(["--file", head, "--base", os.path.join(d, "missing.yml"), "--actor", "owner-dev"])
            self.assertEqual(code, 1)

    def test_duplicate_keys_rejected(self):
        code, out = run(BASE.replace("    share: 5", "    share: 10\n    share: 5"))
        self.assertEqual(code, 1, out)
        self.assertIn("중복 키", out)

    def test_nonfinite_numbers_rejected(self):
        for value in (".nan", ".inf", "-.inf"):
            with self.subTest(value=value):
                code, out = run(BASE.replace("    share: 5", "    share: " + value))
                self.assertEqual(code, 1, out)

    def test_missing_actor_rejected(self):
        code, out = run(BASE, BASE)
        self.assertEqual(code, 1, out)
        self.assertIn("--actor", out)

    def test_owner_cannot_delete_contributor(self):
        head = BASE.split("contributors:")[0] + "contributors: []\n"
        code, out = run(head, BASE, "owner-dev")
        self.assertEqual(code, 1, out)

    def test_history_cannot_be_rewritten_by_either_party(self):
        for actor in ("owner-dev", "alice"):
            with self.subTest(actor=actor):
                code, out = run(BASE.replace("첫 기여자 인정", "다른 이유"), BASE, actor)
                self.assertEqual(code, 1, out)
                self.assertIn("history", out)

    def test_share_change_requires_new_history(self):
        no_history = BASE.split("    history:")[0]
        code, out = run(no_history.replace("share: 5", "share: 10"), no_history, "owner-dev")
        self.assertEqual(code, 1, out)
        self.assertIn("history 추가", out)


if __name__ == "__main__":
    unittest.main()
