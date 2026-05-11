.PHONY: package smoke up down logs

package:
	bash scripts/package.sh

smoke:
	bash scripts/local-smoke.sh

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f backend frontend
