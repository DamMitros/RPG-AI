'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useGame } from '@/contexts/GameContext';
import { gameApi } from '@/services/gameApi';
import { DialogMessage, QuestAction } from '@/types/game';
import { Send, MessageCircle, X } from 'lucide-react';

interface DialogInterfaceProps {
  character: string;
  characterName: string;
  isOpen: boolean;
  onClose: () => void;
  questActions?: QuestAction[]; 
}

export default function DialogInterface({ character, characterName, isOpen, onClose, questActions = [] }: DialogInterfaceProps) {
  const { state, dispatch } = useGame();
  const [messages, setMessages] = useState<DialogMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `${character}_${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadDialogHistory = useCallback(async () => {
    try {
      const history = await gameApi.getDialogHistory(sessionId);
      setMessages(history);
    } catch (error) {
      console.error('Failed to load dialog history:', error);
      setMessages([{
        speaker: characterName,
        text: getGreeting(character)
      }]);
    }
  }, [sessionId, characterName, character]);

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    if (isOpen) {
      loadDialogHistory();
    }
  }, [isOpen, loadDialogHistory]);

  const getGreeting = (char: string): string => {
    const greetings = {
      tavern_keeper: "Welcome to the Rusty Dragon Tavern! What can I do for you, traveler?",
      innkeeper: "Greetings! Looking for a room or perhaps some information?",
      merchant: "Welcome to my shop! I have the finest goods in town.",
      blacksmith: "Ah, another adventurer! Need weapons or armor?",
      guard: "State your business, citizen.",
      mysterious_stranger: "You seek answers... but are you prepared for what you might find?"
    };
    return greetings[char as keyof typeof greetings] || "Hello there, adventurer.";
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: DialogMessage = {
      speaker: 'Player',
      text: inputValue
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const context = {
        character,
        player_stats: {
          level: state.player.level,
          gold: state.player.gold,
          health: state.player.health,
          location: state.currentLocation
        },
        available_quest_actions: questActions 
      };

      const response = await gameApi.sendMessage(sessionId, inputValue, context);
      
      const npcMessage: DialogMessage = {
        speaker: response.speaker || characterName,
        text: response.text
      };

      setMessages(prev => [...prev, npcMessage]);

      dispatch({ 
        type: 'ADD_DIALOG_MESSAGE', 
        payload: { speaker: userMessage.speaker, text: userMessage.text }
      });
      dispatch({ 
        type: 'ADD_DIALOG_MESSAGE', 
        payload: { speaker: npcMessage.speaker, text: npcMessage.text }
      });

    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: DialogMessage = {
        speaker: 'System',
        text: 'Failed to communicate. The connection seems unstable.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-gradient-to-br from-amber-900/95 via-amber-800/90 to-amber-900/95 border-2 border-amber-700 rounded-lg shadow-[0_0_30px_rgba(218,165,32,0.8)] backdrop-blur-md w-full max-w-2xl h-96 flex flex-col">

        <div className="flex items-center justify-between p-4 border-b border-amber-700/50">
          <div className="flex items-center space-x-3">
            <MessageCircle className="w-6 h-6 text-amber-400" />
            <h3 className="text-xl font-bold text-amber-300 tracking-wide">Conversation with {characterName}</h3>
          </div>
          <button onClick={onClose} className="text-amber-400 hover:text-amber-300 transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.speaker === 'Player' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${message.speaker === 'Player' ? 'bg-gradient-to-r from-blue-800/80 via-blue-700/70 to-blue-800/80 border border-blue-600 text-blue-100' : 'bg-gradient-to-r from-amber-800/80 via-amber-700/70 to-amber-800/80 border border-amber-600 text-amber-100'}`}>
                <div className="font-semibold text-sm mb-1">{message.speaker}</div>
                <div className="text-sm leading-relaxed">{message.text}</div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gradient-to-r from-amber-800/80 via-amber-700/70 to-amber-800/80 border border-amber-600 text-amber-100 max-w-xs lg:max-w-md px-4 py-3 rounded-lg">
                <div className="font-semibold text-sm mb-1">{characterName}</div>
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {questActions.length > 0 && (
          <div className="px-4 py-2 bg-blue-900/50 border-t border-blue-700/30">
            <div className="text-xs text-blue-300 mb-1">🎯 Available Quest Objectives:</div>
            <div className="text-xs text-blue-200 space-y-1">
              {questActions.map((action, index) => (
                <div key={`hint-${action.quest_id}-${index}`} className="truncate">
                  • {action.description}
                </div>
              ))}
            </div>
            <div className="text-xs text-blue-400 mt-1 italic">
              Ask the character about these objectives to progress your quests!
            </div>
          </div>
        )}

        <div className="p-4 border-t border-amber-700/50">
          <div className="flex space-x-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 bg-black/30 border border-amber-700/50 rounded-lg text-amber-100 placeholder-amber-400/60 focus:outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-500/30"
            />
            <button onClick={sendMessage} disabled={!inputValue.trim() || isLoading} className="px-6 py-3 bg-gradient-to-r from-amber-700 via-amber-600 to-amber-700 border-2 border-amber-500 hover:bg-gradient-to-r hover:from-amber-600 hover:via-amber-500 hover:to-amber-600 hover:shadow-[0_0_15px_rgba(245,158,11,0.6)] text-amber-100 font-bold rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none">
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
