.PHONY: help build run run-dry discover up down logs clean

CONTAINER_CMD := $(shell which podman 2>/dev/null || which docker 2>/dev/null)
DNS_FLAGS := --dns=192.168.7.12 --dns=8.8.8.8

help:
	@echo "Airsonic Playlist Sync - Podman/Docker Commands"
	@echo "Using: $(CONTAINER_CMD)"
	@echo ""
	@echo "make build    - Build container image"
	@echo "make run-dry  - Test run (dry-run mode)"
	@echo "make run      - Run sync once"
	@echo "make discover - Find folder/playlist IDs"

build:
	$(CONTAINER_CMD) build $(DNS_FLAGS) -f docker/Dockerfile -t airsonic-playlist-sync:latest .

run-dry: build
	@mkdir -p logs
	$(CONTAINER_CMD) run --rm $(DNS_FLAGS) -v "$(PWD)/config.json:/config/config.json:ro" -v "$(PWD)/logs:/app/logs" airsonic-playlist-sync:latest --dry-run

run: build
	@mkdir -p logs
	$(CONTAINER_CMD) run --rm $(DNS_FLAGS) -v "$(PWD)/config.json:/config/config.json:ro" -v "$(PWD)/logs:/app/logs" airsonic-playlist-sync:latest

discover: build
	$(CONTAINER_CMD) run --rm -it $(DNS_FLAGS) -v "$(PWD)/config.json:/config/config.json:ro" airsonic-playlist-sync:latest python3 /app/discover.py --config /config/config.json
