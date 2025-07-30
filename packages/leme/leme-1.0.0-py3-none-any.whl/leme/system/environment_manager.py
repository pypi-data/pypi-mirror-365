"""Gerenciador de ambiente DevOps - Setup de todas as ferramentas necessárias."""

import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from rich import print
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID

from .system_detector import SystemDetector, SystemInfo
from ..config.constants import Tool, DEVOPS_TOOLS_CONFIG


@dataclass
class ToolStatus:
    """Status de uma ferramenta."""
    tool: Tool
    installed: bool
    version: Optional[str] = None
    error: Optional[str] = None


class EnvironmentManager:
    """Gerenciador principal para setup do ambiente DevOps."""
    
    def __init__(self):
        """Inicializa o gerenciador de ambiente."""
        self.console = Console()
        self.system_info = SystemDetector.detect()
        self.tools_status: Dict[Tool, ToolStatus] = {}
    
    def check_tool(self, tool: Tool) -> ToolStatus:
        """
        Verifica se uma ferramenta está instalada.
        
        Args:
            tool: A ferramenta a ser verificada
            
        Returns:
            ToolStatus: Status da ferramenta
        """
        config = DEVOPS_TOOLS_CONFIG[tool]
        
        try:
            result = subprocess.run(
                config["check_command"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Extrair versão do output
                version = self._extract_version(tool, result.stdout)
                return ToolStatus(tool=tool, installed=True, version=version)
            else:
                return ToolStatus(tool=tool, installed=False, error=result.stderr.strip())
                
        except subprocess.TimeoutExpired:
            return ToolStatus(tool=tool, installed=False, error="Timeout")
        except FileNotFoundError:
            return ToolStatus(tool=tool, installed=False, error="Command not found")
        except Exception as e:
            return ToolStatus(tool=tool, installed=False, error=str(e))
    
    def _extract_version(self, tool: Tool, output: str) -> Optional[str]:
        """
        Extrai a versão do output do comando.
        
        Args:
            tool: A ferramenta
            output: Output do comando
            
        Returns:
            str: Versão extraída ou None
        """
        lines = output.strip().split('\n')
        if not lines:
            return None
            
        first_line = lines[0].strip()
        
        # Padrões específicos para cada ferramenta
        if tool == Tool.DOCKER:
            # Docker version 24.0.6, build ed223bc
            if "Docker version" in first_line:
                return first_line.split(',')[0].replace("Docker version", "").strip()
        
        elif tool == Tool.GIT:
            # git version 2.39.2
            if "git version" in first_line:
                return first_line.replace("git version", "").strip()
        
        elif tool == Tool.TERRAFORM:
            # Terraform v1.5.7
            if "Terraform" in first_line:
                return first_line.replace("Terraform", "").strip()
        
        elif tool == Tool.AZURE_CLI:
            # Para az, a versão pode estar em JSON ou texto
            try:
                import json
                data = json.loads(output)
                # Tentar diferentes chaves possíveis
                version = data.get("azure-cli-core") or data.get("azure-cli") or data.get("core")
                if version:
                    return version
            except:
                # Se não for JSON, tentar extrair da primeira linha
                # azure-cli                         2.75.0
                if "azure-cli" in first_line:
                    parts = first_line.split()
                    if len(parts) >= 2:
                        return parts[1]
        
        elif tool == Tool.AWS_CLI:
            # aws-cli/2.13.25 Python/3.11.5
            if "aws-cli" in first_line:
                return first_line.split()[0].replace("aws-cli/", "")
        
        elif tool == Tool.KUBECTL:
            # Client Version: version.Info{Major:"1", Minor:"28"...
            if "Client Version" in first_line:
                # Extrair versão básica
                if "Major:" in first_line and "Minor:" in first_line:
                    import re
                    major = re.search(r'Major:"([^"]+)"', first_line)
                    minor = re.search(r'Minor:"([^"]+)"', first_line)
                    if major and minor:
                        return f"v{major.group(1)}.{minor.group(1)}"
        
        elif tool == Tool.ANSIBLE:
            # ansible [core 2.15.3]
            if "ansible" in first_line:
                import re
                version_match = re.search(r'\[core ([^\]]+)\]', first_line)
                if version_match:
                    return version_match.group(1)
        
        elif tool == Tool.WATCH:
            # watch from procps-ng 3.3.17
            if "watch from" in first_line:
                return first_line.split()[-1]
        
        return first_line
    
    def check_all_tools(self) -> Dict[Tool, ToolStatus]:
        """
        Verifica o status de todas as ferramentas.
        
        Returns:
            Dict[Tool, ToolStatus]: Status de todas as ferramentas
        """
        print("\n:mag: [bold blue]Verificando ferramentas instaladas...[/bold blue]")
        
        with Progress() as progress:
            task = progress.add_task("[blue]Verificando...", total=len(Tool))
            
            for tool in Tool:
                self.tools_status[tool] = self.check_tool(tool)
                progress.update(task, advance=1)
        
        return self.tools_status
    
    def show_status_report(self) -> None:
        """Exibe um relatório detalhado do status das ferramentas."""
        if not self.tools_status:
            self.check_all_tools()
        
        print("\n:clipboard: [bold cyan]Relatório do Ambiente DevOps[/bold cyan]")
        
        # Criar tabela
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Ferramenta", style="dim", width=12)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Versão", width=20)
        table.add_column("Descrição", width=30)
        table.add_column("Obrigatória", justify="center", width=10)
        
        # Ordenar por prioridade
        sorted_tools = sorted(Tool, key=lambda t: DEVOPS_TOOLS_CONFIG[t]["priority"])
        
        for tool in sorted_tools:
            config = DEVOPS_TOOLS_CONFIG[tool]
            status = self.tools_status.get(tool)
            
            if not status:
                continue
            
            # Status visual
            if status.installed:
                status_text = "[green]✓ Instalado[/green]"
                version_text = status.version or "Versão não detectada"
            else:
                status_text = "[red]✗ Não instalado[/red]"
                version_text = "[dim]N/A[/dim]"
            
            # Obrigatória
            required_text = "[red]Sim[/red]" if config["required"] else "[yellow]Não[/yellow]"
            
            table.add_row(
                config["name"],
                status_text,
                version_text,
                config["description"],
                required_text
            )
        
        self.console.print(table)
        
        # Resumo
        installed_count = sum(1 for status in self.tools_status.values() if status.installed)
        total_count = len(self.tools_status)
        required_tools = [t for t in Tool if DEVOPS_TOOLS_CONFIG[t]["required"]]
        required_installed = sum(1 for t in required_tools if self.tools_status.get(t, ToolStatus(t, False)).installed)
        
        print(f"\n:chart_with_upwards_trend: [bold]Resumo:[/bold]")
        print(f"  • [blue]Ferramentas instaladas:[/blue] {installed_count}/{total_count}")
        print(f"  • [red]Ferramentas obrigatórias:[/red] {required_installed}/{len(required_tools)}")
        
        if required_installed == len(required_tools):
            print("  • [green]✓ Ambiente mínimo configurado![/green]")
        else:
            missing_required = [t for t in required_tools if not self.tools_status.get(t, ToolStatus(t, False)).installed]
            print(f"  • [red]✗ Faltam ferramentas obrigatórias: {[DEVOPS_TOOLS_CONFIG[t]['name'] for t in missing_required]}[/red]")
    
    def get_missing_tools(self, only_required: bool = False) -> List[Tool]:
        """
        Retorna lista de ferramentas não instaladas.
        
        Args:
            only_required: Se True, retorna apenas ferramentas obrigatórias
            
        Returns:
            List[Tool]: Lista de ferramentas não instaladas
        """
        if not self.tools_status:
            self.check_all_tools()
        
        missing = []
        for tool, status in self.tools_status.items():
            if not status.installed:
                if only_required:
                    if DEVOPS_TOOLS_CONFIG[tool]["required"]:
                        missing.append(tool)
                else:
                    missing.append(tool)
        
        # Ordenar por prioridade
        return sorted(missing, key=lambda t: DEVOPS_TOOLS_CONFIG[t]["priority"])
    
    def is_environment_ready(self) -> bool:
        """
        Verifica se o ambiente está pronto (todas as ferramentas obrigatórias instaladas).
        
        Returns:
            bool: True se todas as ferramentas obrigatórias estão instaladas
        """
        missing_required = self.get_missing_tools(only_required=True)
        return len(missing_required) == 0