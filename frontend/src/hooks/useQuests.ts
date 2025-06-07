'use client';

import { useState, useCallback } from 'react';
import { useGame } from '@/contexts/GameContext';
import { gameApi } from '@/services/gameApi';
import { QuestAction } from '@/types/game';

export function useQuests() {
  const { state, dispatch } = useGame();
  const [isLoading, setIsLoading] = useState(false);

  const loadActiveQuests = useCallback(async () => {
    setIsLoading(true);
    try {
      const quests = await gameApi.getActiveQuests();
      dispatch({ type: 'SET_ACTIVE_QUESTS', payload: quests });
    } catch (error) {
      console.error('Failed to load active quests:', error);
    } finally {
      setIsLoading(false);
    }
  }, [dispatch]);

  const acceptQuest = useCallback(async (questId: string) => {
    setIsLoading(true);
    try {
      const quest = await gameApi.acceptQuest(questId);
      dispatch({ type: 'ADD_QUEST', payload: quest });

      const playerData = await gameApi.getPlayer();
      dispatch({ type: 'SET_PLAYER', payload: playerData });
      
      return quest;
    } catch (error) {
      console.error('Failed to accept quest:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [dispatch]);

  const abandonQuest = useCallback(async (questId: string) => {
    setIsLoading(true);
    try {
      await gameApi.abandonQuest(questId);
      dispatch({ type: 'ABANDON_QUEST', payload: questId });
      
      const playerData = await gameApi.getPlayer();
      dispatch({ type: 'SET_PLAYER', payload: playerData });
    } catch (error) {
      console.error('Failed to abandon quest:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [dispatch]);

  const performQuestAction = useCallback(async (
    action: string, 
    location: string, 
    questId?: string
  ) => {
    setIsLoading(true);
    try {
      const response = await gameApi.performQuestAction(action, location, questId);

      if (response.player) {
        dispatch({ type: 'SET_PLAYER', payload: response.player });
      } else {
        const playerData = await gameApi.getPlayer();
        dispatch({ type: 'SET_PLAYER', payload: playerData });
      }
      
      const activeQuests = await gameApi.getActiveQuests();
      dispatch({ type: 'SET_ACTIVE_QUESTS', payload: activeQuests });
      
      return response;
    } catch (error) {
      console.error('Failed to perform quest action:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [dispatch]);

  const getQuestActionsForLocation = useCallback(async (location: string): Promise<QuestAction[]> => {
    try {
      const response = await gameApi.getQuestActionsForLocation(location);
      return response.actions;
    } catch (error) {
      console.error('Failed to get quest actions for location:', error);
      return [];
    }
  }, []);

  const generateQuest = useCallback(async (questType?: string) => {
    setIsLoading(true);
    try {
      const quest = await gameApi.generateQuest(questType);
      return quest;
    } catch (error) {
      console.error('Failed to generate quest:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshQuests = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await gameApi.refreshQuests();
      return response.quests;
    } catch (error) {
      console.error('Failed to refresh quests:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    activeQuests: state.activeQuests,
    completedQuests: state.completedQuests,
    isLoading,
    acceptQuest,
    abandonQuest,
    performQuestAction,
    getQuestActionsForLocation,
    generateQuest,
    refreshQuests,
    loadActiveQuests,
  };
}
