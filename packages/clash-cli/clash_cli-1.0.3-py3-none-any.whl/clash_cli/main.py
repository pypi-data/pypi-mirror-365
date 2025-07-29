#!/usr/bin/env python3
"""
clash-cli 主入口文件
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from .cli import cli
from .exceptions import ClashCliError
from .utils import error_message, check_systemd, get_system_info


def check_environment():
    """检查运行环境"""
    # 检查操作系统
    if sys.platform != 'linux':
        error_message("clash-cli 仅支持 Linux 系统")
        sys.exit(1)
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        error_message("需要 Python 3.8 或更高版本")
        sys.exit(1)
    
    # 检查 systemd 支持
    if not check_systemd():
        error_message("系统不支持 systemd，无法管理服务")
        sys.exit(1)
    
    # 检查系统信息
    try:
        sys_info = get_system_info()
        if sys_info['distro'] == 'unknown':
            error_message("无法识别的 Linux 发行版")
            sys.exit(1)
    except Exception as e:
        error_message(f"检查系统信息失败: {e}")
        sys.exit(1)


def setup_sudo_access():
    """设置 sudo 访问权限"""
    # 检查是否是 sudo 环境且找不到系统级命令
    if os.geteuid() == 0 and os.environ.get('SUDO_USER'):
        sudo_user = os.environ.get('SUDO_USER')
        user_clash_cli = f"/home/{sudo_user}/.local/bin/clash-cli"
        system_clash_cli = "/usr/local/bin/clash-cli"

        # 如果用户级存在但系统级不存在，自动创建链接
        if os.path.exists(user_clash_cli) and not os.path.exists(system_clash_cli):
            try:
                os.symlink(user_clash_cli, system_clash_cli)
                print(f"✅ 已创建系统链接: {system_clash_cli} -> {user_clash_cli}")
            except Exception as e:
                print(f"💡 建议手动创建系统链接: sudo ln -s {user_clash_cli} {system_clash_cli}")


def main():
    """主函数"""
    try:
        # 设置 sudo 访问权限
        setup_sudo_access()

        # 检查运行环境
        check_environment()

        # 运行 CLI
        cli()

    except KeyboardInterrupt:
        error_message("操作被用户中断")
        sys.exit(130)
    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"未知错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
