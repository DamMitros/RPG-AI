'use client';

import React, { createContext, useContext, useReducer, ReactNode, useEffect } from 'react';
import { GameState, Player, Quest, DialogMessage } from '@/types/game';
import { gameApi } from '@/services/gameApi';

const initialState: GameState = {
  player: {
    name: 'Hero',
    level: 1,
    health: 100,
    maxHealth: 100,
    mana: 50,
    maxMana: 50,
    experience: 0,
    gold: 100,
    inventory: [],
    equippedItems: {},
    stats: {
      strength: 10,
      dexterity: 10,
      intelligence: 10,
      vitality: 10,
    },
  },
  currentLocation: 'mainPage',
  activeQuests: [],
  completedQuests: [],
  dialogHistory: [],
  isLoading: false,
};

type GameAction =
  | { type: 'SET_PLAYER'; payload: Player }
  | { type: 'SET_LOCATION'; payload: string }
  | { type: 'ADD_QUEST'; payload: Quest }
  | { type: 'COMPLETE_QUEST'; payload: string }
  | { type: 'ABANDON_QUEST'; payload: string }
  | { type: 'UPDATE_QUEST_PROGRESS'; payload: { questId: string; progress: Record<string, unknown> } }
  | { type: 'SET_ACTIVE_QUESTS'; payload: Quest[] }
  | { type: 'ADD_DIALOG_MESSAGE'; payload: DialogMessage }
  | { type: 'CLEAR_DIALOG' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'UPDATE_PLAYER_HEALTH'; payload: number }
  | { type: 'UPDATE_PLAYER_MANA'; payload: number }
  | { type: 'UPDATE_PLAYER_GOLD'; payload: number };

function gameReducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case 'SET_PLAYER':
      const newState = { ...state, player: action.payload };
      return newState;
    
    case 'SET_LOCATION':
      return { ...state, currentLocation: action.payload };
    
    case 'ADD_QUEST':
      return {
        ...state,
        activeQuests: [...state.activeQuests, action.payload],
      };
    
    case 'COMPLETE_QUEST':
      const questToComplete = state.activeQuests.find(q => q.id === action.payload);
      if (!questToComplete) return state;
      
      return {
        ...state,
        activeQuests: state.activeQuests.filter(q => q.id !== action.payload),
        completedQuests: [...state.completedQuests, { ...questToComplete, status: 'completed' }],
      };
    
    case 'ABANDON_QUEST':
      return {
        ...state,
        activeQuests: state.activeQuests.filter(q => q.id !== action.payload),
      };
    
    case 'UPDATE_QUEST_PROGRESS':
      return {
        ...state,
        activeQuests: state.activeQuests.map(quest => 
          quest.id === action.payload.questId 
            ? { ...quest, ...action.payload.progress }
            : quest
        ),
      };
    
    case 'SET_ACTIVE_QUESTS':
      return {
        ...state,
        activeQuests: action.payload,
      };
    
    case 'ADD_DIALOG_MESSAGE':
      return {
        ...state,
        dialogHistory: [...state.dialogHistory, action.payload],
      };
    
    case 'CLEAR_DIALOG':
      return { ...state, dialogHistory: [] };
    
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    
    case 'UPDATE_PLAYER_HEALTH':
      return {
        ...state,
        player: {
          ...state.player,
          health: Math.max(0, Math.min(state.player.maxHealth, action.payload)),
        },
      };
    
    case 'UPDATE_PLAYER_MANA':
      return {
        ...state,
        player: {
          ...state.player,
          mana: Math.max(0, Math.min(state.player.maxMana, action.payload)),
        },
      };
    
    case 'UPDATE_PLAYER_GOLD':
      return {
        ...state,
        player: {
          ...state.player,
          gold: Math.max(0, action.payload),
        },
      };
    
    default:
      return state;
  }
}

const GameContext = createContext<{
  state: GameState;
  dispatch: React.Dispatch<GameAction>;
  refreshPlayer: () => Promise<void>;
} | null>(null);

export function GameProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(gameReducer, initialState);
  const refreshPlayer = async () => {
    try {
      const playerData = await gameApi.getPlayer();
      dispatch({ type: 'SET_PLAYER', payload: playerData });
    } catch (error) {
      console.error('🎮 GameContext: Failed to refresh player data:', error);
    }
  };

  useEffect(() => {
    const loadPlayerData = async () => {
      try {
        console.log('🎮 GameContext: Loading player data from API...');
        dispatch({ type: 'SET_LOADING', payload: true });
        const playerData = await gameApi.getPlayer();
        console.log('🎮 GameContext: Player data loaded:', playerData);
        dispatch({ type: 'SET_PLAYER', payload: playerData });
      } catch (error) {
        console.error('🎮 GameContext: Failed to load player data:', error);
      } finally {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    loadPlayerData();
  }, []);

  return (
    <GameContext.Provider value={{ state, dispatch, refreshPlayer }}>
      {children}
    </GameContext.Provider>
  );
}

export function useGame() {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
}
