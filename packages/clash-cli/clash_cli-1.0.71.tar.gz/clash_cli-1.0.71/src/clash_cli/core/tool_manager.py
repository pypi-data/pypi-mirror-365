"""
工具管理模块
负责下载、安装、更新各种工具（yq, mihomo, clash等）
"""

import os
import json
import hashlib
import shutil
import subprocess
import tarfile
import zipfile
import gzip
import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pkg_resources

from ..utils import info_message, success_message, error_message, warning_message
from ..exceptions import ClashCliError


class ToolManager:
    """工具管理器"""
    
    def __init__(self, base_dir: str = "/opt/clash"):
        self.base_dir = Path(base_dir)
        self.bin_dir = self.base_dir / "bin"
        self.cache_dir = Path.home() / ".cache" / "clash-cli" / "downloads"

        # 使用 pkg_resources 获取包内资源路径
        try:
            # 尝试从包内获取资源路径
            self.fallback_dir = Path(pkg_resources.resource_filename('clash_cli', 'resources/fallback'))
        except Exception:
            # 如果失败，回退到开发环境路径
            self.fallback_dir = Path(__file__).parent.parent / "resources" / "fallback"

        self.version_file = self.base_dir / "tool_versions.json"
        
        # 工具配置
        self.tools_config = {
            "yq": {
                "name": "yq",
                "description": "YAML 处理工具",
                "github_repo": "mikefarah/yq",
                "fallback_version": "v4.40.5",
                "filename_template": "yq_linux_{arch}.tar.gz",
                "executable_name": "yq",
                "required": True
            },
            "mihomo": {
                "name": "mihomo",
                "description": "Mihomo 内核",
                "github_repo": "MetaCubeX/mihomo",
                "fallback_version": "v1.17.0",
                "filename_template": "mihomo-linux-{arch}-{version}.gz",
                "executable_name": "mihomo",
                "required": True
            },
            "clash": {
                "name": "clash",
                "description": "Clash 内核",
                "github_repo": "Dreamacro/clash",
                "fallback_version": "v1.18.0",
                "filename_template": "clash-linux-{arch}-{version}.gz",
                "executable_name": "clash",
                "required": False
            }
        }
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        try:
            self.bin_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
            self.cache_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
        except PermissionError:
            # 如果没有权限创建系统目录，这是正常的，会在需要时提示用户使用 sudo
            pass
    
    def _get_arch(self) -> str:
        """获取系统架构"""
        import platform
        arch_map = {
            'x86_64': 'amd64',
            'aarch64': 'arm64',
            'armv7l': 'armv7'
        }
        return arch_map.get(platform.machine(), 'amd64')
    
    def _load_versions(self) -> Dict:
        """加载版本信息"""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, PermissionError):
                pass
        return {}
    
    def _save_versions(self, versions: Dict):
        """保存版本信息"""
        try:
            with open(self.version_file, 'w') as f:
                json.dump(versions, f, indent=2)
        except PermissionError:
            warning_message("无法保存版本信息，可能需要 sudo 权限")
    
    def _get_latest_version(self, tool_name: str) -> Optional[str]:
        """获取工具的最新版本"""
        if tool_name not in self.tools_config:
            return None
        
        repo = self.tools_config[tool_name]["github_repo"]
        try:
            # 创建带重试的会话
            session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            response = session.get(
                f"https://api.github.com/repos/{repo}/releases/latest",
                timeout=10
            )
            response.raise_for_status()
            return response.json()["tag_name"]
        except Exception:
            return None
    
    def _check_tool_exists(self, tool_name: str) -> Tuple[bool, Optional[str]]:
        """检查工具是否已存在并获取版本"""
        tool_path = self.bin_dir / self.tools_config[tool_name]["executable_name"]
        
        if not tool_path.exists():
            return False, None
        
        # 检查文件权限
        if not os.access(tool_path, os.X_OK):
            return False, None
        
        # 尝试获取版本
        try:
            result = subprocess.run(
                [str(tool_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # 从输出中提取版本号（简单实现）
                version_line = result.stdout.strip().split('\n')[0]
                return True, version_line
        except Exception:
            pass
        
        return True, "unknown"
    
    def _download_file(self, url: str, dest_path: Path, timeout: int = 30) -> bool:
        """下载文件"""
        try:
            info_message(f"📥 正在下载: {url}")
            
            # 创建带重试的会话
            session = requests.Session()
            retry_strategy = Retry(
                total=2,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            response = session.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # 确保目标目录存在
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            success_message(f"✅ 下载完成: {dest_path.name}")
            return True
            
        except Exception as e:
            error_message(f"❌ 下载失败: {e}")
            return False
    
    def _extract_archive(self, archive_path: Path, extract_to: Path, executable_name: str) -> bool:
        """解压文件并提取可执行文件"""
        try:
            if archive_path.suffix == '.gz' and not archive_path.name.endswith('.tar.gz'):
                # 处理 .gz 文件（如 mihomo, clash）
                with gzip.open(archive_path, 'rb') as f_in:
                    executable_path = extract_to / executable_name
                    with open(executable_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                    os.chmod(executable_path, 0o755)
            
            elif archive_path.name.endswith('.tar.gz'):
                # 处理 .tar.gz 文件（如 yq）
                with tarfile.open(archive_path, 'r:gz') as tar:
                    # 查找可执行文件
                    for member in tar.getmembers():
                        if member.name.endswith(executable_name) or member.name == executable_name:
                            member.name = executable_name  # 重命名为标准名称
                            tar.extract(member, extract_to)
                            executable_path = extract_to / executable_name
                            os.chmod(executable_path, 0o755)
                            break
                    else:
                        # 如果没找到，提取第一个可执行文件
                        for member in tar.getmembers():
                            if member.isfile() and (member.mode & 0o111):
                                member.name = executable_name
                                tar.extract(member, extract_to)
                                executable_path = extract_to / executable_name
                                os.chmod(executable_path, 0o755)
                                break
            
            elif archive_path.suffix == '.zip':
                # 处理 .zip 文件
                with zipfile.ZipFile(archive_path, 'r') as zip_file:
                    for file_info in zip_file.filelist:
                        if file_info.filename.endswith(executable_name):
                            file_info.filename = executable_name
                            zip_file.extract(file_info, extract_to)
                            executable_path = extract_to / executable_name
                            os.chmod(executable_path, 0o755)
                            break
            
            return True
            
        except Exception as e:
            error_message(f"❌ 解压失败: {e}")
            return False
    
    def _use_fallback_version(self, tool_name: str) -> bool:
        """使用预置的备用版本"""
        config = self.tools_config[tool_name]
        fallback_version = config["fallback_version"]
        arch = self._get_arch()
        
        # 构建备用文件名
        filename = config["filename_template"].format(
            arch=arch,
            version=fallback_version
        )
        
        fallback_file = self.fallback_dir / filename
        
        if not fallback_file.exists():
            error_message(f"❌ 预置版本不存在: {fallback_file}")
            return False
        
        info_message(f"📦 使用预置版本: {tool_name} {fallback_version}")
        
        # 复制到缓存目录
        cache_file = self.cache_dir / filename
        try:
            shutil.copy2(fallback_file, cache_file)
            
            # 解压并安装
            if self._extract_archive(cache_file, self.bin_dir, config["executable_name"]):
                success_message(f"✅ {config['description']} {fallback_version} 安装完成")
                
                # 更新版本信息
                versions = self._load_versions()
                versions[tool_name] = {
                    "version": fallback_version,
                    "source": "fallback",
                    "install_time": datetime.datetime.now().isoformat()
                }
                self._save_versions(versions)
                
                return True
            
        except Exception as e:
            error_message(f"❌ 安装预置版本失败: {e}")

        return False

    def install_tool(self, tool_name: str, force_download: bool = False, use_fallback: bool = False) -> bool:
        """安装单个工具"""
        if tool_name not in self.tools_config:
            error_message(f"❌ 未知工具: {tool_name}")
            return False

        config = self.tools_config[tool_name]

        # 检查工具是否已存在
        if not force_download:
            exists, current_version = self._check_tool_exists(tool_name)
            if exists:
                success_message(f"✅ {config['description']} 已存在 ({current_version})，跳过安装")
                return True

        # 如果强制使用备用版本
        if use_fallback:
            return self._use_fallback_version(tool_name)

        # 尝试获取最新版本
        latest_version = self._get_latest_version(tool_name)
        if not latest_version:
            warning_message(f"⚠️  无法获取 {tool_name} 的最新版本信息")
            latest_version = config["fallback_version"]

        # 构建下载 URL
        arch = self._get_arch()
        filename = config["filename_template"].format(
            arch=arch,
            version=latest_version
        )

        repo = config["github_repo"]
        download_url = f"https://github.com/{repo}/releases/download/{latest_version}/{filename}"

        # 尝试下载
        cache_file = self.cache_dir / filename
        download_success = self._download_file(download_url, cache_file)

        if download_success:
            # 下载成功，解压安装
            if self._extract_archive(cache_file, self.bin_dir, config["executable_name"]):
                success_message(f"✅ {config['description']} {latest_version} 安装完成")

                # 更新版本信息
                versions = self._load_versions()
                versions[tool_name] = {
                    "version": latest_version,
                    "source": "download",
                    "install_time": datetime.datetime.now().isoformat()
                }
                self._save_versions(versions)

                return True
            else:
                error_message(f"❌ {config['description']} 安装失败")

        # 下载失败，询问是否使用备用版本
        if not use_fallback:
            info_message("")
            warning_message(f"🤔 网络下载失败，是否使用预置的稳定版本？")
            info_message(f"   预置版本：{tool_name} {config['fallback_version']}")
            info_message(f"   最新版本：{tool_name} {latest_version or 'unknown'}")
            info_message("")
            info_message("   选择预置版本后，您可以稍后使用 'clash-cli update-tools' 升级")
            info_message("")

            try:
                choice = input("是否使用预置版本？(y/n): ").strip().lower()
                if choice in ['y', 'yes', '是']:
                    return self._use_fallback_version(tool_name)
                else:
                    error_message(f"❌ 跳过 {config['description']} 安装")
                    return False
            except (KeyboardInterrupt, EOFError):
                error_message(f"❌ 用户取消 {config['description']} 安装")
                return False

        return False

    def install_required_tools(self, force_download: bool = False, use_fallback: bool = False) -> bool:
        """安装所有必需的工具"""
        info_message("🔍 检查必需工具...")

        success_count = 0
        required_tools = [name for name, config in self.tools_config.items() if config["required"]]

        for tool_name in required_tools:
            info_message(f"\n📦 处理工具: {self.tools_config[tool_name]['description']}")

            if self.install_tool(tool_name, force_download, use_fallback):
                success_count += 1
            else:
                error_message(f"❌ {self.tools_config[tool_name]['description']} 安装失败")

                # 如果是必需工具安装失败，询问是否继续
                if not use_fallback:
                    try:
                        choice = input("是否继续安装其他工具？(y/n): ").strip().lower()
                        if choice not in ['y', 'yes', '是']:
                            break
                    except (KeyboardInterrupt, EOFError):
                        break

        if success_count == len(required_tools):
            success_message(f"🎉 所有必需工具安装完成 ({success_count}/{len(required_tools)})")
            return True
        else:
            warning_message(f"⚠️  部分工具安装完成 ({success_count}/{len(required_tools)})")
            return False

    def check_tools_status(self) -> Dict[str, Dict]:
        """检查所有工具的状态"""
        status = {}
        versions = self._load_versions()

        for tool_name, config in self.tools_config.items():
            exists, current_version = self._check_tool_exists(tool_name)
            latest_version = self._get_latest_version(tool_name)

            status[tool_name] = {
                "name": config["description"],
                "exists": exists,
                "current_version": current_version,
                "latest_version": latest_version,
                "installed_info": versions.get(tool_name, {}),
                "required": config["required"]
            }

        return status

    def update_tools(self, tool_names: Optional[List[str]] = None) -> bool:
        """更新工具到最新版本"""
        if tool_names is None:
            tool_names = list(self.tools_config.keys())

        info_message("🔍 检查工具更新...")

        updates_available = []
        for tool_name in tool_names:
            if tool_name not in self.tools_config:
                continue

            exists, current_version = self._check_tool_exists(tool_name)
            if not exists:
                continue

            latest_version = self._get_latest_version(tool_name)
            if latest_version and latest_version != current_version:
                updates_available.append((tool_name, current_version, latest_version))

        if not updates_available:
            success_message("✅ 所有工具都是最新版本")
            return True

        # 显示可用更新
        info_message("📦 发现以下更新:")
        for tool_name, current, latest in updates_available:
            config = self.tools_config[tool_name]
            info_message(f"   {config['description']}: {current} → {latest}")

        try:
            choice = input("\n是否更新这些工具？(y/n): ").strip().lower()
            if choice not in ['y', 'yes', '是']:
                info_message("取消更新")
                return True
        except (KeyboardInterrupt, EOFError):
            info_message("取消更新")
            return True

        # 执行更新
        success_count = 0
        for tool_name, _, _ in updates_available:
            info_message(f"\n🔄 更新 {self.tools_config[tool_name]['description']}...")
            if self.install_tool(tool_name, force_download=True):
                success_count += 1

        if success_count == len(updates_available):
            success_message(f"🎉 所有工具更新完成 ({success_count}/{len(updates_available)})")
        else:
            warning_message(f"⚠️  部分工具更新完成 ({success_count}/{len(updates_available)})")

        return success_count > 0
