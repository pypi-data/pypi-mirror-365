# src/agix/cli/qualia_shell.py
"""Shell interactivo para QualiaSpirit."""

import argparse
from typing import Optional

from src.agix.qualia.spirit import QualiaSpirit
from src.agix.security.blocker import verificar

HELP_TEXT = (
    "Comandos disponibles:\n"
    "  exp <evento>;<carga>;<emocion> - Registrar una experiencia\n"
    "  clasifica <concepto>              - Categorizar un concepto\n"
    "  crea <c1,c2,...>                  - Fusionar conceptos\n"
    "  reflexiona                        - Mostrar reflexion actual\n"
    "  diario                            - Listar recuerdos\n"
    "  guardar <ruta>                   - Guardar estado\n"
    "  cargar <ruta>                    - Cargar estado\n"
    "  salir                             - Terminar la sesión"
)


def handle_command(spirit: QualiaSpirit, command: str) -> str:
    """Procesa un comando de la shell.

    Parameters
    ----------
    spirit: QualiaSpirit
        Instancia sobre la cual actuar.
    command: str
        Texto introducido por el usuario.

    Returns
    -------
    str
        Mensaje de respuesta. Si retorna "exit" se finaliza el bucle.
    """
    command = command.strip()
    if not command:
        return ""

    if not verificar(command):
        spirit.memoria.registrar("bloqueo", command, "", False)
        return "Comando bloqueado."

    if command in {"salir", "exit", "quit"}:
        return "exit"

    if command == "reflexiona":
        return spirit.reflexionar()

    if command == "diario":
        return str(spirit.diario())

    if command.startswith("guardar "):
        ruta = command.split(" ", 1)[1].strip()
        if ruta:
            spirit.guardar_estado(ruta)
            return "Estado guardado."
        return "Debes indicar una ruta"

    if command.startswith("cargar "):
        ruta = command.split(" ", 1)[1].strip()
        if ruta:
            spirit.cargar_estado(ruta)
            return "Estado cargado."
        return "Debes indicar una ruta"

    if command.startswith("clasifica "):
        concepto = command.split(" ", 1)[1].strip()
        if concepto:
            return spirit.clasificar_concepto(concepto)
        return "Debes indicar un concepto"

    if command.startswith("crea "):
        payload = command.split(" ", 1)[1].strip()
        if payload:
            bases = [c.strip() for c in payload.split(",") if c.strip()]
            try:
                return spirit.crear_concepto(bases)
            except ValueError as exc:
                return str(exc)
        return "Debes indicar al menos dos conceptos separados por coma"

    if command.startswith("exp "):
        payload = command[4:].strip()
        try:
            evento, carga, emocion = [p.strip() for p in payload.split(";")]
            spirit.experimentar(evento, float(carga), emocion)
            return "Evento registrado."
        except ValueError:
            return "Formato inválido. Usa: exp <evento>;<carga>;<emocion>"

    return HELP_TEXT


def run_shell(args: argparse.Namespace) -> None:
    """Inicia un loop interactivo con :class:`QualiaSpirit`."""
    spirit = QualiaSpirit(nombre=args.name, edad_aparente=args.age)

    if args.replay:
        spirit.cargar_estado(args.replay)
        spirit.reentrenar_desde_memoria()

    print("\n🌈 Bienvenido al Qualia Shell. Escribe 'ayuda' para ver comandos.\n")
    while True:
        try:
            user_input = input("qualia> ")
        except EOFError:
            print()
            break

        if user_input.strip() == "ayuda":
            print(HELP_TEXT)
            continue

        response = handle_command(spirit, user_input)
        if response == "exit":
            break
        if response:
            print(response)

    print("Hasta pronto. ✨")


def build_parser(parser: Optional[argparse.ArgumentParser] = None) -> argparse.ArgumentParser:
    """Construye el parser para el subcomando ``qualia``."""
    if parser is None:
        parser = argparse.ArgumentParser(description="Shell interactivo para QualiaSpirit")

    parser.add_argument("--name", type=str, default="Qualia", help="Nombre de la entidad")
    parser.add_argument("--age", type=int, default=7, help="Edad aparente")
    parser.add_argument(
        "--replay",
        type=str,
        default="",
        metavar="RUTA",
        help="Reentrena emociones desde el archivo indicado",
    )
    return parser


__all__ = ["run_shell", "build_parser", "handle_command"]
