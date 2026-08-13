from app.db.models.beca import Beca
from app.db.models.institucion import Institucion
from app.db.session import SessionLocal

IPN_URL_ANTIGUA = "https://www.ipn.mx/dae/servicios/becas.html"
IPN_URL_NUEVA = "https://www.ipn.mx/daes/servicios/becas/"

UNAM_INDICE = "Histórico de convocatorias"
UNAM_INDICE_URL = "https://www.becarios.unam.mx/Portal2018/?page_id=1728"

TEC_NOMBRE_PRINCIPAL = "Beca Líderes del Mañana"
TEC_NOMBRE_DUPLICADO = "Líderes del Mañana"


def main() -> None:
    db = SessionLocal()

    try:
        cambios = 0

        # ---------------------------------------------------------
        # 1. Corregir URL antigua del IPN
        # ---------------------------------------------------------
        becas_ipn = (
            db.query(Beca)
            .join(Institucion)
            .filter(
                Institucion.nombre == "IPN",
                Beca.link_oficial == IPN_URL_ANTIGUA,
            )
            .all()
        )

        for beca in becas_ipn:
            beca.link_oficial = IPN_URL_NUEVA
            cambios += 1
            print(f"URL IPN corregida: {beca.nombre}")

        # ---------------------------------------------------------
        # 2. Eliminar "Histórico de convocatorias" de UNAM
        # ---------------------------------------------------------
        registros_historico = (
            db.query(Beca)
            .join(Institucion)
            .filter(
                Institucion.nombre == "UNAM",
                Beca.nombre == UNAM_INDICE,
            )
            .all()
        )

        for beca in registros_historico:
            db.delete(beca)
            cambios += 1
            print(f"Índice UNAM eliminado: {beca.nombre}")

        # ---------------------------------------------------------
        # 3. Eliminar duplicado de Líderes del Mañana
        # ---------------------------------------------------------
        institucion_tec = (
            db.query(Institucion)
            .filter(
                Institucion.nombre == "Tecnológico de Monterrey"
            )
            .first()
        )

        if institucion_tec:
            principal = (
                db.query(Beca)
                .filter(
                    Beca.nombre == TEC_NOMBRE_PRINCIPAL,
                    Beca.institucion_id == institucion_tec.id,
                )
                .first()
            )

            duplicados = (
                db.query(Beca)
                .filter(
                    Beca.nombre == TEC_NOMBRE_DUPLICADO,
                    Beca.institucion_id == institucion_tec.id,
                )
                .all()
            )

            for duplicado in duplicados:
                if principal:
                    db.delete(duplicado)
                    cambios += 1
                    print(
                        f"Duplicado Tec eliminado: {duplicado.nombre}"
                    )
                else:
                    duplicado.nombre = TEC_NOMBRE_PRINCIPAL
                    cambios += 1
                    principal = duplicado
                    print(
                        "Nombre Tec corregido: "
                        f"{TEC_NOMBRE_DUPLICADO} -> "
                        f"{TEC_NOMBRE_PRINCIPAL}"
                    )

        db.commit()

        print()
        print(
            f"Limpieza finalizada correctamente. "
            f"Cambios realizados: {cambios}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()