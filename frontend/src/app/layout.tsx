import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'MapleHub OSS',
  description: 'Open-source MapleStory companion with boss tracking and community drop statistics',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

