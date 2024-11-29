from repository.analytics_repo import Analytics
from core.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session


def get_analytics(db: Session = Depends(get_db)) -> Analytics:
    return Analytics(db)