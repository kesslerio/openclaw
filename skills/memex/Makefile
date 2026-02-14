.PHONY: help install start stop restart status test logs clean uninstall

help:
	@echo "Memex HISTORIAN Search API - Commands"
	@echo ""
	@echo "  make install    - Install as background service (LaunchAgent)"
	@echo "  make start      - Start the API service"
	@echo "  make stop       - Stop the API service"
	@echo "  make restart    - Restart the API service"
	@echo "  make status     - Check service status"
	@echo "  make test       - Run API tests"
	@echo "  make logs       - View service logs"
	@echo "  make clean      - Clean up logs"
	@echo "  make uninstall  - Uninstall the service"
	@echo ""

install:
	@echo "Installing Memex HISTORIAN API service..."
	@chmod +x scripts/*.sh
	@./scripts/install_service.sh

start:
	@launchctl start com.copperdigital.memex-api
	@echo "Service started. Check status with 'make status'"

stop:
	@launchctl stop com.copperdigital.memex-api
	@echo "Service stopped."

restart: stop
	@sleep 2
	@launchctl start com.copperdigital.memex-api
	@echo "Service restarted."

status:
	@./scripts/status_api.sh

test:
	@echo "Running API test suite..."
	@python scripts/test_api.py

logs:
	@echo "=== Standard Output ==="
	@tail -50 ~/Library/Logs/memex-api.log
	@echo ""
	@echo "=== Error Output ==="
	@tail -50 ~/Library/Logs/memex-api-error.log

clean:
	@echo "Cleaning logs..."
	@rm -f ~/Library/Logs/memex-api*.log
	@echo "Logs cleaned."

uninstall:
	@./scripts/uninstall_service.sh
