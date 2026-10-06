#!/usr/bin/env python3
"""取り込んだ外部 skill が上流から古くなっていないか、手元の複製が崩れていないかを調べる。

台帳 vendor/manifest.json の各項目について次を比べ、Markdown の報告を stdout に出す。
- 固定した commit と上流ブランチ先頭とで、取り込んだファイルの内容（blob）が変わったか
- watch_dirs の下に、固定 commit の時点には無かったファイルが上流で増えたか
- 手元のファイルが固定 commit の内容と一致するか（patched のファイルは除く）

exit: 0 = 差分なし / 1 = 上流の更新か手元の崩れあり / 2 = 取得の失敗
GitHub API は gh CLI 経由で呼ぶ（認証は gh の設定か GH_TOKEN）。
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "vendor" / "manifest.json"


def gh_api(path: str):
    out = subprocess.run(
        ["gh", "api", path], check=True, capture_output=True, text=True
    ).stdout
    return json.loads(out)


def blobs_at(repo: str, ref: str) -> tuple[str, dict[str, str]]:
    """ref の commit SHA と、リポジトリ全体の path -> blob SHA を返す。"""
    commit = gh_api(f"repos/{repo}/commits/{ref}")
    tree = gh_api(f"repos/{repo}/git/trees/{commit['commit']['tree']['sha']}?recursive=1")
    # truncated のまま比べると、取得できなかったファイルが「削除」「追加」に見える
    if tree.get("truncated"):
        raise RuntimeError(f"{repo}@{ref} の tree が大きすぎて一括取得できない")
    return commit["sha"], {e["path"]: e["sha"] for e in tree["tree"] if e["type"] == "blob"}


def local_blob(path: Path) -> str | None:
    if not path.exists():
        return None
    return subprocess.run(
        ["git", "hash-object", str(path)], check=True, capture_output=True, text=True
    ).stdout.strip()


def under(path: str, dirs: list[str]) -> bool:
    return any(path == d or path.startswith(d.rstrip("/") + "/") for d in dirs)


def check(entry: dict) -> list[str]:
    repo, pinned = entry["repo"], entry["commit"]
    _, old = blobs_at(repo, pinned)
    head_sha, new = blobs_at(repo, entry["branch"])

    tracked = {f["upstream"] for f in entry["files"]}
    changed = [f for f in sorted(tracked) if old.get(f) != new.get(f) and f in new]
    removed = [f for f in sorted(tracked) if f not in new]
    watch = entry.get("watch_dirs", [])
    added = sorted(p for p in new if under(p, watch) and p not in old)

    drift = []
    for f in entry["files"]:
        if f.get("patched"):
            continue
        if local_blob(ROOT / f["local"]) != old.get(f["upstream"]):
            drift.append(f["local"])

    if not (changed or removed or added or drift):
        return []
    lines = [
        f"## {entry['name']}（{repo}）",
        "",
        f"- 固定: `{pinned[:7]}` / 上流 {entry['branch']}: `{head_sha[:7]}`",
    ]
    for label, items in [
        ("内容が変わった", changed),
        ("上流で消えた", removed),
        ("上流で増えた（取り込み元ディレクトリ）", added),
        ("手元の複製が固定 commit と一致しない", drift),
    ]:
        if items:
            lines.append(f"- {label}: " + ", ".join(f"`{p}`" for p in items))
    if changed or removed or added:
        lines.append(f"- 差分: https://github.com/{repo}/compare/{pinned[:12]}...{head_sha[:12]}")
    if entry.get("patch"):
        lines.append(f"- 取り込み時の改変: `{entry['patch']}` を再適用する")
    return lines + [""]


def main() -> int:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["skills"]
    report: list[str] = []
    try:
        for entry in entries:
            report += check(entry)
    except (subprocess.CalledProcessError, RuntimeError) as e:
        detail = e.stderr if isinstance(e, subprocess.CalledProcessError) else str(e)
        print(f"取得に失敗した: {detail}", file=sys.stderr)
        return 2
    if not report:
        print("取り込んだ外部 skill はすべて固定 commit のまま最新。")
        return 0
    print("取り込んだ外部 skill の上流に更新がある、または手元の複製が崩れている。")
    print("更新の手順は NOTICE.md の各項目を参照。\n")
    print("\n".join(report))
    return 1


if __name__ == "__main__":
    sys.exit(main())
