import "./globals.css";
import type { Metadata } from "next";
import { GameProvider } from '@/contexts/GameContext';

export const metadata: Metadata = {
  title: "RPG AI Adventure - Stonehaven",
  description: "An immersive AI-powered RPG adventure game",
};

export default function RootLayout({children}: Readonly<{children: React.ReactNode;}>) {
  return (
    <html lang="en">
      <body>
        <GameProvider>
          {children}
        </GameProvider>
      </body>
    </html>
  );
}
