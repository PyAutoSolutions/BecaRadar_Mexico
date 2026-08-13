import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper.sources.base import FuenteBase

logger = logging.getLogger(__name__)


class UNAMSource(FuenteBase):
    nombre = "unam"

    # Página oficial vigente del Portal del Becario de la UNAM.
    URL = "https://www.becarios.unam.mx/Portal2018/?page_id=11147"

    def obtener_html(self) -> str:
        response = self.session.get(
            self.URL,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.text

    def extraer_becas(self, html: str) -> list[dict]:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        becas: list[dict] = []
        vistos: set[str] = set()

        for enlace in soup.find_all("a"):
            texto = enlace.get_text(
                " ",
                strip=True,
            )

            href = enlace.get("href")

            if not texto or not href:
                continue

            texto_lower = texto.lower().strip()

            # Solo considerar enlaces relacionados con becas,
            # convocatorias o programas de apoyo.
            es_beca = (
                "beca" in texto_lower
                or "convocatoria" in texto_lower
                or "apoyo nutricional" in texto_lower
                or "manutención" in texto_lower
                or "manutencion" in texto_lower
            )

            if not es_beca:
                continue

            if len(texto) < 8 or len(texto) > 300:
                continue

            link = urljoin(
                self.URL,
                href,
            )

            if link.startswith("#"):
                continue

            if link in vistos:
                continue

            vistos.add(link)

            # No convertir índices, menús o páginas generales
            # en registros de becas individuales.
            texto_generico = {
                "becas",
                "convocatorias",
                "convocatoria",
                "consulta de resultados",
                "resultados",
                "histórico de convocatorias",
                "historico de convocatorias",
            }

            if texto_lower in texto_generico:
                continue

            # También excluir títulos claramente administrativos
            # que no representan una beca concreta.
            if (
                "histórico de convocatorias" in texto_lower
                or "historico de convocatorias" in texto_lower
            ):
                continue

            becas.append(
                {
                    "nombre_raw": texto,
                    "institucion_raw": "UNAM",
                    "nivel_educativo_raw": "universidad",
                    "cobertura_raw": (
                        "Consulta el monto y características "
                        "en la convocatoria oficial."
                    ),
                    "requisitos_raw": (
                        "Consultar requisitos específicos en la "
                        "convocatoria oficial de la UNAM."
                    ),
                    "fecha_limite_raw": None,
                    "link_raw": link,
                    "cobertura_100": False,
                }
            )

        logger.info(
            "[%s] Se detectaron %s posibles convocatorias/becas.",
            self.nombre,
            len(becas),
        )

        return becas