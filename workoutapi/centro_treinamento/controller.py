from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from sqlalchemy.future import select
from fastapi_pagination import LimitOffsetPage, paginate

from workoutapi.centro_treinamento.models import CentroTreinamentoModel
from workoutapi.centro_treinamento.schemas import (
    CentroTreinamentoIn,
    CentroTreinamentoOut,
)
from workoutapi.configs.dependencies import DatabaseDependency

router = APIRouter()


@router.post(
    "/",
    summary="Criar um novo centro de treinamento",
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
)
async def post(
    db_session: DatabaseDependency,
    centro_treinamento_in: CentroTreinamentoIn = Body(...),
) -> CentroTreinamentoOut:
    centro_treinamento_out = CentroTreinamentoOut(
        id=uuid4(), **centro_treinamento_in.model_dump()
    )
    categoria_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())

    db_session.add(categoria_model)
    await db_session.commit()

    return centro_treinamento_out


@router.get(
    "/",
    summary="Consultar todas os centro de treinamento",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[list],
)
async def query(db_session: DatabaseDependency) -> LimitOffsetPage[list]:
    centros_treinamentos: list[CentroTreinamentoOut] = (
        (await db_session.execute(select(CentroTreinamentoModel))).scalars().all()
    )

    lista = [
        CentroTreinamentoOut.model_validate(centros_treinamento)
        for centros_treinamento in centros_treinamentos
    ]
    return paginate(lista)


@router.get(
    "/{id}",
    summary="Consultar centro de treinamento pelo id",
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    categoria: CentroTreinamentoOut = (
        (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Centro treinamento não encontrada com id: {id}",
        )

    return categoria
