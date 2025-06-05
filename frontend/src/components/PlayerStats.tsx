'use client';

import { useGame } from '@/contexts/GameContext';
import { Heart, Shield, Coins, Star, Sword, Zap } from 'lucide-react';

export default function PlayerStats() {
  const { state } = useGame();
  const { player } = state;

  const healthPercentage = (player.health / player.maxHealth) * 100;
  const manaPercentage = (player.mana / player.maxMana) * 100;

  return (
    <header className="fixed top-0 left-0 right-0 bg-gradient-to-r from-amber-900/80 via-amber-800/70 to-amber-900/90 border-b-2 border-amber-700 shadow-[0_2px_10px_rgba(218,165,32,0.8)] backdrop-blur-md flex items-center justify-between px-6 py-2 font-serif font-semibold text-amber-300 z-50" style={{ fontFamily: "'Cinzel', serif" }}>
      <div className="text-2xl text-amber-400 drop-shadow-lg tracking-widest select-none">Stonehaven</div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-1">
          <Star className="w-4 h-4 text-yellow-400 drop-shadow-sm" />
          <span className="text-sm font-medium text-amber-300 tracking-wide">Lvl {player.level}</span>
        </div>

        <div className="flex items-center gap-1 min-w-[110px]">
          <Heart className="w-4 h-4 text-red-400 drop-shadow" />
          <div className="relative w-full h-3 rounded bg-black/40 border border-red-700/60 shadow-inner overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-red-900/60 to-red-700/60"></div>
            <div className="relative h-full bg-gradient-to-r from-red-600 via-red-500 to-red-400 shadow-[0_0_6px_rgba(239,68,68,0.7)] transition-all duration-500" style={{ width: `${healthPercentage}%` }}/>
          </div>
          <span className="text-xs text-red-300 font-mono w-12 text-right">{player.health}/{player.maxHealth}</span>
        </div>

        <div className="flex items-center gap-1 min-w-[110px]">
          <Shield className="w-4 h-4 text-blue-400 drop-shadow" />
          <div className="relative w-full h-3 rounded bg-black/40 border border-blue-700/60 shadow-inner overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-900/60 to-blue-700/60"></div>
            <div className="relative h-full bg-gradient-to-r from-blue-600 via-blue-500 to-blue-400 shadow-[0_0_6px_rgba(59,130,246,0.7)] transition-all duration-500" style={{ width: `${manaPercentage}%` }}/>
          </div>
          <span className="text-xs text-blue-300 font-mono w-12 text-right">{player.mana}/{player.maxMana}</span>
        </div>

        <div className="flex items-center gap-1">
          <Coins className="w-5 h-5 text-yellow-400 drop-shadow-sm" />
          <span className="text-sm font-bold text-yellow-400 font-mono drop-shadow-sm">
            {player.gold}
          </span>
        </div>

        {[
          { label: 'STR', value: player.stats.strength, icon: Sword, color: 'text-red-400' },
          { label: 'DEX', value: player.stats.dexterity, icon: Zap, color: 'text-green-400' },
          { label: 'INT', value: player.stats.intelligence, icon: Shield, color: 'text-blue-400' },
          { label: 'VIT', value: player.stats.vitality, icon: Heart, color: 'text-purple-400' },
        ].map(({ label, value, icon: IconComponent, color }, idx) => (
          <div key={idx} className="flex flex-col items-center min-w-[38px] select-none">
            <IconComponent className={`${color} w-4 h-4 drop-shadow-sm`} />
            <span className={`text-xs font-semibold ${color} leading-none`}>
              {value}
            </span>
            <span className="text-[8px] text-amber-300 uppercase tracking-widest font-mono">
              {label}
            </span>
          </div>
        ))}
      </div>
    </header>
  );
}
