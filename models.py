from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"))

    role = relationship("Role", back_populates="employees")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    salary = Column(Float)

    employees = relationship("Employee", back_populates="role")
