'use client';

import { useGame } from '@/contexts/GameContext';
import { useQuests } from '@/hooks/useQuests';
import { motion } from 'framer-motion';
import { Building, Users, Sun, Footprints, Scroll } from 'lucide-react';
import { useState, useEffect } from 'react';
import { QuestAction } from '@/types/game';

export default function MainPageLocation() {
  const { state, dispatch } = useGame();
  const { performQuestAction, getQuestActionsForLocation } = useQuests();
  const [questActions, setQuestActions] = useState<QuestAction[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const loadQuestActions = async () => {
      const actions = await getQuestActionsForLocation('mainPage');
      setQuestActions(actions);
    };
    
    loadQuestActions();
  }, [getQuestActionsForLocation, state.activeQuests]);

  const handleAction = async (action: string) => {
    setIsLoading(true);
    try {
      const response = await performQuestAction(action, 'mainPage');
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
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuestAction = async (questAction: QuestAction) => {
    setIsLoading(true);
    try {
      const response = await performQuestAction(
        questAction.action, 
        'mainPage', 
        questAction.quest_id
      );
      
      dispatch({
        type: 'ADD_DIALOG_MESSAGE',
        payload: {
          speaker: 'Quest',
          text: `${questAction.quest_title}: ${response.message || questAction.description}`,
        },
      });
    } catch (error) {
      console.error('Failed to perform quest action:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden" style={{ fontFamily: "'Cinzel', serif" }}>
      
      <div className="relative z-10 container max-w-6xl mx-auto py-8">
        <div className="border-8 rounded-2xl p-8 shadow-2xl relative" style={{
            background: 'linear-gradient(145deg, #8b4513, #a0522d)',
            borderColor: '#654321',
            boxShadow: `0 0 30px rgba(212, 175, 55, 0.3), inset 0 0 20px rgba(0, 0, 0, 0.3)`}}>

          <div className="absolute -top-3 left-8 right-8 h-6 rounded-xl shadow-lg" style={{background: 'linear-gradient(45deg, #654321, #8b4513)', boxShadow: '0 4px 8px rgba(0, 0, 0, 0.3)'}}/>

          <div className="text-center mb-8">
            <h1 className="text-5xl font-bold mb-4 text-yellow-300" style={{fontFamily: "'Cinzel Decorative', serif", textShadow: '3px 3px 6px rgba(0, 0, 0, 0.7)'}}>
              VILLAGE SQUARE
            </h1>
            <p className="text-2xl text-yellow-100 italic mb-6">Stonehaven - Heart of Adventure</p>
            <p className="text-lg text-yellow-100 leading-relaxed max-w-3xl mx-auto">
              You stand in the bustling heart of Stonehaven&apos;s village square.  
              Merchants shout their wares, the scent of fresh bread and smoked meats fills the air,  
              and the chatter of townsfolk weaves a tapestry of life and adventure.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {[
              {
                action: 'observe_your_surroundings',
                label: 'Observe Your Surroundings',
                description: 'Look closely at what unfolds around you.',
                icon: Sun,
              },
              {
                action: 'talk_to_townspeople',
                label: 'Talk to Townspeople',
                description: 'Learn stories and secrets from locals.',
                icon: Users,
              },
              {
                action: 'follow_a_suspicious_trail',
                label: 'Follow a Suspicious Trail',
                description: 'You notice footprints leading away from the tavern toward...',
                icon: Footprints,
              },
              {
                action: 'examine_nearby_building',
                label: 'Examine Nearby Buildings',
                description: 'Study architecture for hidden clues.',
                icon: Building,
              },
            ].map(({ action, label, description, icon: Icon }, index) => (
              <motion.button key={action} onClick={() => handleAction(action)}
                disabled={isLoading}
                className="relative bg-gradient-to-br from-yellow-100 to-amber-100 rounded-xl border-3 border-amber-700 shadow-lg p-6 text-left hover:shadow-2xl transition-all duration-300 text-amber-900 disabled:opacity-50" style={{
                  transform: `rotate(${index % 2 === 0 ? '-0.5deg' : '0.5deg'})`,
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3), inset 0 0 10px rgba(139, 69, 19, 0.1)'
                }}
                whileHover={{ 
                  scale: 1.02, 
                  rotate: 0,
                  boxShadow: '0 6px 20px rgba(0, 0, 0, 0.4)' 
                }}
                whileTap={{ scale: 0.95 }}>

                <div className="absolute -top-2 -right-2 text-2xl">📌</div>
                
                <div className="flex gap-4 items-start">
                  <Icon className="w-8 h-8 flex-shrink-0 mt-1 text-amber-700" />
                  <div>
                    <h3 className="text-xl font-bold mb-2 text-red-800 uppercase" style={{ fontFamily: "'Cinzel Decorative', serif" }}>{label}</h3>
                    <p className="text-base leading-relaxed text-amber-800">{description}</p>
                  </div>
                </div>
              </motion.button>
            ))}
          </div>

          {questActions.length > 0 && (
            <div className="mb-8">
              <h2 className="text-3xl font-bold mb-6 text-center text-yellow-300" style={{ 
                fontFamily: "'Cinzel Decorative', serif", 
                textShadow: '2px 2px 4px rgba(0, 0, 0, 0.7)' 
              }}>
                🗡️ Available Quest Actions
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {questActions.map((questAction, index) => (
                  <motion.button
                    key={`${questAction.quest_id}-${questAction.action}`}
                    onClick={() => handleQuestAction(questAction)}
                    disabled={isLoading}
                    className="relative bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl border-3 border-blue-700 shadow-lg p-6 text-left hover:shadow-2xl transition-all duration-300 text-blue-900 disabled:opacity-50"
                    style={{
                      transform: `rotate(${index % 2 === 0 ? '0.5deg' : '-0.5deg'})`,
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3), inset 0 0 10px rgba(30, 64, 175, 0.1)'
                    }}
                    whileHover={{ 
                      scale: 1.02, 
                      rotate: 0,
                      boxShadow: '0 6px 20px rgba(0, 0, 0, 0.4)' 
                    }}
                    whileTap={{ scale: 0.95 }}>
                    <div className="absolute -top-2 -right-2 text-2xl">⚔️</div>
                    
                    <div className="flex gap-4 items-start">
                      <Scroll className="w-8 h-8 flex-shrink-0 mt-1 text-blue-700" />
                      <div>
                        <h3 className="text-lg font-bold mb-1 text-blue-800 uppercase" style={{ fontFamily: "'Cinzel Decorative', serif" }}>
                          {questAction.quest_title}
                        </h3>
                        <p className="text-base leading-relaxed text-blue-800 font-semibold">
                          {questAction.description}
                        </p>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>
          )}

          {state.dialogHistory.length > 0 && (
            <div className="border-t-4 border-amber-700 pt-6">
              <h2 className="text-2xl font-bold mb-4 text-center text-yellow-300" style={{ fontFamily: "'Cinzel Decorative', serif", textShadow: '2px 2px 4px rgba(0, 0, 0, 0.7)' }}>
                📜 Recent Notices
              </h2>
              <div className="space-y-4 max-h-64 overflow-y-auto">
                {state.dialogHistory.slice(-5).map((message, i) => (
                  <motion.div key={i}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gradient-to-br from-yellow-100 to-amber-100 rounded-lg border-2 border-amber-700 p-4 shadow-md" style={{
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2), inset 0 0 10px rgba(139, 69, 19, 0.1)'}}>
                    <div className="font-bold text-red-800 mb-1" style={{ fontFamily: "'Cinzel', serif" }}>
                      {message.speaker}:
                    </div>
                    <div className="text-amber-900 whitespace-pre-line">
                      {message.text}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
