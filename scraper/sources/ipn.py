import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper.sources.base import FuenteBase

logger = logging.getLogger(__name__)


class IPNSource(FuenteBase):
    nombre = "ipn"

    URL = "https://www.ipn.mx/daes/servicios/becas/"

    def obtener_html(self) -> str:
        response = self.session.get(
            self.URL,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.text

    def _normalizar_url(self, enlace: str | None) -> str:
        """
        Convierte enlaces relativos del sitio del IPN en URLs absolutas.

        Ejemplos:
        /daes/servicios/becas/x.html
            -> https://www.ipn.mx/daes/servicios/becas/x.html

        servicios/becas/x.html
            -> https://www.ipn.mx/daes/servicios/becas/x.html

        resultados-dae/x.html
            -> https://www.ipn.mx/daes/resultados-dae/x.html
        """
        if not enlace:
            return self.URL

        enlace = enlace.strip()

        if not enlace:
            return self.URL

        # Ya es una URL absoluta.
        if enlace.startswith(("http://", "https://")):
            return enlace

        # URL absoluta del dominio escrita con / al inicio.
        if enlace.startswith("/"):
            return urljoin("https://www.ipn.mx", enlace)

        # Algunos enlaces del portal están expresados
        # como rutas relativas a /daes/.
        return urljoin("https://www.ipn.mx/daes/", enlace)

    def extraer_becas(self, html: str) -> list[dict]:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        becas: list[dict] = []

        # El portal oficial del IPN presenta diferentes
        # programas de becas. Buscamos encabezados y enlaces.
        elementos = soup.find_all(
            ["h2", "h3", "h4", "a"]
        )

        nombres_detectados: set[str] = set()

        for elemento in elementos:
            texto = elemento.get_text(
                " ",
                strip=True,
            )

            if not texto:
                continue

            texto_lower = texto.lower()

            if "beca" not in texto_lower:
                continue

            # Evitar títulos genéricos o excesivamente largos.
            if len(texto) < 5 or len(texto) > 200:
                continue

            if texto in nombres_detectados:
                continue

            nombres_detectados.add(texto)

            enlace = (
                elemento.get("href")
                if elemento.name == "a"
                else None
            )

            enlace = self._normalizar_url(enlace)

            # Intentamos encontrar texto cercano que sirva
            # como requisitos o descripción.
            descripcion = ""

            padre = elemento.parent

            if padre:
                parrafos = padre.find_all(
                    "p",
                    limit=2,
                )

                for parrafo in parrafos:
                    texto_parrafo = parrafo.get_text(
                        " ",
                        strip=True,
                    )

                    if texto_parrafo:
                        descripcion += " " + texto_parrafo

            descripcion = descripcion.strip()

            if not descripcion:
                descripcion = (
                    "Consulta la convocatoria y los "
                    "requisitos oficiales del IPN."
                )

            becas.append(
                {
                    "nombre_raw": texto,
                    "institucion_raw": "IPN",
                    "nivel_educativo_raw": "universidad",
                    "cobertura_raw": (
                        "Apoyo económico conforme a la "
                        "convocatoria vigente del IPN"
                    ),
                    "requisitos_raw": descripcion[:500],
                    "fecha_limite_raw": (
                        "Consultar convocatoria vigente"
                    ),
                    "link_raw": enlace,
                    "cobertura_100": False,
                }
            )

        logger.info(
            "[%s] Se detectaron %s posibles becas.",
            self.nombre,
            len(becas),
        )

        return becas