from sqlalchemy.exc import IntegrityError
from ..models import Department

class DepartmentService:
    def __init__(self, session):
        self.session = session
    
    def add_department(self, data):
        dept = Department(**data)
        try:
            self.session.add(dept)
            self.session.commit()
            return dept
        except IntegrityError as e:
            self.session.rollback()
            if "name" in str(e):
                raise ValueError("Department name already exists")
            raise ValueError("Department code already exists")
    
    def list_departments(self):
        return self.session.query(Department).all()