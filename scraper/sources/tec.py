import logging
import time

import requests
from bs4 import BeautifulSoup

from scraper.sources.base import FuenteBase

logger = logging.getLogger(__name__)


class TECSource(FuenteBase):
    nombre = "tec"

    # Fuentes oficiales del Tecnológico de Monterrey.
    BECAS_CONOCIDAS = (
        (
            "Beca Líderes del Mañana",
            "https://conecta.tec.mx/es/noticias/nacional/educacion/aplica-para-una-beca-del-100-para-estudiar-en-el-tec-de-monterrey",
            True,
        ),
        (
            "Beca al Talento Académico",
            "https://profesional.admisiones.tec.mx/apoyos-especiales",
            False,
        ),
        (
            "Beca Socioeconómica",
            "https://profesional.admisiones.tec.mx/apoyos-especiales",
            False,
        ),
    )

    def obtener_html(self) -> str:
        return ""

    def extraer_becas(self, html: str) -> list[dict]:
        return []

    def ejecutar(self) -> list[dict]:
        """Consulta las fuentes oficiales de becas del Tec."""

        logger.info(
            "[%s] Iniciando extracción de becas conocidas...",
            self.nombre,
        )

        becas_encontradas: list[dict] = []

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0 Safari/537.36"
            )
        }

        for nombre, url, es_100 in self.BECAS_CONOCIDAS:
            try:
                time.sleep(1)

                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                soup = BeautifulSoup(
                    response.text,
                    "html.parser",
                )

                parrafos = soup.find_all("p")
                textos: list[str] = []

                for parrafo in parrafos:
                    texto = parrafo.get_text(
                        " ",
                        strip=True,
                    )

                    if texto and len(texto) >= 30:
                        textos.append(texto)

                if textos:
                    texto_resumen = " ".join(textos[:3])
                else:
                    texto_resumen = (
                        "Consulta la convocatoria y los requisitos "
                        "en la página oficial del Tecnológico de Monterrey."
                    )

                texto_resumen = texto_resumen[:500]

                if es_100:
                    cobertura = (
                        "100% de colegiatura durante toda la carrera"
                    )
                elif nombre == "Beca al Talento Académico":
                    cobertura = (
                        "Hasta 60% de apoyo, según convocatoria"
                    )
                else:
                    cobertura = (
                        "Porcentaje variable de beca y/o apoyo "
                        "educativo según necesidad económica"
                    )

                becas_encontradas.append(
                    {
                        "nombre_raw": nombre,
                        "institucion_raw": "Tecnológico de Monterrey",
                        "nivel_educativo_raw": "universidad",
                        "cobertura_raw": cobertura,
                        "requisitos_raw": texto_resumen,
                        "fecha_limite_raw": None,
                        "link_raw": url,
                        "cobertura_100": es_100,
                    }
                )

                logger.info(
                    "[%s] Extraída exitosamente: %s",
                    self.nombre,
                    nombre,
                )

            except requests.RequestException as exc:
                logger.warning(
                    "[%s] No se pudo acceder a %s (%s): %s",
                    self.nombre,
                    nombre,
                    url,
                    exc,
                )

            except Exception:
                logger.exception(
                    "[%s] Error procesando %s",
                    self.nombre,
                    nombre,
                )

        return becas_encontradas