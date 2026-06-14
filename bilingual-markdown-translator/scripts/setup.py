#!/usr/bin/env python3
"""
bilingual-markdown-translator 环境配置脚本。

在 skill 的 scripts/ 目录下创建独立虚拟环境并安装所有依赖。
支持 Windows 和 Unix/macOS。

用法：
  python setup.py          # 创建 venv + 安装依赖
  python setup.py --check  # 仅检查环境是否已就绪

运行后打印 Python 路径，可将其设为 <PYTHON> 占位符。
"""

import os
import sys
import subprocess
import argparse

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))  # scripts/
REQUIREMENTS = os.path.join(SKILL_DIR, "requirements.txt")

# venv 路径：scripts/.venv/
VENV_DIR = os.path.join(SKILL_DIR, ".venv")

# Windows 与 Unix 的 Python 可执行文件路径差异
if sys.platform == "win32":
    VENV_PYTHON = os.path.join(VENV_DIR, "Scripts", "python.exe")
    VENV_PIP = os.path.join(VENV_DIR, "Scripts", "pip.exe")
else:
    VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python")
    VENV_PIP = os.path.join(VENV_DIR, "bin", "pip")


def run(cmd, cwd=None):
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=True)


def create_venv():
    print(f"\n[setup] 创建虚拟环境: {VENV_DIR}")
    run([sys.executable, "-m", "venv", VENV_DIR])
    print("[setup] 虚拟环境创建完成")


def install_deps():
    print(f"\n[setup] 安装依赖: {REQUIREMENTS}")
    run([VENV_PIP, "install", "-r", REQUIREMENTS])
    print("[setup] 依赖安装完成")


def check_ready() -> bool:
    if not os.path.isdir(VENV_DIR):
        print(f"[setup] 未就绪：{VENV_DIR} 不存在")
        return False
    if not os.path.isfile(VENV_PYTHON):
        print(f"[setup] 未就绪：{VENV_PYTHON} 不存在")
        return False
    # 尝试验证 pip 可用
    try:
        subprocess.run([VENV_PIP, "--version"], check=True,
                       capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"[setup] 未就绪：pip 不可用")
        return False
    print(f"[setup] 就绪：{VENV_PYTHON}")
    return True


def main():
    parser = argparse.ArgumentParser(description="bilingual-markdown-translator 环境配置")
    parser.add_argument("--check", action="store_true", help="仅检查环境是否已就绪")
    args = parser.parse_args()

    if args.check:
        ready = check_ready()
        if ready:
            print(f"\n<PYTHON> = {VENV_PYTHON}")
        sys.exit(0 if ready else 1)

    print("=" * 50)
    print("bilingual-markdown-translator 环境配置")
    print("=" * 50)

    # 1. 创建 venv
    if os.path.isdir(VENV_DIR):
        print(f"\n[setup] 检测到已有虚拟环境: {VENV_DIR}")
        ans = input("  重新创建？(y/N): ").strip().lower()
        if ans == "y":
            import shutil
            shutil.rmtree(VENV_DIR)
            create_venv()
        else:
            print("  跳过创建步骤")
    else:
        create_venv()

    # 2. 安装依赖
    install_deps()

    # 3. 验证
    if check_ready():
        print(f"\n{'=' * 50}")
        print(f"配置完成！<PYTHON> 占位符 =")
        print(f"  {VENV_PYTHON}")
        print(f"可以将此路径添加到 SKILL.md 的环境说明中。")
        print(f"{'=' * 50}")
    else:
        print("\n[setup] 配置失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
