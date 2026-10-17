"""Pruebas del flujo de autenticación y 2FA."""
import pytest

pytestmark = pytest.mark.asyncio


async def test_register_login_2fa_flow(client, captured_sms):
    # Registro -> devuelve reto 2FA
    r = await client.post("/api/v1/auth/register", json={
        "first_name": "Max", "last_name": "Weller",
        "email": "max@wellq.co.uk", "phone": "+12015550199",
        "password": "S3cret!pass",
    })
    assert r.status_code == 201, r.text
    challenge_id = r.json()["challenge_id"]
    assert captured_sms, "debió enviarse un SMS"
    code = captured_sms[-1]["code"]

    # Verificación 2FA -> emite tokens
    r = await client.post("/api/v1/auth/2fa/verify", json={
        "challenge_id": challenge_id, "code": code,
    })
    assert r.status_code == 200, r.text
    tokens = r.json()
    assert tokens["access_token"] and tokens["refresh_token"]
    assert tokens["user"]["email"] == "max@wellq.co.uk"

    # /users/me con el access token
    r = await client.get("/api/v1/users/me", headers={
        "Authorization": f"Bearer {tokens['access_token']}"
    })
    assert r.status_code == 200
    assert r.json()["phone_verified"] is True

    # Refresh rota el token
    r = await client.post("/api/v1/auth/token/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert r.status_code == 200
    assert r.json()["access_token"]


async def test_register_duplicate_email(client, captured_sms):
    payload = {
        "first_name": "A", "last_name": "B", "email": "dup@test.com",
        "phone": "+12015550111", "password": "S3cret!pass",
    }
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    r = await client.post("/api/v1/auth/register", json={**payload, "phone": "+12015550112"})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "conflict"


async def test_login_bad_credentials(client):
    r = await client.post("/api/v1/auth/login", json={
        "email": "nope@test.com", "password": "whatever"
    })
    assert r.status_code == 401


async def test_2fa_wrong_code(client, captured_sms):
    r = await client.post("/api/v1/auth/register", json={
        "first_name": "C", "last_name": "D", "email": "c@test.com",
        "phone": "+12015550133", "password": "S3cret!pass",
    })
    challenge_id = r.json()["challenge_id"]
    r = await client.post("/api/v1/auth/2fa/verify", json={
        "challenge_id": challenge_id, "code": "000000"
    })
    assert r.status_code == 401


async def test_protected_requires_token(client):
    assert (await client.get("/api/v1/users/me")).status_code == 401
