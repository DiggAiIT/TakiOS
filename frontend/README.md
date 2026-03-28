# TakiOS Frontend

## Stack

- Next.js App Router
- React 19
- TypeScript 5
- next-intl
- React Query
- Zustand
- Tailwind CSS 4

## Einstieg

```bash
cd frontend
npm install
```

## Entwicklung

```bash
cd frontend
npm run dev
```

Die App erwartet standardmaessig die API unter:

- `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`

Vorlage:

- `frontend/.env.example`

## Validierung

```bash
cd frontend
npx tsc --noEmit
```

## Struktur

- `src/app/[locale]`: Seiten nach Locale
- `src/hooks`: React Query Hooks nach Fachdomaine
- `src/lib/api-client.ts`: zentraler API-Client
- `messages`: Uebersetzungsdateien fuer `de` und `en`

## Aktueller Datenfluss

Die zentralen Bereiche verwenden Query-/Mutation-Hooks statt manuellem `useEffect`-Laden, darunter:

- Learn
- Assess
- Projects
- Settings
- Collaborate
- Impact
- Quality
- Compliance
