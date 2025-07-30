"""Instalador do Docker para Ubuntu/Debian."""

import subprocess
from typing import List
from rich import print

from .base_installer import BaseInstaller


class UbuntuInstaller(BaseInstaller):
    """Instalador do Docker para Ubuntu e Debian."""
    
    def install(self) -> bool:
        """
        Instala o Docker no Ubuntu/Debian.
        
        Returns:
            bool: True se a instalação foi bem-sucedida
        """
        print(f":package: Instalando Docker no {self.system_info.os_type.value}...")
        
        try:
            # 1. Atualizar repositórios
            print("  [blue]1/6[/blue] Atualizando repositórios...")
            self._run_command(["sudo", "apt", "update"])
            
            # 2. Instalar dependências
            print("  [blue]2/6[/blue] Instalando dependências...")
            dependencies = [
                "apt-transport-https",
                "ca-certificates", 
                "curl",
                "gnupg",
                "lsb-release"
            ]
            cmd = ["sudo", "apt", "install", "-y"] + dependencies
            self._run_command(cmd)
            
            # 3. Adicionar chave GPG oficial do Docker
            print("  [blue]3/6[/blue] Adicionando chave GPG do Docker...")
            self._run_command([
                "curl", "-fsSL", "https://download.docker.com/linux/ubuntu/gpg",
                "|", "sudo", "gpg", "--dearmor", "-o", "/usr/share/keyrings/docker-archive-keyring.gpg"
            ], shell=True)
            
            # 4. Adicionar repositório do Docker
            print("  [blue]4/6[/blue] Adicionando repositório do Docker...")
            distro = "ubuntu" if "ubuntu" in self.system_info.os_type.value else "debian"
            repo_cmd = [
                "echo",
                f'"deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/{distro} $(lsb_release -cs) stable"',
                "|", "sudo", "tee", "/etc/apt/sources.list.d/docker.list", ">", "/dev/null"
            ]
            self._run_command(repo_cmd, shell=True)
            
            # 5. Atualizar repositórios novamente
            print("  [blue]5/6[/blue] Atualizando repositórios com Docker...")
            self._run_command(["sudo", "apt", "update"])
            
            # 6. Instalar Docker
            print("  [blue]6/6[/blue] Instalando Docker CE...")
            self._run_command([
                "sudo", "apt", "install", "-y", 
                "docker-ce", "docker-ce-cli", "containerd.io"
            ])
            
            # Configurar Docker para usuário atual
            self._configure_docker_user()
            
            print("  [green]✓[/green] Docker instalado com sucesso!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  [red]✗[/red] Erro durante a instalação: {e}")
            return False
        except Exception as e:
            print(f"  [red]✗[/red] Erro inesperado: {e}")
            return False
    
    def _configure_docker_user(self) -> None:
        """Configura o Docker para o usuário atual."""
        try:
            print("  [yellow]📝[/yellow] Configurando permissões do Docker...")
            
            # Adicionar usuário ao grupo docker
            import os
            username = os.getenv("USER")
            if username:
                self._run_command(["sudo", "usermod", "-aG", "docker", username])
                print(f"  [green]✓[/green] Usuário {username} adicionado ao grupo docker")
                print("  [yellow]⚠[/yellow] Faça logout/login para aplicar as permissões")
            
            # Iniciar serviço Docker
            self._run_command(["sudo", "systemctl", "enable", "docker"])
            self._run_command(["sudo", "systemctl", "start", "docker"])
            
        except Exception as e:
            print(f"  [yellow]![/yellow] Aviso: Erro na configuração de usuário: {e}")
    
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
            self._run_command([
                "sudo", "apt", "remove", "-y",
                "docker-ce", "docker-ce-cli", "containerd.io"
            ])
            
            # Remover repositório (opcional)
            self._run_command([
                "sudo", "rm", "-f", "/etc/apt/sources.list.d/docker.list"
            ], ignore_errors=True)
            
            print("  [green]✓[/green] Docker removido com sucesso!")
            return True
            
        except Exception as e:
            print(f"  [red]✗[/red] Erro durante a remoção: {e}")
            return False
    
    def get_install_commands(self) -> List[str]:
        """Retorna lista de comandos para instalação manual."""
        return [
            "sudo apt update",
            "sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release",
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
            'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null',
            "sudo apt update", 
            "sudo apt install -y docker-ce docker-ce-cli containerd.io",
            "sudo usermod -aG docker $USER",
            "sudo systemctl enable docker",
            "sudo systemctl start docker"
        ]