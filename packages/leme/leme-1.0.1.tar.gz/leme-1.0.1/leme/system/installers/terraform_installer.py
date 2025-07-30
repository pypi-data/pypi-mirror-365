"""Instalador do Terraform para diferentes sistemas operacionais."""

import subprocess
import os
import tempfile
import zipfile
import stat
from pathlib import Path
from typing import Optional, List
from rich import print

from .base_installer import BaseInstaller
from ..system_detector import SystemInfo, OperatingSystem


class TerraformInstaller(BaseInstaller):
    """Instalador especializado para Terraform."""
    
    def __init__(self, system_info: SystemInfo):
        """
        Inicializa o instalador do Terraform.
        
        Args:
            system_info: Informações do sistema operacional
        """
        super().__init__(system_info)
        self.tool_name = "Terraform"
        
    def is_installed(self) -> bool:
        """
        Verifica se o Terraform está instalado.
        
        Returns:
            bool: True se o Terraform estiver instalado
        """
        try:
            result = subprocess.run(
                ["terraform", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_installed_version(self) -> Optional[str]:
        """
        Obtém a versão instalada do Terraform.
        
        Returns:
            Optional[str]: Versão instalada ou None
        """
        try:
            result = subprocess.run(
                ["terraform", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Terraform v1.5.7
                first_line = result.stdout.strip().split('\n')[0]
                if "Terraform" in first_line:
                    return first_line.replace("Terraform", "").strip()
            return None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
    
    def install(self) -> bool:
        """
        Instala o Terraform baseado no sistema operacional.
        
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
                print(f":warning: [yellow]Sistema {self.system_info.os_type.value} não suportado para instalação automática do Terraform[/yellow]")
                return self._show_manual_instructions()
        
        except Exception as e:
            print(f":x: [red]Erro durante instalação do Terraform: {str(e)}[/red]")
            return False
    
    def _install_macos(self) -> bool:
        """Instala Terraform no macOS."""
        print(":apple: [blue]Detectado macOS - tentando Homebrew primeiro[/blue]")
        
        # Verificar se Homebrew está disponível
        if self._check_homebrew():
            try:
                print(":beer: [blue]Instalando Terraform via Homebrew...[/blue]")
                result = subprocess.run([
                    "brew", "install", "terraform"
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(":white_check_mark: [green]Terraform instalado via Homebrew![/green]")
                    return True
                else:
                    print(f":warning: [yellow]Falha no Homebrew: {result.stderr}[/yellow]")
            except subprocess.TimeoutExpired:
                print(":warning: [yellow]Timeout do Homebrew[/yellow]")
        
        # Fallback para download manual
        print(":information: [blue]Tentando instalação via download oficial...[/blue]")
        return self._install_via_download()
    
    def _install_ubuntu(self) -> bool:
        """Instala Terraform no Ubuntu/Debian."""
        print(":gear: [blue]Detectado Ubuntu/Debian - usando repositório HashiCorp[/blue]")
        
        try:
            # Método 1: Tentar repositório oficial HashiCorp
            if self._install_ubuntu_repo():
                return True
            
            # Método 2: Fallback para download manual
            print(":information: [blue]Tentando instalação via download oficial...[/blue]")
            return self._install_via_download()
        
        except Exception as e:
            print(f":warning: [yellow]Erro no método de repositório: {str(e)}[/yellow]")
            return self._install_via_download()
    
    def _install_ubuntu_repo(self) -> bool:
        """Instala via repositório oficial da HashiCorp."""
        try:
            # Instalar dependências
            print(":package: [blue]Instalando dependências...[/blue]")
            subprocess.run([
                "sudo", "apt-get", "update"
            ], check=True, capture_output=True)
            
            subprocess.run([
                "sudo", "apt-get", "install", "-y", "gnupg", "software-properties-common", "curl"
            ], check=True, capture_output=True)
            
            # Adicionar chave GPG da HashiCorp
            print(":key: [blue]Adicionando chave GPG da HashiCorp...[/blue]")
            subprocess.run([
                "sudo", "mkdir", "-p", "/etc/apt/keyrings"
            ], capture_output=True)
            
            subprocess.run([
                "bash", "-c",
                "curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/hashicorp.gpg"
            ], check=True, capture_output=True)
            
            # Adicionar repositório
            print(":package: [blue]Adicionando repositório HashiCorp...[/blue]")
            
            # Verificar se lsb_release funciona corretamente
            try:
                codename_result = subprocess.run(["lsb_release", "-cs"], capture_output=True, text=True, check=True)
                codename = codename_result.stdout.strip()
                if not codename:
                    raise subprocess.CalledProcessError(1, "lsb_release -cs")
            except subprocess.CalledProcessError:
                # Fallback para distribuições sem lsb_release ou com problemas
                print(":warning: [yellow]lsb_release falhou, usando codename padrão[/yellow]")
                codename = "bookworm"  # Debian 12 padrão
            
            repo_line = f"deb [signed-by=/etc/apt/keyrings/hashicorp.gpg] https://apt.releases.hashicorp.com {codename} main"
            subprocess.run([
                "bash", "-c",
                f"echo '{repo_line}' | sudo tee /etc/apt/sources.list.d/hashicorp.list"
            ], check=True)
            
            # Atualizar e instalar
            print(":arrows_counterclockwise: [blue]Atualizando repositórios...[/blue]")
            subprocess.run(["sudo", "apt-get", "update"], check=True, capture_output=True)
            
            print(":package: [blue]Instalando Terraform...[/blue]")
            subprocess.run(["sudo", "apt-get", "install", "-y", "terraform"], check=True)
            
            print(":white_check_mark: [green]Terraform instalado via repositório HashiCorp![/green]")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f":warning: [yellow]Falha no repositório HashiCorp: {e}[/yellow]")
            # Limpar repositório corrompido para não afetar outras instalações
            self._cleanup_failed_repository()
            return False
    
    def _install_redhat(self) -> bool:
        """Instala Terraform no CentOS/RHEL/Fedora."""
        print(":gear: [blue]Detectado sistema RedHat - usando repositório HashiCorp[/blue]")
        
        try:
            # Determinar gerenciador de pacotes
            if self.system_info.os_type == OperatingSystem.FEDORA:
                pkg_manager = "dnf"
            else:
                pkg_manager = "yum"
            
            # Instalar yum-utils se necessário
            subprocess.run([
                "sudo", pkg_manager, "install", "-y", "yum-utils"
            ], check=True, capture_output=True)
            
            # Adicionar repositório HashiCorp
            print(":package: [blue]Adicionando repositório HashiCorp...[/blue]")
            subprocess.run([
                "sudo", "yum-config-manager", "--add-repo", "https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo"
            ], check=True)
            
            # Instalar Terraform
            print(":package: [blue]Instalando Terraform...[/blue]")
            subprocess.run([
                "sudo", pkg_manager, "install", "-y", "terraform"
            ], check=True)
            
            print(":white_check_mark: [green]Terraform instalado via repositório HashiCorp![/green]")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f":warning: [yellow]Falha no repositório: {e}[/yellow]")
            return self._install_via_download()
    
    def _install_via_download(self) -> bool:
        """Instala Terraform via download direto (método universal)."""
        print(":globe_with_meridians: [blue]Instalando via download oficial da HashiCorp...[/blue]")
        
        try:
            # Detectar arquitetura e SO
            arch = self._get_architecture()
            os_name = self._get_os_name()
            
            if not arch or not os_name:
                print(":x: [red]Não foi possível detectar arquitetura ou SO[/red]")
                return False
            
            # URL de download (sempre pegar a versão mais recente seria ideal, mas vamos usar uma estável)
            version = "1.5.7"  # Versão estável conhecida
            url = f"https://releases.hashicorp.com/terraform/{version}/terraform_{version}_{os_name}_{arch}.zip"
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                zip_file = temp_path / f"terraform_{version}.zip"
                
                # Download
                print(f":arrow_down: [blue]Baixando Terraform {version} para {os_name} {arch}...[/blue]")
                result = subprocess.run([
                    "curl", "-L", "-o", str(zip_file), url
                ], capture_output=True)
                
                if result.returncode != 0:
                    print(":x: [red]Falha no download[/red]")
                    return False
                
                # Extrair
                print(":package: [blue]Extraindo arquivo...[/blue]")
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Instalar
                terraform_binary = temp_path / "terraform"
                if not terraform_binary.exists():
                    print(":x: [red]Binário do Terraform não encontrado no arquivo[/red]")
                    return False
                
                # Copiar para /usr/local/bin
                install_path = Path("/usr/local/bin/terraform")
                print(f":gear: [blue]Instalando em {install_path}...[/blue]")
                
                subprocess.run([
                    "sudo", "cp", str(terraform_binary), str(install_path)
                ], check=True)
                
                subprocess.run([
                    "sudo", "chmod", "+x", str(install_path)
                ], check=True)
                
                print(":white_check_mark: [green]Terraform instalado via download oficial![/green]")
                return True
        
        except Exception as e:
            print(f":x: [red]Erro na instalação via download: {str(e)}[/red]")
            return False
    
    def _get_architecture(self) -> Optional[str]:
        """Retorna a arquitetura para download."""
        try:
            result = subprocess.run(["uname", "-m"], capture_output=True, text=True)
            if result.returncode == 0:
                arch = result.stdout.strip()
                if arch in ["x86_64", "amd64"]:
                    return "amd64"
                elif arch in ["aarch64", "arm64"]:
                    return "arm64"
                elif arch in ["arm"]:
                    return "arm"
        except Exception:
            pass
        return None
    
    def _get_os_name(self) -> Optional[str]:
        """Retorna o nome do SO para download."""
        if self.system_info.os_type in [
            OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
            OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN,
            OperatingSystem.CENTOS, OperatingSystem.RHEL, OperatingSystem.FEDORA
        ]:
            return "linux"
        elif self.system_info.os_type == OperatingSystem.MACOS:
            return "darwin"
        return None
    
    def _check_homebrew(self) -> bool:
        """Verifica se o Homebrew está instalado."""
        try:
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def _show_manual_instructions(self) -> bool:
        """Mostra instruções para instalação manual."""
        print(":information_source: [cyan]Instruções para instalação manual do Terraform:[/cyan]")
        print()
        print("1. Acesse: https://www.terraform.io/downloads")
        print("2. Baixe o arquivo ZIP para seu sistema operacional")
        print("3. Extraia o arquivo e mova o binário para um diretório no PATH")
        print("4. Verifique a instalação com: terraform --version")
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
                "brew install terraform",
                "",
                "# Ou via download manual:",
                "# 1. Acesse https://www.terraform.io/downloads",
                "# 2. Baixe o ZIP para macOS",
                "# 3. Extraia e mova para /usr/local/bin"
            ]
        
        elif self.system_info.os_type in [
            OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
            OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN
        ]:
            return [
                "# Via repositório HashiCorp",
                "sudo apt-get update && sudo apt-get install -y gnupg software-properties-common curl",
                "curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/hashicorp.gpg",
                "echo 'deb [signed-by=/etc/apt/keyrings/hashicorp.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main' | sudo tee /etc/apt/sources.list.d/hashicorp.list",
                "sudo apt-get update && sudo apt-get install terraform"
            ]
        
        elif self.system_info.os_type in [
            OperatingSystem.CENTOS, OperatingSystem.RHEL, OperatingSystem.FEDORA
        ]:
            pkg_manager = "dnf" if self.system_info.os_type == OperatingSystem.FEDORA else "yum"
            return [
                "# Via repositório HashiCorp",
                f"sudo {pkg_manager} install -y yum-utils",
                "sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo",
                f"sudo {pkg_manager} install terraform"
            ]
        
        else:
            return [
                "# Instalação manual",
                "1. Acesse: https://www.terraform.io/downloads",
                "2. Baixe o arquivo ZIP para seu sistema operacional",
                "3. Extraia o arquivo e mova o binário para um diretório no PATH",
                "4. Verifique com: terraform --version"
            ]

    def uninstall(self) -> bool:
        """
        Remove o Terraform do sistema.
        
        Returns:
            bool: True se a remoção foi bem-sucedida
        """
        print(f":wastebasket: [blue]Removendo {self.tool_name}...[/blue]")
        
        try:
            if self.system_info.os_type == OperatingSystem.MACOS:
                # Tentar remover via Homebrew primeiro
                try:
                    subprocess.run(["brew", "uninstall", "terraform"], check=True)
                    print(":white_check_mark: [green]Terraform removido via Homebrew![/green]")
                    return True
                except subprocess.CalledProcessError:
                    pass
            
            elif self.system_info.os_type in [
                OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
                OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN
            ]:
                try:
                    subprocess.run(["sudo", "apt-get", "remove", "-y", "terraform"], check=True)
                    print(":white_check_mark: [green]Terraform removido via apt![/green]")
                    return True
                except subprocess.CalledProcessError:
                    pass
            
            elif self.system_info.os_type in [
                OperatingSystem.CENTOS, OperatingSystem.RHEL, OperatingSystem.FEDORA
            ]:
                pkg_manager = "dnf" if self.system_info.os_type == OperatingSystem.FEDORA else "yum"
                try:
                    subprocess.run(["sudo", pkg_manager, "remove", "-y", "terraform"], check=True)
                    print(f":white_check_mark: [green]Terraform removido via {pkg_manager}![/green]")
                    return True
                except subprocess.CalledProcessError:
                    pass
            
            # Tentar remover binário manual
            binary_path = Path("/usr/local/bin/terraform")
            if binary_path.exists():
                subprocess.run(["sudo", "rm", str(binary_path)], check=True)
                print(":white_check_mark: [green]Terraform removido (binário manual)![/green]")
                return True
            
            print(":x: [red]Terraform não encontrado para remoção[/red]")
            return False
        
        except Exception as e:
            print(f":x: [red]Erro ao remover Terraform: {str(e)}[/red]")
            return False
    
    def _cleanup_failed_repository(self) -> None:
        """Remove repositório HashiCorp corrompido para não afetar outras instalações."""
        try:
            print(":broom: [blue]Limpando repositório corrompido...[/blue]")
            
            # Remover arquivo de repositório se existir
            subprocess.run([
                "sudo", "rm", "-f", "/etc/apt/sources.list.d/hashicorp.list"
            ], capture_output=True)
            
            # Remover chave GPG se existir
            subprocess.run([
                "sudo", "rm", "-f", "/etc/apt/keyrings/hashicorp.gpg"
            ], capture_output=True)
            
            # Tentar atualizar repositórios para limpar cache
            subprocess.run([
                "sudo", "apt-get", "update"
            ], capture_output=True)
            
            print(":white_check_mark: [green]Repositório limpo com sucesso[/green]")
            
        except Exception as e:
            print(f":warning: [yellow]Aviso: Não foi possível limpar repositório: {str(e)}[/yellow]")