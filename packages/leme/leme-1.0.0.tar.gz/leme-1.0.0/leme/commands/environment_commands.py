"""Comandos para configuração do ambiente DevOps."""

import subprocess
import typer
from rich import print
from typing import Optional, List

from ..system.environment_manager import EnvironmentManager
from ..system.docker_installer import DockerInstaller
from ..system.installers.git_installer import GitInstaller
from ..system.installers.terraform_installer import TerraformInstaller
from ..system.installers.aws_cli_installer import AwsCliInstaller
from ..system.installers.azure_cli_installer import AzureCliInstaller
from ..config.constants import Tool, DEVOPS_TOOLS_CONFIG


def setup_environment(
    check_only: bool = typer.Option(False, "--check-only", help="Apenas verificar o ambiente atual"),
    required_only: bool = typer.Option(False, "--required-only", help="Instalar apenas ferramentas obrigatórias"),
    skip_docker: bool = typer.Option(False, "--skip-docker", help="Pular instalação do Docker"),
    force: bool = typer.Option(False, "--force", "-f", help="Forçar reinstalação de ferramentas"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Modo interativo (LEGACY - agora é padrão)"),
    tools: Optional[List[str]] = typer.Option(None, "--tools", "-t", help="Instalar apenas ferramentas específicas (ex: git,docker)")
) -> None:
    """
    Configura o ambiente DevOps completo para o curso.
    
    Este comando verifica e instala todas as ferramentas necessárias:
    - Docker (obrigatório)
    - Git (obrigatório) 
    - Azure CLI (opcional)
    - AWS CLI v2 (opcional)
    - kubectl (opcional)
    - Ansible (opcional)
    - watch (opcional)
    """
    print(":rocket: [bold green]Setup do Ambiente DevOps[/bold green]")
    print()
    
    # Inicializar gerenciador
    env_manager = EnvironmentManager()
    
    # Modo apenas verificação
    if check_only:
        env_manager.show_status_report()
        return
    
    # Verificar status atual
    print(":mag: [bold blue]Verificando ambiente atual...[/bold blue]")
    env_manager.check_all_tools()
    env_manager.show_status_report()
    
    # Determinar ferramentas a instalar
    if tools:
        # Lista específica de ferramentas
        selected_tools = []
        for tool_name in tools:
            try:
                tool = Tool(tool_name.lower())
                selected_tools.append(tool)
            except ValueError:
                print(f":warning: [yellow]Ferramenta desconhecida: {tool_name}[/yellow]")
        
        if not selected_tools:
            print(":x: [red]Nenhuma ferramenta válida especificada[/red]")
            raise typer.Exit(1)
        
        tools_to_install = [t for t in selected_tools if not env_manager.tools_status.get(t, None) or not env_manager.tools_status[t].installed]
    
    elif required_only:
        # Apenas ferramentas obrigatórias
        tools_to_install = env_manager.get_missing_tools(only_required=True)
    
    else:
        # Todas as ferramentas não instaladas
        tools_to_install = env_manager.get_missing_tools(only_required=False)
    
    # Filtrar Docker se solicitado
    if skip_docker and Tool.DOCKER in tools_to_install:
        tools_to_install.remove(Tool.DOCKER)
        print(":information: [blue]Docker será pulado conforme solicitado[/blue]")
    
    # Verificar se há algo para instalar
    if not tools_to_install:
        print(":white_check_mark: [green]Todas as ferramentas selecionadas já estão instaladas![/green]")
        return
    
    # Sempre perguntar para ferramentas opcionais (exceto se --force)
    if not force:
        print(f"\n:question: [bold cyan]Escolha as ferramentas para instalar:[/bold cyan]")
        selected_tools = []
        
        for tool in tools_to_install:
            config = DEVOPS_TOOLS_CONFIG[tool]
            required_text = "[red](obrigatória)[/red]" if config["required"] else "[yellow](opcional)[/yellow]"
            
            print(f"\n• [blue]{config['name']}[/blue] {required_text}")
            print(f"  {config['description']}")
            
            # Agora todas as ferramentas são opcionais - perguntar para todas
            confirm = typer.confirm(f"  Deseja instalar {config['name']}?")
            if confirm:
                selected_tools.append(tool)
            else:
                print(f"  :information: [yellow]Pulando {config['name']}[/yellow]")
        
        tools_to_install = selected_tools
        
        if not tools_to_install:
            print("\n:information: [yellow]Nenhuma ferramenta selecionada para instalação[/yellow]")
            return
        
        print(f"\n:white_check_mark: [bold green]Ferramentas selecionadas para instalação:[/bold green]")
        for tool in tools_to_install:
            config = DEVOPS_TOOLS_CONFIG[tool]
            print(f"  • [blue]{config['name']}[/blue]")
    
    else:
        # Modo --force - instalar tudo sem perguntar
        print(f"\n:wrench: [bold cyan]Modo Force - Instalando todas as ferramentas:[/bold cyan]")
        for tool in tools_to_install:
            config = DEVOPS_TOOLS_CONFIG[tool]
            required_text = "[red](obrigatória)[/red]" if config["required"] else "[yellow](opcional)[/yellow]"
            print(f"  • [blue]{config['name']}[/blue] {required_text} - {config['description']}")
    
    print("\n:gear: [bold green]Iniciando instalação das ferramentas...[/bold green]")
    
    # Instalar ferramentas uma por vez
    success_count = 0
    for tool in tools_to_install:
        config = DEVOPS_TOOLS_CONFIG[tool]
        print(f"\n:arrow_forward: [bold blue]Instalando {config['name']}...[/bold blue]")
        
        try:
            success = _install_tool(tool, env_manager.system_info, force)
            if success:
                print(f":white_check_mark: [green]{config['name']} instalado com sucesso![/green]")
                success_count += 1
            else:
                print(f":x: [red]Falha ao instalar {config['name']}[/red]")
        
        except Exception as e:
            print(f":x: [red]Erro ao instalar {config['name']}: {str(e)}[/red]")
    
    # Relatório final
    print(f"\n:chart_with_upwards_trend: [bold cyan]Relatório de Instalação:[/bold cyan]")
    print(f"  • [green]Instaladas com sucesso:[/green] {success_count}")
    print(f"  • [red]Falharam:[/red] {len(tools_to_install) - success_count}")
    
    # Verificar ambiente final
    print("\n:mag: [bold blue]Verificando ambiente após instalação...[/bold blue]")
    env_manager.check_all_tools()
    env_manager.show_status_report()
    
    # Status final
    if env_manager.is_environment_ready():
        print("\n:party_popper: [bold green]Ambiente DevOps configurado com sucesso![/bold green]")
        print(":information: [blue]Você está pronto para o curso![/blue]")
    else:
        missing = env_manager.get_missing_tools(only_required=True)
        print(f"\n:warning: [yellow]Ainda faltam algumas ferramentas obrigatórias: {[DEVOPS_TOOLS_CONFIG[t]['name'] for t in missing]}[/yellow]")
        print(":information: [blue]Execute novamente o comando para tentar instalar as ferramentas em falta[/blue]")


def environment_status() -> None:
    """Mostra o status atual de todas as ferramentas DevOps."""
    env_manager = EnvironmentManager()
    env_manager.show_status_report()


def _install_tool(tool: Tool, system_info, force: bool = False) -> bool:
    """
    Instala uma ferramenta específica.
    
    Args:
        tool: Ferramenta a ser instalada
        system_info: Informações do sistema
        force: Forçar reinstalação
        
    Returns:
        bool: True se a instalação foi bem-sucedida
    """
    try:
        if tool == Tool.DOCKER:
            # Docker já tem instalador dedicado
            docker_installer = DockerInstaller()
            return docker_installer.install(force=force, test_after_install=True)
        
        elif tool == Tool.GIT:
            return _install_git(system_info)
        
        elif tool == Tool.TERRAFORM:
            return _install_terraform(system_info)
        
        elif tool == Tool.AZURE_CLI:
            return _install_azure_cli(system_info)
        
        elif tool == Tool.AWS_CLI:
            return _install_aws_cli(system_info)
        
        elif tool == Tool.KUBECTL:
            return _install_kubectl(system_info)
        
        elif tool == Tool.ANSIBLE:
            return _install_ansible(system_info)
        
        elif tool == Tool.WATCH:
            return _install_watch(system_info)
        
        else:
            print(f":warning: [yellow]Instalador para {tool.value} não implementado ainda[/yellow]")
            return False
    
    except Exception as e:
        print(f":x: [red]Erro durante instalação de {tool.value}: {str(e)}[/red]")
        return False


def _install_git(system_info) -> bool:
    """Instala Git baseado no sistema operacional."""
    try:
        git_installer = GitInstaller(system_info)
        return git_installer.install()
    except Exception as e:
        print(f":x: [red]Erro durante instalação do Git: {str(e)}[/red]")
        return False


def _install_terraform(system_info) -> bool:
    """Instala Terraform baseado no sistema operacional."""
    try:
        terraform_installer = TerraformInstaller(system_info)
        return terraform_installer.install()
    except Exception as e:
        print(f":x: [red]Erro durante instalação do Terraform: {str(e)}[/red]")
        return False


def _install_azure_cli(system_info) -> bool:
    """Instala Azure CLI baseado no sistema operacional."""
    try:
        azure_installer = AzureCliInstaller(system_info)
        return azure_installer.install()
    except Exception as e:
        print(f":x: [red]Erro durante instalação do Azure CLI: {str(e)}[/red]")
        return False


def _install_aws_cli(system_info) -> bool:
    """Instala AWS CLI v2 baseado no sistema operacional."""
    try:
        aws_installer = AwsCliInstaller(system_info)
        return aws_installer.install()
    except Exception as e:
        print(f":x: [red]Erro durante instalação do AWS CLI: {str(e)}[/red]")
        return False


def _install_kubectl(system_info) -> bool:
    """Instala kubectl baseado no sistema operacional."""
    try:
        from ..system.system_detector import OperatingSystem
        
        print(":gear: [blue]Instalando kubectl...[/blue]")
        
        if system_info.os_type in [
            OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
            OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN
        ]:
            # Ubuntu/Debian - via repositório oficial do Kubernetes
            # Limpar repositórios corrompidos primeiro
            _cleanup_corrupted_repositories()
            subprocess.run(["sudo", "apt-get", "update"], check=True, capture_output=True)
            subprocess.run([
                "sudo", "apt-get", "install", "-y", "ca-certificates", "curl", "apt-transport-https"
            ], check=True, capture_output=True)
            
            # Adicionar chave GPG do Kubernetes
            subprocess.run([
                "sudo", "mkdir", "-p", "/etc/apt/keyrings"
            ], capture_output=True)
            subprocess.run([
                "bash", "-c", 
                "curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg"
            ], check=True, capture_output=True)
            
            # Adicionar repositório
            subprocess.run([
                "bash", "-c",
                "echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list"
            ], check=True, capture_output=True)
            
            subprocess.run(["sudo", "apt-get", "update"], check=True, capture_output=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "kubectl"], check=True, capture_output=True)
            
        elif system_info.os_type == OperatingSystem.MACOS:
            # macOS - via Homebrew
            subprocess.run(["brew", "install", "kubectl"], check=True, capture_output=True)
            
        elif system_info.os_type in [OperatingSystem.CENTOS, OperatingSystem.RHEL, OperatingSystem.FEDORA]:
            # CentOS/RHEL/Fedora - via repositório oficial
            repo_content = """[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.28/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.28/rpm/repodata/repomd.xml.key"""
            
            subprocess.run([
                "bash", "-c", f"echo '{repo_content}' | sudo tee /etc/yum.repos.d/kubernetes.repo"
            ], check=True)
            
            pkg_manager = "dnf" if system_info.os_type == OperatingSystem.FEDORA else "yum"
            subprocess.run(["sudo", pkg_manager, "install", "-y", "kubectl"], check=True, capture_output=True)
        
        else:
            print(":warning: [yellow]Sistema não suportado para kubectl[/yellow]")
            return False
            
        print(":white_check_mark: [green]kubectl instalado com sucesso![/green]")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f":x: [red]Erro ao instalar kubectl: {e}[/red]")
        return False
    except Exception as e:
        print(f":x: [red]Erro inesperado ao instalar kubectl: {str(e)}[/red]")
        return False


def _install_ansible(system_info) -> bool:
    """Instala Ansible baseado no sistema operacional."""
    try:
        from ..system.system_detector import OperatingSystem
        
        print(":gear: [blue]Instalando Ansible...[/blue]")
        
        if system_info.os_type in [
            OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
            OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN
        ]:
            # Ubuntu/Debian - via pip (método mais confiável)
            # Limpar repositórios corrompidos primeiro
            _cleanup_corrupted_repositories()
            subprocess.run(["sudo", "apt-get", "update"], check=True, capture_output=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "python3-pip"], check=True, capture_output=True)
            
            # Instalar Ansible globalmente para que fique disponível no PATH
            subprocess.run(["sudo", "pip3", "install", "ansible"], check=True, capture_output=True)
            
            # Verificar se o binário está acessível e criar link se necessário
            try:
                subprocess.run(["ansible", "--version"], check=True, capture_output=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                # Se não encontrar, tentar criar link simbólico
                ansible_paths = [
                    "/usr/local/bin/ansible",
                    "/home/user/.local/bin/ansible",
                    "/usr/bin/ansible"
                ]
                for path in ansible_paths:
                    if subprocess.run(["test", "-f", path], capture_output=True).returncode == 0:
                        subprocess.run(["sudo", "ln", "-sf", path, "/usr/bin/ansible"], capture_output=True)
                        break
            
        elif system_info.os_type == OperatingSystem.MACOS:
            # macOS - via Homebrew
            subprocess.run(["brew", "install", "ansible"], check=True, capture_output=True)
            
        elif system_info.os_type in [OperatingSystem.CENTOS, OperatingSystem.RHEL, OperatingSystem.FEDORA]:
            # CentOS/RHEL/Fedora - via pip
            pkg_manager = "dnf" if system_info.os_type == OperatingSystem.FEDORA else "yum"
            subprocess.run(["sudo", pkg_manager, "install", "-y", "python3-pip"], check=True, capture_output=True)
            
            # Instalar Ansible globalmente
            subprocess.run(["sudo", "pip3", "install", "ansible"], check=True, capture_output=True)
            
            # Verificar se o binário está acessível
            try:
                subprocess.run(["ansible", "--version"], check=True, capture_output=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                # Se não encontrar, tentar criar link simbólico
                ansible_paths = [
                    "/usr/local/bin/ansible",
                    "/home/user/.local/bin/ansible",
                    "/usr/bin/ansible"
                ]
                for path in ansible_paths:
                    if subprocess.run(["test", "-f", path], capture_output=True).returncode == 0:
                        subprocess.run(["sudo", "ln", "-sf", path, "/usr/bin/ansible"], capture_output=True)
                        break
        
        else:
            print(":warning: [yellow]Sistema não suportado para Ansible[/yellow]")
            return False
            
        print(":white_check_mark: [green]Ansible instalado com sucesso![/green]")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f":x: [red]Erro ao instalar Ansible: {e}[/red]")
        return False
    except Exception as e:
        print(f":x: [red]Erro inesperado ao instalar Ansible: {str(e)}[/red]")
        return False


def _install_watch(system_info) -> bool:
    """Instala watch baseado no sistema operacional."""
    try:
        from ..system.system_detector import OperatingSystem
        
        print(":gear: [blue]Instalando watch...[/blue]")
        
        if system_info.os_type in [
            OperatingSystem.UBUNTU, OperatingSystem.WSL_UBUNTU,
            OperatingSystem.DEBIAN, OperatingSystem.WSL_DEBIAN
        ]:
            # Ubuntu/Debian - via apt
            # Limpar repositórios corrompidos primeiro
            _cleanup_corrupted_repositories()
            subprocess.run(["sudo", "apt-get", "update"], check=True, capture_output=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "procps"], check=True, capture_output=True)
            
        elif system_info.os_type == OperatingSystem.MACOS:
            # macOS - via Homebrew
            subprocess.run(["brew", "install", "watch"], check=True, capture_output=True)
            
        elif system_info.os_type in [OperatingSystem.CENTOS, OperatingSystem.RHEL, OperatingSystem.FEDORA]:
            # CentOS/RHEL/Fedora - via yum/dnf
            pkg_manager = "dnf" if system_info.os_type == OperatingSystem.FEDORA else "yum"
            subprocess.run(["sudo", pkg_manager, "install", "-y", "procps-ng"], check=True, capture_output=True)
        
        else:
            print(":warning: [yellow]Sistema não suportado para watch[/yellow]")
            return False
            
        print(":white_check_mark: [green]watch instalado com sucesso![/green]")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f":x: [red]Erro ao instalar watch: {e}[/red]")
        return False
    except Exception as e:
        print(f":x: [red]Erro inesperado ao instalar watch: {str(e)}[/red]")
        return False


def _cleanup_corrupted_repositories() -> None:
    """Remove repositórios corrompidos que podem afetar apt-get update."""
    try:
        print(":broom: [blue]Limpando repositórios corrompidos...[/blue]")
        
        # Lista de arquivos de repositório que podem estar corrompidos
        corrupted_repos = [
            "/etc/apt/sources.list.d/hashicorp.list",
            "/etc/apt/sources.list.d/microsoft-prod.list",
            "/etc/apt/sources.list.d/azure-cli.list",
            "/etc/apt/sources.list.d/kubernetes.list"
        ]
        
        # Lista de chaves GPG que podem estar corrompidas
        corrupted_keys = [
            "/etc/apt/keyrings/hashicorp.gpg",
            "/etc/apt/keyrings/microsoft.gpg",
            "/etc/apt/keyrings/kubernetes-apt-keyring.gpg",
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