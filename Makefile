pr-prep: format test

format:
	black *.py epaper/ tests/

test:
	python -m pytest tests/

typecheck:
	python -m mypy run.py

new-example:
	python run.py --debug generate --output-file examples/example.bmp

install-systemd:
	@echo "Installing systemd service..."
	@sudo ln -sf $(PWD)/epaper.service /etc/systemd/system/epaper.service
	@sudo systemctl daemon-reload
	@sudo systemctl enable epaper.service
	@sudo systemctl start epaper.service
	@echo "Systemd service installed and enabled."
