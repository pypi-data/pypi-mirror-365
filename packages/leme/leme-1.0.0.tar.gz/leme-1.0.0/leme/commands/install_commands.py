"""Comandos para instalação de ferramentas."""

import typer
from rich import print
from typing import Optional

from ..system.docker_installer import DockerInstaller
from ..system.installers.terraform_installer import TerraformInstaller
from ..system.installers.azure_cli_installer import AzureCliInstaller
from ..system.installers.aws_cli_installer import AwsCliInstaller
from ..system.system_detector import SystemDetector


def install_docker(
    check_only: bool = typer.Option(False, "--check-only", help="Apenas verificar se o Docker está instalado"),
    force: bool = typer.Option(False, "--force", "-f", help="Forçar reinstalação mesmo se já estiver instalado"),
    manual: bool = typer.Option(False, "--manual", help="Mostrar instruções para instalação manual"),
    no_test: bool = typer.Option(False, "--no-test", help="Não testar a instalação após completar")
) -> None:
    """
    Instala o Docker automaticamente baseado no sistema operacional detectado.
    
    Sistemas suportados:
    - Ubuntu/Debian (incluindo WSL)
    - macOS (Intel e Apple Silicon)
    - CentOS/RHEL/Fedora
    """
    try:
        docker_installer = DockerInstaller()
        
        # Modo apenas verificação
        if check_only:
            print(":mag: [bold blue]Verificando instalação do Docker...[/bold blue]")
            print()
            docker_installer.print_status()
            return
        
        # Modo instruções manuais
        if manual:
            print(":book: [bold blue]Instruções para instalação manual[/bold blue]")
            print()
            docker_installer.get_manual_instructions()
            return
        
        # Instalação automática
        success = docker_installer.install(
            force=force, 
            test_after_install=not no_test
        )
        
        if success:
            print()
            print(":tada: [bold green]Instalação concluída![/bold green]")
            print()
            print("[bold]Próximos passos:[/bold]")
            print("• Use 'docker --version' para verificar a instalação")
            print("• Use 'docker run hello-world' para testar")
            if docker_installer.system_info.os_type.value != "macos":
                print("• Faça logout/login para aplicar permissões de grupo")
        else:
            raise typer.Exit(code=1)
            
    except Exception as e:
        print(f":x: [bold red]Erro inesperado:[/bold red] {e}")
        raise typer.Exit(code=1)


def uninstall_docker() -> None:
    """
    Remove o Docker do sistema.
    """
    try:
        docker_installer = DockerInstaller()
        
        print(":wastebasket: [bold yellow]Remoção do Docker[/bold yellow]")
        print(f"Sistema: {docker_installer.system_info}")
        print()
        
        success = docker_installer.uninstall()
        
        if success:
            print()
            print(":white_check_mark: [bold green]Docker removido com sucesso![/bold green]")
        else:
            raise typer.Exit(code=1)
            
    except Exception as e:
        print(f":x: [bold red]Erro inesperado:[/bold red] {e}")
        raise typer.Exit(code=1)


def check_docker_status() -> None:
    """
    Verifica o status da instalação do Docker.
    """
    try:
        docker_installer = DockerInstaller()
        
        print(":whale: [bold blue]Status do Docker[/bold blue]")
        print()
        docker_installer.print_status()
        
        # Informações adicionais
        info = docker_installer.check_installation()
        print()
        
        if info['installed'] and info['working']:
            print("[bold green]✓ Docker está pronto para uso![/bold green]")
        elif info['installed'] and not info['working']:
            print("[bold yellow]⚠ Docker instalado mas não está funcionando[/bold yellow]")
            print("Tente:")
            print("• Reiniciar o sistema")
            print("• Iniciar o Docker manualmente")
            if docker_installer.system_info.os_type.value == "macos":
                print("• Abrir Docker Desktop")
        elif info['supported']:
            print("[bold red]✗ Docker não está instalado[/bold red]")
            print(f"Use: [cyan]python3 main.py install docker[/cyan]")
        else:
            print("[bold red]✗ Sistema não suportado[/bold red]")
            print("Visite: https://docs.docker.com/get-docker/")
            
    except Exception as e:
        print(f":x: [bold red]Erro inesperado:[/bold red] {e}")
        raise typer.Exit(code=1)


def system_info() -> None:
    """
    Mostra informações detalhadas do sistema.
    """
    try:
        from ..system.system_detector import SystemDetector
        
        system_info = SystemDetector.detect()
        
        print(":computer: [bold blue]Informações do Sistema[/bold blue]")
        print()
        print(f"[bold]Sistema Operacional:[/bold] {system_info.os_type.value}")
        print(f"[bold]Arquitetura:[/bold] {system_info.architecture.value}")
        print(f"[bold]WSL:[/bold] {'Sim' if system_info.is_wsl else 'Não'}")
        if system_info.distro_version:
            print(f"[bold]Versão:[/bold] {system_info.distro_version}")
        
        print()
        print(f"[bold]Gerenciador de Pacotes:[/bold] {SystemDetector.get_package_manager(system_info.os_type) or 'N/A'}")
        print(f"[bold]Instalação Docker Suportada:[/bold] {'Sim' if SystemDetector.supports_docker_installation(system_info.os_type) else 'Não'}")
        
    except Exception as e:
        print(f":x: [bold red]Erro inesperado:[/bold red] {e}")
        raise typer.Exit(code=1)


def install_azure_cli(force: bool = False, manual: bool = False) -> None:
    """
    Instala o Azure CLI automaticamente baseado no sistema operacional.
    
    Args:
        force: Forçar reinstalação mesmo se já estiver instalado
        manual: Mostrar instruções para instalação manual
    """
    try:
        system_info = SystemDetector.detect()
        azure_installer = AzureCliInstaller(system_info)
        
        print(":cloud: [bold blue]Instalação do Azure CLI[/bold blue]")
        print(f"Sistema detectado: [green]{system_info}[/green]")
        print()
        
        # Mostrar instruções manuais se solicitado
        if manual:
            azure_installer.print_manual_instructions()
            return
        
        # Verificar se já está instalado
        if not force and azure_installer.is_installed():
            version = azure_installer.get_installed_version()
            print(f":white_check_mark: Azure CLI já está instalado (versão {version})")
            
            if not typer.confirm("Deseja reinstalar?"):
                return
        
        # Instalar Azure CLI
        print()
        success = azure_installer.install()
        
        if success:
            print()
            print(":white_check_mark: [bold green]Azure CLI instalado com sucesso![/bold green]")
            print("Teste com: [cyan]az --version[/cyan]")
        else:
            print()
            print(":x: [bold red]Falha na instalação automática.[/bold red]")
            print()
            azure_installer.print_manual_instructions()
            raise typer.Exit(code=1)
            
    except Exception as e:
        print(f":x: [bold red]Erro inesperado:[/bold red] {e}")
        raise typer.Exit(code=1)


def install_terraform(force: bool = False, manual: bool = False) -> None:
    """
    Instala o Terraform automaticamente baseado no sistema operacional.
    
    Args:
        force: Forçar reinstalação mesmo se já estiver instalado
        manual: Mostrar instruções para instalação manual
    """
    try:
        system_info = SystemDetector.detect()
        terraform_installer = TerraformInstaller(system_info)
        
        print(":gear: [bold blue]Instalação do Terraform[/bold blue]")
        print(f"Sistema detectado: [green]{system_info}[/green]")
        print()
        
        # Mostrar instruções manuais se solicitado
        if manual:
            terraform_installer.print_manual_instructions()
            return
        
        # Verificar se já está instalado
        if not force and terraform_installer.is_installed():
            version = terraform_installer.get_installed_version()
            print(f":white_check_mark: Terraform já está instalado (versão {version})")
            
            if not typer.confirm("Deseja reinstalar?"):
                return
        
        # Instalar Terraform
        print()
        success = terraform_installer.install()
        
        if success:
            print()
            print(":white_check_mark: [bold green]Terraform instalado com sucesso![/bold green]")
            print("Teste com: [cyan]terraform --version[/cyan]")
        else:
            print()
            print(":x: [bold red]Falha na instalação automática.[/bold red]")
            print()
            terraform_installer.print_manual_instructions()
            raise typer.Exit(code=1)
            
    except Exception as e:
        print(f":x: [bold red]Erro inesperado:[/bold red] {e}")
        raise typer.Exit(code=1)


def install_aws_cli(force: bool = False, manual: bool = False) -> None:
    """
    Instala o AWS CLI v2 automaticamente baseado no sistema operacional.
    
    Args:
        force: Forçar reinstalação mesmo se já estiver instalado
        manual: Mostrar instruções para instalação manual
    """
    try:
        system_info = SystemDetector.detect()
        aws_installer = AwsCliInstaller(system_info)
        
        print(":cloud: [bold blue]Instalação do AWS CLI v2[/bold blue]")
        print(f"Sistema detectado: [green]{system_info}[/green]")
        print()
        
        # Mostrar instruções manuais se solicitado
        if manual:
            aws_installer.print_manual_instructions()
            return
        
        # Verificar se já está instalado
        if not force and aws_installer.is_installed():
            version = aws_installer.get_installed_version()
            print(f":white_check_mark: AWS CLI v2 já está instalado (versão {version})")
            
            if not typer.confirm("Deseja reinstalar?"):
                return
        
        # Instalar AWS CLI
        print()
        success = aws_installer.install()
        
        if success:
            print()
            print(":white_check_mark: [bold green]AWS CLI v2 instalado com sucesso![/bold green]")
            print("Teste com: [cyan]aws --version[/cyan]")
        else:
            print()
            print(":x: [bold red]Falha na instalação automática.[/bold red]")
            print()
            aws_installer.print_manual_instructions()
            raise typer.Exit(code=1)
            
    except Exception as e:
        print(f":x: [bold red]Erro inesperado:[/bold red] {e}")
        raise typer.Exit(code=1)