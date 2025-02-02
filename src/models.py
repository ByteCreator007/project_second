from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PackageType(Base):
    __tablename__ = "package_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    packages = relationship("Package", back_populates="package_type")

class Package(Base):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    weight = Column(Float, nullable=False)
    type_id = Column(Integer, ForeignKey("package_types.id"), nullable=False)
    content_value = Column(Float, nullable=False)
    shipping_cost = Column(Float, nullable=True)

    package_type = relationship("PackageType", back_populates="packages")
