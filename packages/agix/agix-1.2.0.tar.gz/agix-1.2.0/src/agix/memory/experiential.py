"""Memoria de experiencias para agentes AGIX."""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from difflib import get_close_matches

logger = logging.getLogger(__name__)


@dataclass
class Experiencia:
    """Registro de una experiencia particular de un agente."""

    entrada: str
    decision: str
    resultado: str
    exito: bool
    timestamp: Optional[str] = None


class GestorDeMemoria:
    """Gestor simple de memoria experiencial."""

    def __init__(self, backend: str = "json", ruta: Optional[str] = None):
        self.backend = backend
        self.ruta = Path(ruta) if ruta else None
        self.experiencias: List[Experiencia] = []

    def _resolver_ruta(self, ruta: str | Path) -> Path:
        """Resuelve la ruta asegurando que esté dentro del directorio actual."""
        path = Path(ruta).expanduser().resolve()
        permitido = Path.cwd().resolve()
        try:
            path.relative_to(permitido)
        except ValueError as exc:
            logger.error(
                "Intento de acceso fuera del directorio permitido: %s", path
            )
            raise PermissionError("Ruta fuera del directorio permitido") from exc
        return path

    def registrar(
        self,
        entrada: str,
        decision: str,
        resultado: str,
        exito: bool,
        timestamp: Optional[str] = None,
    ) -> Experiencia:
        """Registra una experiencia en memoria."""
        ts = timestamp or datetime.utcnow().isoformat()
        exp = Experiencia(entrada, decision, resultado, exito, ts)
        self.experiencias.append(exp)
        return exp

    # ------------------------------------------------------------------
    def guardar(self, ruta: Optional[str] = None) -> None:
        """Persiste las experiencias en el backend configurado."""
        ruta_final = Path(ruta) if ruta else self.ruta
        if ruta_final is None:
            raise ValueError("Se requiere una ruta para guardar la memoria")
        ruta_final = self._resolver_ruta(ruta_final)

        if self.backend == "json":
            data = [asdict(e) for e in self.experiencias]
            with open(ruta_final, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif self.backend == "sqlite":
            conn = sqlite3.connect(ruta_final)
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS experiencias (
                    entrada TEXT,
                    decision TEXT,
                    resultado TEXT,
                    exito INTEGER,
                    timestamp TEXT
                )
                """
            )
            cur.executemany(
                "INSERT INTO experiencias VALUES (?, ?, ?, ?, ?)",
                [
                    (
                        e.entrada,
                        e.decision,
                        e.resultado,
                        int(e.exito),
                        e.timestamp,
                    )
                    for e in self.experiencias
                ],
            )
            conn.commit()
            conn.close()
        else:
            raise ValueError(f"Backend no soportado: {self.backend}")

    # ------------------------------------------------------------------
    def cargar(self, ruta: Optional[str] = None) -> None:
        """Carga experiencias desde el backend indicado."""
        ruta_final = Path(ruta) if ruta else self.ruta
        if ruta_final is None:
            raise ValueError("Se requiere una ruta para cargar la memoria")
        ruta_final = self._resolver_ruta(ruta_final)

        if self.backend == "json":
            with open(ruta_final, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.experiencias = [Experiencia(**d) for d in data]
        elif self.backend == "sqlite":
            conn = sqlite3.connect(ruta_final)
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS experiencias (
                    entrada TEXT,
                    decision TEXT,
                    resultado TEXT,
                    exito INTEGER,
                    timestamp TEXT
                )
                """
            )
            cur.execute(
                "SELECT entrada, decision, resultado, exito, timestamp FROM experiencias"
            )
            rows = cur.fetchall()
            self.experiencias = [
                Experiencia(
                    entrada,
                    decision,
                    resultado,
                    bool(exito),
                    timestamp,
                )
                for entrada, decision, resultado, exito, timestamp in rows
            ]
            conn.close()
        else:
            raise ValueError(f"Backend no soportado: {self.backend}")

    # ------------------------------------------------------------------
    def buscar_similar(self, consulta: str, campo: str = "entrada", n: int = 1) -> List[Experiencia]:
        """Devuelve las experiencias más parecidas a la consulta."""
        if campo not in {"entrada", "decision", "resultado"}:
            raise ValueError("Campo inválido para búsqueda")
        corpus = [getattr(e, campo) for e in self.experiencias]
        coincidencias = get_close_matches(consulta, corpus, n=n)
        return [e for e in self.experiencias if getattr(e, campo) in coincidencias]
