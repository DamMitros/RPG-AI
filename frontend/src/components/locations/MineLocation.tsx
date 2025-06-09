'use client';

import React, { useState } from 'react';
import { useGame } from '@/contexts/GameContext';
import { gameApi } from '@/services/gameApi';
import { Mountain, Pickaxe, Gem, Coins, AlertTriangle, Zap } from 'lucide-react';
import { DialogMessage, Player } from '@/types/game';
import DialogInterface from '@/components/DialogInterface';
import { useQuests } from '@/hooks/useQuests';

const MineLocation: React.FC = () => {
  const { state, dispatch } = useGame();
  const { performQuestAction } = useQuests();
  const [selectedAction, setSelectedAction] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [dialogMessages, setDialogMessages] = useState<DialogMessage[]>([]);
  const [isStrangerDialogOpen, setIsStrangerDialogOpen] = useState(false);
  const mineActions = [
    {
      id: 'shallow_mining',
      name: 'Mine Shallow Tunnels',
      icon: Pickaxe,
      description: 'Safe mining in the upper levels of the mine',
      danger: 'low',
      stamina: 10,
    },
    {
      id: 'deep_mining',
      name: 'Deep Mining',
      icon: Mountain,
      description: 'Venture into the dangerous depths for rare materials',
      danger: 'high',
      stamina: 20,
    },
    {
      id: 'gem_hunting',
      name: 'Search for Gems',
      icon: Gem,
      description: 'Look for precious gems and crystals',
      danger: 'medium',
      stamina: 15,
    },
    {
      id: 'abandoned_exploration',
      name: 'Explore Abandoned Shafts',
      icon: Zap,
      description: 'Investigate old mining tunnels for treasures',
      danger: 'high',
      stamina: 25,
    },
  ];

  const handleMiningAction = async (actionId: string) => {
    const action = mineActions.find(a => a.id === actionId);
    if (!action) return;

    if (state.player.mana < action.stamina) {
      const message: DialogMessage = {
        speaker: 'Mining Foreman',
        text: `You're too tired to attempt this mining operation. You need at least ${action.stamina} mana points.`,
      };
      setDialogMessages([message]);
      setIsDialogOpen(true);
      return;
    }

    dispatch({ type: 'SET_LOADING', payload: true });
    setSelectedAction(actionId);

    try {
      const questResponse = await performQuestAction(actionId, 'mine');
      let questMessage = '';
      
      if (questResponse.success && questResponse.message && !questResponse.message.includes('No quest progress')) {
        questMessage = questResponse.message;
      }
      
      const response = await gameApi.performAction('mine', actionId);
      let finalMessage = response.message || `You completed ${actionId} in the mines.`;

      if (questMessage) {
        finalMessage = `${questMessage}\n\n${finalMessage}`;
      }
      
      const message: DialogMessage = {
        speaker: 'Mining Result',
        text: finalMessage,
      };
      setDialogMessages([message]);
      setIsDialogOpen(true);

      if (questResponse.player) {
        dispatch({ type: 'SET_PLAYER', payload: questResponse.player as Player });
      } else if (response.data?.player) {
        dispatch({ type: 'SET_PLAYER', payload: response.data.player as Player });
      }
    } catch (error) {
      console.error('Mining action failed:', error);
      const errorMessage: DialogMessage = {
        speaker: 'System',
        text: 'Something went wrong during your mining expedition.',
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

  const handleMysteriousStranger = async () => {
    try {
      const questResponse = await performQuestAction('talk_mysterious_stranger', 'mine');
      let questMessage = '';
      
      if (questResponse.success && questResponse.message && !questResponse.message.includes('No quest progress')) {
        questMessage = questResponse.message;
      }
      
      const response = await gameApi.performAction('mine', 'talk_mysterious_stranger');

      if (response.success && response.data?.character === 'mysterious_stranger') {
        if (questMessage) {
          const message: DialogMessage = {
            speaker: 'Quest Progress',
            text: questMessage,
          };
          setDialogMessages([message]);
          setIsDialogOpen(true);
          setTimeout(() => {
            setIsDialogOpen(false);
            setIsStrangerDialogOpen(true);
          }, 2000);
        } else {
          setIsStrangerDialogOpen(true);
        }
      } else {
        let finalMessage = response.message || 'You sense a presence in the darkness...';
        if (questMessage) {
          finalMessage = `${questMessage}\n\n${finalMessage}`;
        }
        
        const message: DialogMessage = {
          speaker: 'Mining',
          text: finalMessage,
        };
        setDialogMessages([message]);
        setIsDialogOpen(true);
      }

      if (questResponse.player) {
        dispatch({ type: 'SET_PLAYER', payload: questResponse.player as Player });
      } else if (response.data?.player) {
        dispatch({ type: 'SET_PLAYER', payload: response.data.player as Player });
      }
    } catch (error) {
      console.error('Mysterious stranger interaction failed:', error);
    }
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
      <div className="bg-gradient-to-br from-gray-900/95 via-slate-900/90 to-gray-900/95 border-2 border-slate-700 rounded-lg shadow-[0_0_25px_rgba(71,85,105,0.8)] backdrop-blur-md p-6 text-center">
        <h2 className="text-4xl font-bold text-slate-300 mb-4 drop-shadow-lg tracking-wider">Ironhold Mines</h2>
        <p className="text-slate-200 font-medium leading-relaxed">
          The ancient mines delve deep into the heart of the mountain, where veins of precious
          metals and gems await those brave enough to venture into the darkness. The deeper
          you go, the greater the rewards... and the dangers.
        </p>
      </div>

      <div className="bg-gradient-to-br from-stone-900/90 via-gray-900/80 to-stone-900/90 border-2 border-stone-700/80 rounded-lg shadow-[0_0_20px_rgba(68,64,60,0.7)] backdrop-blur-sm p-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-yellow-600/5 via-amber-600/10 to-yellow-600/5 animate-pulse"></div>
        <div className="relative text-center mb-6">
          <Mountain className="w-20 h-20 text-stone-400 mx-auto mb-4 drop-shadow-lg" />
          <h3 className="text-2xl font-bold text-stone-300 tracking-wider drop-shadow">Mine Entrance</h3>
        </div>
        <p className="relative text-stone-200 text-center leading-relaxed font-medium">
          Wooden support beams frame the entrance to the mine. The air is cool and damp,
          carrying the scent of earth and metal. Torches flicker along the walls, casting
          dancing shadows into the depths below.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-gradient-to-r from-blue-900/80 via-blue-800/70 to-blue-900/80 border-2 border-blue-600 rounded-lg shadow-[0_0_15px_rgba(59,130,246,0.6)] backdrop-blur-sm p-6">
          <div className="flex items-center space-x-3">
            <Zap className="w-6 h-6 text-blue-400 drop-shadow animate-pulse" />
            <span className="text-blue-300 font-bold text-lg tracking-wide drop-shadow">
              Stamina (Mana): {state.player.mana}/{state.player.maxMana}
            </span>
          </div>
        </div>
        <div className="bg-gradient-to-r from-yellow-900/80 via-amber-900/70 to-yellow-900/80 border-2 border-yellow-600 rounded-lg shadow-[0_0_15px_rgba(234,179,8,0.6)] backdrop-blur-sm p-6">
          <div className="flex items-center space-x-3">
            <Coins className="w-6 h-6 text-yellow-400 drop-shadow animate-bounce" />
            <span className="text-yellow-300 font-bold text-lg tracking-wide drop-shadow">
              Gold: {state.player.gold}
            </span>
          </div>
        </div>
      </div>

      {state.player.mana < 20 && (
        <div className="bg-gradient-to-r from-orange-900/80 via-red-900/70 to-orange-900/80 border-2 border-orange-600 rounded-lg shadow-[0_0_15px_rgba(249,115,22,0.7)] backdrop-blur-sm p-6">
          <div className="flex items-center space-x-3 text-orange-300">
            <AlertTriangle className="w-6 h-6 animate-pulse drop-shadow" />
            <span className="font-bold text-lg">Low Stamina:</span>
            <span className="font-medium">Your stamina is running low. Rest to recover before attempting strenuous mining.</span>
          </div>
        </div>
      )}

      <div className="relative">
        <div className="bg-gradient-to-r from-slate-900/30 via-gray-800/20 to-slate-900/30 border border-slate-700/30 rounded-lg p-4 text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-900/10 via-indigo-900/5 to-purple-900/10"></div>
          <p className="relative text-slate-400 text-sm italic">
            As you examine the mine entrance, you notice strange shadows moving between the support beams...
          </p>
          
          <button onClick={handleMysteriousStranger} className="absolute right-2 top-2 w-6 h-6 bg-slate-800/50 hover:bg-slate-700/70 border border-slate-600/30 hover:border-slate-500/50 rounded-full transition-all duration-300 opacity-60 hover:opacity-100 group" title="Something moves in the shadows...">
            <div className="w-2 h-2 bg-purple-400/40 group-hover:bg-purple-300/60 rounded-full mx-auto mt-1 animate-pulse"></div>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {mineActions.map((action) => {
          const IconComponent = action.icon;
          const canPerform = state.player.mana >= action.stamina;
          const isHealthTooLow = action.danger === 'high' && state.player.health < state.player.maxHealth * 0.4;
          const isDisabled = !canPerform || isHealthTooLow || state.isLoading || selectedAction !== null;
          
          return (
            <button key={action.id} onClick={() => handleMiningAction(action.id)}
              disabled={isDisabled} className={`p-6 rounded-lg border-2 transition-all duration-300 ${isDisabled ? 'bg-gradient-to-br from-gray-800/60 via-gray-700/50 to-gray-800/60 border-gray-600 opacity-50 cursor-not-allowed text-gray-400' : `${getDangerBorder(action.danger)} bg-gradient-to-br from-stone-900/80 via-gray-900/70 to-stone-900/80 hover:shadow-[0_0_20px_rgba(68,64,60,0.8)] text-stone-200`}`}>
              <div className="flex flex-col items-center text-center space-y-3">
                <IconComponent className={`w-10 h-10 drop-shadow ${isDisabled ? 'text-gray-500' : 'text-stone-400'}`} />
                <h3 className={`font-bold text-lg tracking-wide ${isDisabled ? 'text-gray-400' : 'text-stone-200'}`}>{action.name}</h3>
                <p className={`text-sm leading-relaxed ${isDisabled ? 'text-gray-500' : 'text-stone-300'}`}>{action.description}</p>
                <div className="flex items-center space-x-6">
                  <div className="flex items-center space-x-2">
                    <Zap className="w-5 h-5 text-blue-400 drop-shadow" />
                    <span className="text-blue-400 font-semibold">{action.stamina} stamina</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className={`w-5 h-5 ${getDangerColor(action.danger)} drop-shadow`} />
                    <span className={`text-sm capitalize font-semibold ${getDangerColor(action.danger)}`}>
                      {action.danger} risk
                    </span>
                  </div>
                </div>
                {!canPerform && (
                  <div className="text-xs text-red-400 font-medium bg-red-900/30 px-2 py-1 rounded">Insufficient stamina</div>
                )}
                {isHealthTooLow && (
                  <div className="text-xs text-red-400 font-medium bg-red-900/30 px-2 py-1 rounded">Health too low for dangerous mining</div>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {selectedAction && (
        <div className="text-center py-8">
          <div className="animate-spin w-8 h-8 border-2 border-stone-400 border-t-transparent rounded-full mx-auto mb-2"></div>
          <p className="text-stone-300">Mining in progress...</p>
        </div>
      )}

      {isDialogOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 border border-stone-600/50 rounded-lg p-6 max-w-md w-full max-h-96 overflow-y-auto">
            <div className="space-y-4">
              {dialogMessages.map((message, index) => (
                <div key={index} className="border-b border-gray-700/50 pb-3 last:border-b-0">
                  <h4 className="font-semibold text-stone-300 mb-2">{message.speaker}:</h4>
                  <p className="text-gray-300">{message.text}</p>
                </div>
              ))}
            </div>
            <div className="flex justify-end mt-6">
              <button onClick={closeDialog} className="px-4 py-2 bg-stone-600 hover:bg-stone-500 text-white rounded-lg transition-colors">Continue</button>
            </div>
          </div>
        </div>
      )}

      <DialogInterface
        character="mysterious_stranger"
        characterName="Mysterious Stranger"
        isOpen={isStrangerDialogOpen}
        onClose={() => setIsStrangerDialogOpen(false)}
      />
    </div>
  );
};

export default MineLocation;
