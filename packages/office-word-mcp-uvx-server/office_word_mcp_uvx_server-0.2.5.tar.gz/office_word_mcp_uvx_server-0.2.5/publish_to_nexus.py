#!/usr/bin/env python3
"""发布脚本 - 将包推送到 Nexus3 服务器"""

import subprocess
import sys
import os
import shutil
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并处理错误"""
    print(f"🔄 {description}")
    print(f"   执行: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ 命令失败: {description}")
        print(f"   错误输出: {result.stderr}")
        return False

    if result.stdout.strip():
        print(f"   输出: {result.stdout.strip()}")

    print(f"✅ {description} 完成")
    return True


def clean_build():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '*.egg-info']

    for pattern in dirs_to_clean:
        if '*' in pattern:
            # 处理通配符
            for path in Path('.').glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"🗑️  删除目录: {path}")
        else:
            if os.path.exists(pattern):
                shutil.rmtree(pattern)
                print(f"🗑️  删除目录: {pattern}")


def build_package():
    """构建包"""
    print("\n📦 开始构建包...")

    # 清理旧的构建文件
    clean_build()

    # 构建包
    if not run_command([sys.executable, "-m", "build"], "构建包"):
        return False

    return True


def upload_to_nexus(nexus_url, username, password):
    """上传到 Nexus3"""
    print(f"\n🚀 上传到 Nexus3: {nexus_url}")

    # 配置 twine 上传到 Nexus
    cmd = [
        sys.executable, "-m", "twine", "upload",
        "--repository-url", f"{nexus_url}/repository/pypi-hosted/",
        "--username", username,
        "--password", password,
        "dist/*"
    ]

    return run_command(cmd, "上传到 Nexus3")


def main():
    """主函数"""
    print("🚀 Word MCP 包发布脚本")
    print("=" * 50)

    # 检查必要的工具
    tools = ["build", "twine"]
    missing_tools = []

    for tool in tools:
        result = subprocess.run([sys.executable, "-m", tool, "--help"],
                              capture_output=True, text=True)
        if result.returncode != 0:
            missing_tools.append(tool)

    if missing_tools:
        print(f"❌ 缺少必要工具: {', '.join(missing_tools)}")
        print("请安装: pip install build twine")
        return 1

    # 从环境变量或用户输入获取配置
    nexus_url = os.getenv('NEXUS_URL', 'https://nexus3.m.6do.me:4000')
    nexus_username = os.getenv('NEXUS_USERNAME')
    nexus_password = os.getenv('NEXUS_PASSWORD')

    if not nexus_username:
        nexus_username = input("请输入 Nexus 用户名: ").strip()

    if not nexus_password:
        import getpass
        nexus_password = getpass.getpass("请输入 Nexus 密码: ")

    if not all([nexus_url, nexus_username, nexus_password]):
        print("❌ 缺少必要的配置信息")
        return 1

    # 构建包
    if not build_package():
        print("❌ 构建失败")
        return 1

    # 上传到 Nexus
    if not upload_to_nexus(nexus_url, nexus_username, nexus_password):
        print("❌ 上传失败")
        return 1

    print("\n🎉 发布成功!")
    print(f"现在可以通过以下命令安装:")
    print(f"uv pip install -i {nexus_url}/repository/pypi-group/simple office-word-mcp-uvx-server")
    print(f"uvx --from office-word-mcp-uvx-server word-mcp-server")

    return 0


if __name__ == "__main__":
    sys.exit(main())