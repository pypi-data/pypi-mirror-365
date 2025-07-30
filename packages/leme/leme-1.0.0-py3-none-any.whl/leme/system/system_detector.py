"""Módulo para detectar sistema operacional e arquitetura."""

import platform
import subprocess
import os
from typing import Dict, Optional
from enum import Enum


class OperatingSystem(str, Enum):
    """Sistemas operacionais suportados."""
    UBUNTU = "ubuntu"
    DEBIAN = "debian" 
    CENTOS = "centos"
    FEDORA = "fedora"
    RHEL = "rhel"
    MACOS = "macos"
    WINDOWS = "windows"
    WSL_UBUNTU = "wsl_ubuntu"
    WSL_DEBIAN = "wsl_debian"
    UNKNOWN = "unknown"


class Architecture(str, Enum):
    """Arquiteturas suportadas."""
    X86_64 = "x86_64"
    ARM64 = "arm64"
    AARCH64 = "aarch64"
    UNKNOWN = "unknown"


class SystemInfo:
    """Informações do sistema."""
    
    def __init__(self, os_type: OperatingSystem, architecture: Architecture, 
                 is_wsl: bool = False, distro_version: Optional[str] = None):
        self.os_type = os_type
        self.architecture = architecture
        self.is_wsl = is_wsl
        self.distro_version = distro_version
    
    def __str__(self):
        wsl_str = " (WSL)" if self.is_wsl else ""
        version_str = f" {self.distro_version}" if self.distro_version else ""
        return f"{self.os_type.value}{version_str} {self.architecture.value}{wsl_str}"


class SystemDetector:
    """Detector de sistema operacional e arquitetura."""
    
    @staticmethod
    def detect() -> SystemInfo:
        """
        Detecta o sistema operacional atual.
        
        Returns:
            SystemInfo com informações do sistema
        """
        # Detectar arquitetura
        arch = SystemDetector._detect_architecture()
        
        # Detectar se está no WSL
        is_wsl = SystemDetector._is_wsl()
        
        # Detectar sistema operacional
        system = platform.system().lower()
        
        if system == "linux":
            return SystemDetector._detect_linux_distro(arch, is_wsl)
        elif system == "darwin":
            return SystemDetector._detect_macos(arch)
        elif system == "windows":
            return SystemInfo(OperatingSystem.WINDOWS, arch)
        else:
            return SystemInfo(OperatingSystem.UNKNOWN, arch)
    
    @staticmethod
    def _detect_architecture() -> Architecture:
        """Detecta a arquitetura do processador."""
        machine = platform.machine().lower()
        
        if machine in ["x86_64", "amd64"]:
            return Architecture.X86_64
        elif machine in ["arm64", "aarch64"]:
            return Architecture.ARM64
        else:
            return Architecture.UNKNOWN
    
    @staticmethod
    def _is_wsl() -> bool:
        """Verifica se está rodando no WSL."""
        try:
            # Verificar se existe /proc/version com Microsoft
            if os.path.exists("/proc/version"):
                with open("/proc/version", "r") as f:
                    content = f.read().lower()
                    return "microsoft" in content or "wsl" in content
            return False
        except:
            return False
    
    @staticmethod
    def _detect_linux_distro(arch: Architecture, is_wsl: bool) -> SystemInfo:
        """Detecta a distribuição Linux."""
        distro_info = SystemDetector._get_distro_info()
        distro_name = distro_info.get("name", "").lower()
        version = distro_info.get("version", "")
        
        # Ubuntu
        if "ubuntu" in distro_name:
            os_type = OperatingSystem.WSL_UBUNTU if is_wsl else OperatingSystem.UBUNTU
            return SystemInfo(os_type, arch, is_wsl, version)
        
        # Debian
        elif "debian" in distro_name:
            os_type = OperatingSystem.WSL_DEBIAN if is_wsl else OperatingSystem.DEBIAN
            return SystemInfo(os_type, arch, is_wsl, version)
        
        # CentOS
        elif "centos" in distro_name:
            return SystemInfo(OperatingSystem.CENTOS, arch, is_wsl, version)
        
        # Fedora
        elif "fedora" in distro_name:
            return SystemInfo(OperatingSystem.FEDORA, arch, is_wsl, version)
        
        # RHEL
        elif "red hat" in distro_name or "rhel" in distro_name:
            return SystemInfo(OperatingSystem.RHEL, arch, is_wsl, version)
        
        else:
            return SystemInfo(OperatingSystem.UNKNOWN, arch, is_wsl, version)
    
    @staticmethod
    def _detect_macos(arch: Architecture) -> SystemInfo:
        """Detecta versão do macOS."""
        try:
            version = platform.mac_ver()[0]
            return SystemInfo(OperatingSystem.MACOS, arch, False, version)
        except:
            return SystemInfo(OperatingSystem.MACOS, arch)
    
    @staticmethod
    def _get_distro_info() -> Dict[str, str]:
        """Obtém informações da distribuição Linux."""
        info = {}
        
        # Tentar /etc/os-release primeiro
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        value = value.strip('"')
                        if key == "NAME":
                            info["name"] = value
                        elif key == "VERSION":
                            info["version"] = value
        except:
            pass
        
        # Fallback para /etc/lsb-release
        if not info:
            try:
                with open("/etc/lsb-release", "r") as f:
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            value = value.strip('"')
                            if key == "DISTRIB_ID":
                                info["name"] = value
                            elif key == "DISTRIB_RELEASE":
                                info["version"] = value
            except:
                pass
        
        # Fallback para uname
        if not info:
            try:
                result = subprocess.run(["uname", "-a"], capture_output=True, text=True)
                if result.returncode == 0:
                    uname_output = result.stdout.lower()
                    if "ubuntu" in uname_output:
                        info["name"] = "Ubuntu"
                    elif "debian" in uname_output:
                        info["name"] = "Debian"
            except:
                pass
        
        return info
    
    @staticmethod
    def get_package_manager(os_type: OperatingSystem) -> Optional[str]:
        """Retorna o gerenciador de pacotes para o sistema."""
        package_managers = {
            OperatingSystem.UBUNTU: "apt",
            OperatingSystem.WSL_UBUNTU: "apt",
            OperatingSystem.DEBIAN: "apt", 
            OperatingSystem.WSL_DEBIAN: "apt",
            OperatingSystem.CENTOS: "yum",
            OperatingSystem.FEDORA: "dnf",
            OperatingSystem.RHEL: "yum",
            OperatingSystem.MACOS: "brew"
        }
        return package_managers.get(os_type)
    
    @staticmethod
    def supports_docker_installation(os_type: OperatingSystem) -> bool:
        """Verifica se o sistema suporta instalação automática do Docker."""
        supported_systems = [
            OperatingSystem.UBUNTU,
            OperatingSystem.WSL_UBUNTU,
            OperatingSystem.DEBIAN,
            OperatingSystem.WSL_DEBIAN,
            OperatingSystem.CENTOS,
            OperatingSystem.FEDORA,
            OperatingSystem.RHEL,
            OperatingSystem.MACOS
        ]
        return os_type in supported_systems