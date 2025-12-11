# app/seed_big.py

import random
from datetime import date, timedelta

from sqlalchemy import text

from .db import SessionLocal
from . import models


def seed_big():
    db = SessionLocal()
    try:
        print("Truncating tables...")
        # Чистим основные таблицы + сбрасываем ID
        db.execute(
            text(
                """
                TRUNCATE TABLE
                    supplier_material_prices,
                    supplier_materials,
                    materials,
                    suppliers,
                    categories,
                    units
                RESTART IDENTITY CASCADE;
                """
            )
        )
        db.commit()

        # ===== UNITS =====
        print("Inserting units...")
        units_data = [
            ("Штука", "шт"),
            ("Метры", "м"),
            ("Килограммы", "кг"),
            ("Квадратные метры", "м2"),
            ("Кубические метры", "м3"),
            ("Комплект", "компл"),
        ]
        units = []
        for name, symbol in units_data:
            u = models.Unit(name=name, symbol=symbol)
            db.add(u)
            units.append(u)
        db.flush()  # чтобы появились unit_id

        # ===== CATEGORIES =====
        print("Inserting categories...")
        root_categories = [
            "Кабельная продукция",
            "Трубопровод",
            "Арматура и металлопрокат",
            "Сухие смеси",
            "Крепёж",
        ]
        categories = []
        for rc in root_categories:
            c = models.Category(name=rc, parent_id=None)
            db.add(c)
            categories.append(c)
        db.flush()

        # ===== SUPPLIERS =====
        print("Inserting suppliers...")
        supplier_names = [
            "ТОО СтройПоставка",
            "ТОО ЭлектроСнаб",
            "ТОО ТрубИнвест",
            "ТОО КабельПроф",
            "ТОО МеталлСнаб",
            "ТОО СухСмесь KZ",
            "ТОО КрепёжМаркет",
            "ТОО БилдПоставка",
            "ТОО ЭнергоГрупп",
            "ТОО МагистральСнаб",
        ]
        suppliers = []
        for i, name in enumerate(supplier_names, start=1):
            s = models.Supplier(
                name=name,
                phone=f"+7 700 {100 + i:03d} {10 + i:02d} {20 + i:02d}",
                email=f"info{i}@example.kz",
                bin_iin=f"{100000000000 + i}",
            )
            db.add(s)
            suppliers.append(s)
        db.flush()

        # ===== MATERIALS =====
        print("Inserting materials...")
        materials = []
        material_count = 60  # сколько материалов создаём
        for i in range(1, material_count + 1):
            cat = random.choice(categories)
            unit = random.choice(units)
            sku = f"M-{i:03d}"
            name = f"{cat.name} #{i}"
            m = models.Material(
                sku=sku,
                name=name,
                unit_id=unit.unit_id,
                category_id=cat.category_id,
            )
            db.add(m)
            materials.append(m)
        db.flush()

        # ===== SUPPLIER_MATERIALS =====
        print("Inserting supplier_materials...")
        supplier_materials = []
        for supplier in suppliers:
            # каждый поставщик поставляет от 8 до 20 случайных материалов
            offered_materials = random.sample(
                materials, k=random.randint(8, min(20, len(materials)))
            )
            for mat in offered_materials:
                sm = models.SupplierMaterial(
                    supplier_id=supplier.supplier_id,
                    material_id=mat.material_id,
                    lead_time_days=random.choice([3, 5, 7, 10, 14]),
                    min_order_qty=random.choice([10, 20, 50, 100, 200]),
                    currency="KZT",
                )
                db.add(sm)
                supplier_materials.append(sm)
        db.flush()

        # ===== SUPPLIER_MATERIAL_PRICES =====
        print("Inserting supplier_material_prices...")
        today = date.today()
        for sm in supplier_materials:
            # 3 записи цен по датам: -60, -30, 0 дней
            base_price = random.randint(500, 20000)
            for delta in [60, 30, 0]:
                p = models.SupplierMaterialPrice(
                    supplier_id=sm.supplier_id,
                    material_id=sm.material_id,
                    price=round(base_price * random.uniform(0.9, 1.1), 2),
                    currency="KZT",
                    price_date=today - timedelta(days=delta),
                )
                db.add(p)

        db.commit()

        print("Big seed completed.")
        print(f"Units: {len(units)}")
        print(f"Categories: {len(categories)}")
        print(f"Suppliers: {len(suppliers)}")
        print(f"Materials: {len(materials)}")
        print(f"SupplierMaterials: {len(supplier_materials)}")
        print(f"SupplierMaterialPrices: {len(supplier_materials) * 3}")

    except Exception as e:
        db.rollback()
        print("Error during big seed:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_big()
