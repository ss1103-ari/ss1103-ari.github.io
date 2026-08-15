#!/usr/bin/env python3
"""抓取 AI Builder 的 GitHub 公开动态，产出 data/builders.json 与每日快照。"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
HISTORY = os.path.join(DATA, "history")
CST = timezone(timedelta(hours=8))

BUILDERS = [
    {
        "login": "zarazhangrui",
        "cn": "张咋啦",
        "en": "Zara Zhang",
        "role": "AI 产品经理 @ 湾区 · 前飞书产品营销负责人",
        "why": "参考项目的主角：她的 skill / slides 系列是「AI 产品化」最快的样本",
        "links": [
            {"label": "𝕏 @zarazhangrui", "url": "https://x.com/zarazhangrui"},
            {"label": "小红书", "url": "https://www.xiaohongshu.com/user/profile/260679956"},
        ],
        "accent": "pink",
    },
    {
        "login": "simonw",
        "cn": "Simon Willison",
        "en": "Simon Willison",
        "role": "Datasette 作者 · LLM 工具链布道者",
        "why": "把每个 LLM 新能力都做成能跑的小工具，产出节奏极稳",
        "links": [{"label": "博客", "url": "https://simonwillison.net/"}],
        "accent": "olive",
    },
    {
        "login": "karpathy",
        "cn": "Andrej Karpathy",
        "en": "Andrej Karpathy",
        "role": "前特斯拉 AI 总监 · nanoGPT / llm.c",
        "why": "看他 push 什么，基本等于看未来半年的教学范式",
        "links": [{"label": "𝕏 @karpathy", "url": "https://x.com/karpathy"}],
        "accent": "apricot",
    },
    {
        "login": "mckaywrigley",
        "cn": "Mckay Wrigley",
        "en": "Mckay Wrigley",
        "role": "Chatbot UI 作者 · AI 应用层连续创作者",
        "why": "应用层交互范式的高频试验田",
        "links": [{"label": "𝕏 @mckaywrigley", "url": "https://x.com/mckaywrigley"}],
        "accent": "sky",
    },
    {
        "login": "transitive-bullshit",
        "cn": "Travis Fischer",
        "en": "Travis Fischer",
        "role": "Agentic 工具作者 · agentic / xsai",
        "why": "Agent 工具生态里最勤的独立开发者之一",
        "links": [{"label": "𝕏 @transitive_bs", "url": "https://x.com/transitive_bs"}],
        "accent": "lilac",
    },
    {
        "login": "steven-tey",
        "cn": "Steven Tey",
        "en": "Steven Tey",
        "role": "Dub.co 创始人 · 前 Vercel",
        "why": "开源产品的「上线即营销」教科书",
        "links": [{"label": "𝕏 @steventey", "url": "https://x.com/steventey"}],
        "accent": "olive",
    },
]

EVENT_LABEL = {
    "PushEvent": "推送提交",
    "CreateEvent": "新建仓库/分支",
    "ReleaseEvent": "发布版本",
    "PublicEvent": "仓库转公开",
    "WatchEvent": "star 了仓库",
    "ForkEvent": "fork 了仓库",
    "IssuesEvent": "处理 issue",
    "PullRequestEvent": "处理 PR",
    "IssueCommentEvent": "参与讨论",
}


def api(path, token=None, retries=3):
    url = "https://api.github.com" + path
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "builder-radar (github.com/ss1103-ari)",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    for i in range(retries):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and i < retries - 1:
                time.sleep(8 * (i + 1))
                continue
            print("  ! HTTP %s on %s" % (e.code, path), file=sys.stderr)
            return None
        except Exception as e:  # noqa: BLE001
            print("  ! %s on %s" % (e, path), file=sys.stderr)
            if i < retries - 1:
                time.sleep(4)
                continue
            return None
    return None


def load_prev():
    p = os.path.join(DATA, "builders.json")
    if not os.path.exists(p):
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            old = json.load(f)
        return {b["login"]: b for b in old.get("builders", [])}
    except Exception:  # noqa: BLE001
        return {}


def collect(cfg, token):
    user = api("/users/%s" % cfg["login"], token)
    repos = api("/users/%s/repos?per_page=100&sort=pushed" % cfg["login"], token) or []
    events = api("/users/%s/events/public?per_page=60" % cfg["login"], token) or []

    repos = [r for r in repos if not r.get("fork")]
    repos.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)
    top = [
        {
            "name": r["name"],
            "url": r["html_url"],
            "desc": (r.get("description") or "").strip(),
            "stars": r.get("stargazers_count", 0),
            "lang": r.get("language"),
            "pushed_at": r.get("pushed_at"),
        }
        for r in repos[:6]
    ]
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)

    feed = []
    for e in events[:40]:
        etype = e.get("type")
        if etype in ("WatchEvent", "IssueCommentEvent"):
            continue
        item = {
            "type": etype,
            "label": EVENT_LABEL.get(etype, etype),
            "repo": (e.get("repo") or {}).get("name", ""),
            "at": e.get("created_at"),
            "detail": "",
        }
        payload = e.get("payload") or {}
        if etype == "PushEvent":
            commits = payload.get("commits") or []
            if commits:
                item["detail"] = commits[-1].get("message", "").split("\n")[0][:110]
            item["count"] = payload.get("size", len(commits))
        elif etype == "ReleaseEvent":
            item["detail"] = (payload.get("release") or {}).get("tag_name", "")
        elif etype == "CreateEvent":
            item["detail"] = "%s %s" % (payload.get("ref_type", ""), payload.get("ref") or "")
        elif etype == "PullRequestEvent":
            pr = payload.get("pull_request") or {}
            item["detail"] = "%s · %s" % (payload.get("action", ""), (pr.get("title") or "")[:90])
        elif etype == "IssuesEvent":
            issue = payload.get("issue") or {}
            item["detail"] = "%s · %s" % (payload.get("action", ""), (issue.get("title") or "")[:90])
        feed.append(item)
        if len(feed) >= 12:
            break

    out = dict(cfg)
    out.update(
        {
            "name": (user or {}).get("name") or cfg["en"],
            "avatar": (user or {}).get("avatar_url", ""),
            "bio": ((user or {}).get("bio") or "").strip(),
            "followers": (user or {}).get("followers", 0),
            "public_repos": (user or {}).get("public_repos", 0),
            "total_stars": total_stars,
            "repo_count": len(repos),
            "top_repos": top,
            "feed": feed,
            "ok": user is not None,
        }
    )
    return out


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    prev = load_prev()
    now = datetime.now(timezone.utc)
    builders = []
    for cfg in BUILDERS:
        print("→ %s" % cfg["login"])
        b = collect(cfg, token)
        old = prev.get(cfg["login"])
        if old and old.get("ok") and b["ok"]:
            b["delta_stars"] = b["total_stars"] - old.get("total_stars", b["total_stars"])
            b["delta_followers"] = b["followers"] - old.get("followers", b["followers"])
        else:
            b["delta_stars"] = 0
            b["delta_followers"] = 0
        if not b["ok"] and old:
            old["stale"] = True
            builders.append(old)
        else:
            builders.append(b)

    latest = ""
    for b in builders:
        for f in b.get("feed", []):
            if f.get("at") and f["at"] > latest:
                latest = f["at"]

    payload = {
        "generated_at": now.isoformat(),
        "generated_at_cst": now.astimezone(CST).strftime("%Y-%m-%d %H:%M CST"),
        "latest_activity_at": latest,
        "source": "GitHub REST API v3 (public)",
        "builders": builders,
        "totals": {
            "builders": len(builders),
            "stars": sum(b.get("total_stars", 0) for b in builders),
            "events": sum(len(b.get("feed", [])) for b in builders),
        },
    }

    os.makedirs(HISTORY, exist_ok=True)
    with open(os.path.join(DATA, "builders.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    snap = {
        "date": now.astimezone(CST).strftime("%Y-%m-%d"),
        "at": payload["generated_at"],
        "stars": {b["login"]: b.get("total_stars", 0) for b in builders},
        "followers": {b["login"]: b.get("followers", 0) for b in builders},
    }
    with open(os.path.join(HISTORY, snap["date"] + ".json"), "w", encoding="utf-8") as f:
        json.dump(snap, f, ensure_ascii=False, indent=1)

    print("done: %s builders, %s stars" % (payload["totals"]["builders"], payload["totals"]["stars"]))


if __name__ == "__main__":
    main()
