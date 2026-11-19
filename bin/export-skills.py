#!/usr/bin/env python3
"""公開するスキルを、marketplace の repo（ukwhatn/skills）の作業ツリーに書き出す。

使い方: export-skills.py <公開 repo の作業ツリー> [--no-validate]

- 原本は ~/.claude のまま。publish/skills/manifest.json に載せたスキル・context と、
  publish/skills/ の公開専用のファイル（marketplace.json・plugin.json・hooks.json・dev-flow・README など）を写す。
  スキルは git で追跡しているファイルだけを写す（.pyc などの生成物を入れないため）
- vendor（vendor/manifest.json の外部スキル）は無改変で写す
- Markdown には次を当てる。これ以外の書き換えはしない
  - `<!-- publish:omit -->` 〜 `<!-- /publish:omit -->` を削除し、`<!-- publish:only` 〜 `-->` を本文にする
  - context の参照、`AGENTS.md「X」`（dev-flow の同じ見出しへ）、公開するスキルの `/名前`（名前空間付きへ）
- 書き出し先で、書き出すファイルに無いものは削除する（.git を除く）
- 写した後に残った作者の環境への参照を全件出し、1 件でもあれば exit 1。manifest の optional の外部スキル
  （同梱せず、原本の側で「入っていれば使う」と書いたもの）への呼び出しは数えない
- plugin ごとに、HEAD と比べて plugin.json 以外が変わっていれば version の patch を上げる

exit: 0 = 書き出しと検査が通った / 1 = 残りの参照・dev-flow の見出し・validate の失敗
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLISH = ROOT / "publish" / "skills"
NAMESPACE = "ukwhatn-skills"
SKILLS_PLUGIN = Path("plugins") / NAMESPACE
GUARDS_PLUGIN = Path("plugins") / "ukwhatn-guards"
FIRST_VERSION = "0.1.0"

# 行に印だけを置いた形（行ごと削除）と、行の途中に置いた形（その部分だけ削除）。行の形を先に当てる
OMIT_LINES = re.compile(r"^[ \t]*<!-- publish:omit -->[ \t]*\n.*?^[ \t]*<!-- /publish:omit -->[ \t]*\n", re.S | re.M)
OMIT_INLINE = re.compile(r"<!-- publish:omit -->.*?<!-- /publish:omit -->", re.S)
# 開始の印の行の残り（「公開版だけの文」の注記）は書き出さない
ONLY = re.compile(r"<!-- publish:only[^\n]*\n(.*?)\n-->", re.S)
AGENTS_SECTION = re.compile(r"AGENTS\.md「([^」]+)」")
CONTEXT_REF = re.compile(r"(?:~/\.claude/|@)?context/([a-z0-9-]+)\.md")
# 作者の環境にしか無いものへの参照。書き出した Markdown に残っていたら失敗にする
LEFTOVER = [
    (re.compile(r"(?<!/)(?:AGENTS\.md|CLAUDE\.local\.md)"), "AGENTS.md の参照"),  # URL の中の AGENTS.md は他の repo のもの
    (re.compile(r"~/\.claude|\$HOME/\.claude|CLAUDE_CONFIG_DIR"), "~/.claude のパス"),
    (re.compile(r"(?i)herdr|codex-usage|taskboard"), "作者の環境の道具"),
    (re.compile(r"dangerously-bypass"), "sandbox を外すフラグ"),
    (re.compile(r"publish:"), "publish の印の残り"),
]


@dataclass(frozen=True)
class Entry:
    src: Path
    kind: str  # raw | skill | ref | context | style | doc | plugin


def git_tracked(path: Path) -> list[Path]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z", "--", str(path.relative_to(ROOT))],
                         check=True, capture_output=True, text=True).stdout
    return [ROOT / p for p in out.split("\0") if p]


def markdown_kind(path: Path) -> str:
    return "skill" if path.name == "SKILL.md" else "ref"


def plan(manifest: dict) -> dict[Path, Entry]:
    files: dict[Path, Entry] = {}
    for skill in manifest["skills"]:
        for src in git_tracked(ROOT / "skills" / skill):
            kind = markdown_kind(src) if src.suffix == ".md" else "raw"
            files[SKILLS_PLUGIN / src.relative_to(ROOT)] = Entry(src, kind)
    vendor = json.loads((ROOT / "vendor" / "manifest.json").read_text())
    for item in vendor["skills"]:
        if item["name"] in manifest["vendor"]:
            for f in item["files"]:
                files[SKILLS_PLUGIN / f["local"]] = Entry(ROOT / f["local"], "raw")
    for name in manifest["context"]:
        files[SKILLS_PLUGIN / "context" / name] = Entry(ROOT / "context" / name, "context")
    for dst, src, kind in manifest["files"]:
        files[Path(dst)] = Entry(ROOT / src, kind)
    missing = [str(e.src) for e in files.values() if not e.src.is_file()]
    if missing:
        sys.exit("原本が無い: " + ", ".join(missing))
    return files


def context_ref(name: str, kind: str) -> str:
    if kind == "skill":
        return f"${{CLAUDE_PLUGIN_ROOT}}/context/{name}.md"
    if kind == "context":
        return f"{name}.md（このファイルと同じフォルダ）"
    return f"context/{name}.md（plugin のフォルダの直下）"


def transform(text: str, kind: str, published: dict) -> tuple[str, list[str], list[str]]:
    """変換した本文、参照した dev-flow の節、印の問題を返す。"""
    # HTML のコメントを閉じるのは `-->`（と `--!>`）だけ。中に書くと原本の表示で残りがコメントの外に出る
    problems = [f"publish:only の中にコメントの終わりがある: {m.group(1)[:40]!r}"
                for m in ONLY.finditer(text) if "--!>" in m.group(1) or "-->" in m.group(1)]
    text = OMIT_INLINE.sub("", OMIT_LINES.sub("", text))
    # 行の途中から始まる印は、本文を次の行に置く（印の後の改行の分）
    text = ONLY.sub(lambda m: m.group(1) if m.start() == 0 or text[m.start() - 1] == "\n" else "\n" + m.group(1), text)
    sections = AGENTS_SECTION.findall(text)
    text = AGENTS_SECTION.sub(lambda m: f"`/{NAMESPACE}:dev-flow` の「{m.group(1)}」", text)
    text = CONTEXT_REF.sub(
        lambda m: context_ref(m.group(1), kind) if m.group(1) + ".md" in published["context"] else m.group(0), text)
    skill_ref = re.compile(r"(?<![\w/.:-])/(" + "|".join(map(re.escape, published["skills"])) + r")(?![\w-])")
    text = skill_ref.sub(lambda m: f"/{NAMESPACE}:{m.group(1)}", text)
    return text, sections, problems


def leftovers(text: str, published: dict, unpublished_skills: list[str]) -> list[str]:
    found = []
    for pattern, label in LEFTOVER:
        found += [f"{label}: {m.group(0)}" for m in pattern.finditer(text)]
    for m in CONTEXT_REF.finditer(text):
        if m.group(1) + ".md" not in published["context"]:
            found.append(f"同梱しない context: {m.group(0)}")
    other = re.compile(r"(?<![\w/.:-])/(" + "|".join(map(re.escape, unpublished_skills)) + r")(?![\w/-])")
    found += [f"同梱しないスキル: {m.group(0)}" for m in other.finditer(text)]
    return found


def git(dst: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(dst), *args], capture_output=True, text=True)


def head_version(dst: Path, path: Path) -> str | None:
    shown = git(dst, "show", f"HEAD:{path.as_posix()}")
    return json.loads(shown.stdout).get("version") if shown.returncode == 0 else None


def bump(version: str) -> str:
    major, minor, patch = (int(x) for x in version.split("."))
    return f"{major}.{minor}.{patch + 1}"


def changed_besides_manifest(dst: Path, plugin: Path) -> bool:
    status = git(dst, "status", "--porcelain", "--untracked-files=all", "--", plugin.as_posix()).stdout
    manifest = (plugin / ".claude-plugin" / "plugin.json").as_posix()
    return any(line[3:].strip() != manifest for line in status.splitlines())


def write_if_changed(path: Path, data: bytes, mode: int = 0o644) -> None:
    if not (path.exists() and path.read_bytes() == data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    path.chmod(mode)


def remove_unlisted(dst: Path, keep: set[Path]) -> list[Path]:
    removed = []
    for path in sorted(dst.rglob("*"), reverse=True):
        rel = path.relative_to(dst)
        if rel.parts[0] == ".git":
            continue
        if path.is_file() and rel not in keep:
            path.unlink()
            removed.append(rel)
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    return removed


def write_plugin_manifests(dst: Path, files: dict[Path, Entry]) -> None:
    """plugin.json の version を、HEAD の版のまま（変わっていなければ）か patch を上げた版にして書く。"""
    for rel, entry in files.items():
        if entry.kind != "plugin":
            continue
        plugin = rel.parent.parent
        version = head_version(dst, rel)
        version = FIRST_VERSION if version is None else bump(version) if changed_besides_manifest(dst, plugin) else version
        data = json.loads(entry.src.read_text())
        data["version"] = version
        write_if_changed(dst / rel, (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode())


def check_dev_flow(dst: Path, sections: set[str]) -> list[str]:
    dev_flow = (dst / SKILLS_PLUGIN / "skills" / "dev-flow" / "SKILL.md").read_text()
    headings = {line.lstrip("#").strip() for line in dev_flow.splitlines() if line.startswith("#")}
    return [f"dev-flow に節が無い: 「{s}」" for s in sorted(sections)
            if not any(s in h for h in headings) and f"**{s}" not in dev_flow]


def validate(dst: Path) -> list[str]:
    targets = [dst, dst / SKILLS_PLUGIN, dst / GUARDS_PLUGIN]
    problems = []
    for target in targets:
        result = subprocess.run(["claude", "plugin", "validate", "--strict", str(target)], capture_output=True, text=True)
        if result.returncode != 0:
            problems.append(f"validate が失敗: {target.relative_to(dst) or '.'}\n{result.stdout}{result.stderr}")
    return problems


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    dst = Path(sys.argv[1]).expanduser().resolve()
    if not (dst / ".git").exists():
        sys.exit(f"{dst} は git の作業ツリーでない")
    manifest = json.loads((PUBLISH / "manifest.json").read_text())
    published = {"skills": manifest["skills"] + manifest["vendor"] + ["dev-flow"], "context": manifest["context"]}
    unpublished = sorted(p.name for p in (ROOT / "skills").iterdir()
                         if p.is_dir() and p.name not in published["skills"] + manifest["optional"] and p.name != "synced")
    files = plan(manifest)

    problems: list[str] = []
    sections: set[str] = set()
    for rel, entry in files.items():
        if entry.kind == "plugin":
            continue
        data = entry.src.read_bytes()
        if entry.kind not in ("raw",):
            text, used, marker_problems = transform(data.decode(), entry.kind, published)
            sections.update(used)
            problems += [f"{rel}: {p}" for p in marker_problems + leftovers(text, published, unpublished)]
            data = text.encode()
        write_if_changed(dst / rel, data, entry.src.stat().st_mode & 0o777)
    removed = remove_unlisted(dst, set(files))
    write_plugin_manifests(dst, files)
    problems += check_dev_flow(dst, sections)
    if "--no-validate" not in sys.argv:
        problems += validate(dst)

    print(f"書き出し: {len(files)} ファイル、削除: {len(removed)} ファイル")
    for rel in removed:
        print(f"  削除 {rel}")
    for problem in problems:
        print(problem)
    print(f"問題: {len(problems)} 件")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
