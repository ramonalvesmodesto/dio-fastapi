from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi_pagination import LimitOffsetPage, paginate

from workoutapi.atleta.models import AtletaModel
from workoutapi.atleta.schemas import AtletaCustom, AtletaIn, AtletaOut, AtletaUpdate
from workoutapi.categorias.models import CategoriaModel
from workoutapi.centro_treinamento.models import CentroTreinamentoModel
from workoutapi.configs.dependencies import DatabaseDependency

router = APIRouter()


@router.post("/", summary="Criar novo atleta", status_code=status.HTTP_201_CREATED)
async def post(db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...)):
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centros_treinamentos.nome

    categoria = (
        (
            await db_session.execute(
                select(CategoriaModel).filter_by(nome=categoria_nome)
            )
        )
        .scalars()
        .first()
    )

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categoria {categoria_nome} não encontrada",
        )

    centro_treinamento = (
        (
            await db_session.execute(
                select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome)
            )
        )
        .scalars()
        .first()
    )

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Centro de treinamento {centro_treinamento_nome} não encontrada",
        )

    #
    try:
        atleta_out = AtletaOut(
            id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump()
        )
        atleta_model = AtletaModel(
            **atleta_out.model_dump(exclude={"categoria", "centros_treinamentos"})
        )
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centros_treinamentos_id = centro_treinamento.pk_id

        db_session.add(atleta_model)
        await db_session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um atleta cadastrado com o cpf: {atleta_out.cpf}",
        )

    return atleta_out


@router.get(
    "/",
    summary="Consultar todos os atletas",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[list],
)
async def query(
    db_session: DatabaseDependency, nome: str = None, cpf: str = None
) -> LimitOffsetPage[list]:
    if nome is not None:
        atletas: list[AtletaOut] = (
            (await db_session.execute(select(AtletaModel).filter_by(nome=nome)))
            .scalars()
            .all()
        )

        if atletas[0].cpf != cpf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não possui nenhum usuário {nome } com o cpf {cpf}",
            )

    elif cpf is not None:
        atletas: list[AtletaOut] = (
            (await db_session.execute(select(AtletaModel).filter_by(cpf=cpf)))
            .scalars()
            .all()
        )
    else:
        atletas: list[AtletaOut] = (
            (await db_session.execute(select(AtletaModel))).scalars().all()
        )

        lista = [AtletaCustom.model_validate(atleta) for atleta in atletas]

    return paginate(lista)


@router.get(
    "/{id}",
    summary="Consultar atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrada com id: {id}",
        )

    return atleta


@router.patch(
    "/{id}",
    summary="Editar atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(
    id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrada com id: {id}",
        )

    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.delete(
    "/{id}", summary="Deletar atleta pelo id", status_code=status.HTTP_204_NO_CONTENT
)
async def get(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrada com id: {id}",
        )

    await db_session.delete(atleta)
    await db_session.commit()
