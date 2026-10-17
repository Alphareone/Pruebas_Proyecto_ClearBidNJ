"""Pruebas de propiedades, semáforo, roles y guardadas."""
import pytest

from tests.conftest import TestSession, auth_header, make_user

pytestmark = pytest.mark.asyncio


async def _seed_county(db):
    from app.models.geography import County, ZipCode
    c = County(name="Essex", state="NJ", main_city="Newark")
    db.add(c)
    await db.flush()
    db.add(ZipCode(zip="07108", city="Newark", state="NJ", county_id=c.id))
    await db.commit()
    return c


async def test_admin_create_property_and_traffic_light(client):
    async with TestSession() as db:
        county = await _seed_county(db)
        analyst = await make_user(db, role="analyst", email="analyst@test.com")
        # Regla crítica: IRS lien sobreviviente -> red
        from app.models.rules import Rule
        db.add(Rule(
            code="surviving_irs_lien", severity="critical",
            title="Gravamen IRS", message="Lien federal sobrevive.",
            condition="legal.surviving_irs_lien and legal.surviving_irs_lien > 0",
            active=True,
        ))
        await db.commit()

    # Crea propiedad con IRS lien -> debe salir 'red'
    r = await client.post("/api/v1/admin/properties", headers=auth_header(analyst), json={
        "address": "212 Clinton Ave", "city": "Newark", "zip": "07108",
        "county_id": county.id, "property_type": "single_family",
        "financial": {"opening_price": 52000, "arv": 245000},
        "legal": {"auction_type": "sheriff_sale", "surviving_irs_lien": 61000},
        "physical": {"beds": 3, "baths": 2},
    })
    assert r.status_code == 201, r.text
    prop_id = r.json()["id"]
    assert r.json()["flag"] == "red"

    # Detalle incluye semáforo con la regla fallida
    investor = None
    async with TestSession() as db:
        investor = await make_user(db, role="investor", email="inv@test.com")
    r = await client.get(f"/api/v1/properties/{prop_id}", headers=auth_header(investor))
    assert r.status_code == 200
    tl = r.json()["traffic_light"]
    assert tl["flag"] == "red"
    assert any(rule["code"] == "surviving_irs_lien" and rule["status"] == "fail"
               for rule in tl["rules"])


async def test_investor_cannot_create_property(client):
    async with TestSession() as db:
        investor = await make_user(db, role="investor", email="inv2@test.com")
    r = await client.post("/api/v1/admin/properties", headers=auth_header(investor), json={
        "address": "x", "city": "y", "zip": "07108",
        "county_id": "cty_x", "property_type": "condo",
    })
    assert r.status_code == 403


async def test_list_and_filter_properties(client):
    async with TestSession() as db:
        county = await _seed_county(db)
        analyst = await make_user(db, role="analyst", email="a2@test.com")
    for price, ptype in [(30000, "condo"), (90000, "single_family")]:
        await client.post("/api/v1/admin/properties", headers=auth_header(analyst), json={
            "address": f"addr {price}", "city": "Newark", "zip": "07108",
            "county_id": county.id, "property_type": ptype,
            "financial": {"opening_price": price, "arv": 200000},
            "legal": {"auction_type": "sheriff_sale"}, "physical": {},
        })
    # Filtro por precio máximo
    r = await client.get("/api/v1/properties?max_opening=50000", headers=auth_header(analyst))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["opening_price"] == 30000

    # Facetas
    r = await client.get("/api/v1/properties/facets", headers=auth_header(analyst))
    assert r.status_code == 200
    assert r.json()["total"] == 2


async def test_save_and_list_favorites(client):
    async with TestSession() as db:
        county = await _seed_county(db)
        analyst = await make_user(db, role="analyst", email="a3@test.com")
        investor = await make_user(db, role="investor", email="i3@test.com")
    r = await client.post("/api/v1/admin/properties", headers=auth_header(analyst), json={
        "address": "fav", "city": "Newark", "zip": "07108",
        "county_id": county.id, "property_type": "condo",
        "financial": {"opening_price": 45000}, "legal": {}, "physical": {},
    })
    prop_id = r.json()["id"]

    assert (await client.post("/api/v1/saved", headers=auth_header(investor),
                              json={"property_id": prop_id})).status_code == 201
    # Duplicado -> 409
    assert (await client.post("/api/v1/saved", headers=auth_header(investor),
                              json={"property_id": prop_id})).status_code == 409
    r = await client.get("/api/v1/saved", headers=auth_header(investor))
    assert len(r.json()["items"]) == 1
    assert (await client.delete(f"/api/v1/saved/{prop_id}",
                                headers=auth_header(investor))).status_code == 204


async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
