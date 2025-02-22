from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.group import Group
from ..schemas.group import GroupCreate, GroupUpdate

class GroupService:
    @staticmethod
    async def get_groups(db: Session, skip: int = 0, limit: int = 100) -> List[Group]:
        return db.query(Group).offset(skip).limit(limit).all()

    @staticmethod
    async def get_group(db: Session, group_id: int) -> Optional[Group]:
        return db.query(Group).filter(Group.id == group_id).first()

    @staticmethod
    async def create_group(db: Session, group: GroupCreate) -> Group:
        db_group = Group(**group.dict())
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return db_group

    @staticmethod
    async def get_group_words(db: Session, group_id: int, skip: int = 0, limit: int = 100):
        group = await GroupService.get_group(db, group_id)
        if group:
            return group.words[skip:skip + limit]
        return [] 