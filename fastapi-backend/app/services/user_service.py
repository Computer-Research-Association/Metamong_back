from sqlalchemy.orm import Session


class UserService:
    def __init__(self, db: Session):
        self.db = db
