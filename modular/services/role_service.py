from sqlalchemy.exc import IntegrityError
from ..models import Role

class RoleService:
    def __init__(self, session):
        self.session = session
    
    def add_role(self, data):
        role = Role(**data)
        try:
            self.session.add(role)
            self.session.commit()
            return role
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Role title already exists")
    
    def list_roles(self):
        return self.session.query(Role).all()