from fastapi import APIRouter, Depends, Request, Response, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from src import schemas, models, database, tasks
from src.utils import get_or_create_session

router = APIRouter()

@router.post("/packages", response_model=schemas.PackageResponse)
async def register_package(
    package: schemas.PackageCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(database.get_db)
):
    # Получаем или создаем сессию пользователя
    session_id = get_or_create_session(request, response)

    # Валидация: проверка, существует ли тип посылки
    result = await db.execute(select(models.PackageType).where(models.PackageType.id == package.type_id))
    package_type = result.scalars().first()
    if not package_type:
        raise HTTPException(status_code=400, detail="Неверный тип посылки")

    new_package = models.Package(
        session_id=session_id,
        name=package.name,
        weight=package.weight,
        type_id=package.type_id,
        content_value=package.content_value,
        shipping_cost=None
    )
    db.add(new_package)
    await db.commit()
    await db.refresh(new_package)

    return schemas.PackageResponse(
        id=new_package.id,
        name=new_package.name,
        weight=new_package.weight,
        type_name=package_type.name,
        content_value=new_package.content_value,
        shipping_cost="Не рассчитано"
    )

@router.get("/packages", response_model=List[schemas.PackageResponse])
async def get_packages(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    type_id: Optional[int] = Query(None),
    has_shipping_cost: Optional[bool] = Query(None),
    db: AsyncSession = Depends(database.get_db)
):
    session_id = request.cookies.get("session_id")
    if not session_id:
        return []
    query = (
        select(models.Package)
        .options(selectinload(models.Package.package_type))
        .where(models.Package.session_id == session_id)
    )
    if type_id:
        query = query.where(models.Package.type_id == type_id)
    if has_shipping_cost is not None:
        if has_shipping_cost:
            query = query.where(models.Package.shipping_cost.isnot(None))
        else:
            query = query.where(models.Package.shipping_cost.is_(None))
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    packages = result.scalars().all()
    response_list = []
    for pkg in packages:
        type_name = pkg.package_type.name if pkg.package_type else "Неизвестно"
        shipping_cost = (
            f"{pkg.shipping_cost:.2f}" if pkg.shipping_cost is not None else "Не рассчитано"
        )
        response_list.append(schemas.PackageResponse(
            id=pkg.id,
            name=pkg.name,
            weight=pkg.weight,
            type_name=type_name,
            content_value=pkg.content_value,
            shipping_cost=shipping_cost
        ))
    return response_list

@router.get("/packages/{package_id}", response_model=schemas.PackageResponse)
async def get_package(package_id: int, request: Request, db: AsyncSession = Depends(database.get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=404, detail="Посылка не найдена")
    query = (
        select(models.Package)
        .options(selectinload(models.Package.package_type))
        .where(models.Package.id == package_id, models.Package.session_id == session_id)
    )
    result = await db.execute(query)
    pkg = result.scalars().first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Посылка не найдена")
    type_name = pkg.package_type.name if pkg.package_type else "Неизвестно"
    shipping_cost = f"{pkg.shipping_cost:.2f}" if pkg.shipping_cost is not None else "Не рассчитано"
    return schemas.PackageResponse(
        id=pkg.id,
        name=pkg.name,
        weight=pkg.weight,
        type_name=type_name,
        content_value=pkg.content_value,
        shipping_cost=shipping_cost
    )

# Эндпоинт для ручного запуска задачи (отладка)
@router.post("/run_task")
async def manual_run_task():
    await tasks.run_shipping_cost_task()
    return {"message": "Задача запущена"}
