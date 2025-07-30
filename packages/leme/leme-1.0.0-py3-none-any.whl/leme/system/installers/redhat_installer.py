"""Instalador do Docker para CentOS/RHEL/Fedora."""

import subprocess
from typing import List
from rich import print

from .base_installer import BaseInstaller
from ..system_detector import OperatingSystem


class RedHatInstaller(BaseInstaller):
    """Instalador do Docker para CentOS, RHEL e Fedora."""
    
    def install(self) -> bool:
        """
        Instala o Docker no CentOS/RHEL/Fedora.
        
        Returns:
            bool: True se a instalação foi bem-sucedida
        """
        print(f":package: Instalando Docker no {self.system_info.os_type.value}...")
        
        try:
            if self.system_info.os_type == OperatingSystem.FEDORA:
                return self._install_fedora()
            else:
                return self._install_centos_rhel()
                
        except subprocess.CalledProcessError as e:
            print(f"  [red]✗[/red] Erro durante a instalação: {e}")
            return False
        except Exception as e:
            print(f"  [red]✗[/red] Erro inesperado: {e}")
            return False
    
    def _install_fedora(self) -> bool:
        """Instala Docker no Fedora."""
        print("  [blue]1/5[/blue] Removendo versões antigas...")
        self._run_command([
            "sudo", "dnf", "remove", "-y",
            "docker", "docker-client", "docker-client-latest",
            "docker-common", "docker-latest", "docker-latest-logrotate",
            "docker-logrotate", "docker-engine"
        ], ignore_errors=True)
        
        print("  [blue]2/5[/blue] Instalando dependências...")
        self._run_command([
            "sudo", "dnf", "install", "-y",
            "dnf-plugins-core"
        ])
        
        print("  [blue]3/5[/blue] Adicionando repositório do Docker...")
        self._run_command([
            "sudo", "dnf", "config-manager", "--add-repo",
            "https://download.docker.com/linux/fedora/docker-ce.repo"
        ])
        
        print("  [blue]4/5[/blue] Instalando Docker CE...")
        self._run_command([
            "sudo", "dnf", "install", "-y",
            "docker-ce", "docker-ce-cli", "containerd.io"
        ])
        
        print("  [blue]5/5[/blue] Configurando Docker...")
        self._configure_docker_service()
        
        return True
    
    def _install_centos_rhel(self) -> bool:
        """Instala Docker no CentOS/RHEL."""
        print("  [blue]1/5[/blue] Removendo versões antigas...")
        self._run_command([
            "sudo", "yum", "remove", "-y",
            "docker", "docker-client", "docker-client-latest",
            "docker-common", "docker-latest", "docker-latest-logrotate",
            "docker-logrotate", "docker-engine"
        ], ignore_errors=True)
        
        print("  [blue]2/5[/blue] Instalando dependências...")
        self._run_command([
            "sudo", "yum", "install", "-y",
            "yum-utils"
        ])
        
        print("  [blue]3/5[/blue] Adicionando repositório do Docker...")
        repo_url = "https://download.docker.com/linux/centos/docker-ce.repo"
        self._run_command([
            "sudo", "yum-config-manager", "--add-repo", repo_url
        ])
        
        print("  [blue]4/5[/blue] Instalando Docker CE...")
        self._run_command([
            "sudo", "yum", "install", "-y",
            "docker-ce", "docker-ce-cli", "containerd.io"
        ])
        
        print("  [blue]5/5[/blue] Configurando Docker...")
        self._configure_docker_service()
        
        return True
    
    def _configure_docker_service(self) -> None:
        """Configura o serviço Docker."""
        try:
            # Iniciar e habilitar Docker
            self._run_command(["sudo", "systemctl", "start", "docker"])
            self._run_command(["sudo", "systemctl", "enable", "docker"])
            
            # Adicionar usuário ao grupo docker
            import os
            username = os.getenv("USER")
            if username:
                self._run_command(["sudo", "usermod", "-aG", "docker", username])
                print(f"  [green]✓[/green] Usuário {username} adicionado ao grupo docker")
                print("  [yellow]⚠[/yellow] Faça logout/login para aplicar as permissões")
            
        except Exception as e:
            print(f"  [yellow]![/yellow] Aviso: Erro na configuração: {e}")
    
    def uninstall(self) -> bool:
        """
        Remove o Docker do sistema.
        
        Returns:
            bool: True se a remoção foi bem-sucedida
        """
        try:
            print(":wastebasket: Removendo Docker...")
            
            # Parar serviços
            self._run_command(["sudo", "systemctl", "stop", "docker"], ignore_errors=True)
            self._run_command(["sudo", "systemctl", "disable", "docker"], ignore_errors=True)
            
            # Remover pacotes
            if self.system_info.os_type == OperatingSystem.FEDORA:
                self._run_command([
                    "sudo", "dnf", "remove", "-y",
                    "docker-ce", "docker-ce-cli", "containerd.io"
                ])
            else:
                self._run_command([
                    "sudo", "yum", "remove", "-y",
                    "docker-ce", "docker-ce-cli", "containerd.io"
                ])
            
            print("  [green]✓[/green] Docker removido com sucesso!")
            return True
            
        except Exception as e:
            print(f"  [red]✗[/red] Erro durante a remoção: {e}")
            return False
    
    def get_install_commands(self) -> List[str]:
        """Retorna lista de comandos para instalação manual."""
        if self.system_info.os_type == OperatingSystem.FEDORA:
            return [
                "sudo dnf remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine",
                "sudo dnf install -y dnf-plugins-core",
                "sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo",
                "sudo dnf install -y docker-ce docker-ce-cli containerd.io",
                "sudo systemctl start docker",
                "sudo systemctl enable docker",
                "sudo usermod -aG docker $USER"
            ]
        else:
            return [
                "sudo yum remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine",
                "sudo yum install -y yum-utils",
                "sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo",
                "sudo yum install -y docker-ce docker-ce-cli containerd.io",
                "sudo systemctl start docker",
                "sudo systemctl enable docker",
                "sudo usermod -aG docker $USER"
            ]