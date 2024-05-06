run:
	@uvicorn workoutapi.main:app --reload

create-migrations:
	@PYTHONPATH=$PYTHONPATH:$(pwd) alembic revision --autogenerate -m $(d)

run-migrations:
	@PYTHONPATH=$PYTHONPATH:$(pwd) alembic upgrade head