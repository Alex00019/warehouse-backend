# app/main.py

from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Пытаемся сначала импортировать как пакет (когда запускаем app.main),
# если не получится — как обычные модули (когда в Docker запускаем main.py)
try:
    from .db import SessionLocal
    from . import models, schemas
except ImportError:
    from db import SessionLocal
    import models, schemas


def get_db():
    """
    Зависимость FastAPI для работы с БД.
    На каждый запрос создаётся сессия и потом закрывается.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(
    title="Warehouse Backend",
    description="API для складского учета строительных материалов",
    version="1.0.0",
)


@app.get("/ping")
def ping():
    """
    Простой эндпоинт-проверка, что сервер жив.
    Не трогает базу данных.
    """
    return {"status": "ok"}


# ===== UNITS =====

@app.post("/units", response_model=schemas.Unit, status_code=status.HTTP_201_CREATED)
def create_unit(unit_in: schemas.UnitCreate, db: Session = Depends(get_db)):
    """
    Создание единицы измерения (шт, м, кг и т.п.).
    """
    unit = models.Unit(
        name=unit_in.name,
        symbol=unit_in.symbol,
    )
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


@app.get("/units", response_model=List[schemas.Unit])
def list_units(db: Session = Depends(get_db)):
    """
    Список всех единиц измерения.
    """
    units = db.query(models.Unit).order_by(models.Unit.unit_id).all()
    return units


# ===== CATEGORIES =====

@app.post("/categories", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(category_in: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """
    Создание категории материалов (кабель, труба, арматура и т.п.).
    parent_id можно оставить пустым для корневых категорий.
    """
    category = models.Category(
        name=category_in.name,
        parent_id=category_in.parent_id,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@app.get("/categories", response_model=List[schemas.Category])
def list_categories(db: Session = Depends(get_db)):
    """
    Список всех категорий.
    """
    categories = db.query(models.Category).order_by(models.Category.category_id).all()
    return categories


# ===== SUPPLIERS =====

@app.post("/suppliers", response_model=schemas.Supplier, status_code=status.HTTP_201_CREATED)
def create_supplier(supplier_in: schemas.SupplierCreate, db: Session = Depends(get_db)):
    """
    Создание поставщика.
    """
    supplier = models.Supplier(
        name=supplier_in.name,
        phone=supplier_in.phone,
        email=supplier_in.email,
        bin_iin=supplier_in.bin_iin,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@app.get("/suppliers", response_model=List[schemas.Supplier])
def list_suppliers(db: Session = Depends(get_db)):
    """
    Список всех поставщиков.
    """
    suppliers = db.query(models.Supplier).order_by(models.Supplier.supplier_id).all()
    return suppliers


# ===== SUPPLIER MATERIALS (номенклатура поставщика) =====

@app.get("/supplier-materials", response_model=List[schemas.SupplierMaterial])
def list_supplier_materials(db: Session = Depends(get_db)):
    """
    Номенклатура: какие материалы поставляют поставщики.
    """
    rows = (
        db.query(models.SupplierMaterial)
        .order_by(models.SupplierMaterial.sup_id)
        .all()
    )
    return rows


# ===== SUPPLIER MATERIAL PRICES (история цен) =====

@app.get("/supplier-material-prices", response_model=List[schemas.SupplierMaterialPrice])
def list_supplier_material_prices(db: Session = Depends(get_db)):
    """
    История цен поставщиков по материалам.
    """
    rows = (
        db.query(models.SupplierMaterialPrice)
        .order_by(models.SupplierMaterialPrice.price_id)
        .all()
    )
    return rows


# ===== PROJECTS =====

@app.post("/projects", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(project_in: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """
    Создание строительного проекта/объекта.
    """
    project = models.Project(
        code=project_in.code,
        name=project_in.name,
        city=project_in.city,
        customer=project_in.customer,
        address=project_in.address,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.get("/projects", response_model=List[schemas.Project])
def list_projects(db: Session = Depends(get_db)):
    """
    Список всех проектов/объектов.
    """
    projects = db.query(models.Project).order_by(models.Project.project_id).all()
    return projects


# ===== WAREHOUSES =====

@app.post("/warehouses", response_model=schemas.Warehouse, status_code=status.HTTP_201_CREATED)
def create_warehouse(warehouse_in: schemas.WarehouseCreate, db: Session = Depends(get_db)):
    """
    Создание склада, привязанного к проекту.
    """
    warehouse = models.Warehouse(
        project_id=warehouse_in.project_id,
        name=warehouse_in.name,
        address=warehouse_in.address,
        type=warehouse_in.type,
    )
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@app.get("/warehouses", response_model=List[schemas.Warehouse])
def list_warehouses(db: Session = Depends(get_db)):
    """
    Список всех складов.
    """
    warehouses = db.query(models.Warehouse).order_by(models.Warehouse.warehouse_id).all()
    return warehouses


# ===== WAREHOUSE MATERIAL POLICY (минимальные остатки) =====

@app.post(
    "/warehouse-policies",
    response_model=schemas.WarehouseMaterialPolicy,
    status_code=status.HTTP_201_CREATED,
)
def create_warehouse_policy(
    policy_in: schemas.WarehouseMaterialPolicyCreate,
    db: Session = Depends(get_db),
):
    """
    Создание политики минимальных остатков по складу и материалу.
    """
    policy = models.WarehouseMaterialPolicy(
        warehouse_id=policy_in.warehouse_id,
        material_id=policy_in.material_id,
        min_stock=policy_in.min_stock,
    )
    db.add(policy)
    db.commit()
    return policy


@app.get("/warehouse-policies", response_model=List[schemas.WarehouseMaterialPolicy])
def list_warehouse_policies(db: Session = Depends(get_db)):
    """
    Список всех политик минимальных остатков.
    """
    policies = db.query(models.WarehouseMaterialPolicy).all()
    return policies


# ===== PURCHASE ORDERS =====

@app.post(
    "/purchase-orders",
    response_model=schemas.PurchaseOrder,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase_order(
    po_in: schemas.PurchaseOrderCreate,
    db: Session = Depends(get_db),
):
    """
    Создание заявки на поставку (Purchase Order).
    """
    po = models.PurchaseOrder(
        supplier_id=po_in.supplier_id,
        warehouse_id=po_in.warehouse_id,
        order_date=po_in.order_date,
        expected_date=po_in.expected_date,
        status=po_in.status,
    )
    db.add(po)
    db.commit()
    db.refresh(po)
    return po


@app.get("/purchase-orders", response_model=List[schemas.PurchaseOrder])
def list_purchase_orders(db: Session = Depends(get_db)):
    """
    Список всех заявок на поставку.
    """
    orders = db.query(models.PurchaseOrder).order_by(models.PurchaseOrder.po_id).all()
    return orders


# ===== PO ITEMS =====

@app.post(
    "/po-items",
    response_model=schemas.POItem,
    status_code=status.HTTP_201_CREATED,
)
def create_po_item(
    item_in: schemas.POItemCreate,
    db: Session = Depends(get_db),
):
    """
    Создание позиции в заявке на поставку.
    """
    item = models.POItem(
        po_id=item_in.po_id,
        material_id=item_in.material_id,
        qty_ordered=item_in.qty_ordered,
        unit_price=item_in.unit_price,
        currency=item_in.currency,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/po-items", response_model=List[schemas.POItem])
def list_po_items(db: Session = Depends(get_db)):
    """
    Список всех позиций во всех заявках.
    """
    items = db.query(models.POItem).order_by(models.POItem.po_item_id).all()
    return items


# ===== STOCK MOVEMENTS =====

@app.post(
    "/stock-movements",
    response_model=schemas.StockMovement,
    status_code=status.HTTP_201_CREATED,
)
def create_stock_movement(
    mv_in: schemas.StockMovementCreate,
    db: Session = Depends(get_db),
):
    """
    Создание движения по складу:
    - move_type: 'IN', 'OUT', 'TRANSFER', 'ADJUST'
    """
    mv = models.StockMovement(
        move_type=mv_in.move_type,
        move_date=mv_in.move_date,
        status=mv_in.status,
        supplier_id=mv_in.supplier_id,
        from_warehouse_id=mv_in.from_warehouse_id,
        to_warehouse_id=mv_in.to_warehouse_id,
        project_id=mv_in.project_id,
        related_po_id=mv_in.related_po_id,
        material_id=mv_in.material_id,
        qty=mv_in.qty,
        unit_price=mv_in.unit_price,
        ext_doc_no=mv_in.ext_doc_no,
        ext_doc_date=mv_in.ext_doc_date,
        vehicle_number=mv_in.vehicle_number,
        driver_name=mv_in.driver_name,
        shipped_by_name=mv_in.shipped_by_name,
        accepted_by_name=mv_in.accepted_by_name,
        ship_date=mv_in.ship_date,
        load_date=mv_in.load_date,
        file_url=mv_in.file_url,
        file_mime=mv_in.file_mime,
        file_hash=mv_in.file_hash,
    )
    db.add(mv)
    db.commit()
    db.refresh(mv)
    return mv


@app.get("/stock-movements", response_model=List[schemas.StockMovement])
def list_stock_movements(db: Session = Depends(get_db)):
    """
    Список всех движений по складам.
    """
    moves = db.query(models.StockMovement).order_by(models.StockMovement.move_id).all()
    return moves


# ===== DEBUG (можно потом удалить) =====

@app.get("/debug/materials")
def debug_list_materials(db: Session = Depends(get_db)):
    """
    Временный эндпоинт для проверки связи с базой:
    пытается вытащить первые 10 материалов.
    Пока таблица пустая, вернёт пустой список.
    """
    materials = db.query(models.Material).limit(10).all()
    return [
        {
            "material_id": m.material_id,
            "sku": m.sku,
            "name": m.name,
        }
        for m in materials
    ]


# ===== MATERIALS =====

@app.post("/materials", response_model=schemas.Material, status_code=status.HTTP_201_CREATED)
def create_material(material_in: schemas.MaterialCreate, db: Session = Depends(get_db)):
    """
    Создание нового материала.
    Проверяем уникальность sku.
    """
    existing = db.query(models.Material).filter(models.Material.sku == material_in.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Material with this SKU already exists",
        )

    material = models.Material(
        sku=material_in.sku,
        name=material_in.name,
        unit_id=material_in.unit_id,
        category_id=material_in.category_id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@app.get("/materials", response_model=List[schemas.Material])
def list_materials(db: Session = Depends(get_db)):
    """
    Список всех материалов (пока без пагинации).
    """
    materials = db.query(models.Material).order_by(models.Material.material_id).all()
    return materials
