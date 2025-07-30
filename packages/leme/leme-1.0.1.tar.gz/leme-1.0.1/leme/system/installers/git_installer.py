"""Instalador do Git para diferentes sistemas operacionais."""

import subprocess
from typing import Optional, List
from rich import print

from .base_installer import BaseInstaller
from ..system_detector import SystemInfo, OperatingSystem


class GitInstaller(BaseInstaller):
    """Instalador especializado para Git."""
    
    def __init__(self, system_info: SystemInfo):
        """
        Inicializa o instalador do Git.
        
        Args:
            system_info: Informações do sistema operacional
        """
        super().__init__(system_info)
        self.tool_name = "Git"
        
    def is_installed(self) -> bool:
        """
        Verifica se o Git está instalado.
        
        Returns:
            bool: True se o Git estiver instalado
        """
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_installed_version(self) -> Optional[str]:
        """
        Obtém a versão instalada do Git.
        
        Returns:
            Optional[str]: Versão instalada ou None
        """
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # git version 2.39.2
                output = result.stdout.strip()
                if "git version" in output:
                    return output.replace("git version", "").strip()
            return None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
    
    def install(self) -> bool:
        """
        Instala o Git baseado no sistema operacional.
        
        Returns:
            bool: True se a instalação foi bem-sucedida
        """
        print(f":gear: [blue]Instalando {self.tool_name}...[/blue]")
        
        # Verificar se já está instalado
        if self.is_installed():
            version = self.get_installed_version()
            print(f":white_check_mark: [green]Git já está instalado (versão {version})[/green]")
            return True
        
        try:
            if self.system_info.os_type == OperatingSystem.MACOS:
                return self._install_macos()
            
            elif self.system_info.os_type in [
                OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
                OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN
            ]:
                return self._install_ubuntu()
            
            elif self.system_info.os_type in [
                OperatingSystem.CENTOS, OperatingSystem.RHEL, OperatingSystem.FEDORA
            ]:
                return self._install_redhat()
            
            else:
                print(f":warning: [yellow]Sistema {self.system_info.os_type.value} não suportado para instalação automática do Git[/yellow]")
                return self._show_manual_instructions()
        
        except Exception as e:
            print(f":x: [red]Erro durante instalação do Git: {str(e)}[/red]")
            return False
    
    def _install_macos(self) -> bool:
        """Instala Git no macOS."""
        print(":apple: [blue]Detectado macOS[/blue]")
        
        # Verificar se Xcode Command Line Tools estão instalados
        if self._check_xcode_tools():
            print(":white_check_mark: [green]Git já disponível via Xcode Command Line Tools![/green]")
            return True
        
        # Verificar se Homebrew está disponível
        if self._check_homebrew():
            return self._install_via_homebrew()
        
        # Instalar Xcode Command Line Tools
        return self._install_xcode_tools()
    
    def _install_ubuntu(self) -> bool:
        """Instala Git no Ubuntu/Debian."""
        print(":gear: [blue]Detectado Ubuntu/Debian - usando apt[/blue]")
        
        try:
            # Atualizar repositórios
            print(":arrows_counterclockwise: [blue]Atualizando repositórios...[/blue]")
            subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)
            
            # Instalar Git
            print(":package: [blue]Instalando Git...[/blue]")
            subprocess.run(["sudo", "apt", "install", "-y", "git"], check=True)
            
            # Verificar instalação
            if self.is_installed():
                version = self.get_installed_version()
                print(f":white_check_mark: [green]Git {version} instalado com sucesso![/green]")
                return True
            else:
                print(":x: [red]Falha na verificação pós-instalação[/red]")
                return False
        
        except subprocess.CalledProcessError as e:
            print(f":x: [red]Erro na instalação via apt: {e}[/red]")
            return self._show_manual_instructions()
    
    def _install_redhat(self) -> bool:
        """Instala Git no CentOS/RHEL/Fedora."""
        print(":gear: [blue]Detectado sistema RedHat[/blue]")
        
        try:
            # Determinar gerenciador de pacotes
            if self.system_info.os_type == OperatingSystem.FEDORA:
                pkg_manager = "dnf"
            else:
                pkg_manager = "yum"
            
            print(f":package: [blue]Instalando Git via {pkg_manager}...[/blue]")
            subprocess.run(["sudo", pkg_manager, "install", "-y", "git"], check=True)
            
            # Verificar instalação
            if self.is_installed():
                version = self.get_installed_version()
                print(f":white_check_mark: [green]Git {version} instalado com sucesso![/green]")
                return True
            else:
                print(":x: [red]Falha na verificação pós-instalação[/red]")
                return False
        
        except subprocess.CalledProcessError as e:
            print(f":x: [red]Erro na instalação via {pkg_manager}: {e}[/red]")
            return self._show_manual_instructions()
    
    def _install_via_homebrew(self) -> bool:
        """Instala Git via Homebrew no macOS."""
        print(":beer: [blue]Instalando Git via Homebrew...[/blue]")
        
        try:
            subprocess.run(["brew", "install", "git"], check=True, timeout=300)
            
            if self.is_installed():
                version = self.get_installed_version()
                print(f":white_check_mark: [green]Git {version} instalado via Homebrew![/green]")
                return True
            else:
                print(":x: [red]Falha na verificação pós-instalação[/red]")
                return False
        
        except subprocess.CalledProcessError as e:
            print(f":warning: [yellow]Falha no Homebrew: {e}[/yellow]")
            return self._install_xcode_tools()
        except subprocess.TimeoutExpired:
            print(":warning: [yellow]Timeout do Homebrew[/yellow]")
            return self._install_xcode_tools()
    
    def _install_xcode_tools(self) -> bool:
        """Instala Xcode Command Line Tools (inclui Git)."""
        print(":hammer_and_wrench: [blue]Instalando Xcode Command Line Tools...[/blue]")
        
        try:
            # Tentar instalar Xcode Command Line Tools
            result = subprocess.run([
                "xcode-select", "--install"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(":information: [blue]Instalação do Xcode Command Line Tools iniciada[/blue]")
                print(":information: [yellow]Uma janela será aberta - siga as instruções para completar a instalação[/yellow]")
                print(":information: [yellow]Após a instalação, execute novamente este comando[/yellow]")
                return False  # Instalação requer interação do usuário
            
            elif "already installed" in result.stderr:
                print(":white_check_mark: [green]Xcode Command Line Tools já instalados![/green]")
                return self.is_installed()
            
            else:
                print(f":x: [red]Falha ao instalar Xcode Command Line Tools: {result.stderr}[/red]")
                return self._show_manual_instructions()
        
        except Exception as e:
            print(f":x: [red]Erro ao instalar Xcode Command Line Tools: {str(e)}[/red]")
            return self._show_manual_instructions()
    
    def _check_xcode_tools(self) -> bool:
        """Verifica se Xcode Command Line Tools estão instalados."""
        try:
            result = subprocess.run([
                "xcode-select", "-p"
            ], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_homebrew(self) -> bool:
        """Verifica se o Homebrew está instalado."""
        try:
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def _show_manual_instructions(self) -> bool:
        """Mostra instruções para instalação manual."""
        print(":information_source: [cyan]Instruções para instalação manual do Git:[/cyan]")
        print()
        
        if self.system_info.os_type == OperatingSystem.MACOS:
            print("macOS:")
            print("1. Instalar Xcode Command Line Tools:")
            print("   xcode-select --install")
            print("2. Ou baixar o Git em: https://git-scm.com/download/mac")
            print("3. Ou instalar Homebrew e executar: brew install git")
        
        elif self.system_info.os_type in [
            OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
            OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN
        ]:
            print("Ubuntu/Debian:")
            print("1. sudo apt update")
            print("2. sudo apt install git")
        
        elif self.system_info.os_type in [
            OperatingSystem.CENTOS, OperatingSystem.RHEL, OperatingSystem.FEDORA
        ]:
            if self.system_info.os_type == OperatingSystem.FEDORA:
                print("Fedora:")
                print("1. sudo dnf install git")
            else:
                print("CentOS/RHEL:")
                print("1. sudo yum install git")
        
        else:
            print("Geral:")
            print("1. Acesse: https://git-scm.com/downloads")
            print("2. Baixe a versão para seu sistema operacional")
            print("3. Siga as instruções de instalação")
        
        print()
        return False
    
    def get_install_commands(self) -> List[str]:
        """
        Retorna lista de comandos para instalação manual.
        
        Returns:
            List[str]: Lista de comandos
        """
        if self.system_info.os_type == OperatingSystem.MACOS:
            return [
                "# Via Xcode Command Line Tools (recomendado)",
                "xcode-select --install",
                "",
                "# Ou via Homebrew:",
                "brew install git",
                "",
                "# Ou baixar instalador:",
                "# https://git-scm.com/download/mac"
            ]
        
        elif self.system_info.os_type in [
            OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
            OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN
        ]:
            return [
                "sudo apt update",
                "sudo apt install git"
            ]
        
        elif self.system_info.os_type in [
            OperatingSystem.CENTOS, OperatingSystem.RHEL, OperatingSystem.FEDORA
        ]:
            if self.system_info.os_type == OperatingSystem.FEDORA:
                return ["sudo dnf install git"]
            else:
                return ["sudo yum install git"]
        
        else:
            return [
                "# Acesse: https://git-scm.com/downloads",
                "# Baixe e instale a versão para seu sistema operacional"
            ]

    def uninstall(self) -> bool:
        """
        Remove o Git do sistema.
        
        Returns:
            bool: True se a remoção foi bem-sucedida
        """
        print(f":wastebasket: [blue]Removendo {self.tool_name}...[/blue]")
        
        try:
            if self.system_info.os_type == OperatingSystem.MACOS:
                # No macOS, Git geralmente vem com Xcode Tools ou Homebrew
                if self._check_homebrew():
                    try:
                        subprocess.run(["brew", "uninstall", "git"], check=True)
                        print(":white_check_mark: [green]Git removido via Homebrew![/green]")
                        return True
                    except subprocess.CalledProcessError:
                        pass
                
                print(":information: [yellow]No macOS, Git geralmente vem com Xcode Command Line Tools[/yellow]")
                print(":information: [yellow]Para remover completamente, desinstale Xcode Command Line Tools[/yellow]")
                return False
            
            elif self.system_info.os_type in [
                OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
                OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN
            ]:
                subprocess.run(["sudo", "apt", "remove", "-y", "git"], check=True)
                print(":white_check_mark: [green]Git removido via apt![/green]")
                return True
            
            elif self.system_info.os_type in [
                OperatingSystem.CENTOS, OperatingSystem.RHEL, OperatingSystem.FEDORA
            ]:
                pkg_manager = "dnf" if self.system_info.os_type == OperatingSystem.FEDORA else "yum"
                subprocess.run(["sudo", pkg_manager, "remove", "-y", "git"], check=True)
                print(f":white_check_mark: [green]Git removido via {pkg_manager}![/green]")
                return True
            
            else:
                print(":information: [yellow]Remoção manual necessária para este sistema[/yellow]")
                return False
        
        except subprocess.CalledProcessError as e:
            print(f":x: [red]Erro ao remover Git: {e}[/red]")
            return False
        except Exception as e:
            print(f":x: [red]Erro ao remover Git: {str(e)}[/red]")
            return False
    
    def configure_git(self, name: Optional[str] = None, email: Optional[str] = None) -> bool:
        """
        Configura Git com nome e email do usuário.
        
        Args:
            name: Nome do usuário
            email: Email do usuário
            
        Returns:
            bool: True se a configuração foi bem-sucedida
        """
        if not self.is_installed():
            print(":x: [red]Git não está instalado[/red]")
            return False
        
        try:
            print(":gear: [blue]Configurando Git...[/blue]")
            
            if name:
                subprocess.run(["git", "config", "--global", "user.name", name], check=True)
                print(f":white_check_mark: [green]Nome configurado: {name}[/green]")
            
            if email:
                subprocess.run(["git", "config", "--global", "user.email", email], check=True)
                print(f":white_check_mark: [green]Email configurado: {email}[/green]")
            
            # Configurações recomendadas
            subprocess.run(["git", "config", "--global", "init.defaultBranch", "main"], check=True)
            subprocess.run(["git", "config", "--global", "pull.rebase", "false"], check=True)
            
            print(":white_check_mark: [green]Git configurado com sucesso![/green]")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f":x: [red]Erro ao configurar Git: {e}[/red]")
            return False
    
    def show_config(self) -> bool:
        """
        Mostra a configuração atual do Git.
        
        Returns:
            bool: True se conseguiu mostrar a configuração
        """
        if not self.is_installed():
            print(":x: [red]Git não está instalado[/red]")
            return False
        
        try:
            print(":gear: [blue]Configuração atual do Git:[/blue]")
            
            # Nome
            try:
                result = subprocess.run(["git", "config", "--global", "user.name"], 
                                     capture_output=True, text=True, check=True)
                print(f":person: [green]Nome: {result.stdout.strip()}[/green]")
            except subprocess.CalledProcessError:
                print(":warning: [yellow]Nome não configurado[/yellow]")
            
            # Email
            try:
                result = subprocess.run(["git", "config", "--global", "user.email"], 
                                     capture_output=True, text=True, check=True)
                print(f":email: [green]Email: {result.stdout.strip()}[/green]")
            except subprocess.CalledProcessError:
                print(":warning: [yellow]Email não configurado[/yellow]")
            
            return True
        
        except Exception as e:
            print(f":x: [red]Erro ao mostrar configuração: {str(e)}[/red]")
            return False