'use client';

import { useGame } from '@/contexts/GameContext';
import { MapPin, Backpack, Scroll, Store, Hammer, TreePine, Mountain, Beer } from 'lucide-react';
import { motion } from 'framer-motion';

interface NavigationProps {
  onLocationChange: (location: string) => void;
}

export default function Navigation({ onLocationChange }: NavigationProps) {
  const { state } = useGame();
  const { currentLocation } = state;

  const locations = [
    { id: 'mainPage', name: 'Market Square', icon: MapPin },
    { id: 'tavern', name: 'Tavern', icon: Beer },
    { id: 'shop', name: 'Shop', icon: Store },
    { id: 'smithy', name: 'Smithy', icon: Hammer },
    { id: 'forest', name: 'Forest', icon: TreePine },
    { id: 'mine_entrance', name: 'Mine Entrance', icon: Mountain },
    { id: 'inventory', name: 'Inventory', icon: Backpack },
    { id: 'quest', name: 'Quests', icon: Scroll },
  ];

  return (
    <nav className="w-64 bg-gradient-to-b from-[#4b2e14] via-[#5c3b1d] to-[#3b220f] border-r-4 border-[#daa520] shadow-[0_0_20px_rgba(212,175,55,0.7)] fixed top-0 left-0 h-full flex flex-col font-serif font-semibold text-amber-300">
      <div className="flex flex-col space-y-3 px-6 py-30">
        {locations.map((location) => {
          const Icon = location.icon;
          const isActive = currentLocation === location.id;

          return (
            <motion.button
              key={location.id}
              onClick={() => onLocationChange(location.id)}
              className={`flex items-center gap-3 text-lg px-4 py-3 rounded-lg cursor-pointer transition-colors duration-300 ${isActive ? 'bg-gradient-to-r from-[#daa520] to-[#b8860b] text-gray-900 shadow-[0_0_15px_4px_rgba(218,165,32,0.8)]' : 'hover:bg-[#8b4513] hover:text-amber-200 text-amber-300'} ring-1 ring-[#daa520]`} 
              whileHover={{ scale: 1.05 }} 
              whileTap={{ scale: 0.95 }} 
              style={{ fontFamily: "'Cinzel', serif" }}
            >
              <Icon className={`${isActive ? 'text-yellow-700' : 'text-amber-400'} w-6 h-6`} />
              <span>{location.name}</span>
            </motion.button>
          );
        })}
      </div>
    </nav>
  );
}
