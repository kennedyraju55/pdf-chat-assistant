.PHONY: install test run run-web lint clean

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

run:
	python -m pdf_chat.cli --pdf example.pdf

run-web:
	streamlit run src/pdf_chat/web_ui.py

lint:
	python -m py_compile src/pdf_chat/core.py
	python -m py_compile src/pdf_chat/cli.py
	python -m py_compile src/pdf_chat/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf *.egg-info build dist
