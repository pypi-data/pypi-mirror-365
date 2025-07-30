"""Instalador do AWS CLI v2 para diferentes sistemas operacionais."""

import subprocess
import os
import tempfile
import zipfile
import shutil
from pathlib import Path
from typing import Optional, List
from rich import print

from .base_installer import BaseInstaller
from ..system_detector import SystemInfo, OperatingSystem


class AwsCliInstaller(BaseInstaller):
    """Instalador especializado para AWS CLI v2."""
    
    def __init__(self, system_info: SystemInfo):
        """
        Inicializa o instalador do AWS CLI v2.
        
        Args:
            system_info: Informações do sistema operacional
        """
        super().__init__(system_info)
        self.tool_name = "AWS CLI v2"
        
    def is_installed(self) -> bool:
        """
        Verifica se o AWS CLI v2 está instalado.
        
        Returns:
            bool: True se o AWS CLI v2 estiver instalado
        """
        try:
            result = subprocess.run(
                ["aws", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # AWS CLI v2 deve mostrar "aws-cli/2.x.x"
            return result.returncode == 0 and "aws-cli/2." in result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_installed_version(self) -> Optional[str]:
        """
        Obtém a versão instalada do AWS CLI.
        
        Returns:
            Optional[str]: Versão instalada ou None
        """
        try:
            result = subprocess.run(
                ["aws", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # aws-cli/2.13.25 Python/3.11.5 Linux/5.4.0-74-generic exe/x86_64.ubuntu.20
                version_line = result.stdout.strip()
                if "aws-cli/" in version_line:
                    return version_line.split()[0].replace("aws-cli/", "")
            return None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
    
    def install(self) -> bool:
        """
        Instala o AWS CLI v2 baseado no sistema operacional.
        
        Returns:
            bool: True se a instalação foi bem-sucedida
        """
        print(f":gear: [blue]Instalando {self.tool_name}...[/blue]")
        
        try:
            if self.system_info.os_type == OperatingSystem.MACOS:
                return self._install_macos()
            
            elif self.system_info.os_type in [
                OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
                OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN,
                OperatingSystem.CENTOS, OperatingSystem.RHEL,
                OperatingSystem.FEDORA
            ]:
                return self._install_linux()
            
            else:
                print(f":warning: [yellow]Sistema {self.system_info.os_type.value} não suportado para instalação automática do AWS CLI[/yellow]")
                return self._show_manual_instructions()
        
        except Exception as e:
            print(f":x: [red]Erro durante instalação do AWS CLI: {str(e)}[/red]")
            return False
    
    def _install_macos(self) -> bool:
        """Instala AWS CLI v2 no macOS."""
        print(":apple: [blue]Detectado macOS - usando instalador oficial[/blue]")
        
        try:
            # Determinar arquitetura
            arch = self._get_macos_architecture()
            if not arch:
                print(":x: [red]Não foi possível determinar arquitetura do macOS[/red]")
                return False
            
            url = f"https://awscli.amazonaws.com/AWSCLIV2-{arch}.pkg"
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                pkg_file = temp_path / "AWSCLIV2.pkg"
                
                # Download
                print(f":arrow_down: [blue]Baixando AWS CLI v2 para {arch}...[/blue]")
                result = subprocess.run([
                    "curl", "-L", "-o", str(pkg_file), url
                ], capture_output=True)
                
                if result.returncode != 0:
                    print(":x: [red]Falha no download[/red]")
                    return False
                
                # Instalar
                print(":package: [blue]Instalando AWS CLI v2...[/blue]")
                result = subprocess.run([
                    "sudo", "installer", "-pkg", str(pkg_file), "-target", "/"
                ], capture_output=True)
                
                if result.returncode == 0:
                    print(":white_check_mark: [green]AWS CLI v2 instalado via instalador oficial![/green]")
                    return True
                else:
                    print(f":x: [red]Falha na instalação: {result.stderr.decode()}[/red]")
                    return False
        
        except Exception as e:
            print(f":x: [red]Erro na instalação para macOS: {str(e)}[/red]")
            return False
    
    def _install_linux(self) -> bool:
        """Instala AWS CLI v2 no Linux."""
        print(":penguin: [blue]Detectado Linux - usando instalador oficial[/blue]")
        
        try:
            # Determinar arquitetura
            arch = self._get_linux_architecture()
            if not arch:
                print(":x: [red]Não foi possível determinar arquitetura do Linux[/red]")
                return False
            
            url = f"https://awscli.amazonaws.com/awscli-exe-linux-{arch}.zip"
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                zip_file = temp_path / "awscliv2.zip"
                
                # Download
                print(f":arrow_down: [blue]Baixando AWS CLI v2 para {arch}...[/blue]")
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
                install_script = temp_path / "aws" / "install"
                if not install_script.exists():
                    print(":x: [red]Script de instalação não encontrado[/red]")
                    return False
                
                # Tornar script executável
                install_script.chmod(0o755)
                
                print(":gear: [blue]Executando instalador...[/blue]")
                result = subprocess.run([
                    "sudo", str(install_script)
                ], capture_output=True)
                
                if result.returncode == 0:
                    # Corrigir permissões dos binários
                    self._fix_binary_permissions()
                    print(":white_check_mark: [green]AWS CLI v2 instalado via instalador oficial![/green]")
                    return True
                else:
                    # Tentar instalação sem sudo em diretório local
                    print(":information: [blue]Tentando instalação sem sudo...[/blue]")
                    return self._install_linux_local(install_script)
        
        except Exception as e:
            print(f":x: [red]Erro na instalação para Linux: {str(e)}[/red]")
            return False
    
    def _install_linux_local(self, install_script: Path) -> bool:
        """Instala AWS CLI v2 em diretório local no Linux."""
        try:
            # Criar diretório local
            local_dir = Path.home() / ".local"
            local_dir.mkdir(exist_ok=True)
            
            # Tornar script executável
            install_script.chmod(0o755)
            
            result = subprocess.run([
                str(install_script), "--install-dir", str(local_dir / "aws-cli"),
                "--bin-dir", str(local_dir / "bin")
            ], capture_output=True)
            
            if result.returncode == 0:
                print(":white_check_mark: [green]AWS CLI v2 instalado em ~/.local/![/green]")
                print(":information: [blue]Adicione ~/.local/bin ao seu PATH se necessário[/blue]")
                return True
            else:
                print(f":x: [red]Falha na instalação local: {result.stderr.decode()}[/red]")
                return False
        
        except Exception as e:
            print(f":x: [red]Erro na instalação local: {str(e)}[/red]")
            return False
    
    def _get_macos_architecture(self) -> Optional[str]:
        """Retorna a arquitetura para macOS."""
        try:
            result = subprocess.run(["uname", "-m"], capture_output=True, text=True)
            if result.returncode == 0:
                arch = result.stdout.strip()
                if arch in ["arm64", "aarch64"]:
                    return "arm64"
                elif arch in ["x86_64", "amd64"]:
                    return "x86_64"
        except Exception:
            pass
        return None
    
    def _get_linux_architecture(self) -> Optional[str]:
        """Retorna a arquitetura para Linux."""
        try:
            result = subprocess.run(["uname", "-m"], capture_output=True, text=True)
            if result.returncode == 0:
                arch = result.stdout.strip()
                if arch in ["aarch64", "arm64"]:
                    return "aarch64"
                elif arch in ["x86_64", "amd64"]:
                    return "x86_64"
        except Exception:
            pass
        return None
    
    def _fix_binary_permissions(self) -> None:
        """Corrige permissões dos binários do AWS CLI."""
        try:
            binaries = ["/usr/local/bin/aws", "/usr/local/bin/aws_completer"]
            for binary in binaries:
                if Path(binary).exists():
                    subprocess.run(["sudo", "chmod", "755", binary], capture_output=True)
        except Exception:
            pass  # Não é crítico se falhar
    
    def _show_manual_instructions(self) -> bool:
        """Mostra instruções para instalação manual."""
        print(":information_source: [cyan]Instruções para instalação manual do AWS CLI v2:[/cyan]")
        print()
        print("1. Acesse: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html")
        print("2. Baixe o instalador para seu sistema operacional")
        print("3. Execute o instalador seguindo as instruções")
        print("4. Verifique a instalação com: aws --version")
        print()
        return False
    
    def get_install_commands(self) -> List[str]:
        """
        Retorna lista de comandos para instalação manual.
        
        Returns:
            List[str]: Lista de comandos
        """
        if self.system_info.os_type == OperatingSystem.MACOS:
            arch = self._get_macos_architecture() or "x86_64"
            return [
                "# Via instalador oficial AWS",
                f"curl -L -o AWSCLIV2-{arch}.pkg https://awscli.amazonaws.com/AWSCLIV2-{arch}.pkg",
                f"sudo installer -pkg AWSCLIV2-{arch}.pkg -target /",
                "rm AWSCLIV2-{arch}.pkg"
            ]
        
        elif self.system_info.os_type in [
            OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
            OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN,
            OperatingSystem.CENTOS, OperatingSystem.RHEL,
            OperatingSystem.FEDORA
        ]:
            arch = self._get_linux_architecture() or "x86_64"
            return [
                "# Via instalador oficial AWS",
                f"curl -L -o awscliv2.zip https://awscli.amazonaws.com/awscli-exe-linux-{arch}.zip",
                "unzip awscliv2.zip",
                "sudo ./aws/install",
                "rm -rf aws awscliv2.zip"
            ]
        
        else:
            return [
                "# Instalação manual",
                "1. Acesse: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html",
                "2. Baixe o instalador para seu sistema operacional",
                "3. Execute o instalador seguindo as instruções",
                "4. Verifique com: aws --version"
            ]

    def uninstall(self) -> bool:
        """
        Remove o AWS CLI v2 do sistema.
        
        Returns:
            bool: True se a remoção foi bem-sucedida
        """
        print(f":wastebasket: [blue]Removendo {self.tool_name}...[/blue]")
        
        try:
            if self.system_info.os_type == OperatingSystem.MACOS:
                # No macOS, remover via paths padrão
                paths_to_remove = [
                    "/usr/local/bin/aws",
                    "/usr/local/bin/aws_completer",
                    "/usr/local/aws-cli"
                ]
            else:
                # No Linux, remover via paths padrão
                paths_to_remove = [
                    "/usr/local/bin/aws",
                    "/usr/local/bin/aws_completer",
                    "/usr/local/aws-cli"
                ]
            
            removed_any = False
            for path in paths_to_remove:
                if Path(path).exists():
                    try:
                        subprocess.run(["sudo", "rm", "-rf", path], check=True)
                        print(f":white_check_mark: [green]Removido: {path}[/green]")
                        removed_any = True
                    except subprocess.CalledProcessError:
                        continue
            
            if removed_any:
                print(":white_check_mark: [green]AWS CLI v2 removido com sucesso![/green]")
                return True
            else:
                print(":x: [red]AWS CLI v2 não encontrado para remoção[/red]")
                return False
        
        except Exception as e:
            print(f":x: [red]Erro ao remover AWS CLI v2: {str(e)}[/red]")
            return False