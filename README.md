# ss1103-ari.github.io · 冯本爽个人作品集

杂志编辑风的个人作品集站点，纯静态 + GitHub Actions，托管在 GitHub Pages。

## 目录结构

```
.
├── index.html                     # 作品集首页（个人介绍 + 4 件作品）
├── assets/
│   ├── style.css                  # 共用视觉（奶油底 + 衬线大字 + 彩色卡片）
│   └── shots/*.png                # 作品预览图
├── works/
│   ├── lunch/index.html           # 作品 01 按时吃饭 Skill（含交互 Demo）
│   ├── radar/index.html           # 作品 02 AI Builder 捕捉器（读 data/builders.json）
│   └── rice/index.html            # 作品 03 优先级罗盘（纯前端工具）
├── data/
│   ├── builders.json              # 雷达最新数据（由 Actions 自动更新）
│   └── history/YYYY-MM-DD.json    # 每日快照，用于算 Δ Stars
├── scripts/
│   ├── fetch_builders.py          # 抓取 GitHub 公开动态
│   └── shoot.py                   # 用 Playwright 重新生成作品预览图（可选）
└── .github/workflows/update-radar.yml   # 每 3 小时自动抓数并提交
```

## 上线步骤

```bash
# 1. 在 GitHub 新建仓库：ss1103-ari.github.io（Public，不要初始化 README）
# 2. 推送本目录
git remote add origin https://github.com/ss1103-ari/ss1103-ari.github.io.git
git branch -M main
git push -u origin main
```

3. 仓库 **Settings → Pages**：Source 选 `Deploy from a branch`，分支 `main`，目录 `/ (root)`，保存。
   1–2 分钟后访问 <https://ss1103-ari.github.io/>。
4. 仓库 **Settings → Actions → General → Workflow permissions**：勾选 `Read and write permissions`（Actions 需要把新数据提交回仓库）。
5. 仓库 **Actions** 页签 → 选中「更新 AI Builder 捕捉器数据」→ `Run workflow` 手动跑一次，验证数据能自动更新。之后每 3 小时自动执行。

## 本地预览

```bash
python3 -m http.server 8765     # 然后打开 http://127.0.0.1:8765/
```

> 注意：作品 02 需要 fetch 本地 JSON，直接双击打开 HTML 会被浏览器拦截，请用上面的本地服务器或线上地址访问。

## 手动更新雷达数据

```bash
python3 scripts/fetch_builders.py          # 无 token 时走匿名额度（60 次/小时）
GITHUB_TOKEN=xxx python3 scripts/fetch_builders.py   # 有 token 更稳
```

想加/换监测对象：编辑 `scripts/fetch_builders.py` 顶部的 `BUILDERS` 数组即可，前端无需改动。
