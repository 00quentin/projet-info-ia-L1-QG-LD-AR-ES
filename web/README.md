# Quant Terminal — site web

Nouveau site (Next.js + Tailwind) qui affiche les résultats du moteur Python via l'API (`../api`).

```bash
# 1. Lancer l'API (depuis la racine du dépôt)
uvicorn api.main:app --reload --port 8000

# 2. Lancer le site (depuis ce dossier)
npm install
npm run dev        # http://localhost:3000
```

L'adresse de l'API se règle avec la variable `NEXT_PUBLIC_API_URL` (par défaut `http://localhost:8000`).

- `src/app/` : pages
- `src/components/` : formulaire, résultats, graphiques (`charts/`)
- `src/lib/api.ts` : appels à l'API et types · `src/lib/format.ts` : formats français
