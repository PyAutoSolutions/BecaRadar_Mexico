import argparse
import logging
import sys

from scraper.pipeline import ejecutar_pipeline
from scraper.sources import (
    BenitoJuarezSource,
    IPNSource,
    TECSource,
    UNAMSource,
)


def main():
    parser = argparse.ArgumentParser(description="Ejecuta el scraper de BecaRadar")
    parser.add_argument(
        "--fuente", 
        type=str, 
        help="Ejecutar solo una fuente específica (benito_juarez, unam, ipn, tec)"
    )
    args = parser.parse_args()

    # Configuración básica de logging para stdout (capturada por GitHub Actions)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logger = logging.getLogger(__name__)

    try:
        todas_las_fuentes = [
            BenitoJuarezSource(),
            UNAMSource(),
            IPNSource(),
            TECSource()
        ]

        if args.fuente:
            fuentes_a_ejecutar = [f for f in todas_las_fuentes if f.nombre == args.fuente.lower()]
            if not fuentes_a_ejecutar:
                logger.error(f"Fuente '{args.fuente}' no encontrada.")
                sys.exit(1)
            logger.info(f"Ejecutando fuente aislada: {args.fuente}")
        else:
            fuentes_a_ejecutar = todas_las_fuentes
            logger.info(f"Ejecutando todas las fuentes ({len(fuentes_a_ejecutar)})")

        resultado = ejecutar_pipeline(fuentes_a_ejecutar)
        
        logger.info(f"Pipeline finalizado. Exitoso: {resultado.exitoso}")
        sys.exit(0 if resultado.exitoso else 1)

    except Exception:
        logger.exception("Error catastrófico no manejado en la ejecución del scraper.")
        sys.exit(1)

if __name__ == "__main__":
    main()