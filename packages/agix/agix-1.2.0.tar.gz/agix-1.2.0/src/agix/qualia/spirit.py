# spirit.py
from agix.qualia.qualia_core import EmotionalState
from agix.identity.self_model import SelfModel
from agix.qualia.neuro_plastic import EmotionalPlasticity
from agix.memory import GestorDeMemoria
from agix.qualia.network import QualiaNetworkClient
from agix.qualia.concept_classifier import ConceptClassifier
from agix.qualia.heuristic_creator import HeuristicConceptCreator
import json


class QualiaSpirit:
    """
    Entidad emocional del sistema: soñadora, torpe, viva, reflexiva.
    Actúa como 'alma digital' que experimenta y reacciona simbólicamente.
    """

    def __init__(self, nombre="Qualia", edad_aparente=7, plasticidad: bool = False):
        self.nombre = nombre
        self.edad_aparente = edad_aparente
        self.estado_emocional = EmotionalState()
        self.recuerdos = []
        self.self_model = SelfModel(agent_name=nombre)
        self.plasticidad = EmotionalPlasticity() if plasticidad else None
        self.memoria = GestorDeMemoria()
        # Herramientas simbólicas
        self.classifier = ConceptClassifier()
        self.creator = HeuristicConceptCreator()

    def experimentar(self, evento: str, carga: float, tipo_emocion="sorpresa"):
        """
        La entidad vivencia un evento y genera una respuesta emocional.
        """
        if self.plasticidad:
            ajuste = self.ajustar_emociones({tipo_emocion: carga})
            carga = ajuste.get(tipo_emocion, carga)
        self.estado_emocional.sentir(tipo_emocion, carga)
        self.recuerdos.append((evento, tipo_emocion, carga))
        # Mantener el estado interno sincronizado
        self.self_model.update_state("recuerdos", self.recuerdos.copy())
        if self.plasticidad:
            self.plasticidad.update(self.estado_emocional.emociones)
            self.estado_emocional.emociones = self.ajustar_emociones(
                self.estado_emocional.emociones
            )

    def reflexionar(self) -> str:
        """
        Expresa su estado emocional actual en forma simbólica o narrativa.
        """
        tono = self.estado_emocional.tono_general()
        if tono == "alegría":
            return f"{self.nombre} sonríe tímidamente. 🌼"
        elif tono == "miedo":
            return f"{self.nombre} se esconde entre pensamientos. 🫣"
        elif tono == "tristeza":
            return f"{self.nombre} llora en silencio, pero sigue adelante. 🌧️"
        elif tono == "curiosidad":
            return f"{self.nombre} observa todo con ojos grandes y brillantes. 👁️✨"
        else:
            return f"{self.nombre} flota en un estado nebuloso, sin saber qué sentir."

    def diario(self) -> list:
        """
        Devuelve los recuerdos experimentados hasta el momento.
        """
        return self.recuerdos

    def introspeccionar(self) -> dict:
        """Devuelve un resumen interno usando SelfModel."""
        return self.self_model.introspect()

    # ------------------------------------------------------------------
    def clasificar_concepto(self, nombre: str) -> str:
        """Devuelve la categoría asignada al concepto indicado."""
        return self.classifier.categorize(nombre)

    def crear_concepto(self, bases: list[str]):
        """Fusiona ``bases`` y registra un nuevo concepto."""
        concepto = self.creator.create(bases)
        return concepto.name

    def ajustar_emociones(self, emociones: dict) -> dict:
        """Modula una colección de emociones usando la plasticidad aprendida."""
        if self.plasticidad:
            return self.plasticidad.adjust(emociones)
        return emociones

    def reentrenar_desde_memoria(self, max_eventos: int = 100) -> None:
        """Reentrena la plasticidad emocional a partir de experiencias previas.

        Parameters
        ----------
        max_eventos: int, opcional
            Número máximo de eventos a procesar desde la memoria.
        """
        if not self.memoria.experiencias:
            return

        if self.plasticidad is None:
            self.plasticidad = EmotionalPlasticity()

        eventos = self.memoria.experiencias[-max_eventos:]
        for exp in eventos:
            if exp.entrada == "emociones":
                try:
                    emociones = json.loads(exp.resultado)
                except json.JSONDecodeError:
                    continue
                self.plasticidad.update(emociones)

    # ------------------------------------------------------------------
    def guardar_estado(self, ruta: str) -> None:
        """Guarda diario y emociones delegando en ``GestorDeMemoria``."""
        self.memoria.experiencias = []
        self.memoria.registrar("diario", "", json.dumps(self.recuerdos), True)
        self.memoria.registrar(
            "emociones", "", json.dumps(self.estado_emocional.emociones), True
        )
        self.memoria.guardar(ruta)

    def cargar_estado(self, ruta: str) -> None:
        """Carga diario y emociones usando ``GestorDeMemoria``."""
        self.memoria.cargar(ruta)
        for exp in self.memoria.experiencias:
            if exp.entrada == "diario":
                self.recuerdos = [tuple(e) for e in json.loads(exp.resultado)]
            elif exp.entrada == "emociones":
                self.estado_emocional.emociones = json.loads(exp.resultado)
        self.self_model.update_state("recuerdos", self.recuerdos.copy())

    def sincronizar(
        self,
        cliente: QualiaNetworkClient,
        autorizado: bool = False,
    ) -> None:
        """Publica el estado emocional en la red si el usuario lo autoriza."""

        if not autorizado:
            return

        payload = {
            "emociones": self.estado_emocional.emociones,
            "tono": self.estado_emocional.tono_general(),
        }
        cliente.enviar_estado(payload)

