"""Modelo interno simplificado del agente."""


class SelfModel:
    """Representa estado y módulos propios para introspección."""

    def __init__(self, agent_name: str = "AGI-Core", version: str = "1.1.0") -> None:
        self.identity = {
            "name": agent_name,
            "version": version,
        }
        self.state = {}
        self.modules = {}

    def register_module(self, name: str, description: str) -> None:
        """Registra una descripción simbólica de un módulo interno."""
        self.modules[name] = description

    def update_state(self, key: str, value) -> None:
        """Actualiza variables internas del agente (estado reflexivo)."""
        self.state[key] = value

    def introspect(self) -> dict:
        """Retorna un resumen reflexivo del estado y estructura interna."""
        return {
            "identity": self.identity,
            "modules": self.modules,
            "state": self.state,
        }

    def generate_self_query(self) -> str:
        """Devuelve una pregunta típica que el agente se haría a sí mismo."""
        return f"¿Estoy cumpliendo mi propósito como {self.identity['name']}?"

