.PHONY: init scan scan-demo scan-loop latest smoke package clean

init:
	python -m pip install -r backend/requirements.txt

scan:
	python -m backend.main scan

scan-demo:
	python -m backend.main scan --demo

scan-demo-ai-off:
	python -m backend.main scan --demo --no-deepseek

scan-loop:
	python -m backend.main scan --loop --interval 3600

latest:
	python -m backend.main latest

smoke:
	bash scripts/local-smoke.sh

package:
	bash scripts/package.sh

clean:
	rm -rf data/*.sqlite3 __pycache__ .pytest_cache
	find backend -type d -name __pycache__ -prune -exec rm -rf {} +
