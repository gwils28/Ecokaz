# Ecokaz

Le copilote énergie et carbone du foyer : consommation réelle d'électricité, de gaz, d'eau et de carburant, en unités, en euros et en kgCO₂e, avec un coach IA qui explique et propose des actions.

> **Statut : V0 en cours (lot 0, socle).** Usage personnel d'abord, France métropolitaine. Voir [`PLAN.md`](PLAN.md).

## Démarrer

```bash
cp .env.example .env      # puis changer les valeurs
make setup                # dépendances + hook commit-msg
make check                # lint, types, tests
make dev-api              # API sur :8001
make dev-web              # interface sur :5174
make up                   # stack complète sur https://localhost:8453
```

Prérequis : Docker, [uv](https://docs.astral.sh/uv/), Node (via fnm) et pnpm.

## Stack

FastAPI · SQLAlchemy · Alembic · PostgreSQL 17 · React · TypeScript · Vite · Tailwind · Caddy · Docker Compose.

## Sources des données et des facteurs

- Électricité : Enedis, via [Conso API](https://conso.boris.sh/) ou un export CSV de l'espace client.
- Facteurs d'émission : ADEME, Base Empreinte. Chaque valeur est versionnée avec sa source.
