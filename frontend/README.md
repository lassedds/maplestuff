# MapleHub OSS Frontend

Next.js 14 frontend for MapleHub OSS.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Project Structure

- `src/app/` - Next.js App Router pages
- `src/components/` - React components
- `src/services/` - API client and services
- `src/types/` - TypeScript type definitions

## Development

- Uses TypeScript for type safety
- Tailwind CSS for styling
- Axios for API calls
- Next.js 14 App Router

