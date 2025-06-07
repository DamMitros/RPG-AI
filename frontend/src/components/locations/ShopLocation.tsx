'use client';

import React, { useState, useEffect } from 'react';
import { useGame } from '@/contexts/GameContext';
import { useQuests } from '@/hooks/useQuests';
import { gameApi } from '@/services/gameApi';
import { Coins, Package, MessageCircle, User, AlertTriangle, ArrowLeft } from 'lucide-react';
import { InventoryItem, QuestAction } from '@/types/game';
import DialogInterface from '@/components/DialogInterface';

type ShopMode = 'menu' | 'buy' | 'sell' | 'talk';

const ShopLocation: React.FC = () => {
  const { state, dispatch } = useGame();
  const { getQuestActionsForLocation } = useQuests();
  const [shopItems, setShopItems] = useState<InventoryItem[]>([]);
  const [playerInventory, setPlayerInventory] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [shopMessage, setShopMessage] = useState<string>('');
  const [currentMode, setCurrentMode] = useState<ShopMode>('menu');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [questActions, setQuestActions] = useState<QuestAction[]>([]);

  useEffect(() => {
    const loadShopData = async () => {
      try {
        setIsLoading(true);
        const shopResponse = await gameApi.getShopItems() as { items?: InventoryItem[] };
        setShopItems(shopResponse.items || []);
        const playerData = await gameApi.getPlayer();
        dispatch({ type: 'SET_PLAYER', payload: playerData });
        setPlayerInventory(Array.isArray(playerData.inventory) ? playerData.inventory : []);
        
      } catch (error) {
        console.error('Failed to load shop data:', error);
        setShopItems([]);
        setPlayerInventory([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadShopData();
  }, [dispatch]);

  useEffect(() => {
    const loadQuestActions = async () => {
      try {
        const actions = await getQuestActionsForLocation('shop');
        setQuestActions(actions);
      } catch (error) {
        console.error('Failed to load quest actions:', error);
        setQuestActions([]);
      }
    };

    loadQuestActions();
  }, [getQuestActionsForLocation, isDialogOpen]); 

  const shopActions = [
    {
      id: 'buy',
      name: 'Browse Wares',
      icon: Package,
      description: 'Browse Erik\'s collection of mysterious goods',
      mode: 'buy' as const,
    },
    {
      id: 'sell',
      name: 'Sell Items',
      icon: Coins,
      description: 'Sell your items to Erik for gold',
      mode: 'sell' as const,
    },
    {
      id: 'talk',
      name: 'Speak with Erik',
      icon: MessageCircle,
      description: 'Have a conversation with the mysterious merchant',
      mode: 'talk' as const,
    },
  ];

  const handleModeChange = (mode: ShopMode) => {
    if (mode === 'talk') {
      setIsDialogOpen(true);
    } else {
      setCurrentMode(mode);
    }
    setShopMessage('');
  };

  const handleBuyItem = async (item: InventoryItem) => {
    if (!item.value || state.player.gold < item.value) {
      setShopMessage(`You don't have enough gold for the ${item.name}. You need ${item.value} gold coins.`);
      return;
    }

    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      const result = await gameApi.buyItem(item.id, 1) as { success: boolean; message?: string };
      
      if (result.success) {
        const updatedPlayer = await gameApi.getPlayer();
        console.log('Updated player after purchase:', updatedPlayer);
        dispatch({ type: 'SET_PLAYER', payload: updatedPlayer });

        const shopResponse = await gameApi.getShopItems() as { items?: InventoryItem[] };
        setShopItems(shopResponse.items || []);
        setPlayerInventory(Array.isArray(updatedPlayer.inventory) ? updatedPlayer.inventory : []);
        
        setShopMessage(result.message || `Successfully purchased ${item.name}!`);
      } else {
        setShopMessage(result.message || 'Something went wrong with the purchase.');
      }
    } catch (error) {
      console.error('Purchase failed:', error);
      setShopMessage(`Purchase failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const handleSellItem = async (item: InventoryItem, itemIndex: number) => {
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      const result = await gameApi.sellItem(itemIndex.toString(), 1) as { success: boolean; message?: string };
      
      if (result.success) {
        const updatedPlayer = await gameApi.getPlayer();
        console.log('Updated player after sale:', updatedPlayer);
        dispatch({ type: 'SET_PLAYER', payload: updatedPlayer });
        setPlayerInventory(Array.isArray(updatedPlayer.inventory) ? updatedPlayer.inventory : []);
        setShopMessage(result.message || `Successfully sold ${item.name}!`);
      } else {
        setShopMessage(result.message || 'Something went wrong with the sale.');
      }
    } catch (error) {
      console.error('Sale failed:', error);
      setShopMessage(`Sale failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const closeDialog = () => {
    setIsDialogOpen(false);
  };

  const resetToMenu = () => {
    setCurrentMode('menu');
    setShopMessage('');
  };

  if (isLoading) {
    return (
      <div className="p-6 text-center">
        <div className="text-amber-300">Loading Erik&apos;s mysterious wares...</div>
      </div>
    );
  }

  const renderShopMenu = () => (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {shopActions.map((action) => {
        const IconComponent = action.icon;
        const isDisabled = state.isLoading;
        
        return (
          <button key={action.id} onClick={() => handleModeChange(action.mode)} disabled={isDisabled} className={`p-6 rounded-lg border-2 transition-all duration-300 ${isDisabled ? 'bg-gradient-to-br from-gray-800/60 via-gray-700/50 to-gray-800/60 border-gray-600 opacity-50 cursor-not-allowed text-gray-400' : 'bg-gradient-to-br from-amber-900/80 via-orange-900/70 to-amber-900/80 border-amber-600/50 hover:border-amber-400 hover:shadow-[0_0_20px_rgba(245,158,11,0.8)] text-amber-200'}`}>
            <div className="flex flex-col items-center text-center space-y-3">
              <IconComponent className={`w-12 h-12 drop-shadow ${isDisabled ? 'text-gray-500' : 'text-amber-400'}`} />
              <h3 className={`font-bold text-lg tracking-wide ${isDisabled ? 'text-gray-400' : 'text-amber-200'}`}>
                {action.name}
              </h3>
              <p className={`text-sm leading-relaxed ${isDisabled ? 'text-gray-500' : 'text-amber-300'}`}>
                {action.description}
              </p>
            </div>
          </button>
        );
      })}
    </div>
  );

  const renderBuyMode = () => {
    const itemsToRender = Array.isArray(shopItems) ? shopItems : [];
    
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-2xl font-bold text-amber-300">🎒 Erik&apos;s Wares</h3>
          <button onClick={resetToMenu} className="flex items-center space-x-2 px-4 py-2 bg-amber-700 hover:bg-amber-600 text-amber-100 rounded-lg font-bold transition-colors">
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Menu</span>
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {itemsToRender.length > 0 ? itemsToRender.map((item, index) => {
            const canAfford = item.value ? state.player.gold >= item.value : false;
          
          return (
            <div key={`buy-${item.id}-${index}`} className={`p-4 rounded-lg border-2 transition-all duration-300 ${canAfford ? 'bg-gradient-to-br from-blue-900/80 via-blue-800/70 to-purple-900/80 border-blue-600 hover:border-blue-400 text-blue-200' : 'bg-gradient-to-br from-gray-800/60 via-gray-700/50 to-gray-800/60 border-gray-600 opacity-50 text-gray-400'}`}>
              <div className="flex flex-col space-y-2">
                <h4 className={`font-bold text-lg ${canAfford ? 'text-blue-200' : 'text-gray-400'}`}>{item.name}</h4>
                <p className={`text-sm ${canAfford ? 'text-blue-300' : 'text-gray-500'}`}>{item.description}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1">
                    <Coins className="w-4 h-4 text-yellow-400" />
                    <span className="text-yellow-400 font-bold">{item.value}</span>
                  </div>
                  <span className={`text-xs ${canAfford ? 'text-blue-300' : 'text-gray-500'}`}>Qty: {item.quantity}</span>
                </div>
                <button onClick={() => handleBuyItem(item)} disabled={!canAfford || state.isLoading} className={`px-3 py-2 rounded font-bold transition-all duration-300 ${canAfford && !state.isLoading ? 'bg-gradient-to-r from-green-700 to-green-600 hover:from-green-600 hover:to-green-500 text-green-100' : 'bg-gray-600 border border-gray-500 cursor-not-allowed text-gray-400'}`}>
                  {canAfford ? 'Buy' : 'Cannot Afford'}
                </button>
              </div>
            </div>
          );
        }) : (
          <div className="col-span-full text-center p-8 text-gray-400">
            Erik&apos;s cart seems empty today...
          </div>
        )}
      </div>
    </div>
    );
  };

  const renderSellMode = () => {
    const inventoryToRender = Array.isArray(playerInventory) ? playerInventory : [];
    
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-2xl font-bold text-amber-300">💰 Your Items to Sell</h3>
          <button onClick={resetToMenu} className="flex items-center space-x-2 px-4 py-2 bg-amber-700 hover:bg-amber-600 text-amber-100 rounded-lg font-bold transition-colors">
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Menu</span>
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {inventoryToRender.length > 0 ? inventoryToRender.map((item, index) => {
            const sellValue = Math.floor((item.value || 0) / 2);
          
          return (
            <div key={`sell-${item.id}-${index}`} className="p-4 rounded-lg border-2 bg-gradient-to-br from-purple-900/80 via-purple-800/70 to-indigo-900/80 border-purple-600 text-purple-200">
              <div className="flex flex-col space-y-2">
                <h4 className="font-bold text-lg text-purple-200">{item.name}</h4>
                <p className="text-sm text-purple-300">{item.description}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1">
                    <Coins className="w-4 h-4 text-yellow-400" />
                    <span className="text-yellow-400 font-bold">{sellValue}</span>
                  </div>
                  <span className="text-xs text-purple-300">Qty: {item.quantity}</span>
                </div>
                <button onClick={() => handleSellItem(item, index)} disabled={state.isLoading} className="px-3 py-2 rounded font-bold bg-gradient-to-r from-orange-700 to-orange-600 hover:from-orange-600 hover:to-orange-500 text-orange-100 transition-all duration-300 disabled:bg-gray-600 disabled:text-gray-400">
                  Sell for {sellValue} gold
                </button>
              </div>
            </div>
          );
        }) : (
          <div className="col-span-full text-center p-8 text-gray-400">Your pockets are empty...</div>
        )}
      </div>
    </div>
    );
  };

  const renderCurrentMode = () => {
    switch (currentMode) {
      case 'buy':
        return renderBuyMode();
      case 'sell':
        return renderSellMode();
      case 'menu':
      default:
        return renderShopMenu();
    }
  };

  return (
    <>
      <div className="p-6 space-y-6 min-h-screen" style={{ fontFamily: "'Cinzel', serif" }}>
        <div className="bg-gradient-to-br from-amber-900/90 via-amber-800/80 to-amber-900/90 border-2 border-amber-700 rounded-lg shadow-[0_0_20px_rgba(218,165,32,0.8)] backdrop-blur-md p-6 text-center">
          <h2 className="text-4xl font-bold text-amber-300 mb-4 drop-shadow-lg tracking-wider">🛒 Erik&apos;s Wares</h2>
          <p className="text-amber-200 font-medium leading-relaxed">
            Erik the Wanderer stands beside his cart of mysterious goods. His eyes have an unsettling gleam 
            that wasn&apos;t there before his last journey to the city...
          </p>
        </div>

        <div className="bg-gradient-to-br from-orange-900/90 via-amber-900/80 to-orange-900/90 border-2 border-orange-700/80 rounded-lg shadow-[0_0_20px_rgba(234,88,12,0.7)] backdrop-blur-sm p-8 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-amber-600/5 via-yellow-600/10 to-amber-600/5 animate-pulse"></div>
          <div className="relative text-center mb-6">
            <User className="w-20 h-20 text-amber-400 mx-auto mb-4 drop-shadow-lg" />
            <h3 className="text-2xl font-bold text-amber-300 tracking-wider drop-shadow">Erik the Wanderer</h3>
          </div>
          <p className="relative text-amber-200 text-center leading-relaxed font-medium">
            The merchant&apos;s cart is laden with exotic goods from distant lands. Strange trinkets catch the light,
            and you can&apos;t shake the feeling that some of these items are watching you back...
          </p>
        </div>

        <div className="bg-gradient-to-r from-yellow-900/80 via-amber-900/70 to-yellow-900/80 border-2 border-yellow-600 rounded-lg shadow-[0_0_15px_rgba(234,179,8,0.6)] backdrop-blur-sm p-6">
          <div className="flex items-center justify-center space-x-3">
            <Coins className="w-8 h-8 text-yellow-400 drop-shadow animate-bounce" />
            <span className="text-yellow-300 font-bold text-xl tracking-wide drop-shadow">
              Welcome, {state.player.name} | Gold: {state.player.gold} coins
            </span>
          </div>
        </div>

        {shopMessage && (
          <div className="bg-gradient-to-r from-green-900/80 via-emerald-900/70 to-green-900/80 border-2 border-green-600 rounded-lg shadow-[0_0_15px_rgba(34,197,94,0.6)] backdrop-blur-sm p-6">
            <div className="text-green-300 font-medium text-center">{shopMessage}</div>
          </div>
        )}
        {renderCurrentMode()}
      </div>

      <div className="bg-gradient-to-r from-orange-900/80 via-red-900/70 to-orange-900/80 border-2 border-orange-600 rounded-lg shadow-[0_0_15px_rgba(249,115,22,0.7)] backdrop-blur-sm p-6">
        <div className="flex items-center space-x-3 text-orange-300">
          <AlertTriangle className="w-6 h-6 animate-pulse drop-shadow" />
            <span className="font-medium italic">
              Erik whispers: &quot;I&apos;ve got special items from distant lands... some say they&apos;re cursed, but I say they&apos;re just... unique.&quot;
            </span>
          </div>
      </div>

      {isDialogOpen && (
        <DialogInterface
          character="merchant"
          characterName="Erik"
          isOpen={isDialogOpen}
          onClose={closeDialog}
          questActions={questActions}
        />
      )}
    </>
  );
};

export default ShopLocation;
