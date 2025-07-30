"""Classe base para instaladores do Docker."""

import subprocess
import shutil
from abc import ABC, abstractmethod
from typing import List, Optional
from rich import print

from ..system_detector import SystemInfo


class BaseInstaller(ABC):
    """Classe base para instaladores do Docker."""
    
    def __init__(self, system_info: SystemInfo):
        """
        Inicializa o instalador.
        
        Args:
            system_info: Informações do sistema
        """
        self.system_info = system_info
    
    @abstractmethod
    def install(self) -> bool:
        """
        Instala o Docker no sistema.
        
        Returns:
            bool: True se a instalação foi bem-sucedida
        """
        pass
    
    @abstractmethod
    def uninstall(self) -> bool:
        """
        Remove o Docker do sistema.
        
        Returns:
            bool: True se a remoção foi bem-sucedida
        """
        pass
    
    @abstractmethod
    def get_install_commands(self) -> List[str]:
        """
        Retorna lista de comandos para instalação manual.
        
        Returns:
            List[str]: Lista de comandos
        """
        pass
    
    def is_docker_installed(self) -> bool:
        """
        Verifica se o Docker está instalado.
        
        Returns:
            bool: True se o Docker está instalado
        """
        return shutil.which("docker") is not None
    
    def get_docker_version(self) -> Optional[str]:
        """
        Obtém a versão do Docker instalada.
        
        Returns:
            Optional[str]: Versão do Docker ou None se não instalado
        """
        try:
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Output típico: "Docker version 20.10.7, build f0df350"
                version_line = result.stdout.strip()
                if "version" in version_line:
                    return version_line.split()[2].rstrip(",")
            return None
        except Exception:
            return None
    
    def test_docker_installation(self) -> bool:
        """
        Testa se o Docker está funcionando corretamente.
        
        Returns:
            bool: True se o Docker está funcionando
        """
        try:
            print("  [blue]🧪[/blue] Testando instalação do Docker...")
            
            # Testar comando docker version
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                # Verificar se é problema de permissão específico
                if "permission denied" in result.stderr.lower() or "connect: permission denied" in result.stderr.lower():
                    print("  [red]✗[/red] Problema de permissão detectado no Docker daemon")
                else:
                    print("  [yellow]![/yellow] Docker instalado mas não está rodando")
                return False
            
            # Tentar rodar container de teste
            print("  [blue]🧪[/blue] Executando container de teste...")
            result = subprocess.run(
                ["docker", "run", "--rm", "hello-world"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("  [green]✓[/green] Docker está funcionando corretamente!")
                return True
            else:
                # Verificar se é problema de permissão específico
                if "permission denied" in result.stderr.lower() or "connect: permission denied" in result.stderr.lower():
                    print("  [red]✗[/red] Problema de permissão detectado ao executar containers")
                else:
                    print("  [yellow]![/yellow] Docker instalado mas não consegue executar containers")
                return False
                
        except subprocess.TimeoutExpired:
            print("  [yellow]![/yellow] Timeout ao testar Docker")
            return False
        except Exception as e:
            print(f"  [yellow]![/yellow] Erro ao testar Docker: {e}")
            return False
    
    def _run_command(self, command: List[str], shell: bool = False, ignore_errors: bool = False) -> subprocess.CompletedProcess:
        """
        Executa um comando no sistema.
        
        Args:
            command: Comando a ser executado
            shell: Se deve usar shell
            ignore_errors: Se deve ignorar erros
            
        Returns:
            subprocess.CompletedProcess: Resultado do comando
            
        Raises:
            subprocess.CalledProcessError: Se o comando falhar e ignore_errors=False
        """
        try:
            if shell:
                cmd_str = " ".join(command)
                result = subprocess.run(
                    cmd_str,
                    shell=True,
                    check=not ignore_errors,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutos
                )
            else:
                result = subprocess.run(
                    command,
                    check=not ignore_errors,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutos
                )
            
            return result
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Comando demorou muito para executar: {' '.join(command)}")
        except subprocess.CalledProcessError as e:
            if not ignore_errors:
                raise e
            return e
    
    def check_prerequisites(self) -> bool:
        """
        Verifica pré-requisitos para instalação.
        
        Returns:
            bool: True se todos os pré-requisitos estão atendidos
        """
        # Verificar se tem sudo (para Linux)
        if self.system_info.os_type.value != "macos":
            if not shutil.which("sudo"):
                print("  [red]✗[/red] sudo não encontrado. Necessário para instalação.")
                return False
        
        # Verificar se tem curl
        if not shutil.which("curl"):
            print("  [yellow]![/yellow] curl não encontrado. Tentando instalar...")
            try:
                if self.system_info.os_type.value in ["ubuntu", "debian", "wsl_ubuntu", "wsl_debian"]:
                    self._run_command(["sudo", "apt", "install", "-y", "curl"])
                elif self.system_info.os_type.value == "macos":
                    print("  [yellow]![/yellow] Instale curl usando: brew install curl")
                    return False
            except Exception:
                print("  [red]✗[/red] Não foi possível instalar curl.")
                return False
        
        return True
    
    def print_manual_instructions(self) -> None:
        """Imprime instruções para instalação manual."""
        print(f"\n[bold yellow]📋 Instruções para instalação manual no {self.system_info.os_type.value}:[/bold yellow]")
        print()
        
        for i, command in enumerate(self.get_install_commands(), 1):
            print(f"  [blue]{i}.[/blue] {command}")
        
        print()
        print("[bold]💡 Dica:[/bold] Copie e cole os comandos acima no terminal.")
        print("[bold]⚠ Importante:[/bold] Faça logout/login após a instalação para aplicar as permissões.")