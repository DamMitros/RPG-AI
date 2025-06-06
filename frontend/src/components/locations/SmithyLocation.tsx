'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useGame } from '@/contexts/GameContext';
import { gameApi } from '@/services/gameApi';
import { Hammer, Sword, Shield, Wrench, Coins, Flame, MessageCircle } from 'lucide-react';
import { InventoryItem, Player, CraftingRecipe, SmithyRecipesResponse } from '@/types/game';
import DialogInterface from '@/components/DialogInterface';

const SmithyLocation: React.FC = () => {
  const { state, dispatch } = useGame();
  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [dialogMessage, setDialogMessage] = useState('');
  const [isBlacksmithDialogOpen, setIsBlacksmithDialogOpen] = useState(false);
  const [recipes, setRecipes] = useState<CraftingRecipe[]>([]);
  const [isLoadingRecipes, setIsLoadingRecipes] = useState(false);
  const loadRecipes = useCallback(async () => {
    if (isLoadingRecipes || recipes.length > 0) return; 
    
    setIsLoadingRecipes(true);
    try {
      const response = await gameApi.getSmithyRecipes() as SmithyRecipesResponse;
      if (response.success) {
        setRecipes(response.recipes);
      } else {
        setDialogMessage(response.message || 'Failed to load recipes');
        setIsDialogOpen(true);
      }
    } catch (error) {
      console.error('Error loading recipes:', error);
      setDialogMessage('Error loading recipes. Please try again.');
      setIsDialogOpen(true);
    } finally {
      setIsLoadingRecipes(false);
    }
  }, [isLoadingRecipes, recipes.length]);

  useEffect(() => {
    if (selectedService === 'craft_weapon' || selectedService === 'craft_armor') {
      loadRecipes();
    }
  }, [selectedService, loadRecipes]);

  const smithyServices = [
    {
      id: 'talk_blacksmith',
      name: 'Talk to Blacksmith',
      icon: MessageCircle,
      description: 'Speak with Anja, the village blacksmith',
      baseCost: 0,
    },
    {
      id: 'repair',
      name: 'Repair Equipment',
      icon: Wrench,
      description: 'Repair damaged weapons and armor',
      baseCost: 20,
    },
    {
      id: 'upgrade',
      name: 'Upgrade Equipment',
      icon: Hammer,
      description: 'Enhance your weapons and armor',
      baseCost: 50,
    },
    {
      id: 'craft_weapon',
      name: 'Craft Weapon',
      icon: Sword,
      description: 'Create new weapons from materials',
      baseCost: 100,
    },
    {
      id: 'craft_armor',
      name: 'Craft Armor',
      icon: Shield,
      description: 'Create new armor from materials',
      baseCost: 80,
    },
  ];

  const getPlayerEquipment = () => {
    return state.player.inventory.filter(item => 
      item.type === 'weapon' || item.type === 'armor'
    );
  };

  const handleServiceSelect = (serviceId: string) => {
    if (serviceId === 'talk_blacksmith') {
      setIsBlacksmithDialogOpen(true);
      return;
    }
    
    setSelectedService(serviceId);
    
    if (serviceId === 'repair' || serviceId === 'upgrade') {
      const equipment = getPlayerEquipment();
      if (equipment.length === 0) {
        setDialogMessage('You don\'t have any equipment that can be repaired or upgraded.');
        setIsDialogOpen(true);
        return;
      }
    }
  };

  const handleRepairUpgrade = async (item: InventoryItem, serviceType: 'repair' | 'upgrade') => {
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      const response = await gameApi.performAction('smithy', serviceType, {
        itemId: item.id,
        itemName: item.name
      });
      
      setDialogMessage(response.message || `${serviceType} completed successfully!`);
      setIsDialogOpen(true);
      setSelectedService(null);

      if (response.data?.player) {
        dispatch({ type: 'SET_PLAYER', payload: response.data.player as Player });
      }
    } catch (error) {
      console.error('Smithy service failed:', error);
      setDialogMessage('Something went wrong. Please try again.');
      setIsDialogOpen(true);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const handleCraft = async (recipe: CraftingRecipe) => {
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      const response = await gameApi.performAction('smithy', 'craft', {
        itemId: recipe.id,
        itemName: recipe.name,
        itemType: recipe.type
      });
      
      setDialogMessage(response.message || `The blacksmith has crafted a ${recipe.name} for you!`);
      setIsDialogOpen(true);
      setSelectedService(null);

      if (response.data?.player) {
        dispatch({ type: 'SET_PLAYER', payload: response.data.player as Player });
      }

      setRecipes([]);
    } catch (error) {
      console.error('Crafting failed:', error);
      setDialogMessage('Something went wrong. Please try again.');
      setIsDialogOpen(true);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const closeDialog = () => {
    setIsDialogOpen(false);
    setDialogMessage('');
  };

  return (
    <div className="p-6 space-y-6 min-h-screen" style={{ fontFamily: "'Cinzel', serif" }}>
      <div className="bg-gradient-to-br from-red-900/90 via-orange-900/80 to-red-900/90 border-2 border-red-700 rounded-lg shadow-[0_0_25px_rgba(239,68,68,0.8)] backdrop-blur-md p-6 text-center">
        <h2 className="text-4xl font-bold text-red-300 mb-4 drop-shadow-lg tracking-wider">The Forge</h2>
        <p className="text-orange-200 font-medium leading-relaxed">
          The rhythmic hammering echoes through the smithy as the master blacksmith works his craft.
          Sparks fly from the forge as metal is shaped into instruments of war and protection.
        </p>
      </div>

      <div className="bg-gradient-to-br from-red-900/80 via-orange-900/70 to-red-900/80 border-2 border-red-700/80 rounded-lg shadow-[0_0_20px_rgba(234,88,12,0.7)] backdrop-blur-sm p-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-orange-600/10 via-red-600/20 to-orange-600/10 animate-pulse"></div>
        <div className="relative text-center mb-6">
          <Flame className="w-20 h-20 text-orange-400 mx-auto mb-4 drop-shadow-lg animate-pulse" />
          <h3 className="text-2xl font-bold text-orange-300 tracking-wider drop-shadow">Master Blacksmith&apos;s Forge</h3>
        </div>
        <p className="relative text-orange-200 text-center leading-relaxed font-medium">
          The forge burns bright with magical flames. Tools of the trade hang on the walls,
          and the sound of hammer on anvil fills the air. The blacksmith greets you with soot-covered hands.
        </p>
      </div>

      <div className="bg-gradient-to-r from-yellow-900/80 via-amber-900/70 to-yellow-900/80 border-2 border-yellow-600 rounded-lg shadow-[0_0_15px_rgba(234,179,8,0.7)] backdrop-blur-sm p-6">
        <div className="flex items-center justify-center space-x-3">
          <Coins className="w-8 h-8 text-yellow-400 drop-shadow animate-bounce" />
          <span className="text-yellow-300 font-bold text-xl tracking-wide drop-shadow">
            Your Gold: {state.player.gold}
          </span>
        </div>
      </div>

      {!selectedService && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {smithyServices.map((service) => {
            const IconComponent = service.icon;
            const canAfford = service.baseCost === 0 || state.player.gold >= service.baseCost;
            
            return (
              <button key={service.id} onClick={() => handleServiceSelect(service.id)}
                disabled={state.isLoading || !canAfford} className={`p-6 rounded-lg border-2 transition-all duration-300 ${canAfford ? 'bg-gradient-to-br from-red-900/80 via-orange-900/70 to-red-900/80 border-red-600 hover:border-orange-500 hover:shadow-[0_0_20px_rgba(249,115,22,0.8)] text-orange-200' : 'bg-gradient-to-br from-gray-800/60 via-gray-700/50 to-gray-800/60 border-gray-600 opacity-50 cursor-not-allowed text-gray-400'}`}>
                <div className="flex flex-col items-center text-center space-y-3">
                  <IconComponent className={`w-10 h-10 drop-shadow ${canAfford ? 'text-orange-400' : 'text-gray-500'}`} />
                  <h3 className={`font-bold text-lg tracking-wide ${canAfford ? 'text-orange-200' : 'text-gray-400'}`}>
                    {service.name}
                  </h3>
                  <p className={`text-sm leading-relaxed ${canAfford ? 'text-orange-300' : 'text-gray-500'}`}>
                    {service.description}
                  </p>
                  {service.baseCost > 0 && (
                    <div className="flex items-center space-x-2">
                      <Coins className="w-5 h-5 text-yellow-400 drop-shadow" />
                      <span className="text-yellow-400 font-bold">from {service.baseCost}</span>
                    </div>
                  )}
                  {service.baseCost === 0 && (
                    <div className="flex items-center space-x-2">
                      <span className="text-green-400 font-bold">Free</span>
                    </div>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      )}

      {(selectedService === 'repair' || selectedService === 'upgrade') && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-red-200">
              Select Equipment to {selectedService === 'repair' ? 'Repair' : 'Upgrade'}
            </h3>
            <button onClick={() => setSelectedService(null)} className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg transition-colors">Back</button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {getPlayerEquipment().map((item) => (
              <button
                key={`${item.id}-${item.name}`}
                onClick={() => handleRepairUpgrade(item, selectedService as 'repair' | 'upgrade')}
                className="p-4 rounded-lg border-2 border-red-600/50 bg-gradient-to-b from-red-800/20 to-orange-800/20 hover:border-red-400 hover:shadow-lg transition-all duration-200">
                <div className="flex flex-col items-center text-center space-y-2">
                  {item.type === 'weapon' ? (
                    <Sword className="w-6 h-6 text-red-400" />
                  ) : (
                    <Shield className="w-6 h-6 text-red-400" />
                  )}
                  <h4 className="font-semibold text-red-200">{item.name}</h4>
                  <div className="flex items-center space-x-1">
                    <Coins className="w-4 h-4 text-yellow-400" />
                    <span className="text-yellow-400 text-sm">
                      {smithyServices.find(s => s.id === selectedService)?.baseCost}
                    </span>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {(selectedService === 'craft_weapon' || selectedService === 'craft_armor') && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-red-200">
              {selectedService === 'craft_weapon' ? 'Craft Weapons' : 'Craft Armor'}
            </h3>
            <button onClick={() => setSelectedService(null)} className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg transition-colors">Back</button>
          </div>
          
          {isLoadingRecipes && (
            <div className="text-center py-8">
              <div className="animate-spin w-8 h-8 border-2 border-red-400 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-orange-200">Loading recipes...</p>
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recipes
              .filter(recipe => 
                selectedService === 'craft_weapon' 
                  ? recipe.type === 'weapon' || recipe.type === 'tool'
                  : recipe.type === 'armor')
              .map((recipe) => (
                <div key={recipe.id} className="p-4 rounded-lg border-2 border-red-600/50 bg-gradient-to-b from-red-800/20 to-orange-800/20">
                  <div className="text-center space-y-2">
                    {recipe.type === 'weapon' || recipe.type === 'tool' ? (
                      <Sword className="w-8 h-8 text-red-400 mx-auto" />
                    ) : (
                      <Shield className="w-8 h-8 text-red-400 mx-auto" />
                    )}
                    <h4 className="font-semibold text-red-200">{recipe.name}</h4>
                    <p className="text-sm text-gray-300">{recipe.description}</p>

                    {recipe.result.stats && (
                      <div className="text-xs text-green-400">
                        {Object.entries(recipe.result.stats).map(([stat, value]) => (
                          <span key={stat} className="mr-2">
                            {typeof value === 'number' && value > 0 ? '+' : ''}{value} {stat}
                          </span>
                        ))}
                      </div>
                    )}

                    {recipe.result.damage && (
                      <div className="text-xs text-blue-400">Damage: {recipe.result.damage}</div>
                    )}
                    {recipe.result.armor && (
                      <div className="text-xs text-blue-400">Armor: {recipe.result.armor}</div>
                    )}
                    {recipe.result.mining_bonus && (
                      <div className="text-xs text-blue-400">Mining Bonus: +{recipe.result.mining_bonus}</div>
                    )}

                    <div className="text-xs text-gray-400">
                      <div className="font-semibold mb-1">Materials needed:</div>
                      {recipe.materials.map((material, index) => (
                        <div key={index}>
                          {material.quantity}x {material.name}
                        </div>
                      ))}
                    </div>

                    {recipe.level_required > 1 && (
                      <div className="text-xs text-purple-400">Level {recipe.level_required} required</div>
                    )}

                    <div className="text-xs text-yellow-300">Time: {recipe.crafting_time}</div>

                    <div className="flex items-center justify-center space-x-1">
                      <Coins className="w-4 h-4 text-yellow-400" />
                      <span className="text-yellow-400">{recipe.cost} gold</span>
                    </div>

                    <button onClick={() => handleCraft(recipe)} disabled={!recipe.can_craft || state.isLoading}
                      className={`w-full mt-2 px-4 py-2 rounded-lg transition-colors ${recipe.can_craft && !state.isLoading ? 'bg-red-600 hover:bg-red-500 text-white' : 'bg-gray-600 cursor-not-allowed text-gray-300'}`} title={recipe.can_craft ? 'Click to craft' : recipe.craft_message}>
                      {state.isLoading ? 'Crafting...' : 'Craft'}
                    </button>

                    {!recipe.can_craft && (
                      <div className="text-xs text-red-400 mt-1">
                        {recipe.craft_message}
                      </div>
                    )}
                  </div>
                </div>
              ))}
          </div>
          
          {recipes.length === 0 && !isLoadingRecipes && (
            <div className="text-center py-8 text-gray-400">
              No recipes available for {selectedService === 'craft_weapon' ? 'weapons' : 'armor'}.
            </div>
          )}
        </div>
      )}

      {isDialogOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 border border-red-600/50 rounded-lg p-6 max-w-md w-full">
            <div className="text-center space-y-4">
              <Hammer className="w-12 h-12 text-red-400 mx-auto" />
              <h4 className="font-semibold text-red-300 text-lg">Blacksmith</h4>
              <p className="text-gray-300">{dialogMessage}</p>
            </div>
            <div className="flex justify-end mt-6">
              <button onClick={closeDialog} className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors">Close</button>
            </div>
          </div>
        </div>
      )}

      <DialogInterface
        character="blacksmith"
        characterName="Anja Ironbite"
        isOpen={isBlacksmithDialogOpen}
        onClose={() => setIsBlacksmithDialogOpen(false)}
      />
    </div>
  );
};

export default SmithyLocation;