# Ecokaz — Plan V0

> Statut : **validé le 2026-10-09**. Nom : Ecokaz. Repo GitHub public.
> Dernière mise à jour : 2026-10-09

## 1. Promesse V0

Pour **mon foyer** (France métropolitaine), en un seul endroit :
voir ma consommation réelle d'électricité, de gaz, d'eau et de carburant, en **unités, € et kgCO₂e**,
la comparer à mon bilan carbone de départ, et être prévenu quand quelque chose dérive.

Critère de succès V0 : je l'ouvre chaque semaine sur mon téléphone pendant 2 mois et j'ai pris au moins une décision grâce à elle.

## 2. Périmètre

| Dans la V0 | Hors V0 (plus tard) |
|---|---|
| Profil foyer (logement, surface, année, occupants, chauffage, véhicules) | OCR de factures |
| Bilan carbone déclaratif rapide à l'onboarding (≈ 15 questions) | Benchmark social, multi-foyers |
| Électricité : connecteur Conso API (Enedis Metering V5) + import CSV Enedis | Simulations « what-if » complètes |
| Gaz, eau, km voiture : saisie d'index (relevé compteur / odomètre) | Prévision ML (après 3 mois de données) |
| Tarifs saisis par l'utilisateur → € | Gamification, badges |
| Dashboard : jour / semaine / mois / année, par poste | Freemium, paiement |
| Objectifs de réduction + suivi de progression | App mobile (V2), notifications push |
| Détection de pics (méthode statistique simple, expliquée) | RAG sur corpus documentaire |
| Coach : règles déterministes + Mistral pour expliquer et répondre | |

## 3. Principes non négociables

1. **Le LLM ne calcule jamais.** Tous les chiffres viennent de fonctions Python testées ; le coach les appelle (tool calling) et les commente.
2. **Facteurs d'émission versionnés et sourcés** (ADEME Base Empreinte), dans un fichier unique avec la source et la date de chaque valeur. Aucun chiffre en dur dans le code.
3. **Une source de données = un adaptateur** derrière une même interface (`fetch() → mesures normalisées`). Ajouter une source ne touche ni le stockage, ni le dashboard.
4. **Baseline avant modèle** : anomalies d'abord par règles statistiques simples ; le ML seulement s'il fait mieux sur un protocole écrit à l'avance.
5. **Données perso** : hébergement UE, secrets hors du repo, sauvegardes chiffrées, export et suppression possibles.

## 4. Architecture (monolithe modulaire)

```
App web React responsive (Vite, TS, Tailwind, charte gwils28) — mobile en V2
        │ HTTPS (Caddy)
FastAPI ─┬─ domain/      calculs purs : conso, €, CO₂e, anomalies, objectifs   ← cœur testé
         ├─ sources/     linky_api, linky_csv, manual_index
         ├─ coach/       règles + client Mistral (tool calling sur domain/)
         ├─ api/         routes REST, auth
         └─ jobs/        sync quotidienne Linky (APScheduler, pas de Celery)
PostgreSQL 16 (pas de TimescaleDB : ~17 500 points/an à 30 min, Postgres suffit)
```

Déploiement : Docker Compose sur un VPS UE (Hetzner ou Scaleway, ≈ 5 €/mois), Caddy pour le HTTPS, `pg_dump` chiffré quotidien.
Outillage : `uv` + `ruff` + `pytest` (back), `pnpm` + `vitest` + Playwright (front), CI GitHub Actions.

### Modèle de données (première version)

- `household` (profil), `user`
- `meter` (type : elec / gas / water / vehicle ; unité ; source)
- `reading` (meter_id, ts_start, ts_end, value, unit, source, imported_at), unique sur (meter, ts_start, ts_end)
- `tariff` (meter, période de validité, abonnement, prix unitaire, HP/HC)
- `emission_factor` (poste, valeur, unité, source, date de validité)
- `footprint_survey` (réponses du bilan déclaratif + résultat)
- `goal` (poste, période de référence, cible en %)
- `alert` (meter, période, type, sévérité, explication)

Les index manuels (gaz, eau, km) sont convertis en consommation par intervalle entre deux relevés, sans inventer de répartition intra-période.

## 5. Lots (chacun se termine par une preuve)

| # | Lot | Preuve de fin |
|---|---|---|
| 0 | Socle : git, uv, pnpm, Docker Compose, CI, CLAUDE.md, hooks | `docker compose up` + CI verte |
| 1 | Domaine : conversions, €, CO₂e, index → conso (test-first) | tests de propriétés verts (non-négativité, additivité, index décroissant rejeté) |
| 2 | Électricité : import CSV Enedis + connecteur Conso API V5 + sync quotidienne | ma courbe réelle importée, contrôles qualité (trous, doublons, unités) passés |
| 3 | Auth (compte du foyer) + front : charte, onboarding/profil, dashboard électricité | capture navigateur desktop et petit écran, clair et sombre |
| 4 | **Déploiement VPS** (tôt, pour l'utiliser au quotidien) | URL HTTPS accessible, restauration de sauvegarde testée |
| 5 | Gaz, eau, voiture (saisie d'index) + tarifs + dashboard multi-postes | totaux cohérents avec mes factures (écart expliqué) |
| 6 | Bilan carbone déclaratif + comparaison bilan / mesuré | résultat comparé à Nos Gestes Climat sur mon profil, écart expliqué |
| 7 | Objectifs + détection de pics (baseline robuste par jour de semaine) | tests sur séries synthétiques (pic injecté détecté, série plate sans fausse alerte) |
| 8 | Coach : règles, puis Mistral en tool calling, avec un jeu d'évaluation écrit **avant** les prompts | jeu d'éval versionné, aucun chiffre halluciné |

Estimation, au rythme soirs et week-ends : lots 0 à 4 ≈ 3-4 semaines, V0 complète ≈ 8-10 semaines.

## 6. Outillage Claude Code (minimal au départ, enrichi au besoin)

- **CLAUDE.md** court : commandes non évidentes, règles 1-3 ci-dessus avec leur raison.
- **Hooks** : formatage (ruff / Biome) après chaque édition ; secrets (`.env*`) illisibles et `data/` en lecture seule ; hook `Stop` qui refuse de finir si `make check-fast` échoue ; garde sur les commandes de versionnement (ni contournement des hooks, ni co-auteur).
- **Subagent `code-reviewer`** (lecture seule) : relit le diff dans un contexte vierge, ne remonte que les problèmes de correction.
- **Skills** : `prepare-commit` (message Conventional Commit, le mainteneur committe) ; `db-migration` (modèle + migration Alembic testée).
- **Plus tard, si le besoin revient** : skill `dictionnaire-donnees-energie` (unités, pièges Enedis, sources ADEME) ; subagent `statisticien` au lot 7.
- **Chrome MCP** pour vérifier l'UI dans un vrai navigateur.

## 7. Décisions qui te reviennent / points ouverts

- [x] Plan validé ; nom **Ecokaz** ; repo **public** ; web d'abord, mobile en V2.
- [x] Réutiliser le socle de Kwak Finance (tooling ; auth à reprendre au lot 3).
- [ ] Hetzner ou Scaleway ; nom de domaine ?
- [ ] Vérifier sur ton espace GRDF s'il existe un export de fichier (sinon le gaz reste en saisie d'index).
- [ ] Fournisseur d'eau (certains exposent un historique en ligne).
- [ ] Clé API Mistral (au lot 8 seulement).

## 8. Ce que je corrige par rapport au plan

_(journal des écarts, rempli au fil de l'eau)_

- **2026-10-09, lot 0.** Socle repris de Kwak Finance (commit 7d67666) au lieu d'être écrit de zéro, pour garder les mêmes conventions : le mainteneur est seul à committer, hooks, Stop hook `make check-fast`, testcontainers. Conséquences : PostgreSQL **17** au lieu de 16 ; Biome au lieu de Prettier ; scheduler et i18n reportés au lot où ils servent.
- **2026-10-09, lot 0, revue.** Le socle hérité avait des défauts, corrigés : Alembic ne voyait aucun modèle (ajout de `ecokaz_api/models`) ; le conteneur `api` n'appliquait pas les migrations (il lance maintenant `python -m ecokaz_api.migrate`) ; le conteneur `web` recevait les identifiants de la base ; l'en-tête HSTS était envoyé sur localhost (désormais `ECOKAZ_HSTS_MAX_AGE`, 0 en local). Ports dédiés 8090/8453 et 8001/5174, pour cohabiter avec Kwak Finance.
- **2026-10-09, charte.** En mode sombre, le fond passe à `neutral-800`, comme sur le blog (Kwak Finance utilisait `neutral-900`).
