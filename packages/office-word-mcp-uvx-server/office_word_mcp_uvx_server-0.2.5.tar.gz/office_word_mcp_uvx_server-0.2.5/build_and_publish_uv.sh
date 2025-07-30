#!/bin/bash
# Word MCP 包构建和发布脚本 - 使用 uv

set -e

export NEXUS_USERNAME=admin
export NEXUS_PASSWORD=GTj7aGFy3F7ZAt
# export NEXUS_PASSWORD=vMAhm5oem2dp3o

echo "🚀 Word MCP 包发布到 Nexus3 (使用 uv)"
echo "======================================"

# 配置
# NEXUS_URL="${NEXUS_URL:-https://nexus3.gs.dogwof.com:8088/}"
NEXUS_URL="${NEXUS_URL:-https://nexus3.m.6do.me:4000/}"
PACKAGE_NAME="office-word-mcp-uvx-server"

# 检查必要工具
echo "🔍 安装构建工具..."
uv pip install build twine

# 清理旧构建
echo "🗑️  清理旧构建文件..."
rm -rf build/ dist/ *.egg-info/

# 构建包
echo "📦 构建包..."
uv run python -m build

# 检查构建结果
if [ ! -d "dist" ] || [ -z "$(ls -A dist/)" ]; then
    echo "❌ 构建失败，dist 目录为空"
    exit 1
fi

echo "✅ 构建完成，生成的文件："
ls -la dist/

# 自动上传
echo "🚀 上传到 Nexus3..."
uv run python -m twine upload \
  --repository-url "$NEXUS_URL/repository/pip-hosted/" \
  --username "$NEXUS_USERNAME" \
  --password "$NEXUS_PASSWORD" \
  dist/*

if [ $? -eq 0 ]; then
    echo "🎉 发布成功！"
    echo ""
    echo "📋 安装命令："
    echo "uv pip install -i $NEXUS_URL/repository/pypi-group/simple $PACKAGE_NAME"
    echo ""
    echo "📋 使用命令："
    echo "uvx --from $PACKAGE_NAME word-mcp-server"
else
    echo "❌ 上传失败"
    exit 1
fi