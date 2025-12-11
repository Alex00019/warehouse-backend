# app/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# ===================== SPRAVOCHNIKI =====================

class Unit(Base):
    __tablename__ = "units"

    unit_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    symbol = Column(String, nullable=True)

    # 1 : M -> materials
    materials = relationship("Material", back_populates="unit")


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)

    # self-referencing hierarchy
    parent = relationship(
        "Category",
        remote_side=[category_id],
        back_populates="children",
    )
    children = relationship("Category", back_populates="parent")

    materials = relationship("Material", back_populates="category")


class Material(Base):
    __tablename__ = "materials"

    material_id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)

    unit_id = Column(Integer, ForeignKey("units.unit_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)

    unit = relationship("Unit", back_populates="materials")
    category = relationship("Category", back_populates="materials")

    supplier_links = relationship("SupplierMaterial", back_populates="material")
    price_history = relationship("SupplierMaterialPrice", back_populates="material")
    warehouse_policies = relationship(
        "WarehouseMaterialPolicy",
        back_populates="material",
    )
    po_items = relationship("POItem", back_populates="material")
    stock_movements = relationship("StockMovement", back_populates="material")


# ===================== SUPPLIERS & PRICES =====================

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    bin_iin = Column(String, nullable=True)  # можно сделать unique при необходимости

    supplier_materials = relationship(
        "SupplierMaterial",
        back_populates="supplier",
        cascade="all, delete-orphan",
    )
    prices = relationship("SupplierMaterialPrice", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    stock_movements = relationship("StockMovement", back_populates="supplier")


class SupplierMaterial(Base):
    """
    Ассортимент поставщика: какие материалы он поставляет
    + бизнес-параметры (минимальная партия, срок поставки).
    """
    __tablename__ = "supplier_materials"
    __table_args__ = (
        UniqueConstraint("supplier_id", "material_id", name="uq_supplier_material"),
    )

    sup_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.material_id"), nullable=False)

    lead_time_days = Column(Integer, nullable=True)
    min_order_qty = Column(Numeric, nullable=True)
    currency = Column(String, nullable=True)

    supplier = relationship("Supplier", back_populates="supplier_materials")
    material = relationship("Material", back_populates="supplier_links")


class SupplierMaterialPrice(Base):
    """
    История цен поставщика по материалам.
    """
    __tablename__ = "supplier_material_prices"
    __table_args__ = (
        UniqueConstraint(
            "supplier_id",
            "material_id",
            "price_date",
            name="uq_supplier_price_date",
        ),
    )

    price_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.material_id"), nullable=False)

    price = Column(Numeric, nullable=False)
    currency = Column(String, nullable=True)
    price_date = Column(Date, nullable=False)

    supplier = relationship("Supplier", back_populates="prices")
    material = relationship("Material", back_populates="price_history")


# ===================== PROJECTS & WAREHOUSES =====================

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=True)
    customer = Column(String, nullable=True)
    address = Column(String, nullable=True)

    warehouses = relationship("Warehouse", back_populates="project")


class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    address = Column(String, nullable=True)

    project = relationship("Project", back_populates="warehouses")
    policies = relationship(
        "WarehouseMaterialPolicy",
        back_populates="warehouse",
        cascade="all, delete-orphan",
    )
    purchase_orders = relationship("PurchaseOrder", back_populates="warehouse")

    outgoing_movements = relationship(
        "StockMovement",
        back_populates="from_warehouse",
        foreign_keys="StockMovement.from_warehouse_id",
    )
    incoming_movements = relationship(
        "StockMovement",
        back_populates="to_warehouse",
        foreign_keys="StockMovement.to_warehouse_id",
    )


class WarehouseMaterialPolicy(Base):
    """
    Минимальные остатки на складе по каждому материалу.
    """
    __tablename__ = "warehouse_material_policy"
    __table_args__ = (
        UniqueConstraint(
            "warehouse_id",
            "material_id",
            name="pk_warehouse_material_policy",
        ),
    )

    warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"), primary_key=True)
    material_id = Column(Integer, ForeignKey("materials.material_id"), primary_key=True)

    min_stock = Column(Numeric, nullable=True)

    warehouse = relationship("Warehouse", back_populates="policies")
    material = relationship("Material", back_populates="warehouse_policies")


# ===================== PURCHASE ORDERS & ITEMS =====================

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    po_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"), nullable=False)

    order_date = Column(Date, nullable=False)
    expected_date = Column(Date, nullable=True)
    status = Column(String, nullable=True)

    supplier = relationship("Supplier", back_populates="purchase_orders")
    warehouse = relationship("Warehouse", back_populates="purchase_orders")
    items = relationship(
        "POItem",
        back_populates="purchase_order",
        cascade="all, delete-orphan",
    )
    stock_movements = relationship("StockMovement", back_populates="purchase_order")


class POItem(Base):
    __tablename__ = "po_items"
    __table_args__ = (
        UniqueConstraint("po_id", "material_id", name="uq_po_material"),
    )

    po_item_id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.po_id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.material_id"), nullable=False)

    qty_ordered = Column(Numeric, nullable=False)
    unit_price = Column(Numeric, nullable=True)
    currency = Column(String, nullable=True)

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    material = relationship("Material", back_populates="po_items")


# ===================== STOCK MOVEMENTS =====================

class StockMovement(Base):
    __tablename__ = "stock_movements"

    move_id = Column(Integer, primary_key=True, index=True)
    move_type = Column(String, nullable=False)  # приход / выдача / перемещение / корректировка
    move_date = Column(Date, nullable=False)
    status = Column(String, nullable=True)

    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=True)
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"), nullable=True)
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"), nullable=True)

    related_po_id = Column(Integer, ForeignKey("purchase_orders.po_id"), nullable=True)
    material_id = Column(Integer, ForeignKey("materials.material_id"), nullable=False)

    qty = Column(Numeric, nullable=False)
    unit_price = Column(Numeric, nullable=True)

    ext_doc_no = Column(String, nullable=True)
    ext_doc_date = Column(Date, nullable=True)
    vehicle_number = Column(String, nullable=True)
    shipped_by_name = Column(String, nullable=True)
    accepted_by_name = Column(String, nullable=True)
    ship_date = Column(Date, nullable=True)
    load_date = Column(Date, nullable=True)
    file_url = Column(String, nullable=True)

    supplier = relationship("Supplier", back_populates="stock_movements")
    from_warehouse = relationship(
        "Warehouse",
        back_populates="outgoing_movements",
        foreign_keys=[from_warehouse_id],
    )
    to_warehouse = relationship(
        "Warehouse",
        back_populates="incoming_movements",
        foreign_keys=[to_warehouse_id],
    )
    purchase_order = relationship("PurchaseOrder", back_populates="stock_movements")
    material = relationship("Material", back_populates="stock_movements")
