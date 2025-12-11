# app/schemas.py

from datetime import date
from pydantic import BaseModel
from typing import Optional


# ===== UNITS =====

class UnitBase(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None


class UnitCreate(UnitBase):
    pass


class Unit(UnitBase):
    unit_id: int

    class Config:
        orm_mode = True


# ===== CATEGORIES =====

class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    category_id: int

    class Config:
        orm_mode = True


# ===== MATERIALS =====

class MaterialBase(BaseModel):
    sku: str
    name: str
    unit_id: int
    category_id: int


class MaterialCreate(MaterialBase):
    pass


class Material(MaterialBase):
    material_id: int

    class Config:
        orm_mode = True


# ===== SUPPLIERS =====

class SupplierBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    bin_iin: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class Supplier(SupplierBase):
    supplier_id: int

    class Config:
        orm_mode = True


# ===== SUPPLIER MATERIALS (номенклатура поставщика) =====

class SupplierMaterialBase(BaseModel):
    supplier_id: int
    material_id: int
    lead_time_days: Optional[int] = None
    min_order_qty: Optional[float] = None
    currency: Optional[str] = None


class SupplierMaterialCreate(SupplierMaterialBase):
    pass


class SupplierMaterial(SupplierMaterialBase):
    sup_id: int

    class Config:
        orm_mode = True


# ===== SUPPLIER MATERIAL PRICES (история цен) =====

class SupplierMaterialPriceBase(BaseModel):
    supplier_id: int
    material_id: int
    price: float
    currency: str
    price_date: date


class SupplierMaterialPriceCreate(SupplierMaterialPriceBase):
    pass


class SupplierMaterialPrice(SupplierMaterialPriceBase):
    price_id: int

    class Config:
        orm_mode = True


# ===== PROJECTS =====

class ProjectBase(BaseModel):
    code: str
    name: str
    city: Optional[str] = None
    customer: Optional[str] = None
    address: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    project_id: int

    class Config:
        orm_mode = True


# ===== WAREHOUSES =====

class WarehouseBase(BaseModel):
    project_id: int
    name: str
    address: Optional[str] = None
    type: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    pass


class Warehouse(WarehouseBase):
    warehouse_id: int

    class Config:
        orm_mode = True


# ===== WAREHOUSE MATERIAL POLICY (минимальные остатки) =====

class WarehouseMaterialPolicyBase(BaseModel):
    warehouse_id: int
    material_id: int
    min_stock: float


class WarehouseMaterialPolicyCreate(WarehouseMaterialPolicyBase):
    pass


class WarehouseMaterialPolicy(WarehouseMaterialPolicyBase):
    class Config:
        orm_mode = True



# ===== PURCHASE ORDERS =====

class PurchaseOrderBase(BaseModel):
    supplier_id: int
    warehouse_id: int
    order_date: date
    expected_date: Optional[date] = None
    status: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    pass


class PurchaseOrder(PurchaseOrderBase):
    po_id: int

    class Config:
        orm_mode = True


# ===== PO ITEMS =====

class POItemBase(BaseModel):
    po_id: int
    material_id: int
    qty_ordered: float
    unit_price: float
    currency: str


class POItemCreate(POItemBase):
    pass


class POItem(POItemBase):
    po_item_id: int

    class Config:
        orm_mode = True




# ===== STOCK MOVEMENTS =====

class StockMovementBase(BaseModel):
    move_type: str              # 'IN', 'OUT', 'TRANSFER', 'ADJUST'
    move_date: date
    status: Optional[str] = None

    supplier_id: Optional[int] = None
    from_warehouse_id: Optional[int] = None
    to_warehouse_id: Optional[int] = None
    project_id: Optional[int] = None
    related_po_id: Optional[int] = None

    material_id: int
    qty: float
    unit_price: Optional[float] = None

    ext_doc_no: Optional[str] = None
    ext_doc_date: Optional[date] = None

    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    shipped_by_name: Optional[str] = None
    accepted_by_name: Optional[str] = None

    ship_date: Optional[date] = None
    load_date: Optional[date] = None

    file_url: Optional[str] = None
    file_mime: Optional[str] = None
    file_hash: Optional[str] = None


class StockMovementCreate(StockMovementBase):
    pass


class StockMovement(StockMovementBase):
    move_id: int

    class Config:
        orm_mode = True
