"""Instalador do Azure CLI para diferentes sistemas operacionais."""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List
from rich import print

from .base_installer import BaseInstaller
from ..system_detector import SystemInfo, OperatingSystem


class AzureCliInstaller(BaseInstaller):
    """Instalador especializado para Azure CLI."""
    
    def __init__(self, system_info: SystemInfo):
        """
        Inicializa o instalador do Azure CLI.
        
        Args:
            system_info: Informações do sistema operacional
        """
        super().__init__(system_info)
        self.tool_name = "Azure CLI"
        
    def is_installed(self) -> bool:
        """
        Verifica se o Azure CLI está instalado.
        
        Returns:
            bool: True se o Azure CLI estiver instalado
        """
        try:
            result = subprocess.run(
                ["az", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_installed_version(self) -> Optional[str]:
        """
        Obtém a versão instalada do Azure CLI.
        
        Returns:
            Optional[str]: Versão instalada ou None
        """
        try:
            result = subprocess.run(
                ["az", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # O output é JSON-like, pegar a primeira linha que contém "azure-cli"
                for line in result.stdout.split('\n'):
                    if 'azure-cli' in line and 'core' not in line:
                        # azure-cli         2.53.0
                        parts = line.split()
                        if len(parts) >= 2:
                            return parts[1]
            return None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
    
    def install(self) -> bool:
        """
        Instala o Azure CLI baseado no sistema operacional.
        
        Returns:
            bool: True se a instalação foi bem-sucedida
        """
        print(f":gear: [blue]Instalando {self.tool_name}...[/blue]")
        
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
                print(f":warning: [yellow]Sistema {self.system_info.os_type.value} não suportado para instalação automática do Azure CLI[/yellow]")
                return self._show_manual_instructions()
        
        except Exception as e:
            print(f":x: [red]Erro durante instalação do Azure CLI: {str(e)}[/red]")
            return False
    
    def _install_macos(self) -> bool:
        """Instala Azure CLI no macOS."""
        print(":apple: [blue]Detectado macOS - tentando Homebrew primeiro[/blue]")
        
        # Verificar se Homebrew está disponível
        if self._check_homebrew():
            try:
                print(":beer: [blue]Instalando Azure CLI via Homebrew...[/blue]")
                result = subprocess.run([
                    "brew", "install", "azure-cli"
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(":white_check_mark: [green]Azure CLI instalado via Homebrew![/green]")
                    return True
                else:
                    print(f":warning: [yellow]Falha no Homebrew: {result.stderr}[/yellow]")
            except subprocess.TimeoutExpired:
                print(":warning: [yellow]Timeout do Homebrew[/yellow]")
        
        # Fallback para script oficial
        print(":information: [blue]Tentando instalação via script oficial...[/blue]")
        return self._install_via_curl_script()
    
    def _install_ubuntu(self) -> bool:
        """Instala Azure CLI no Ubuntu/Debian."""
        print(":gear: [blue]Detectado Ubuntu/Debian - usando repositório oficial[/blue]")
        
        try:
            # Método 1: Tentar repositório oficial Microsoft
            if self._install_ubuntu_repo():
                return True
            
            # Método 2: Fallback para script de instalação
            print(":information: [blue]Tentando instalação via script oficial...[/blue]")
            return self._install_via_curl_script()
        
        except Exception as e:
            print(f":warning: [yellow]Erro no método de repositório: {str(e)}[/yellow]")
            return self._install_via_curl_script()
    
    def _install_ubuntu_repo(self) -> bool:
        """Instala via repositório oficial da Microsoft."""
        try:
            # Instalar dependências
            print(":package: [blue]Instalando dependências...[/blue]")
            
            # Limpar repositórios corrompidos antes de tentar atualizar
            self._cleanup_corrupted_repositories()
            
            subprocess.run([
                "sudo", "apt-get", "update"
            ], check=True, capture_output=True)
            
            subprocess.run([
                "sudo", "apt-get", "install", "-y", "ca-certificates", "curl", "apt-transport-https", "lsb-release", "gnupg"
            ], check=True, capture_output=True)
            
            # Adicionar chave GPG da Microsoft
            print(":key: [blue]Adicionando chave GPG da Microsoft...[/blue]")
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write("""#!/bin/bash
# Criar diretório de keyrings se não existir
sudo mkdir -p /etc/apt/keyrings
curl -sLS https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/keyrings/microsoft.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/microsoft.gpg
""")
                script_path = f.name
            
            subprocess.run(["bash", script_path], check=True)
            Path(script_path).unlink()
            
            # Adicionar repositório
            print(":package: [blue]Adicionando repositório Microsoft...[/blue]")
            distro = self._get_ubuntu_codename()
            repo_line = f"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ {distro} main"
            
            subprocess.run([
                "bash", "-c", f"echo '{repo_line}' | sudo tee /etc/apt/sources.list.d/azure-cli.list"
            ], check=True)
            
            # Atualizar e instalar
            print(":arrows_counterclockwise: [blue]Atualizando repositórios...[/blue]")
            subprocess.run(["sudo", "apt-get", "update"], check=True, capture_output=True)
            
            print(":package: [blue]Instalando Azure CLI...[/blue]")
            subprocess.run(["sudo", "apt-get", "install", "-y", "azure-cli"], check=True)
            
            print(":white_check_mark: [green]Azure CLI instalado via repositório oficial![/green]")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f":warning: [yellow]Falha no repositório oficial: {e}[/yellow]")
            return False
    
    def _install_redhat(self) -> bool:
        """Instala Azure CLI no CentOS/RHEL/Fedora."""
        print(":gear: [blue]Detectado sistema RedHat - usando repositório oficial[/blue]")
        
        try:
            # Determinar gerenciador de pacotes
            if self.system_info.os_type == OperatingSystem.FEDORA:
                pkg_manager = "dnf"
            else:
                pkg_manager = "yum"
            
            # Importar chave GPG da Microsoft
            print(":key: [blue]Importando chave GPG da Microsoft...[/blue]")
            subprocess.run([
                "sudo", "rpm", "--import", "https://packages.microsoft.com/keys/microsoft.asc"
            ], check=True)
            
            # Adicionar repositório
            print(":package: [blue]Adicionando repositório Microsoft...[/blue]")
            repo_content = """[azure-cli]
name=Azure CLI
baseurl=https://packages.microsoft.com/yumrepos/azure-cli
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc"""
            
            subprocess.run([
                "bash", "-c", f"echo '{repo_content}' | sudo tee /etc/yum.repos.d/azure-cli.repo"
            ], check=True)
            
            # Instalar Azure CLI
            print(":package: [blue]Instalando Azure CLI...[/blue]")
            subprocess.run([
                "sudo", pkg_manager, "install", "-y", "azure-cli"
            ], check=True)
            
            print(":white_check_mark: [green]Azure CLI instalado via repositório oficial![/green]")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f":warning: [yellow]Falha no repositório: {e}[/yellow]")
            return self._install_via_curl_script()
    
    def _install_via_curl_script(self) -> bool:
        """Instala Azure CLI via script oficial (método universal)."""
        print(":globe_with_meridians: [blue]Instalando via script oficial da Microsoft...[/blue]")
        
        try:
            result = subprocess.run([
                "curl", "-sL", "https://aka.ms/InstallAzureCLIDeb"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(":x: [red]Falha ao baixar script de instalação[/red]")
                return False
            
            # Executar script
            process = subprocess.run([
                "sudo", "bash"
            ], input=result.stdout, text=True, capture_output=True, timeout=300)
            
            if process.returncode == 0:
                print(":white_check_mark: [green]Azure CLI instalado via script oficial![/green]")
                return True
            else:
                print(f":x: [red]Falha na execução do script: {process.stderr}[/red]")
                return False
        
        except subprocess.TimeoutExpired:
            print(":x: [red]Timeout durante instalação via script[/red]")
            return False
        except Exception as e:
            print(f":x: [red]Erro na instalação via script: {str(e)}[/red]")
            return False
    
    def _get_ubuntu_codename(self) -> str:
        """Obtém o codename da distribuição Ubuntu."""
        try:
            result = subprocess.run([
                "lsb_release", "-cs"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # Fallback baseado na versão
        version_map = {
            "22.04": "jammy",
            "20.04": "focal", 
            "18.04": "bionic"
        }
        return version_map.get(self.system_info.os_version, "focal")
    
    def _check_homebrew(self) -> bool:
        """Verifica se o Homebrew está instalado."""
        try:
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def _show_manual_instructions(self) -> bool:
        """Mostra instruções para instalação manual."""
        print(":information_source: [cyan]Instruções para instalação manual do Azure CLI:[/cyan]")
        print()
        print("1. Acesse: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        print("2. Escolha o método de instalação para seu sistema operacional")
        print("3. Execute os comandos fornecidos na documentação")
        print("4. Verifique a instalação com: az --version")
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
                "# Via Homebrew (recomendado)",
                "brew install azure-cli",
                "",
                "# Ou via script oficial:",
                "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
            ]
        
        elif self.system_info.os_type in [
            OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
            OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN
        ]:
            return [
                "# Via repositório oficial Microsoft",
                "sudo apt-get update",
                "sudo apt-get install ca-certificates curl apt-transport-https lsb-release gnupg",
                "curl -sLS https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/keyrings/microsoft.gpg > /dev/null",
                "sudo chmod go+r /etc/apt/keyrings/microsoft.gpg",
                f"echo 'deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ {self._get_ubuntu_codename()} main' | sudo tee /etc/apt/sources.list.d/azure-cli.list",
                "sudo apt-get update",
                "sudo apt-get install azure-cli"
            ]
        
        elif self.system_info.os_type in [
            OperatingSystem.CENTOS, OperatingSystem.RHEL, OperatingSystem.FEDORA
        ]:
            pkg_manager = "dnf" if self.system_info.os_type == OperatingSystem.FEDORA else "yum"
            return [
                "# Via repositório oficial Microsoft",
                "sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc",
                "echo -e '[azure-cli]\\nname=Azure CLI\\nbaseurl=https://packages.microsoft.com/yumrepos/azure-cli\\nenabled=1\\ngpgcheck=1\\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc' | sudo tee /etc/yum.repos.d/azure-cli.repo",
                f"sudo {pkg_manager} install azure-cli"
            ]
        
        else:
            return [
                "# Instalação manual",
                "1. Acesse: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli",
                "2. Escolha o método de instalação para seu sistema operacional",
                "3. Execute os comandos fornecidos na documentação",
                "4. Verifique com: az --version"
            ]

    def uninstall(self) -> bool:
        """
        Remove o Azure CLI do sistema.
        
        Returns:
            bool: True se a remoção foi bem-sucedida
        """
        print(f":wastebasket: [blue]Removendo {self.tool_name}...[/blue]")
        
        try:
            if self.system_info.os_type == OperatingSystem.MACOS:
                # Tentar remover via Homebrew primeiro
                try:
                    subprocess.run(["brew", "uninstall", "azure-cli"], check=True)
                    print(":white_check_mark: [green]Azure CLI removido via Homebrew![/green]")
                    return True
                except subprocess.CalledProcessError:
                    pass
            
            elif self.system_info.os_type in [
                OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
                OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN
            ]:
                try:
                    subprocess.run(["sudo", "apt-get", "remove", "-y", "azure-cli"], check=True)
                    print(":white_check_mark: [green]Azure CLI removido via apt![/green]")
                    return True
                except subprocess.CalledProcessError:
                    pass
            
            elif self.system_info.os_type in [
                OperatingSystem.CENTOS, OperatingSystem.RHEL, OperatingSystem.FEDORA
            ]:
                pkg_manager = "dnf" if self.system_info.os_type == OperatingSystem.FEDORA else "yum"
                try:
                    subprocess.run(["sudo", pkg_manager, "remove", "-y", "azure-cli"], check=True)
                    print(f":white_check_mark: [green]Azure CLI removido via {pkg_manager}![/green]")
                    return True
                except subprocess.CalledProcessError:
                    pass
            
            print(":x: [red]Azure CLI não encontrado para remoção[/red]")
            return False
        
        except Exception as e:
            print(f":x: [red]Erro ao remover Azure CLI: {str(e)}[/red]")
            return False
    
    def _cleanup_corrupted_repositories(self) -> None:
        """Remove repositórios corrompidos que podem afetar apt-get update."""
        try:
            print(":broom: [blue]Limpando repositórios corrompidos...[/blue]")
            
            # Lista de arquivos de repositório que podem estar corrompidos
            corrupted_repos = [
                "/etc/apt/sources.list.d/hashicorp.list",
                "/etc/apt/sources.list.d/microsoft-prod.list",
                "/etc/apt/sources.list.d/azure-cli.list"
            ]
            
            # Lista de chaves GPG que podem estar corrompidas
            corrupted_keys = [
                "/etc/apt/keyrings/hashicorp.gpg",
                "/etc/apt/keyrings/microsoft.gpg",
                "/etc/apt/trusted.gpg.d/microsoft.gpg"
            ]
            
            # Remover arquivos de repositório corrompidos
            for repo_file in corrupted_repos:
                subprocess.run([
                    "sudo", "rm", "-f", repo_file
                ], capture_output=True)
            
            # Remover chaves GPG corrompidas
            for key_file in corrupted_keys:
                subprocess.run([
                    "sudo", "rm", "-f", key_file
                ], capture_output=True)
            
            # Tentar atualizar repositórios para limpar cache
            result = subprocess.run([
                "sudo", "apt-get", "update"
            ], capture_output=True)
            
            if result.returncode == 0:
                print(":white_check_mark: [green]Repositórios limpos com sucesso[/green]")
            else:
                print(":warning: [yellow]Aviso: Alguns repositórios ainda podem ter problemas[/yellow]")
            
        except Exception as e:
            print(f":warning: [yellow]Aviso: Não foi possível limpar repositórios: {str(e)}[/yellow]")