.PHONY: help build run run-dry discover list up down logs clean

CONTAINER_CMD := $(shell which podman 2>/dev/null || which docker 2>/dev/null)
DNS_FLAGS := --dns=192.168.7.12 --dns=8.8.8.8
MAX_SONGS ?= 25

BOLD  := \033[1m
CYAN  := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

help:
	@echo ""
	@echo "$(BOLD)$(CYAN)Airsonic Playlist Sync$(RESET)"
	@echo "$(CYAN)Using: $(CONTAINER_CMD)$(RESET)"
	@echo ""
	@echo "$(BOLD)$(YELLOW)Targets:$(RESET)"
	@echo "  $(GREEN)make build$(RESET)                   Build container image"
	@echo "  $(GREEN)make run-dry$(RESET)                 Test run (dry-run mode)"
	@echo "  $(GREEN)make run$(RESET)                     Run sync once"
	@echo "  $(GREEN)make run MAX_SONGS=20$(RESET)        Run with custom episode limit $(YELLOW)(default: 25)$(RESET)"
	@echo "  $(GREEN)make discover$(RESET)                Find folder/playlist IDs"
	@echo "  $(GREEN)make list$(RESET)                    List current playlist contents"
	@echo ""

build:
	@$(CONTAINER_CMD) build --quiet $(DNS_FLAGS) -f docker/Dockerfile -t airsonic-playlist-sync:latest . > /dev/null

run-dry: build
	@mkdir -p logs
	@$(CONTAINER_CMD) run --rm $(DNS_FLAGS) -v "$(PWD)/config.json:/config/config.json:ro" -v "$(PWD)/logs:/app/logs" airsonic-playlist-sync:latest --dry-run --max-songs $(MAX_SONGS)

run: build
	@mkdir -p logs
	@$(CONTAINER_CMD) run --rm $(DNS_FLAGS) -v "$(PWD)/config.json:/config/config.json:ro" -v "$(PWD)/logs:/app/logs" airsonic-playlist-sync:latest --max-songs $(MAX_SONGS)

discover: build
	@$(CONTAINER_CMD) run --rm -it $(DNS_FLAGS) --entrypoint python3 -v "$(PWD)/config.json:/config/config.json:ro" airsonic-playlist-sync:latest /app/discover.py --config /config/config.json

list: build
	@$(CONTAINER_CMD) run --rm $(DNS_FLAGS) --entrypoint python3 -v "$(PWD)/config.json:/config/config.json:ro" airsonic-playlist-sync:latest /app/discover.py --config /config/config.json --list
