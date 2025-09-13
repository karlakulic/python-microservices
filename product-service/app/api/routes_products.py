from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel

from app.api.deps import db_session, get_user_id
from app import models
from app.schemas import ProductCreate, ProductRead, ProductUpdate, StockAdjust
from app.messaging.publisher import publish_product_created


router = APIRouter(prefix="/api/products", tags=["products"])

class ProductList(BaseModel):
    items: List[ProductRead]
    total: int

@router.get("/", response_model=ProductList)
def list_products(db: Session = Depends(db_session), user_id: str = Depends(get_user_id), limit: int = 50, offset: int = 0):
    q = (
        db.query(models.Product)
        .filter(
            and_(
                models.Product.user_id == user_id, 
                models.Product.is_active == True
            )
        )
        .order_by(models.Product.created_at.desc())
    )
    total = q.count()
    items = q.limit(limit).offset(offset).all()
    items_read: List[ProductRead] = [ProductRead.model_validate(i) for i in items]
    return ProductList(items = items_read, total = total)

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(db_session), user_id: str = Depends(get_user_id)):

    dup = (
        db.query(models.Product)
        .filter(
            and_(
                models.Product.user_id == user_id,
                or_(models.Product.name == payload.name, models.Product.sku == payload.sku)
            )
        )
        .first()
    )
    if dup:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with same name or SKU already exists.",
        )

    product = models.Product(
        user_id=user_id,
        name=payload.name,
        sku=payload.sku,
        description=payload.description,
        price=payload.price,
        currency=payload.currency,
        stock=payload.stock,
        is_active=payload.is_active,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    try:
        publish_product_created(product)
    except Exception as e:
        print(f"[events] WARN publish product.created failed: {e}")
    return ProductRead.model_validate(product) 

@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: str, db: Session = Depends(db_session), user_id: str = Depends(get_user_id)):
    product = (
        db.query(models.Product)
        .filter(and_(models.Product.id == product_id, models.Product.user_id == user_id))
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return ProductRead.model_validate(product) 

@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: str,
    payload: ProductUpdate,
    db: Session = Depends(db_session),
    user_id: str = Depends(get_user_id)
):
    product = (
        db.query(models.Product)
        .filter(and_(models.Product.id == product_id, models.Product.user_id == user_id))
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        exists = (
            db.query(models.Product)
            .filter(
                and_(
                    models.Product.user_id == user_id,
                    models.Product.id != product_id,
                    models.Product.name == data["name"],
                )
            )
            .first()
        )
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Name already in use.")
    if "sku" in data and data["sku"] is not None:
        exists = (
            db.query(models.Product)
            .filter(
                and_(
                    models.Product.user_id == user_id,
                    models.Product.id != product_id,
                    models.Product.sku == data["sku"],
                )
            )
            .first()
        )
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already in use.")


    for field, value in data.items():
        setattr(product, field, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductRead.model_validate(product) 

@router.delete("/{product_id}", response_model=ProductRead, status_code=status.HTTP_200_OK)
def delete_product(product_id: str, db: Session = Depends(db_session), user_id: str = Depends(get_user_id) ):
    product = (
        db.query(models.Product)
        .filter(and_(models.Product.id == product_id, models.Product.user_id == user_id))
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    if not product.is_active:
        return product 
    product.is_active = False
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductRead.model_validate(product) 

@router.post("/{product_id}/stock-adjust", response_model=ProductRead)
def adjust_stock(product_id: str, payload: StockAdjust, db: Session = Depends(db_session), user_id: str = Depends(get_user_id)):
    product = (
        db.query(models.Product)
        .filter(and_(models.Product.id == product_id, models.Product.user_id == user_id))
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    if not product.is_active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product is inactive.")
    new_stock = product.stock + payload.delta
    if new_stock < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock cannot go below 0.")
    product.stock = new_stock
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductRead.model_validate(product) 


