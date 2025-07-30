"""Instalador do Docker para macOS."""

import subprocess
import shutil
from typing import List
from rich import print

from .base_installer import BaseInstaller


class MacOSInstaller(BaseInstaller):
    """Instalador do Docker para macOS."""
    
    def install(self) -> bool:
        """
        Instala o Docker no macOS usando Homebrew.
        
        Returns:
            bool: True se a instalação foi bem-sucedida
        """
        print(":apple: Instalando Docker no macOS...")
        
        try:
            # Verificar se Homebrew está instalado
            if not self._check_homebrew():
                return False
            
            # 1. Atualizar Homebrew
            print("  [blue]1/3[/blue] Atualizando Homebrew...")
            self._run_command(["brew", "update"])
            
            # 2. Instalar Docker
            print("  [blue]2/3[/blue] Instalando Docker...")
            self._run_command(["brew", "install", "--cask", "docker"])
            
            # 3. Instruções para iniciar Docker
            print("  [blue]3/3[/blue] Configuração finalizada!")
            print()
            print("[yellow]📝 Próximos passos:[/yellow]")
            print("  1. Abra o Docker Desktop na pasta Applications")
            print("  2. Aguarde o Docker inicializar (pode demorar alguns minutos)")
            print("  3. O Docker estará pronto para uso!")
            print()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  [red]✗[/red] Erro durante a instalação: {e}")
            return False
        except Exception as e:
            print(f"  [red]✗[/red] Erro inesperado: {e}")
            return False
    
    def _check_homebrew(self) -> bool:
        """Verifica se o Homebrew está instalado."""
        if shutil.which("brew"):
            return True
        
        print("  [yellow]![/yellow] Homebrew não encontrado.")
        print("  [blue]📦[/blue] Instalando Homebrew...")
        
        try:
            # Instalar Homebrew
            install_cmd = [
                "/bin/bash", "-c", 
                "\"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            ]
            self._run_command(install_cmd, shell=True)
            
            print("  [green]✓[/green] Homebrew instalado com sucesso!")
            return True
            
        except Exception as e:
            print(f"  [red]✗[/red] Erro ao instalar Homebrew: {e}")
            print("  [yellow]💡[/yellow] Instale manualmente: https://brew.sh")
            return False
    
    def uninstall(self) -> bool:
        """
        Remove o Docker do sistema.
        
        Returns:
            bool: True se a remoção foi bem-sucedida
        """
        try:
            print(":wastebasket: Removendo Docker...")
            
            # Remover Docker Desktop
            self._run_command(["brew", "uninstall", "--cask", "docker"], ignore_errors=True)
            
            print("  [green]✓[/green] Docker removido com sucesso!")
            return True
            
        except Exception as e:
            print(f"  [red]✗[/red] Erro durante a remoção: {e}")
            return False
    
    def get_install_commands(self) -> List[str]:
        """Retorna lista de comandos para instalação manual."""
        return [
            "# Instalar Homebrew (se não estiver instalado)",
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            "",
            "# Instalar Docker",
            "brew update",
            "brew install --cask docker",
            "",
            "# Abrir Docker Desktop",
            "open /Applications/Docker.app"
        ]
    
    def test_docker_installation(self) -> bool:
        """
        Testa se o Docker está funcionando no macOS.
        
        Returns:
            bool: True se o Docker está funcionando
        """
        # No macOS, o Docker Desktop precisa estar rodando
        if not self.is_docker_installed():
            return False
        
        print("  [blue]🧪[/blue] Verificando se Docker Desktop está rodando...")
        
        try:
            # Verificar se Docker daemon está ativo
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print("  [yellow]![/yellow] Docker Desktop não está rodando")
                print("  [blue]💡[/blue] Inicie o Docker Desktop manualmente")
                return False
            
            return super().test_docker_installation()
            
        except Exception as e:
            print(f"  [yellow]![/yellow] Erro ao verificar Docker: {e}")
            return False