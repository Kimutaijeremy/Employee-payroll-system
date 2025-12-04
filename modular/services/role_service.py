from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Role, Employee
from typing import Optional, List, Dict

class RoleService:
    def __init__(self, session: Session):
        self.session = session
    
    def create_role(self, data: Dict) -> Role:
        """Create a new role"""
        try:
            role = Role(**data)
            self.session.add(role)
            self.session.commit()
            return role
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Role title already exists")
    
    def update_role(self, role_id: int, data: Dict) -> Optional[Role]:
        """Update role details"""
        role = self.session.query(Role).get(role_id)
        
        if not role:
            raise ValueError("Role not found")
        
        for key, value in data.items():
            if hasattr(role, key):
                setattr(role, key, value)
        
        self.session.commit()
        return role
    
    def delete_role(self, role_id: int) -> bool:
        """Delete a role (if no employees assigned)"""
        role = self.session.query(Role).get(role_id)
        
        if not role:
            raise ValueError("Role not found")
        
        # Check if any employees are assigned to this role
        employee_count = self.session.query(Employee).filter(
            Employee.role_id == role_id
        ).count()
        
        if employee_count > 0:
            raise ValueError(f"Cannot delete role. {employee_count} employees are assigned to it.")
        
        self.session.delete(role)
        self.session.commit()
        return True
    
    def get_role(self, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        return self.session.query(Role).get(role_id)
    
    def list_roles(self) -> List[Role]:
        """List all roles"""
        return self.session.query(Role).order_by(Role.title).all()
    
    def get_role_by_title(self, title: str) -> Optional[Role]:
        """Get role by title"""
        return self.session.query(Role).filter(
            Role.title.ilike(title)
        ).first()