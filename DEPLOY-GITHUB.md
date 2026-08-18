# 部署到 GitHub Pages（ss1103-ari.github.io）

整个作品集（首页 + 3 个作品子页面）是一个纯静态站点，**一个仓库就能全部上线**，子页面会自动变成子路径：

| 页面 | 上线后地址 |
| --- | --- |
| 首页 | https://ss1103-ari.github.io/ |
| 01 工作再忙也要按时吃饭 | https://ss1103-ari.github.io/works/lunch/ |
| 02 AI Builder 捕捉器 | https://ss1103-ari.github.io/works/radar/ |
| 03 优先级罗盘 | https://ss1103-ari.github.io/works/rice/ |
| Skill 下载包 | https://ss1103-ari.github.io/assets/downloads/lunch-radar-skill.zip |

## 步骤

### 1. 建仓库
在 GitHub 新建仓库，名字必须是 `ss1103-ari.github.io`，选 **Public**，不要勾选 README/.gitignore。

### 2. 生成 Token
https://github.com/settings/tokens → Generate new token (classic) → 勾选 **repo** 和 **workflow** → 复制 `ghp_...`。

### 3. 推送
在本目录下执行：

```bash
GH_TOKEN=ghp_你的token ./push-to-github.sh
```

### 4. 打开 Pages
仓库 → Settings → Pages → Source 选 **Deploy from a branch** → 分支 `main`、目录 `/ (root)` → Save。约 1 分钟后访问 https://ss1103-ari.github.io/ 。

### 5. 让 02 的数据自动更新（可选）
仓库 → Settings → Actions → General → Workflow permissions 选 **Read and write permissions** → Save。
之后 `.github/workflows/update-radar.yml` 会每 3 小时自动抓 GitHub 数据并提交，AI Builder 捕捉器的数字就会一直是新的。
（也可以在 Actions 页手动点 Run workflow 先跑一次。）

## 注意
- 已包含 `.nojekyll`，Jekyll 不会处理 `assets/` 等目录。
- 全站纯静态，无需构建，直接 push 即可生效。
