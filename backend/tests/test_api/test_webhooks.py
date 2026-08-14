from app.db.models.usuario_bot import UsuarioBot

API_HEADERS = {
    "X-API-Key": "test-secret-api-key",
}

BAD_API_HEADERS = {
    "X-API-Key": "clave-incorrecta",
}


def test_scraper_completado_sin_api_key_devuelve_422(client):
    response = client.post(
        "/api/v1/webhooks/scraper-completado",
        json={
            "fuente": "unam",
            "becas_nuevas": 2,
        },
    )

    assert response.status_code == 401


def test_scraper_completado_con_api_key_incorrecta_devuelve_401(client):
    response = client.post(
        "/api/v1/webhooks/scraper-completado",
        headers=BAD_API_HEADERS,
        json={
            "fuente": "unam",
            "becas_nuevas": 2,
        },
    )

    assert response.status_code == 401


def test_scraper_completado_acepta_api_key(client):
    response = client.post(
        "/api/v1/webhooks/scraper-completado",
        headers=API_HEADERS,
        json={
            "fuente": "unam",
            "becas_nuevas": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["detail"] == "Evento registrado"
    assert data["alertas_pendientes"] is True


def test_crear_usuario_sin_api_key_devuelve_422(client):
    response = client.post(
        "/api/v1/webhooks/usuario",
        json={
            "telegram_user_id": 123456789,
            "username": "usuario_test",
            "first_name": "Usuario",
        },
    )

    assert response.status_code == 401


def test_crear_usuario_con_api_key_incorrecta_devuelve_401(client):
    response = client.post(
        "/api/v1/webhooks/usuario",
        headers=BAD_API_HEADERS,
        json={
            "telegram_user_id": 123456789,
            "username": "usuario_test",
            "first_name": "Usuario",
        },
    )

    assert response.status_code == 401


def test_crear_usuario(client, db_session):
    response = client.post(
        "/api/v1/webhooks/usuario",
        headers=API_HEADERS,
        json={
            "telegram_user_id": 123456789,
            "username": "usuario_test",
            "first_name": "Usuario",
            "alertas_activas": False,
            "filtros_guardados": None,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["detail"] == "Usuario guardado exitosamente"

    usuario = db_session.get(
        UsuarioBot,
        123456789,
    )

    assert usuario is not None
    assert usuario.telegram_user_id == 123456789
    assert usuario.username == "usuario_test"
    assert usuario.first_name == "Usuario"
    assert usuario.alertas_activas is False


def test_obtener_usuario_sin_api_key_devuelve_401(client):
    response = client.get(
        "/api/v1/webhooks/usuario/123456789",
    )

    assert response.status_code == 401


def test_obtener_usuario_con_api_key_incorrecta_devuelve_401(client):
    response = client.get(
        "/api/v1/webhooks/usuario/123456789",
        headers=BAD_API_HEADERS,
    )

    assert response.status_code == 401


def test_obtener_usuario_inexistente_devuelve_404(client):
    response = client.get(
        "/api/v1/webhooks/usuario/999999999",
        headers=API_HEADERS,
    )

    assert response.status_code == 404


def test_obtener_usuario_existente(client, db_session):
    usuario = UsuarioBot(
        telegram_user_id=555555555,
        username="usuario_existente",
        first_name="Existente",
        alertas_activas=False,
        filtros_guardados=None,
    )

    db_session.add(usuario)
    db_session.commit()

    response = client.get(
        "/api/v1/webhooks/usuario/555555555",
        headers=API_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["telegram_user_id"] == 555555555
    assert data["username"] == "usuario_existente"
    assert data["first_name"] == "Existente"
    assert data["alertas_activas"] is False


def test_usuario_hace_upsert(client, db_session):
    response1 = client.post(
        "/api/v1/webhooks/usuario",
        headers=API_HEADERS,
        json={
            "telegram_user_id": 777777777,
            "username": "primero",
            "first_name": "Primero",
            "alertas_activas": False,
            "filtros_guardados": None,
        },
    )

    assert response1.status_code == 200

    response2 = client.post(
        "/api/v1/webhooks/usuario",
        headers=API_HEADERS,
        json={
            "telegram_user_id": 777777777,
            "username": "segundo",
            "first_name": "Segundo",
            "alertas_activas": True,
            "filtros_guardados": '{"nivel_educativo":"universidad"}',
        },
    )

    assert response2.status_code == 200

    usuario = db_session.get(
        UsuarioBot,
        777777777,
    )

    assert usuario is not None
    assert usuario.username == "segundo"
    assert usuario.first_name == "Segundo"
    assert usuario.alertas_activas is True
    assert (
        usuario.filtros_guardados
        == '{"nivel_educativo":"universidad"}'
    )


def test_usuario_actualiza_solo_campos_enviados(
    client,
    db_session,
):
    usuario = UsuarioBot(
        telegram_user_id=888888888,
        username="original",
        first_name="Original",
        alertas_activas=False,
        filtros_guardados="filtro_original",
    )

    db_session.add(usuario)
    db_session.commit()

    response = client.post(
        "/api/v1/webhooks/usuario",
        headers=API_HEADERS,
        json={
            "telegram_user_id": 888888888,
            "alertas_activas": True,
        },
    )

    assert response.status_code == 200

    usuario = db_session.get(
        UsuarioBot,
        888888888,
    )

    assert usuario is not None
    assert usuario.alertas_activas is True
    assert usuario.username == "original"
    assert usuario.first_name == "Original"
    assert usuario.filtros_guardados == "filtro_original"


def test_scraper_completado_con_cero_nuevas(client):
    response = client.post(
        "/api/v1/webhooks/scraper-completado",
        headers=API_HEADERS,
        json={
            "fuente": "ipn",
            "becas_nuevas": 0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["detail"] == "Evento registrado"
    assert data["alertas_pendientes"] is False


def test_scraper_completado_con_nuevas(client):
    response = client.post(
        "/api/v1/webhooks/scraper-completado",
        headers=API_HEADERS,
        json={
            "fuente": "tec",
            "becas_nuevas": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["detail"] == "Evento registrado"
    assert data["alertas_pendientes"] is True
