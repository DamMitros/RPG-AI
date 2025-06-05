'use client';

import { useState } from 'react';
import { useGame } from '@/contexts/GameContext';
import PlayerStats from '@/components/PlayerStats';
import Navigation from '@/components/Navigation';
import MainPageLocation from '@/components/locations/MainPageLocation';
import InventoryLocation from '@/components/locations/InventoryLocation';
import TavernLocation from '@/components/locations/TavernLocation';
import ShopLocation from '@/components/locations/ShopLocation';
import SmithyLocation from '@/components/locations/SmithyLocation';
import ForestLocation from '@/components/locations/ForestLocation';
import MineLocation from '@/components/locations/MineLocation';
import QuestLocation from '@/components/locations/QuestLocation';

export default function Home() {
  const { state, dispatch } = useGame();
  const [currentView, setCurrentView] = useState('mainPage');

  const handleLocationChange = (location: string) => {
    setCurrentView(location);
    dispatch({ type: 'SET_LOCATION', payload: location });
  };

  const renderCurrentLocation = () => {
    switch (currentView) {
      case 'mainPage':
        return <MainPageLocation />;
      case 'inventory':
        return <InventoryLocation />;
      case 'tavern':
        return <TavernLocation />;
      case 'shop':
        return <ShopLocation />;
      case 'smithy':
        return <SmithyLocation />;
      case 'forest':
        return <ForestLocation />;
      case 'mine_entrance':
        return <MineLocation />;
      case 'quest':
        return <QuestLocation />;
      default:
        return <MainPageLocation />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden" style={{ fontFamily: "'Cinzel', serif" }}>
      <div className="fixed inset-0 -z-10" style={{
          background: 'linear-gradient(135deg, #2c1810 0%, #4a2c1a 50%, #6b3e2a 100%)',
          backgroundAttachment: 'fixed',
        }}/>

      <div className="fixed inset-0 -z-10 opacity-20" style={{
          backgroundImage: `url("data:image/svg+xml,${encodeURIComponent(
            '<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="circles" x="0" y="0" width="60" height="60" patternUnits="userSpaceOnUse"><circle cx="30" cy="30" r="10" fill="none" stroke="%23d4af37" stroke-width="2" opacity="0.3"/></pattern></defs><rect width="100%" height="100%" fill="url(%23circles)"/></svg>'
          )}")`,
          backgroundSize: '60px 60px',
        }}/>

      <div className="relative z-40">
        <PlayerStats />
      </div>

      <div className="flex flex-1 max-w-screen-xl mx-auto mt-4 px-6 gap-8 pt-12 relative z-10">
        <nav className="w-48 relative z-10">
          <Navigation onLocationChange={handleLocationChange} />
        </nav>

        <main className="flex-1 pt-12 relative z-10">
          {renderCurrentLocation()}
        </main>
      </div>

      {state.isLoading && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="fantasy-panel text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto mb-4"></div>
            <p className="text-lg">Ładowanie...</p>
          </div>
        </div>
      )}
    </div>
  );
}
