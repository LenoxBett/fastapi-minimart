from typing import List, Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship, Session
from datetime import datetime

from sqlalchemy import create_engine
DATABASE_URL='sqlite:///mysales.db'


engine = create_engine(
    DATABASE_URL
)

SessionLocal = Session(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ---------------- BASE ----------------
class Base(DeclarativeBase):
    pass


# ---------------- PRODUCT ----------------
class Product(Base):
    __tablename__ = "Products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    buying_price: Mapped[float] = mapped_column(nullable=False)
    selling_price: Mapped[float] = mapped_column(nullable=False)

    # Relationships
    sales: Mapped[List["Sale"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )

    purchases: Mapped[List["Purchase"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )

    # Serializer
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price
        }


# ---------------- SALE ----------------
class Sale(Base):
    __tablename__ = "Sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("Products.id"),
        nullable=False
    )
    quantity: Mapped[String] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationship
    product: Mapped["Product"] = relationship(back_populates="sales")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "quantity": self.quantity,
            # "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ---------------- PURCHASE ----------------
class Purchase(Base):
    __tablename__ = "Purchases"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("Products.id"),
        nullable=False
    )
    quantity: Mapped[String] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationship
    product: Mapped["Product"] = relationship(back_populates="purchases")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "quantity": self.quantity,
            # "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ---------------- USER ----------------
class User(Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }