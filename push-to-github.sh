#!/usr/bin/env bash
# 一键推送作品集到 GitHub Pages（仓库：ss1103-ari/ss1103-ari.github.io）
# 用法：GH_TOKEN=你的PersonalAccessToken ./push-to-github.sh
set -euo pipefail

USER_NAME="ss1103-ari"
REPO="ss1103-ari.github.io"

if [ -z "${GH_TOKEN:-}" ]; then
  echo "缺少 GH_TOKEN。请先在 https://github.com/settings/tokens 生成 classic token（勾选 repo + workflow），然后："
  echo "  GH_TOKEN=ghp_xxx ./push-to-github.sh"
  exit 1
fi

cd "$(dirname "$0")"

git add -A
git commit -m "更新作品集" || echo "没有新改动，跳过 commit"

git remote remove origin 2>/dev/null || true
git remote add origin "https://${USER_NAME}:${GH_TOKEN}@github.com/${USER_NAME}/${REPO}.git"

git branch -M main
git push -u origin main --force

git remote set-url origin "https://github.com/${USER_NAME}/${REPO}.git"

echo "✅ 推送完成，约 1 分钟后访问：https://${USER_NAME}.github.io/"
