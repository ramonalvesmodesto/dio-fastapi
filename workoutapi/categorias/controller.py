from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from sqlalchemy.future import select
from fastapi_pagination import LimitOffsetPage, paginate

from workoutapi.categorias.models import CategoriaModel
from workoutapi.categorias.schemas import CategoriaIn, CategoriaOut
from workoutapi.configs.dependencies import DatabaseDependency

router = APIRouter()


@router.post(
    "/",
    summary="Criar nova categoria",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoriaOut,
)
async def post(
    db_session: DatabaseDependency, categorias_in: CategoriaIn = Body(...)
) -> CategoriaOut:
    categoria_out = CategoriaOut(id=uuid4(), **categorias_in.model_dump())
    categoria_model = CategoriaModel(**categoria_out.model_dump())

    db_session.add(categoria_model)
    await db_session.commit()

    return categoria_out


@router.get(
    "/",
    summary="Consultar todas as categoria",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[list],
)
async def query(db_session: DatabaseDependency) -> LimitOffsetPage[list]:
    categorias: list[CategoriaOut] = (
        (await db_session.execute(select(CategoriaModel))).scalars().all()
    )

    lista = [CategoriaOut.model_validate(categoria) for categoria in categorias]
    return paginate(lista)


@router.get(
    "/{id}",
    summary="Consultar categoria pelo id",
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> CategoriaOut:
    categoria: CategoriaOut = (
        (await db_session.execute(select(CategoriaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria não encontrada com id: {id}",
        )

    return categoria
