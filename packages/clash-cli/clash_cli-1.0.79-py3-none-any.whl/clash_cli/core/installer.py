"""
Clash 安装器
"""

import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from ..constants import (
    CLASH_BASE_DIR, CLASH_BIN_DIR, CLASH_CONFIG_DIR, CLASH_LOG_DIR,
    BIN_MIHOMO, BIN_CLASH, BIN_YQ, BIN_SUBCONVERTER_DIR, BIN_SUBCONVERTER,
    DOWNLOAD_URLS, SUPPORTED_ARCHITECTURES
)
from ..exceptions import InstallationError, NetworkError
from ..utils import (
    check_root_permission, get_architecture, download_file, extract_archive,
    success_message, error_message, info_message, console
)
from .tool_manager import ToolManager


class ClashInstaller:
    """Clash 安装器"""
    
    def __init__(self):
        self.arch = get_architecture()
        if self.arch not in SUPPORTED_ARCHITECTURES:
            raise InstallationError(f"不支持的架构: {self.arch}")

        # 初始化工具管理器
        self.tool_manager = ToolManager()
    
    def is_installed(self) -> bool:
        """检查是否已安装"""
        return (BIN_MIHOMO.exists() or BIN_CLASH.exists()) and BIN_YQ.exists()
    
    def get_installation_info(self) -> Dict[str, Any]:
        """获取安装信息"""
        return {
            'installed': self.is_installed(),
            'base_dir': str(CLASH_BASE_DIR),
            'bin_dir': str(CLASH_BIN_DIR),
            'config_dir': str(CLASH_CONFIG_DIR),
            'log_dir': str(CLASH_LOG_DIR),
            'mihomo_exists': BIN_MIHOMO.exists(),
            'clash_exists': BIN_CLASH.exists(),
            'yq_exists': BIN_YQ.exists(),
            'subconverter_exists': BIN_SUBCONVERTER.exists(),
            'architecture': self.arch,
        }
    
    def install(self, kernel: str = 'mihomo', subscription_url: Optional[str] = None, offline_mode: bool = False, tool_paths: Optional[Dict[str, str]] = None) -> None:
        """安装 Clash"""
        check_root_permission()
        
        if self.is_installed():
            info_message("Clash 已安装，如需重新安装请先卸载")
            return
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                
                # 创建目录
                task1 = progress.add_task("创建目录结构...", total=1)
                self._create_directories()
                progress.update(task1, completed=1)
                
                # 下载和安装内核
                task2 = progress.add_task(f"安装 {kernel} 内核...", total=1)
                self._install_kernel(kernel)
                progress.update(task2, completed=1)
                
                # 安装工具（使用新的工具管理器）
                task3 = progress.add_task("安装必需工具...", total=1)
                progress.update(task3, advance=0.3)

                # 在进度条内执行工具安装
                if tool_paths:
                    # 用户指定了工具路径，使用指定文件
                    success = self._install_tools_from_paths(tool_paths)
                elif offline_mode:
                    # 离线模式，使用预置版本
                    success = self.tool_manager.install_required_tools(use_fallback=True)
                else:
                    # 网络模式，尝试下载最新版本
                    success = self.tool_manager.install_required_tools()

                if not success:
                    raise InstallationError("必需工具安装失败")

                progress.update(task3, completed=1)

                # 安装其他组件
                task3_extra = progress.add_task("安装其他组件...", total=2)
                self._install_subconverter()
                progress.update(task3_extra, advance=1)

                self._install_ui()
                progress.update(task3_extra, advance=1)
                
                # 下载 GeoIP 数据库
                task4 = progress.add_task("下载 GeoIP 数据库...", total=1)
                self._install_geoip()
                progress.update(task4, completed=1)
                
                # 初始化配置
                task5 = progress.add_task("初始化配置...", total=1)
                self._initialize_config(subscription_url)
                progress.update(task5, completed=1)
            
            success_message("Clash 安装完成！")
            
        except Exception as e:
            error_message(f"安装失败: {e}")
            # 清理安装文件
            self._cleanup_installation()
            raise InstallationError(f"安装失败: {e}")

    def _install_tools_from_paths(self, tool_paths: Dict[str, str]) -> bool:
        """从指定路径安装工具"""
        success_count = 0
        required_tools = ['mihomo', 'yq']  # 必需工具列表

        for tool_name in required_tools:
            if tool_name in tool_paths:
                # 用户指定了路径
                tool_path = tool_paths[tool_name]
                info_message(f"📦 安装 {tool_name} 从: {tool_path}")

                if self.tool_manager.install_tool_from_file(tool_name, tool_path):
                    success_count += 1
                else:
                    error_message(f"❌ 从 {tool_path} 安装 {tool_name} 失败")
            else:
                # 用户没有指定路径，使用预置版本
                info_message(f"📦 安装 {tool_name} 使用预置版本")

                if self.tool_manager.install_tool(tool_name, use_fallback=True):
                    success_count += 1
                else:
                    error_message(f"❌ 安装 {tool_name} 预置版本失败")

        return success_count == len(required_tools)

    def uninstall(self) -> None:
        """卸载 Clash"""
        check_root_permission()
        
        try:
            # 停止服务
            from .service import ClashService
            service = ClashService()
            if service.is_running():
                service.stop()
            if service.is_installed():
                service.uninstall_service()
            
            # 删除文件
            if CLASH_BASE_DIR.exists():
                shutil.rmtree(CLASH_BASE_DIR)
            
            # 清理 Shell 集成
            self._cleanup_shell_integration()
            
            success_message("Clash 卸载完成")
            
        except Exception as e:
            raise InstallationError(f"卸载失败: {e}")
    
    def _create_directories(self) -> None:
        """创建目录结构"""
        directories = [
            CLASH_BASE_DIR,
            CLASH_BIN_DIR,
            CLASH_CONFIG_DIR,
            CLASH_LOG_DIR,
            BIN_SUBCONVERTER_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _install_kernel(self, kernel: str) -> None:
        """安装内核"""
        if kernel not in ['mihomo', 'clash']:
            raise InstallationError(f"不支持的内核: {kernel}")
        
        if kernel not in DOWNLOAD_URLS:
            raise InstallationError(f"未找到 {kernel} 的下载链接")
        
        if self.arch not in DOWNLOAD_URLS[kernel]:
            raise InstallationError(f"{kernel} 不支持架构 {self.arch}")
        
        url = DOWNLOAD_URLS[kernel][self.arch]
        filename = Path(url).name
        download_path = CLASH_BIN_DIR / filename
        
        # 下载
        download_file(url, download_path, show_progress=False)
        
        # 解压
        extract_archive(download_path, CLASH_BIN_DIR)
        
        # 设置权限
        if kernel == 'mihomo':
            if BIN_MIHOMO.exists():
                BIN_MIHOMO.chmod(0o755)
            else:
                # 查找解压出的文件
                for file in CLASH_BIN_DIR.glob('mihomo*'):
                    if file.is_file() and not file.suffix:
                        file.rename(BIN_MIHOMO)
                        BIN_MIHOMO.chmod(0o755)
                        break
        else:
            if BIN_CLASH.exists():
                BIN_CLASH.chmod(0o755)
            else:
                for file in CLASH_BIN_DIR.glob('clash*'):
                    if file.is_file() and not file.suffix:
                        file.rename(BIN_CLASH)
                        BIN_CLASH.chmod(0o755)
                        break
        
        # 清理下载文件
        download_path.unlink(missing_ok=True)
    
    def _install_yq(self) -> None:
        """安装 yq"""
        url = DOWNLOAD_URLS['yq']
        filename = Path(url).name
        download_path = CLASH_BIN_DIR / filename
        
        # 下载
        download_file(url, download_path, show_progress=False)
        
        # 解压
        extract_archive(download_path, CLASH_BIN_DIR)
        
        # 查找并重命名 yq 文件
        for file in CLASH_BIN_DIR.glob('yq_*'):
            if file.is_file():
                file.rename(BIN_YQ)
                BIN_YQ.chmod(0o755)
                break
        
        # 清理下载文件
        download_path.unlink(missing_ok=True)
    
    def _install_subconverter(self) -> None:
        """安装 subconverter"""
        url = DOWNLOAD_URLS['subconverter']
        filename = Path(url).name
        download_path = CLASH_BIN_DIR / filename
        
        # 下载
        download_file(url, download_path, show_progress=False)
        
        # 解压到 subconverter 目录
        extract_archive(download_path, BIN_SUBCONVERTER_DIR)
        
        # 设置权限
        if BIN_SUBCONVERTER.exists():
            BIN_SUBCONVERTER.chmod(0o755)
        
        # 清理下载文件
        download_path.unlink(missing_ok=True)
    
    def _install_ui(self) -> None:
        """安装 Web UI"""
        url = DOWNLOAD_URLS['yacd']
        filename = Path(url).name
        download_path = CLASH_BASE_DIR / filename
        
        # 下载
        download_file(url, download_path, show_progress=False)
        
        # 解压到 public 目录
        ui_dir = CLASH_BASE_DIR / 'public'
        extract_archive(download_path, ui_dir)
        
        # 清理下载文件
        download_path.unlink(missing_ok=True)
    
    def _install_geoip(self) -> None:
        """安装 GeoIP 数据库"""
        url = DOWNLOAD_URLS['country_mmdb']
        download_path = CLASH_BASE_DIR / 'Country.mmdb'
        
        # 下载
        download_file(url, download_path, show_progress=False)
    
    def _initialize_config(self, subscription_url: Optional[str] = None) -> None:
        """初始化配置"""
        from .config import ClashConfig
        from .service import ClashService
        from .proxy import ProxyManager
        
        # 初始化配置管理器
        config_manager = ClashConfig()
        config_manager.init_mixin_config()
        
        # 如果提供了订阅链接，下载配置
        if subscription_url:
            try:
                config_manager.download_config(subscription_url)
                config_manager.merge_configs()
            except Exception as e:
                error_message(f"下载订阅配置失败: {e}")
                info_message("请稍后使用 'clash-cli update' 命令更新订阅")
        
        # 安装服务
        service = ClashService()
        service.install_service()
        service.enable()
        
        # 设置 Shell 集成
        proxy_manager = ProxyManager()
        proxy_manager.setup_shell_integration()
    
    def _cleanup_installation(self) -> None:
        """清理安装文件"""
        try:
            if CLASH_BASE_DIR.exists():
                shutil.rmtree(CLASH_BASE_DIR)
        except Exception:
            pass
    
    def _cleanup_shell_integration(self) -> None:
        """清理 Shell 集成"""
        try:
            shell_files = [
                Path.home() / '.bashrc',
                Path.home() / '.zshrc',
                Path.home() / '.config/fish/conf.d/clash-cli.fish',
            ]
            
            for shell_file in shell_files:
                if shell_file.exists():
                    # 读取文件内容
                    with open(shell_file, 'r') as f:
                        lines = f.readlines()
                    
                    # 过滤掉 clash-cli 相关行
                    filtered_lines = []
                    skip_section = False
                    
                    for line in lines:
                        if '# clash-cli integration' in line:
                            skip_section = True
                            continue
                        elif skip_section and line.strip() == '':
                            skip_section = False
                            continue
                        elif not skip_section:
                            filtered_lines.append(line)
                    
                    # 写回文件
                    with open(shell_file, 'w') as f:
                        f.writelines(filtered_lines)
                        
        except Exception:
            pass
