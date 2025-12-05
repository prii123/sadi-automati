.PHONY: help build up down restart logs ps clean init backup test deploy

# Variables
COMPOSE=docker-compose
CONTAINER=sadi-facturacion

help: ## Muestra esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Construye la imagen Docker
	$(COMPOSE) build

up: ## Inicia los contenedores
	$(COMPOSE) up -d

down: ## Detiene los contenedores
	$(COMPOSE) down

restart: ## Reinicia los contenedores
	$(COMPOSE) restart

logs: ## Muestra los logs
	$(COMPOSE) logs -f

ps: ## Muestra el estado de los contenedores
	$(COMPOSE) ps

clean: ## Elimina contenedores, volúmenes e imágenes
	$(COMPOSE) down -v --rmi all

init: ## Inicializa la base de datos
	$(COMPOSE) exec web python scripts/init_db.py

backup: ## Crea backup de la base de datos
	@echo "Creando backup..."
	@DATE=$$(date +%Y%m%d_%H%M%S); \
	docker cp $(CONTAINER):/app/data/facturacion.db ./backup_$$DATE.db && \
	echo "Backup creado: backup_$$DATE.db"

test: ## Ejecuta tests (si existen)
	$(COMPOSE) exec web python scripts/test_sistema.py

shell: ## Accede a la shell del contenedor
	$(COMPOSE) exec web /bin/bash

python: ## Accede a la consola Python del contenedor
	$(COMPOSE) exec web python

deploy: ## Despliega la aplicación
	@echo "Desplegando aplicación..."
	@if [ ! -f .env.production ]; then \
		echo "Error: .env.production no existe. Crea el archivo primero."; \
		exit 1; \
	fi
	$(MAKE) down
	$(MAKE) build
	$(MAKE) up
	@echo "Aplicación desplegada!"

update: ## Actualiza la aplicación (git pull + rebuild)
	@echo "Actualizando aplicación..."
	git pull
	$(MAKE) deploy

stats: ## Muestra estadísticas de uso del contenedor
	docker stats $(CONTAINER)

health: ## Verifica el estado de salud del contenedor
	docker inspect $(CONTAINER) | grep Health -A 10

prod: ## Prepara para producción
	@if [ ! -f .env.production ]; then \
		cp .env.production.example .env.production; \
		echo "Archivo .env.production creado. Edítalo con tus valores reales."; \
	else \
		echo ".env.production ya existe."; \
	fi
