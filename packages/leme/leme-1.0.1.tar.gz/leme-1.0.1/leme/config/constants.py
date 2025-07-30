"""Constantes e configurações da aplicação."""

import enum
from pathlib import Path




class Tool(str, enum.Enum):
    """Ferramentas que podem ser instaladas."""
    DOCKER = "docker"
    TERRAFORM = "terraform"
    ANSIBLE = "ansible"
    AZURE_CLI = "az"
    AWS_CLI = "aws"
    GIT = "git"
    KUBECTL = "kubectl"
    WATCH = "watch"


# Configurações de paths
BASE_PATH = Path(__file__).parent.parent.parent
SRC_PATH = BASE_PATH / "src"

# Configurações das ferramentas DevOps
DEVOPS_TOOLS_CONFIG = {
    Tool.DOCKER: {
        "name": "Docker",
        "description": "Plataforma de containerização",
        "check_command": ["docker", "--version"],
        "priority": 1,
        "required": False
    },
    Tool.TERRAFORM: {
        "name": "Terraform",
        "description": "Ferramenta de infraestrutura como código",
        "check_command": ["terraform", "--version"],
        "priority": 2,
        "required": False
    },
    Tool.GIT: {
        "name": "Git",
        "description": "Sistema de controle de versão",
        "check_command": ["git", "--version"],
        "priority": 3,
        "required": False
    },
    Tool.AZURE_CLI: {
        "name": "Azure CLI",
        "description": "Interface de linha de comando da Azure",
        "check_command": ["az", "--version"],
        "priority": 4,
        "required": False
    },
    Tool.AWS_CLI: {
        "name": "AWS CLI v2",
        "description": "Interface de linha de comando da AWS",
        "check_command": ["aws", "--version"],
        "priority": 5,
        "required": False
    },
    Tool.KUBECTL: {
        "name": "kubectl",
        "description": "Cliente para Kubernetes",
        "check_command": ["kubectl", "version", "--client"],
        "priority": 6,
        "required": False
    },
    Tool.ANSIBLE: {
        "name": "Ansible",
        "description": "Automação e gerenciamento de configuração",
        "check_command": ["ansible", "--version"],
        "priority": 7,
        "required": False
    },
    Tool.WATCH: {
        "name": "watch",
        "description": "Executa comandos periodicamente",
        "check_command": ["watch", "--version"],
        "priority": 8,
        "required": False
    }
}