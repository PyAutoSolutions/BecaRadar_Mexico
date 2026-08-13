.PHONY: dev scrape migrate test seed metrics logs

dev:
	docker-compose up backend bot

scrape:
	docker-compose run --rm scraper

migrate:
	cd backend && alembic upgrade head

test:
	cd backend && pytest

seed:
	python scripts/seed_data.py

metrics:
	python scripts/export_metrics.py

logs:
	docker-compose logs -f