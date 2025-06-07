'use client';

import React, { useState, useEffect } from 'react';
import { useGame } from '@/contexts/GameContext';
import { useQuests } from '@/hooks/useQuests';
import { gameApi } from '@/services/gameApi';
import { Beer, Users, MessageCircle, Coins } from 'lucide-react';
import { DialogMessage, QuestAction } from '@/types/game';
import DialogInterface from '@/components/DialogInterface';

const TavernLocation: React.FC = () => {
  const { state, dispatch } = useGame();
  const { getQuestActionsForLocation, performQuestAction } = useQuests();
  const [dialogMessages, setDialogMessages] = useState<DialogMessage[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [currentCharacter, setCurrentCharacter] = useState('');
  const [currentCharacterName, setCurrentCharacterName] = useState('');
  const [questActions, setQuestActions] = useState<QuestAction[]>([]);

  const tavernActions = [
    {
      id: 'rest',
      name: 'Rest (10 gold)',
      icon: Beer,
      description: 'Restore health and mana',
      cost: 10,
    },
    {
      id: 'talk_innkeeper',
      name: 'Talk to Innkeeper',
      icon: MessageCircle,
      description: 'Get local information and rumors',
    },
    {
      id: 'talk_regular',
      name: 'Talk to Regular',
      icon: Users,
      description: 'Chat with local tavern regulars',
    },
  ];

  useEffect(() => {
    const loadQuestActions = async () => {
      try {
        const actions = await getQuestActionsForLocation('tavern');
        setQuestActions(actions);
      } catch (error) {
        console.error('Failed to load quest actions for tavern:', error);
      }
    };

    loadQuestActions();
  }, [getQuestActionsForLocation]);

  const handleAction = async (actionId: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      if (actionId === 'rest') {
        if (state.player.gold >= 10) {
          const response = await gameApi.performAction('tavern', 'rest', { cost: 10 });
          
          if (response.success) {
            if (response.data) {
              dispatch({ type: 'UPDATE_PLAYER_GOLD', payload: response.data.gold as number });
              dispatch({ type: 'UPDATE_PLAYER_HEALTH', payload: response.data.health as number });
              dispatch({ type: 'UPDATE_PLAYER_MANA', payload: response.data.mana as number });
            }
            
            const message: DialogMessage = {
              speaker: 'Innkeeper',
              text: response.message,
            };
            setDialogMessages([message]);
            setIsDialogOpen(true);
          } else {
            const message: DialogMessage = {
              speaker: 'Innkeeper',
              text: response.message,
            };
            setDialogMessages([message]);
            setIsDialogOpen(true);
          }
        } else {
          const message: DialogMessage = {
            speaker: 'Innkeeper',
            text: "Sorry, you don't have enough gold for a room. A night's rest costs 10 gold.",
          };
          setDialogMessages([message]);
          setIsDialogOpen(true);
        }
      } else if (actionId === 'talk_innkeeper') {
        setCurrentCharacter('tavern_keeper');
        setCurrentCharacterName('Innkeeper');
        setIsDialogOpen(true);
      } else if (actionId === 'talk_regular') {
        setCurrentCharacter('tavern_regular');
        setCurrentCharacterName('Tavern Regular');
        setIsDialogOpen(true);
      }

      try {
        const questResponse = await performQuestAction(actionId, 'tavern');
        
        if (questResponse.success && questResponse.message) {
          const questMessage: DialogMessage = {
            speaker: 'Quest Progress',
            text: questResponse.message,
          };
          setDialogMessages(prev => [...prev, questMessage]);
        }
      } catch {
        console.log('No quest action triggered for:', actionId);
      }
    } catch (error) {
      console.error('Action failed:', error);
      const errorMessage: DialogMessage = {
        speaker: 'System',
        text: 'Something went wrong. Please try again.',
      };
      setDialogMessages([errorMessage]);
      setIsDialogOpen(true);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const closeDialog = () => {
    setIsDialogOpen(false);
    setDialogMessages([]);
  };

  return (
    <div className="p-6 space-y-6 min-h-screen" style={{ fontFamily: "'Cinzel', serif" }}>
      <div className="bg-gradient-to-br from-amber-900/90 via-amber-800/80 to-amber-900/90 border-2 border-amber-700 rounded-lg shadow-[0_0_20px_rgba(218,165,32,0.8)] backdrop-blur-md p-6 text-center">
        <h2 className="text-4xl font-bold text-amber-300 mb-4 drop-shadow-lg tracking-wider">The Rusty Dragon Tavern</h2>
        <p className="text-amber-200 font-medium leading-relaxed">
          A warm, welcoming tavern filled with the aroma of hearty meals and the sound of laughter.
          Adventurers and locals gather here to share tales and rest their weary bones.
        </p>
      </div>

      <div className="bg-gradient-to-br from-amber-900/70 via-red-900/60 to-amber-900/70 border-2 border-amber-700/80 rounded-lg shadow-[0_0_15px_rgba(218,165,32,0.6)] backdrop-blur-sm p-8">
        <div className="text-center mb-6">
          <Beer className="w-16 h-16 text-amber-400 mx-auto mb-4 drop-shadow-lg" />
          <h3 className="text-2xl font-bold text-amber-300 tracking-wider drop-shadow">Tavern Interior</h3>
        </div>
        <p className="text-amber-200 text-center leading-relaxed font-medium">
          The tavern is bustling with activity. A fire crackles in the hearth, casting dancing shadows
          on the wooden walls. The innkeeper polishes mugs behind the bar while patrons share stories
          over tankards of ale.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {tavernActions.map((action) => {
          const IconComponent = action.icon;
          const canAfford = action.cost ? state.player.gold >= action.cost : true;
          
          return (
            <button
              key={action.id} className={`p-6 rounded-lg border-2 transition-all duration-300 ${canAfford ? 'bg-gradient-to-br from-amber-900/80 via-amber-800/70 to-amber-900/80 border-amber-700 hover:border-amber-500 hover:shadow-[0_0_15px_rgba(218,165,32,0.6)] text-amber-300' : 'bg-gradient-to-br from-gray-800/60 via-gray-700/50 to-gray-800/60 border-gray-600 opacity-50 cursor-not-allowed text-gray-400'}`}
              onClick={() => handleAction(action.id)}
              disabled={state.isLoading || !canAfford}>
              <div className="flex flex-col items-center text-center space-y-3">
                <IconComponent className={`w-10 h-10 drop-shadow ${canAfford ? 'text-amber-400' : 'text-gray-500'}`} />
                <h3 className={`font-bold text-lg tracking-wide ${canAfford ? 'text-amber-300' : 'text-gray-400'}`}>{action.name}</h3>
                <p className={`text-sm leading-relaxed ${canAfford ? 'text-amber-200' : 'text-gray-500'}`}>{action.description}</p>
                {action.cost && (
                  <div className="flex items-center space-x-2 mt-2">
                    <Coins className="w-5 h-5 text-yellow-400 drop-shadow" />
                    <span className="text-yellow-400 font-bold">{action.cost}</span>
                  </div>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {isDialogOpen && dialogMessages.length > 0 && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-gradient-to-br from-amber-900/95 via-amber-800/90 to-amber-900/95 border-2 border-amber-700 rounded-lg shadow-[0_0_30px_rgba(218,165,32,0.8)] backdrop-blur-md p-8 max-w-md w-full">
            <div className="space-y-6">
              {dialogMessages.map((message, index) => (
                <div key={index} className="border-b border-amber-700/50 pb-4 last:border-b-0">
                  <h4 className="font-bold text-amber-300 mb-3 text-lg tracking-wide drop-shadow">{message.speaker}:</h4>
                  <p className="text-amber-200 leading-relaxed font-medium">{message.text}</p>
                </div>
              ))}
            </div>
            <div className="flex justify-end mt-8">
              <button onClick={closeDialog} className="px-6 py-3 bg-gradient-to-r from-amber-700 via-amber-600 to-amber-700 border-2 border-amber-500 hover:bg-gradient-to-r hover:from-amber-600 hover:via-amber-500 hover:to-amber-600 hover:shadow-[0_0_15px_rgba(245,158,11,0.6)] text-amber-100 font-bold rounded-lg transition-all duration-300 tracking-wide">Close</button>
            </div>
          </div>
        </div>
      )}

      <DialogInterface
        character={currentCharacter}
        characterName={currentCharacterName}
        isOpen={isDialogOpen && currentCharacter !== ''}
        questActions={questActions} 
        onClose={() => {
          setIsDialogOpen(false);
          setCurrentCharacter('');
          setCurrentCharacterName('');
        }}
      />
    </div>
  );
};

export default TavernLocation;
