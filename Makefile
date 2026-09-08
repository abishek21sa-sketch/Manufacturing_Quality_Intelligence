install:
	pip install -e '.[dev]'
bootstrap:
	mqi bootstrap
validate:
	pytest && mqi validate
serve:
	uvicorn mqi.service.api:app --reload
