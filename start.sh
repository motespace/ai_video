#!/usr/bin/env bash
# 一键启动：后端 8011 + 前端 5173
set -e
cd "$(dirname "$0")"

if [ ! -d backend/.venv ]; then
  echo "==> 创建 Python 虚拟环境"
  python3 -m venv backend/.venv
  backend/.venv/bin/pip install -q -r backend/requirements.txt
fi

echo "==> 启动后端 http://localhost:8011  (文档 /docs)"
(cd backend && .venv/bin/python -m uvicorn app.main:app --port 8011 --reload) &
BACKEND_PID=$!

echo "==> 启动前端 http://localhost:5173"
(cd frontend && pnpm dev) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
echo ""
echo "两个服务已启动，按 Ctrl+C 全部停止。"
echo "  界面:  http://localhost:5173"
echo "  接口文档: http://localhost:8011/docs"
wait
