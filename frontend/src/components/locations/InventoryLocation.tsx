'use client';

import { useState } from 'react';
import { useGame } from '@/contexts/GameContext';
import { gameApi } from '@/services/gameApi';
import { motion, AnimatePresence } from 'framer-motion';
import { Package, Sword, Shield, Sparkles, Trash2, Play } from 'lucide-react';
import { InventoryItem, Player } from '@/types/game';

export default function InventoryLocation() {
  const { state, dispatch } = useGame();
  const { player } = state;
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);

  const getItemIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'weapon':
        return Sword;
      case 'armor':
        return Shield;
      case 'consumable':
        return Sparkles;
      default:
        return Package;
    }
  };

  const getItemRarityColor = (rarity: string = 'common') => {
    switch (rarity.toLowerCase()) {
      case 'legendary':
        return 'border-orange-400 bg-orange-900/20';
      case 'epic':
        return 'border-purple-400 bg-purple-900/20';
      case 'rare':
        return 'border-blue-400 bg-blue-900/20';
      case 'uncommon':
        return 'border-green-400 bg-green-900/20';
      default:
        return 'border-gray-400 bg-gray-900/20';
    }
  };

  const handleUseItem = async (item: InventoryItem) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const itemIndex = player.inventory.findIndex(invItem => 
        invItem.id === item.id && invItem.name === item.name
      );
      
      if (itemIndex === -1) {
        console.error('Item not found in inventory');
        return;
      }
      
      const response = await gameApi.useInventoryItem(itemIndex);

      if (response.data?.player) {
        dispatch({ type: 'SET_PLAYER', payload: response.data.player as Player });
        setSelectedItem(null); 
      }

      console.log('Used the item like a boss:', response.message);
    } catch (error) {
      console.error('Couldn\'t use the item. Chill, we\'ll fix it:', error);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const handleDropItem = async (item: InventoryItem) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });

      const response = await gameApi.performAction('inventory', 'drop', {
        itemId: item.id,
        itemName: item.name,
      });

      if (response.data?.player) {
        dispatch({ type: 'SET_PLAYER', payload: response.data.player as Player });
      }

      console.log('Dropped that trash like a pro:', response.message);
    } catch (error) {
      console.error('Dropping failed. Rage quit? Nah, just debugging:', error);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const handleUnequipItem = async (slot: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });

      const response = await gameApi.unequipItem(slot);

      if (response.data?.player) {
        dispatch({ type: 'SET_PLAYER', payload: response.data.player as Player });
      }

      console.log('Unequipped item:', response.message);
    } catch (error) {
      console.error('Failed to unequip item:', error);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  return (
    <div className="p-6 space-y-6 min-h-screen" style={{ fontFamily: "'Cinzel', serif" }}>
      <div className="bg-gradient-to-br from-amber-900/90 via-amber-800/80 to-amber-900/90 border-2 border-amber-700 rounded-lg shadow-[0_0_25px_rgba(218,165,32,0.8)] backdrop-blur-md p-6 text-center">
        <h2 className="text-4xl font-bold text-amber-300 mb-4 drop-shadow-lg tracking-wider">Traveler&apos;s Inventory</h2>
        <p className="text-amber-200 font-medium leading-relaxed">
          Your personal collection of treasures, tools, and treasured belongings gathered
          throughout your adventures in the realm.
        </p>
      </div>

      <div className="bg-gradient-to-br from-amber-900/80 via-yellow-900/70 to-amber-900/80 border-2 border-amber-700/80 rounded-lg shadow-[0_0_20px_rgba(245,158,11,0.7)] backdrop-blur-sm p-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-yellow-600/10 via-amber-600/20 to-yellow-600/10 animate-pulse"></div>
        <div className="relative text-center mb-6">
          <Package className="w-20 h-20 text-amber-400 mx-auto mb-4 drop-shadow-lg" />
          <h3 className="text-2xl font-bold text-amber-300 tracking-wider drop-shadow">Your Personal Storage</h3>
        </div>
        <p className="relative text-amber-200 text-center leading-relaxed font-medium">
          A well-organized collection of your most valuable possessions. Each item tells
          a story of your journey and adventures throughout the mystical lands.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-gradient-to-r from-purple-900/80 via-violet-900/70 to-purple-900/80 border-2 border-purple-600 rounded-lg shadow-[0_0_15px_rgba(168,85,247,0.6)] backdrop-blur-sm p-6">
          <div className="flex items-center justify-center space-x-3">
            <Package className="w-6 h-6 text-purple-400 drop-shadow" />
            <span className="text-purple-300 font-bold text-lg tracking-wide drop-shadow">
              Items: {player.inventory.length}
            </span>
          </div>
        </div>
        <div className="bg-gradient-to-r from-yellow-900/80 via-amber-900/70 to-yellow-900/80 border-2 border-yellow-600 rounded-lg shadow-[0_0_15px_rgba(234,179,8,0.6)] backdrop-blur-sm p-6">
          <div className="flex items-center justify-center space-x-3">
            <Sparkles className="w-6 h-6 text-yellow-400 drop-shadow animate-pulse" />
            <span className="text-yellow-300 font-bold text-lg tracking-wide drop-shadow">
              Gold: {player.gold}
            </span>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-amber-900/90 via-amber-800/80 to-amber-900/90 border-2 border-amber-700 rounded-lg shadow-[0_0_20px_rgba(218,165,32,0.8)] backdrop-blur-md p-6">
        <h3 className="text-xl font-bold mb-4 text-amber-300 drop-shadow-lg tracking-wider text-center">Currently Equipped</h3>
        <div className="grid grid-cols-4 gap-4">
          {['weapon', 'armor', 'helmet', 'boots', 'gloves', 'ring', 'tool'].map((slot) => {
            const equipped = player.equippedItems[slot as keyof typeof player.equippedItems];
            const Icon = getItemIcon(slot);
            const placeholderText = slot.charAt(0).toUpperCase() + slot.slice(1);

            return (
              <div key={slot} className="text-center">
                <div className="bg-gradient-to-br from-amber-900/60 via-amber-800/50 to-amber-900/60 border-2 border-amber-700/60 rounded-lg h-16 w-16 mx-auto flex items-center justify-center mb-2 shadow-inner">
                  {equipped ? (
                    <Icon className={`w-6 h-6 ${slot === 'weapon' ? 'text-red-400' : slot === 'armor' ? 'text-blue-400' : 'text-purple-400'} drop-shadow`} />
                  ) : (
                    <div className="text-amber-500 text-xs font-semibold">{placeholderText}</div>
                  )}
                </div>
                <div className="text-xs font-semibold text-amber-200 truncate mb-2">
                  {equipped?.name || `No ${placeholderText.toLowerCase()}`}
                </div>
                {equipped && (
                  <button onClick={() => handleUnequipItem(slot)} disabled={state.isLoading} className="bg-gradient-to-r from-red-800 via-red-700 to-red-800 border border-red-600 rounded px-2 py-1 text-xs text-red-200 font-semibold hover:from-red-700 hover:via-red-600 hover:to-red-700 hover:shadow-[0_0_10px_rgba(239,68,68,0.5)] transition-all duration-300 disabled:opacity-50">
                    Unequip
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="bg-gradient-to-br from-amber-900/90 via-amber-800/80 to-amber-900/90 border-2 border-amber-700 rounded-lg shadow-[0_0_20px_rgba(218,165,32,0.8)] backdrop-blur-md p-6">
        <h3 className="text-xl font-bold mb-4 text-amber-300 drop-shadow-lg tracking-wider text-center">Inventory ({player.inventory.length} items)</h3>

        {player.inventory.length === 0 ? (
          <div className="text-center text-amber-400 py-8">
            <Package className="w-12 h-12 mx-auto mb-3 opacity-70 drop-shadow" />
            <p className="font-semibold">Your inventory awaits adventures</p>
          </div>
        ) : (
          <div className="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-7 gap-3">
            {player.inventory.map((item, index) => {
              const ItemIcon = getItemIcon(item.type);

              return (
                <motion.div
                  key={`${item.id}-${index}`}
                  className={`bg-gradient-to-br from-amber-900/60 via-amber-800/50 to-amber-900/60 border-2 border-amber-700/60 rounded-lg p-3 cursor-pointer relative hover:border-amber-500 hover:shadow-[0_0_15px_rgba(218,165,32,0.6)] transition-all duration-300 ${getItemRarityColor(item.rarity || 'common')} ${selectedItem?.id === item.id ? 'ring-2 ring-yellow-400 shadow-[0_0_20px_rgba(255,255,0,0.7)]' : ''}`}
                  whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={() => setSelectedItem(item)}>
                  <div className="flex flex-col items-center">
                    <ItemIcon className="w-6 h-6 mb-1 drop-shadow" />
                    <div className="text-xs text-center font-bold text-amber-200 leading-tight">{item.name}</div>
                    {item.quantity > 1 && (
                      <div className="absolute -top-1 -right-1 bg-red-600 border border-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold shadow-md">
                        {item.quantity}
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>

      <AnimatePresence>
        {selectedItem && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            exit={{ opacity: 0 }} className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50" onClick={() => setSelectedItem(null)}>
            <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }} className="bg-gradient-to-br from-amber-900/95 via-amber-800/90 to-amber-900/95 border-2 border-amber-700 rounded-lg shadow-[0_0_30px_rgba(218,165,32,0.8)] backdrop-blur-md p-8 max-w-md w-full m-4" onClick={(e) => e.stopPropagation()}
              style={{ fontFamily: "'Cinzel', serif" }}>
              <h3 className="text-2xl font-bold mb-6 text-amber-300 drop-shadow-lg tracking-wider text-center">{selectedItem.name}</h3>

              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-amber-300 font-semibold">Type:</span>
                  <span className="capitalize text-amber-200 font-medium">{selectedItem.type}</span>
                </div>

                {selectedItem.description && (
                  <div>
                    <span className="text-amber-300 font-semibold">Description:</span>
                    <div className="text-amber-200 mt-2 leading-relaxed">{selectedItem.description}</div>
                  </div>
                )}

                {selectedItem.value && (
                  <div className="flex justify-between">
                    <span className="text-amber-300 font-semibold">Value:</span>
                    <span className="text-yellow-400 font-bold">{selectedItem.value} gold</span>
                  </div>
                )}

                <div className="flex justify-between">
                  <span className="text-amber-300 font-semibold">Quantity:</span>
                  <span className="text-amber-200 font-medium">{selectedItem.quantity}</span>
                </div>
              </div>

              <div className="flex gap-4 mt-8">
                <button onClick={() => handleUseItem(selectedItem)} className="bg-gradient-to-r from-green-800 via-green-700 to-green-800 border-2 border-green-600 rounded-lg px-6 py-3 text-green-200 font-semibold hover:bg-gradient-to-r hover:from-green-700 hover:via-green-600 hover:to-green-700 hover:shadow-[0_0_15px_rgba(34,197,94,0.6)] transition-all duration-300 flex-1 flex items-center justify-center gap-2">
                  <Play className="w-4 h-4" />
                  Use
                </button>
                <button onClick={() => handleDropItem(selectedItem)} className="bg-gradient-to-r from-red-800 via-red-700 to-red-800 border-2 border-red-600 rounded-lg px-4 py-3 text-red-200 font-semibold hover:bg-gradient-to-r hover:from-red-700 hover:via-red-600 hover:to-red-700 hover:shadow-[0_0_15px_rgba(239,68,68,0.6)] transition-all duration-300 flex items-center justify-center">
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
