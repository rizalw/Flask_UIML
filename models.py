from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import MetaData, String, ForeignKey
from sqlalchemy.sql import expression
from datetime import datetime, timezone


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

db = SQLAlchemy(model_class=Base)

class User(db.Model, UserMixin):
    __name__ = "user_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(20), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    date_created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc), nullable=False)
    model: Mapped[List["Model"]] = relationship(back_populates="user")

class Dataset(db.Model):
    __name__ = "dataset_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    type : Mapped[str] = mapped_column(String(20), nullable=False)
    label_name : Mapped[str] = mapped_column(String(20), nullable=False)
    filepath: Mapped[str] = mapped_column(nullable=False)
    date_created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc), nullable=False)
    model: Mapped[List["Model"]] = relationship(back_populates="dataset")
    
class Model(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)    
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    user : Mapped["User"] = relationship(back_populates="model")
    dataset_id: Mapped[int] = mapped_column(ForeignKey(Dataset.id))
    dataset : Mapped["Dataset"] = relationship(back_populates="model")
    algorithm_id = db.Column(db.Integer, nullable=False)    #Bentuk aslinya dictionary, jadi gak ada tabel sendiri
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[bool] = mapped_column(default=expression.false(), nullable=False)
    accuracy: Mapped[float] = mapped_column(nullable=True)
    parameter: Mapped[bytes] = mapped_column(nullable=True)
    filepath: Mapped[str] = mapped_column(nullable=True)
    date_created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc), nullable=False)