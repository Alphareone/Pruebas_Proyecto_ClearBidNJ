"""Fixtures de pruebas: app con BD SQLite en memoria y cliente async.

Se usa SQLite (aiosqlite) para no depender de un Postgres en CI. El esquema se
crea desde los modelos (Base.metadata) en cada sesión de test.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
import app.models  # noqa: F401
from app.main import app

# Engine en memoria con StaticPool: reutiliza una única conexión, de modo que la
# BD in-memory persiste durante toda la prueba.
test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)


async def _override_get_db():
    async with TestSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture(autouse=True)
async def _schema():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_session():
    async with TestSession() as session:
        yield session
        await session.commit()


@pytest.fixture
def captured_sms(monkeypatch):
    """Captura los SMS enviados (incluye el código OTP en el mensaje)."""
    import re

    store: list[dict] = []

    class _Capture:
        async def send(self, phone, message):
            m = re.search(r"(\d{6})", message)
            store.append({"phone": phone, "message": message, "code": m.group(1) if m else None})

    monkeypatch.setattr("app.services.auth_service.get_sms_provider", lambda: _Capture())
    return store


_phone_counter = [1000]


async def make_user(db, role="investor", email="user@test.com", active=True):
    """Crea un usuario activo directamente en BD (para probar rutas protegidas)."""
    from app.core.security import hash_password
    from app.models.user import AlertSetting, User, UserPreference

    _phone_counter[0] += 1
    phone = f"+1201555{_phone_counter[0]:04d}"
    user = User(
        first_name="Test", last_name="User", email=email, phone=phone,
        password_hash=hash_password("S3cret!pass"), role=role,
        is_active=active, phone_verified=True,
    )
    db.add(user)
    await db.flush()
    db.add(UserPreference(user_id=user.id))
    db.add(AlertSetting(user_id=user.id))
    await db.commit()
    return user


def auth_header(user):
    from app.core.security import create_access_token

    return {"Authorization": f"Bearer {create_access_token(user.id, user.role)}"}
