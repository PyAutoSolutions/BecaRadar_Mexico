import logging
from abc import ABC, abstractmethod

import requests

logger = logging.getLogger(__name__)

class FuenteNoDisponibleException(Exception):
    """Excepción lanzada cuando hay un error de red o timeout intentando acceder a la fuente."""

class FuenteBase(ABC):
    nombre: str = ""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "BecaRadar Bot (Educativo/No-Comercial) - https://github.com/gabriel/becaradar"
        })
        self.timeout = 15

    @abstractmethod
    def obtener_html(self) -> str:
        """Realiza la petición HTTP y retorna el HTML crudo."""

    @abstractmethod
    def extraer_becas(self, html: str) -> list[dict]:
        """Parsea el HTML y retorna una lista de diccionarios crudos."""

    def ejecutar(self) -> list[dict]:
        """Patrón Template Method: Orquesta los pasos de extracción."""
        logger.info(f"[{self.nombre}] Iniciando extracción...")
        try:
            html = self.obtener_html()
            logger.debug(f"[{self.nombre}] HTML obtenido, iniciando parseo...")
            return self.extraer_becas(html)
        except requests.RequestException as e:
            logger.error(f"[{self.nombre}] Error de red: {e}")
            raise FuenteNoDisponibleException(f"Error conectando a la fuente: {e}")