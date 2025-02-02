from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from src import models, schemas
from src.database import get_db

router = APIRouter()

@router.get("/package_types", response_model=List[schemas.PackageTypeResponse])
async def get_package_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.PackageType))
    types = result.scalars().all()
    return types
