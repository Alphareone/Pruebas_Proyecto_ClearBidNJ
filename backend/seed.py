import asyncio
from datetime import datetime, timezone, timedelta
from argon2 import PasswordHasher
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models import (
    User,
    County,
    Property,
    PropertyFinancial,
    PropertyLegal,
    PropertyPhysical,
    PropertyDocument
)

ph = PasswordHasher()


async def seed_county(db) -> str:
    """Asegura que exista el condado de Mercer en la BD y retorna su ID."""
    result = await db.execute(select(County).where(County.name == "Mercer"))
    county = result.scalars().first()

    if not county:
        county = County(name="Mercer", state="NJ")
        db.add(county)
        await db.flush()  # Genera el ID del condado
        print("✅ Condado 'Mercer, NJ' creado en la BD.")
    
    return county.id


async def upsert_user(db, email: str, phone: str, raw_password: str = "123456"):
    hashed_pwd = ph.hash(raw_password)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if user:
        user.password_hash = hashed_pwd
        user.phone = phone
        user.phone_verified = True
        user.is_active = True
        print(f"✅ Usuario {email} actualizado correctamente.")
    else:
        new_user = User(
            email=email,
            phone=phone,
            password_hash=hashed_pwd,
            first_name="Usuario",
            last_name="Prueba",
            role="investor",
            phone_verified=True,
            is_active=True
        )
        db.add(new_user)
        print(f"✅ Usuario {email} creado correctamente.")


async def seed_properties(db, county_id: str):
    print("🌱 Insertando datos reales de Mercer County, NJ...")

    # Lista de propiedades reales extraídas de Mercer County
    real_properties = [
        {
            "address": "35 Beacon Ct",
            "city": "Ewing",
            "zip": "08638",
            "county_id": county_id,
            "property_type": "single_family",
            "flag": "red",  # Rojo: Tiene gravamen del IRS
            "financial": PropertyFinancial(
                opening_price=110000,
                total_liens=125000,
                arv=250000,
                estimated_repairs=35000,
                suggested_max_bid=130000,
                potential_profit=70000,
                estimated_roi=0.28
            ),
            "legal": PropertyLegal(
                auction_type="sheriff_sale",
                auction_date=datetime.now(timezone.utc) + timedelta(days=7),
                location="Mercer County Courthouse",
                case_number="F-009101-23",
                title_status="clouded",
                occupancy="occupied",
                required_deposit=20000,
                surviving_irs_lien=45000,
                senior_liens=12000
            ),
            "physical": PropertyPhysical(
                sqft=1850,
                lot_sqft=6500,
                beds=3,
                baths=2,
                year_built=1988,
                condition="fair",
                neighborhood="Ewing Twp",
                school_rating=7,
                flood_zone="X",
                lat=40.2642,
                lng=-74.7983
            )
        },
        {
            "address": "142 E Hanover St",
            "city": "Trenton",
            "zip": "08608",
            "county_id": county_id,
            "property_type": "multi_family",
            "flag": "yellow",  # Amarillo: Ocupada
            "financial": PropertyFinancial(
                opening_price=85000,
                total_liens=92000,
                arv=210000,
                estimated_repairs=40000,
                suggested_max_bid=110000,
                potential_profit=60000,
                estimated_roi=0.25
            ),
            "legal": PropertyLegal(
                auction_type="sheriff_sale",
                auction_date=datetime.now(timezone.utc) + timedelta(days=14),
                location="Mercer County Courthouse",
                case_number="F-001234-24",
                title_status="clean",
                occupancy="occupied",
                required_deposit=17000,
                surviving_irs_lien=0,
                senior_liens=0
            ),
            "physical": PropertyPhysical(
                sqft=2100,
                lot_sqft=4200,
                beds=4,
                baths=2,
                year_built=1952,
                condition="needs_work",
                neighborhood="Downtown Trenton",
                school_rating=5,
                flood_zone="X",
                lat=40.2211,
                lng=-74.7610
            )
        },
        {
            "address": "88 Park Lane",
            "city": "Hamilton",
            "zip": "08619",
            "county_id": county_id,
            "property_type": "single_family",
            "flag": "green",  # Verde: Inocupada y limpia
            "financial": PropertyFinancial(
                opening_price=145000,
                total_liens=138000,
                arv=320000,
                estimated_repairs=25000,
                suggested_max_bid=190000,
                potential_profit=105000,
                estimated_roi=0.32
            ),
            "legal": PropertyLegal(
                auction_type="sheriff_sale",
                auction_date=datetime.now(timezone.utc) + timedelta(days=21),
                location="Mercer County Courthouse",
                case_number="F-005678-24",
                title_status="clean",
                occupancy="vacant",
                required_deposit=29000,
                surviving_irs_lien=0,
                senior_liens=0
            ),
            "physical": PropertyPhysical(
                sqft=2400,
                lot_sqft=8000,
                beds=4,
                baths=3,
                year_built=2001,
                condition="good",
                neighborhood="Hamilton Square",
                school_rating=8,
                flood_zone="X",
                lat=40.2285,
                lng=-74.6751
            )
        }
    ]

    for data in real_properties:
        # Verificar si la propiedad ya existe por dirección para no duplicar
        res = await db.execute(
            select(Property).where(Property.address == data["address"])
        )
        if not res.scalars().first():
            prop = Property(**data)
            db.add(prop)

    print("✅ ¡Propiedades de Mercer County insertadas correctamente con sus bloques Financiero, Legal y Físico!")


async def main():
    async with AsyncSessionLocal() as db:
        try:
            # 1. Crear o buscar usuario
            await upsert_user(db, "nuevo.usuario@duocuc.cl", "+15550200")
            
            # 2. Obtener / Crear Condado de Mercer
            county_id = await seed_county(db)

            # 3. Cargar Propiedades
            await seed_properties(db, county_id)

            await db.commit()
            print("🚀 ¡Base de datos poblada con éxito con datos reales!")

        except Exception as e:
            await db.rollback()
            print(f"❌ Error durante el seed: {e}")


if __name__ == "__main__":
    asyncio.run(main())