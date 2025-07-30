#!/bin/bash

# 设置错误时退出
set -e

echo "🚀 开始构建和推送到PyPI..."

# 检查是否安装了必要的工具
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到python命令"
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "❌ 错误: 未找到uv命令，请先安装uv"
    exit 1
fi

# 清理之前的构建
echo "🧹 清理之前的构建文件..."
rm -rf dist/ build/ *.egg-info/

# 构建项目
echo "🔨 构建Python包..."
uv build

# 检查构建是否成功
if [ ! -d "dist" ]; then
    echo "❌ 构建失败: dist目录不存在"
    exit 1
fi

echo "✅ 构建成功！"
echo "📦 构建的文件:"
ls -la dist/

# 提示用户上传到PyPI
echo ""
echo "🎯 准备上传到PyPI..."
echo "📋 请按照以下步骤操作："
echo ""
echo "1. 确保您已经登录PyPI:"
echo "   python -m twine upload --repository pypi dist/*"
echo ""
echo "2. 或者使用uv上传:"
echo "   uv publish"
echo ""
echo "3. 首次上传可能需要输入您的PyPI用户名和密码"
echo ""

# 询问是否自动上传
read -p "是否现在上传到PyPI? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 开始上传到PyPI..."
    export UV_PUBLISH_TOKEN=pypi-AgEIcHlwaS5vcmcCJGUwYmM2MjI1LTlkNmYtNDQ4Yi05OWFmLWIzMGFiMjBhODhjOAACIlsxLFsib2ZmaWNlLXdvcmQtbWNwLXV2eC1zZXJ2ZXIiXV0AAixbMixbImFjYzBmNzcxLTk2OTgtNDRhYy1iMmRjLWIwZjFjZjU4NDQ2NyJdXQAABiD-aw1v6XXz4MxxYtn9eY7rrk1s8lhFzDyRm9KdLkayjQ
    uv publish
    echo "✅ 上传完成！"
    echo "🌐 您可以在 https://pypi.org/project/office-word-mcp-uvx-server/ 查看您的包"
else
    echo "📝 您可以稍后手动运行以下命令上传:"
    echo "   uv publish"
    echo "   或者"
    echo "   python -m twine upload --repository pypi dist/*"
fi