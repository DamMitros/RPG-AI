'use client';

import React, { useState } from 'react';
import { useGame } from '@/contexts/GameContext';
import { gameApi } from '@/services/gameApi';
import { Trees, Search, Swords, Gem, Package, AlertTriangle } from 'lucide-react';
import { DialogMessage, Player } from '@/types/game';
import { useQuests } from '@/hooks/useQuests';

const ForestLocation: React.FC = () => {
  const { state, dispatch } = useGame();
  const { performQuestAction } = useQuests();
  const [selectedAction, setSelectedAction] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [dialogMessages, setDialogMessages] = useState<DialogMessage[]>([]);
  const forestActions = [
    {
      id: 'explore',
      id_quest: 'explore_forest',
      name: 'Explore Deeper',
      icon: Search,
      description: 'Search for resources and hidden treasures',
      danger: 'low',
    },
    {
      id: 'hunt',
      id_quest: 'hunt_creatures',
      name: 'Hunt Creatures',
      icon: Swords,
      description: 'Battle forest creatures for experience and loot',
      danger: 'medium',
    },
    {
      id: 'gather',
      id_quest: 'gather_materials',
      name: 'Gather Materials',
      icon: Package,
      description: 'Collect herbs, wood, and other crafting materials',
      danger: 'low',
    },
    {
      id: 'search_treasure',
      id_quest: 'search_treasure',
      name: 'Search for Treasure',
      icon: Gem,
      description: 'Look for hidden chests and valuable items',
      danger: 'high',
    },
  ];

  const handleAction = async (action: string) => {
    try {
      const response = await performQuestAction(action, 'forest');
      if (response.message && !response.message.includes('No quest progress')) {
        dispatch({
          type: 'ADD_DIALOG_MESSAGE',
          payload: {
            speaker: 'Quest Progress',
            text: response.message,
          },
        });
      }
    } catch (error) {
      console.error('Failed to perform action:', error);
    }
  };

  const handleForestAction = async (actionId: string, questId: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    setSelectedAction(actionId);

    try {
      const response = await gameApi.performAction('forest', actionId);      
      const message: DialogMessage = {
        speaker: 'Forest',
        text: response.message || `You performed ${actionId} in the forest.`,
      };
      setDialogMessages([message]);
      setIsDialogOpen(true);
      handleAction(questId);
      if (response.data?.player) {
        dispatch({ type: 'SET_PLAYER', payload: response.data.player as Player });
      } else {
        console.warn('ForestLocation: No player data in response for action:', actionId);
      }
    } catch (error) {
      console.error('Forest action failed:', error);
      const errorMessage: DialogMessage = {
        speaker: 'System',
        text: 'Something went wrong during your forest adventure.',
      };
      setDialogMessages([errorMessage]);
      setIsDialogOpen(true);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
      setSelectedAction(null);
    }
  };

  const closeDialog = () => {
    setIsDialogOpen(false);
    setDialogMessages([]);
  };

  const getDangerColor = (danger: string) => {
    switch (danger) {
      case 'low':
        return 'text-green-400';
      case 'medium':
        return 'text-yellow-400';
      case 'high':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getDangerBorder = (danger: string) => {
    switch (danger) {
      case 'low':
        return 'border-green-600/50 hover:border-green-400';
      case 'medium':
        return 'border-yellow-600/50 hover:border-yellow-400';
      case 'high':
        return 'border-red-600/50 hover:border-red-400';
      default:
        return 'border-gray-600/50 hover:border-gray-400';
    }
  };

  return (
    <div className="p-6 space-y-6 min-h-screen" style={{ fontFamily: "'Cinzel', serif" }}>
      <div className="bg-gradient-to-br from-green-900/90 via-emerald-900/80 to-green-900/90 border-2 border-green-700 rounded-lg shadow-[0_0_25px_rgba(34,197,94,0.8)] backdrop-blur-md p-6 text-center">
        <h2 className="text-4xl font-bold text-green-300 mb-4 drop-shadow-lg tracking-wider">Whispering Woods</h2>
        <p className="text-emerald-200 font-medium leading-relaxed">
          Ancient trees stretch towards the sky, their branches creating a canopy that filters
          the sunlight into dappled patterns. The forest is alive with sounds of wildlife
          and holds many secrets for the brave explorer.
        </p>
      </div>

      <div className="bg-gradient-to-br from-green-900/80 via-emerald-900/70 to-green-900/80 border-2 border-green-700/80 rounded-lg shadow-[0_0_20px_rgba(16,185,129,0.7)] backdrop-blur-sm p-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-green-600/10 via-emerald-600/20 to-green-600/10 animate-pulse"></div>
        <div className="relative text-center mb-6">
          <Trees className="w-20 h-20 text-emerald-400 mx-auto mb-4 drop-shadow-lg" />
          <h3 className="text-2xl font-bold text-emerald-300 tracking-wider drop-shadow">Deep Forest</h3>
        </div>
        <p className="relative text-emerald-200 text-center leading-relaxed font-medium">
          Moss-covered rocks and fallen logs create natural pathways through the underbrush.
          You can hear the distant howl of wolves and the rustling of creatures in the shadows.
          Adventure and danger await those who venture deeper.
        </p>
      </div>

      {state.player.health < state.player.maxHealth * 0.3 && (
        <div className="bg-gradient-to-r from-red-900/80 via-red-800/70 to-red-900/80 border-2 border-red-600 rounded-lg shadow-[0_0_15px_rgba(239,68,68,0.7)] backdrop-blur-sm p-6">
          <div className="flex items-center space-x-3 text-red-300">
            <AlertTriangle className="w-6 h-6 animate-pulse drop-shadow" />
            <span className="font-bold text-lg">Warning:</span>
            <span className="font-medium">Your health is low. Consider resting before engaging in dangerous activities.</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {forestActions.map((action) => {
          const IconComponent = action.icon;
          const isHealthTooLow = action.danger === 'high' && state.player.health < state.player.maxHealth * 0.5;
          
          return (
            <button key={action.id} onClick={() => handleForestAction(action.id, action.id_quest)}
              disabled={state.isLoading || selectedAction !== null || isHealthTooLow}
              className={`p-6 rounded-lg border-2 transition-all duration-300 ${isHealthTooLow ? 'bg-gradient-to-br from-gray-800/60 via-gray-700/50 to-gray-800/60 border-gray-600 opacity-50 cursor-not-allowed text-gray-400' : `${getDangerBorder(action.danger)} bg-gradient-to-br from-green-900/80 via-emerald-900/70 to-green-900/80 hover:shadow-[0_0_20px_rgba(16,185,129,0.7)] text-green-200`}`}>
              <div className="flex flex-col items-center text-center space-y-3">
                <IconComponent className={`w-10 h-10 drop-shadow ${isHealthTooLow ? 'text-gray-500' : 'text-emerald-400'}`} />
                <h3 className={`font-bold text-lg tracking-wide ${isHealthTooLow ? 'text-gray-400' : 'text-emerald-200'}`}>{action.name}</h3>
                <p className={`text-sm leading-relaxed ${isHealthTooLow ? 'text-gray-500' : 'text-emerald-300'}`}>{action.description}</p>
                <div className="flex items-center space-x-2">
                  <AlertTriangle className={`w-5 h-5 ${getDangerColor(action.danger)} drop-shadow`} />
                  <span className={`text-sm capitalize font-semibold ${getDangerColor(action.danger)}`}>
                    {action.danger} Risk
                  </span>
                </div>
                {isHealthTooLow && (
                  <div className="text-xs text-red-400 font-medium bg-red-900/30 px-2 py-1 rounded">
                    Health too low for this action
                  </div>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {selectedAction && (
        <div className="text-center py-8">
          <div className="animate-spin w-8 h-8 border-2 border-green-400 border-t-transparent rounded-full mx-auto mb-2"></div>
          <p className="text-green-300">
            {selectedAction === 'hunt' ? 'Engaging in combat...' : 'Exploring the forest...'}
          </p>
        </div>
      )}

      {isDialogOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 border border-green-600/50 rounded-lg p-6 max-w-md w-full">
            <div className="space-y-4">
              {dialogMessages.map((message, index) => (
                <div key={index} className="border-b border-gray-700/50 pb-3 last:border-b-0">
                  <h4 className="font-semibold text-green-300 mb-2">{message.speaker}:</h4>
                  <p className="text-gray-300">{message.text}</p>
                </div>
              ))}
            </div>
            <div className="flex justify-end mt-6">
              <button onClick={closeDialog} className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg transition-colors">Continue</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ForestLocation;
