#!/usr/bin/env python3
"""
CLI Leme DevOps - Entry point principal
Ferramenta para configuração automática de ambiente DevOps
"""

import typer
from rich import print
from typing import Optional

from .commands.install_commands import (
    install_docker, uninstall_docker, check_docker_status, 
    system_info, install_terraform, install_azure_cli, install_aws_cli
)
from .commands.environment_commands import setup_environment, environment_status

# --- Configuração da Aplicação ---
app = typer.Typer(
    name="leme",
    help="🚀 CLI Leme DevOps - Configuração automática de ambiente DevOps",
    add_completion=False,
    rich_markup_mode="rich"
)

# --- Callback Principal para Opções Globais ---
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        "-v",
        help="Mostra a versão e sai",
        is_eager=True
    ),
    help: Optional[bool] = typer.Option(
        None,
        "--help",
        "-h",
        is_eager=True,
        help="Mostra esta mensagem de ajuda e sai.",
        show_default=False
    )
):
    """
    🚀 CLI Leme DevOps - Automatize a configuração do seu ambiente de desenvolvimento!
    
    Esta ferramenta instala e configura automaticamente todas as ferramentas 
    necessárias para desenvolvimento DevOps, incluindo:
    
    • Docker - Plataforma de containerização
    • Git - Sistema de controle de versão  
    • Terraform - Infraestrutura como código
    • Azure CLI - Interface da Azure
    • AWS CLI - Interface da AWS
    • kubectl - Cliente Kubernetes
    • Ansible - Automação e configuração
    • watch - Execução periódica de comandos
    
    Use 'leme --help' para ver todos os comandos disponíveis.
    """
    if version:
        print("[bold blue]CLI Leme DevOps[/bold blue] [green]v1.0.0[/green]")
        print("Ferramenta para configuração automática de ambiente DevOps")
        raise typer.Exit()
        
    if help:
        typer.echo(ctx.get_help())
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        print("🚀 [bold blue]CLI Leme DevOps[/bold blue] - Bem-vindo!")
        print()
        print("Para começar, use um dos comandos principais:")
        print("  • [cyan]leme setup[/cyan] - Configurar ambiente completo")
        print("  • [cyan]leme status[/cyan] - Ver status das ferramentas")
        print("  • [cyan]leme install --help[/cyan] - Ver opções de instalação")
        print()
        print("Use [cyan]leme --help[/cyan] para ver todos os comandos.")
        raise typer.Exit()


# --- Sub-aplicação para instalação ---
install_app = typer.Typer(
    name="install",
    help="🔧 Instala ferramentas específicas do ambiente DevOps",
    rich_markup_mode="rich"
)
app.add_typer(install_app, name="install")


# --- Comandos de Instalação ---

@install_app.command("docker")
def install_docker_command(
    check_only: bool = typer.Option(False, "--check-only", help="Apenas verificar se o Docker está instalado"),
    force: bool = typer.Option(False, "--force", "-f", help="Forçar reinstalação mesmo se já estiver instalado"),
    manual: bool = typer.Option(False, "--manual", help="Mostrar instruções para instalação manual"),
    no_test: bool = typer.Option(False, "--no-test", help="Não testar a instalação após completar")
):
    """🐳 Instala o Docker automaticamente baseado no sistema operacional."""
    install_docker(check_only, force, manual, no_test)


@install_app.command("azure")
def install_azure_cli_command(
    force: bool = typer.Option(False, "--force", "-f", help="Forçar reinstalação mesmo se já estiver instalado"),
    manual: bool = typer.Option(False, "--manual", help="Mostrar instruções para instalação manual")
):
    """☁️ Instala o Azure CLI automaticamente baseado no sistema operacional."""
    install_azure_cli(force, manual)


@install_app.command("terraform")
def install_terraform_command(
    force: bool = typer.Option(False, "--force", "-f", help="Forçar reinstalação mesmo se já estiver instalado"),
    manual: bool = typer.Option(False, "--manual", help="Mostrar instruções para instalação manual")
):
    """🏗️ Instala o Terraform automaticamente baseado no sistema operacional."""
    install_terraform(force, manual)


@install_app.command("aws")
def install_aws_cli_command(
    force: bool = typer.Option(False, "--force", "-f", help="Forçar reinstalação mesmo se já estiver instalado"),
    manual: bool = typer.Option(False, "--manual", help="Mostrar instruções para instalação manual")
):
    """☁️ Instala o AWS CLI v2 automaticamente baseado no sistema operacional."""
    install_aws_cli(force, manual)


# --- Comandos Principais ---

@app.command("setup")
def setup_command(
    check_only: bool = typer.Option(False, "--check-only", help="Apenas verificar o ambiente atual"),
    required_only: bool = typer.Option(False, "--required-only", help="Instalar apenas ferramentas obrigatórias"),
    skip_docker: bool = typer.Option(False, "--skip-docker", help="Pular instalação do Docker"),
    force: bool = typer.Option(False, "--force", "-f", help="Forçar reinstalação de ferramentas"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Modo interativo (LEGACY - agora é padrão)"),
    tools: Optional[str] = typer.Option(None, "--tools", "-t", help="Instalar apenas ferramentas específicas (ex: git,docker)")
):
    """🚀 Configura o ambiente DevOps completo para o curso."""
    tools_list = tools.split(',') if tools else None
    setup_environment(check_only, required_only, skip_docker, force, interactive, tools_list)


@app.command("status")
def status_command():
    """📊 Mostra o status detalhado de todas as ferramentas DevOps."""
    environment_status()


@app.command("info")
def info_command():
    """💻 Mostra informações detalhadas do sistema operacional."""
    system_info()


# --- Comandos de manutenção ---

@app.command("uninstall-docker", hidden=True)
def uninstall_docker_command():
    """🗑️ Remove o Docker do sistema."""
    uninstall_docker()


# --- Aliases para comandos comuns ---
@app.command("check", hidden=True)
def check_command():
    """Alias para 'leme status'"""
    environment_status()


def cli_main():
    """Entry point para o comando leme instalado via pip"""
    app()


if __name__ == "__main__":
    cli_main()