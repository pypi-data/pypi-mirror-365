"""
clash-cli 命令行接口
"""

import os
import sys
import subprocess
import shutil
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from . import __version__
from .core.service import ClashService
from .core.config import ClashConfig
from .core.proxy import ProxyManager
from .core.installer import ClashInstaller
from .core.tool_manager import ToolManager
from .exceptions import ClashCliError
from .utils import success_message, error_message, info_message, console
from .i18n import _, get_current_lang, set_language, get_help_text


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='显示版本信息 / Show version')
@click.pass_context
def cli(ctx, version):
    """clash-cli - Linux 一键安装 Clash 代理工具 / Easy Linux Command Line Proxy"""
    if version:
        click.echo(f"clash-cli version {__version__}")
        return

    if ctx.invoked_subcommand is None:
        # 显示多语言帮助信息
        click.echo(get_help_text())


@cli.command()
def init():
    """初始化 clash-cli 环境 / Initialize clash-cli environment"""
    try:
        info_message("🚀 正在初始化 clash-cli 环境...")

        # 找到当前 clash-cli 的位置
        current_clash_cli = shutil.which('clash-cli')
        if not current_clash_cli:
            error_message("无法找到 clash-cli 命令，请确认安装正确")
            sys.exit(1)

        system_clash_cli = "/usr/local/bin/clash-cli"

        # 检查是否已经初始化
        if os.path.exists(system_clash_cli):
            # 检查链接是否正确
            if os.path.islink(system_clash_cli):
                link_target = os.readlink(system_clash_cli)
                if link_target == current_clash_cli:
                    success_message("✅ clash-cli 环境已经正确配置")
                    info_message(f"系统链接: {system_clash_cli} -> {current_clash_cli}")
                    info_message("🎉 可以正常使用 sudo clash-cli 命令了")
                    return
                else:
                    info_message(f"⚠️  发现旧的系统链接，正在更新...")
                    try:
                        os.remove(system_clash_cli)
                    except Exception as e:
                        error_message(f"删除旧链接失败: {e}")
                        info_message(f"请手动删除: sudo rm {system_clash_cli}")
                        sys.exit(1)
            else:
                error_message(f"系统路径 {system_clash_cli} 已存在但不是符号链接")
                error_message("请手动处理后重新运行 clash-cli init")
                sys.exit(1)

        # 创建系统链接
        info_message(f"🔗 创建系统链接: {system_clash_cli} -> {current_clash_cli}")

        try:
            # 使用 subprocess 调用 sudo ln
            result = subprocess.run([
                'sudo', 'ln', '-s', current_clash_cli, system_clash_cli
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_message("✅ 系统链接创建成功！")
                success_message("🎉 clash-cli 环境初始化完成")
                info_message("")
                info_message("现在可以正常使用以下命令:")
                info_message("  sudo clash-cli install    # 安装 Clash 服务")
                info_message("  clash-cli on              # 开启代理")
                info_message("  clash-cli off             # 关闭代理")
                info_message("  clash-cli status          # 查看状态")
            else:
                error_message(f"创建系统链接失败: {result.stderr.strip()}")
                info_message(f"💡 请手动运行: sudo ln -s {current_clash_cli} {system_clash_cli}")
                sys.exit(1)

        except subprocess.TimeoutExpired:
            error_message("创建系统链接超时，可能需要输入密码")
            info_message(f"💡 请手动运行: sudo ln -s {current_clash_cli} {system_clash_cli}")
            sys.exit(1)
        except Exception as e:
            error_message(f"创建系统链接失败: {e}")
            info_message(f"💡 请手动运行: sudo ln -s {current_clash_cli} {system_clash_cli}")
            sys.exit(1)

    except Exception as e:
        error_message(f"初始化失败: {e}")
        sys.exit(1)


def check_sudo_requirement():
    """检查是否需要 sudo 权限"""
    if os.geteuid() != 0:
        error_message("此命令需要 sudo 权限，请使用: sudo clash-cli <command>")
        error_message("如果提示'找不到命令'，请先运行: clash-cli init")
        sys.exit(1)


@cli.command()
@click.option('--kernel', type=click.Choice(['mihomo', 'clash']), default='mihomo', help='选择内核类型 / Choose kernel type')
@click.option('--subscription', '-s', help='订阅链接 / Subscription URL')
@click.option('--offline', is_flag=True, help='离线安装模式 / Offline installation mode')
@click.option('--mihomo', help='指定 Mihomo 文件路径 / Specify Mihomo file path')
@click.option('--yq', help='指定 YQ 文件路径 / Specify YQ file path')
def install(kernel, subscription, offline, mihomo, yq):
    """安装 Clash / Install Clash"""
    try:
        check_sudo_requirement()
        installer = ClashInstaller()

        if installer.is_installed():
            info_message("Clash 已安装")
            return

        if subscription:
            info_message(f"使用订阅链接: {subscription}")

        # 构建工具路径字典
        tool_paths = {}
        if mihomo:
            tool_paths['mihomo'] = mihomo
        if yq:
            tool_paths['yq'] = yq

        installer.install(
            kernel=kernel,
            subscription_url=subscription,
            offline_mode=offline,
            tool_paths=tool_paths
        )

    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"安装失败: {e}")
        sys.exit(1)


@cli.command()
def uninstall():
    """卸载 Clash / Uninstall Clash"""
    try:
        if not click.confirm('确定要卸载 Clash 吗？这将删除所有配置文件'):
            return
        
        installer = ClashInstaller()
        installer.uninstall()
        
    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"卸载失败: {e}")
        sys.exit(1)


@cli.command()
def on():
    """开启代理 / Enable proxy"""
    try:
        service = ClashService()
        proxy_manager = ProxyManager()
        
        # 启动服务
        service.start()
        
        # 设置系统代理
        proxy_manager.set_system_proxy()
        
        success_message(_("proxy_on"))
        
    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"开启代理失败: {e}")
        sys.exit(1)


@cli.command()
def off():
    """关闭代理 / Disable proxy"""
    try:
        service = ClashService()
        proxy_manager = ProxyManager()
        
        # 停止服务
        service.stop()
        
        # 清除系统代理
        proxy_manager.unset_system_proxy()
        
        success_message(_("proxy_off"))
        
    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"关闭代理失败: {e}")
        sys.exit(1)


@cli.command()
@click.option('--lines', '-n', default=50, help='显示日志行数')
@click.option('--follow', '-f', is_flag=True, help='实时跟踪日志')
def status(lines, follow):
    """查看服务状态"""
    try:
        service = ClashService()
        status_info = service.get_status()
        
        # 创建状态表格
        table = Table(title="Clash 服务状态")
        table.add_column("项目", style="cyan")
        table.add_column("状态", style="green")
        
        table.add_row("服务安装", "✅ 已安装" if status_info['installed'] else "❌ 未安装")
        table.add_row("服务运行", "✅ 运行中" if status_info['running'] else "❌ 已停止")
        table.add_row("开机自启", "✅ 已启用" if status_info['enabled'] else "❌ 未启用")
        
        console.print(table)
        
        if follow:
            info_message("实时跟踪日志 (Ctrl+C 退出):")
            logs = service.get_logs(lines=0, follow=True)
            console.print(logs)
        else:
            if lines > 0:
                logs = service.get_logs(lines=lines)
                console.print(Panel(logs, title="服务日志"))
        
    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"获取状态失败: {e}")
        sys.exit(1)


@cli.group(invoke_without_command=True)
@click.pass_context
def proxy(ctx):
    """系统代理管理"""
    if ctx.invoked_subcommand is None:
        # 显示代理状态
        try:
            proxy_manager = ProxyManager()
            status = proxy_manager.get_proxy_status()
            
            if status['enabled']:
                success_message(_("proxy_enabled"))
                info_message(f"HTTP 代理：{status['proxy_info']['http_proxy']}")
                info_message(f"SOCKS 代理：{status['proxy_info']['socks_proxy']}")
            else:
                error_message(_("proxy_disabled"))
                
        except Exception as e:
            error_message(f"获取代理状态失败: {e}")


@proxy.command()
def on():
    """开启系统代理"""
    try:
        proxy_manager = ProxyManager()
        proxy_manager.set_system_proxy()
        
    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"开启系统代理失败: {e}")
        sys.exit(1)


@proxy.command()
def off():
    """关闭系统代理"""
    try:
        proxy_manager = ProxyManager()
        proxy_manager.unset_system_proxy()
        
    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"关闭系统代理失败: {e}")
        sys.exit(1)


@cli.command()
def ui():
    """显示 Web 控制台信息"""
    try:
        proxy_manager = ProxyManager()
        ui_info = proxy_manager.get_ui_info()
        
        # 创建 UI 信息面板
        ui_content = f"""
🔓 注意放行端口：{ui_info['port']}
🏠 内网：{ui_info['local_url']}
🌏 公网：{ui_info['public_url']}
☁️  公共：{ui_info['cloud_url']}
🔑 密钥：{ui_info['secret']}
"""
        
        console.print(Panel(ui_content, title="😼 Web 控制台", border_style="green"))
        
    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"获取 UI 信息失败: {e}")
        sys.exit(1)


@cli.command()
@click.argument('secret', required=False)
def secret(secret):
    """设置或查看 Web 控制台密钥"""
    try:
        proxy_manager = ProxyManager()
        
        if secret is None:
            # 查看当前密钥
            current_secret = proxy_manager._get_ui_secret()
            info_message(f"当前密钥：{current_secret or '无'}")
        else:
            # 设置新密钥
            proxy_manager.set_ui_secret(secret)
            
            # 重启服务使配置生效
            service = ClashService()
            if service.is_running():
                service.restart()
        
    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"设置密钥失败: {e}")
        sys.exit(1)


@cli.group(invoke_without_command=True)
@click.pass_context
def tun(ctx):
    """Tun 模式管理"""
    if ctx.invoked_subcommand is None:
        # 显示 Tun 状态
        try:
            proxy_manager = ProxyManager()
            tun_enabled = proxy_manager.get_tun_status()
            
            if tun_enabled:
                success_message(_("tun_status_on"))
            else:
                error_message(_("tun_status_off"))
                
        except Exception as e:
            error_message(f"获取 Tun 状态失败: {e}")


@tun.command()
def on():
    """开启 Tun 模式"""
    try:
        proxy_manager = ProxyManager()
        proxy_manager.enable_tun_mode()
        
        # 重启服务使配置生效
        service = ClashService()
        if service.is_running():
            service.restart()

        success_message(_("tun_enabled"))

    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"开启 Tun 模式失败: {e}")
        sys.exit(1)


@cli.group(invoke_without_command=True)
@click.pass_context
def update(ctx):
    """订阅管理"""
    if ctx.invoked_subcommand is None:
        # 显示当前订阅信息
        try:
            config_manager = ClashConfig()
            current_url = config_manager.get_current_subscription_url()

            if current_url:
                info_message(f"当前订阅：{current_url}")
            else:
                error_message("未设置订阅链接")

        except Exception as e:
            error_message(f"获取订阅信息失败: {e}")


@update.command()
@click.argument('url', required=False)
def sync(url):
    """更新订阅"""
    try:
        config_manager = ClashConfig()

        if url:
            config_manager.update_subscription(url)
        else:
            config_manager.update_subscription()

        # 重启服务使配置生效
        service = ClashService()
        if service.is_running():
            service.restart()

    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"更新订阅失败: {e}")
        sys.exit(1)


@update.command()
@click.option('--lines', '-n', default=20, help='显示日志行数')
def log(lines):
    """查看更新日志"""
    try:
        config_manager = ClashConfig()
        logs = config_manager.get_update_log(lines=lines)

        if logs:
            for log_line in logs:
                console.print(log_line)
        else:
            info_message("暂无更新日志")

    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"获取更新日志失败: {e}")
        sys.exit(1)


@cli.group(invoke_without_command=True)
@click.pass_context
def mixin(ctx):
    """Mixin 配置管理"""
    if ctx.invoked_subcommand is None:
        # 显示 Mixin 配置
        try:
            config_manager = ClashConfig()
            mixin_config = config_manager.get_mixin_config()

            import yaml
            config_yaml = yaml.dump(mixin_config, default_flow_style=False, allow_unicode=True)
            console.print(Panel(config_yaml, title="Mixin 配置"))

        except Exception as e:
            error_message(f"获取 Mixin 配置失败: {e}")


@mixin.command()
def edit():
    """编辑 Mixin 配置"""
    try:
        from .constants import CLASH_CONFIG_MIXIN

        # 使用系统默认编辑器
        editor = os.environ.get('EDITOR', 'vim')
        subprocess.run([editor, str(CLASH_CONFIG_MIXIN)])

        # 重新合并配置
        config_manager = ClashConfig()
        config_manager.merge_configs()

        # 重启服务使配置生效
        service = ClashService()
        if service.is_running():
            service.restart()

        success_message(_("config_updated"))

    except Exception as e:
        error_message(f"编辑配置失败: {e}")
        sys.exit(1)


@mixin.command()
def runtime():
    """查看运行时配置"""
    try:
        config_manager = ClashConfig()
        runtime_config = config_manager.load_yaml(config_manager.config_runtime)

        import yaml
        config_yaml = yaml.dump(runtime_config, default_flow_style=False, allow_unicode=True)
        console.print(Panel(config_yaml, title="运行时配置"))

    except Exception as e:
        error_message(f"获取运行时配置失败: {e}")


@cli.command()
def info():
    """显示系统信息"""
    try:
        from .utils import get_system_info

        # 获取系统信息
        sys_info = get_system_info()

        # 获取安装信息
        installer = ClashInstaller()
        install_info = installer.get_installation_info()

        # 获取服务状态
        service = ClashService()
        service_status = service.get_status()

        # 创建信息表格
        table = Table(title="系统信息")
        table.add_column("项目", style="cyan")
        table.add_column("值", style="green")

        # 系统信息
        table.add_row("操作系统", f"{sys_info['distro']} {sys_info['version']}")
        table.add_row("架构", sys_info['arch'])
        table.add_row("内核版本", sys_info['kernel'])
        table.add_row("Python 版本", sys_info['python'])

        # 安装信息
        table.add_row("", "")  # 分隔行
        table.add_row("安装状态", "✅ 已安装" if install_info['installed'] else "❌ 未安装")
        table.add_row("安装目录", install_info['base_dir'])
        table.add_row("Mihomo", "✅" if install_info['mihomo_exists'] else "❌")
        table.add_row("Clash", "✅" if install_info['clash_exists'] else "❌")
        table.add_row("YQ", "✅" if install_info['yq_exists'] else "❌")
        table.add_row("Subconverter", "✅" if install_info['subconverter_exists'] else "❌")

        # 服务状态
        table.add_row("", "")  # 分隔行
        table.add_row("服务运行", "✅ 运行中" if service_status['running'] else "❌ 已停止")
        table.add_row("开机自启", "✅ 已启用" if service_status['enabled'] else "❌ 未启用")

        console.print(table)

    except Exception as e:
        error_message(f"获取系统信息失败: {e}")
        sys.exit(1)


@tun.command()
def off():
    """关闭 Tun 模式"""
    try:
        proxy_manager = ProxyManager()
        proxy_manager.disable_tun_mode()
        
        # 重启服务使配置生效
        service = ClashService()
        if service.is_running():
            service.restart()

        success_message(_("tun_disabled"))

    except ClashCliError as e:
        error_message(str(e))
        sys.exit(e.code)
    except Exception as e:
        error_message(f"关闭 Tun 模式失败: {e}")
        sys.exit(1)


@cli.command()
@click.argument('language', required=False)
def lang(language):
    """切换语言 / Switch language"""
    try:
        if language in ['zh', 'en']:
            if set_language(language):
                success_message(_('lang_switched'))
            else:
                error_message("Failed to set language")
                sys.exit(1)
        elif language is None:
            info_message(_('current_lang'))
        else:
            info_message(_('lang_usage'))

    except Exception as e:
        error_message(f"Language operation failed: {e}")
        sys.exit(1)


@cli.command()
def fix_sudo():
    """修复 sudo 访问问题 / Fix sudo access issue"""
    try:
        # 找到当前 clash-cli 的位置
        current_clash_cli = shutil.which('clash-cli')
        if not current_clash_cli:
            error_message("无法找到 clash-cli 命令")
            sys.exit(1)

        system_clash_cli = "/usr/local/bin/clash-cli"

        # 检查是否已经存在系统链接
        if os.path.exists(system_clash_cli):
            success_message(f"系统链接已存在: {system_clash_cli}")
            return

        # 创建系统链接
        info_message(f"正在创建系统链接: {system_clash_cli} -> {current_clash_cli}")

        try:
            # 使用 subprocess 调用 sudo ln
            result = subprocess.run([
                'sudo', 'ln', '-s', current_clash_cli, system_clash_cli
            ], capture_output=True, text=True)

            if result.returncode == 0:
                success_message("✅ 系统链接创建成功！")
                success_message("🎉 现在可以使用: sudo clash-cli install")
            else:
                error_message(f"创建系统链接失败: {result.stderr}")
                info_message(f"💡 请手动运行: sudo ln -s {current_clash_cli} {system_clash_cli}")

        except Exception as e:
            error_message(f"创建系统链接失败: {e}")
            info_message(f"💡 请手动运行: sudo ln -s {current_clash_cli} {system_clash_cli}")

    except Exception as e:
        error_message(f"修复 sudo 访问失败: {e}")
        sys.exit(1)



