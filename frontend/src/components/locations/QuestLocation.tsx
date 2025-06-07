'use client';

import React, { useState, useEffect } from 'react';
import { useGame } from '@/contexts/GameContext';
import { useQuests } from '@/hooks/useQuests';
import { gameApi } from '@/services/gameApi';
import { CheckCircle, Coins, Award, X, RefreshCw } from 'lucide-react';
import { Quest } from '@/types/game';
import { motion, AnimatePresence } from 'framer-motion';

const QuestLocation: React.FC = () => {
  const { state } = useGame();
  const { acceptQuest: acceptQuestHook, refreshQuests: refreshQuestsHook } = useQuests();
  const [selectedQuest, setSelectedQuest] = useState<Quest | null>(null);
  const [availableQuests, setAvailableQuests] = useState<Quest[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadQuests = async () => {
      try {
        const response = await gameApi.getAvailableQuests();
        setAvailableQuests(response.quests);
      } catch (error) {
        console.error('Failed to load quests:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadQuests();
  }, []);

  const acceptQuest = async (quest: Quest) => {
    if (state.activeQuests.find((q: Quest) => q.id === quest.id)) {
      return;
    }

    try {
      await acceptQuestHook(quest.id);
      setAvailableQuests((prev: Quest[]) => prev.filter((q: Quest) => q.id !== quest.id));
      setSelectedQuest(null);
    } catch (error) {
      console.error('Failed to accept quest:', error);
    }
  };

  const refreshQuests = async () => {
    setIsLoading(true);
    try {
      const refreshedQuests = await refreshQuestsHook();
      setAvailableQuests(refreshedQuests);
    } catch (error) {
      console.error('Failed to refresh quests:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden" style={{ fontFamily: "'Cinzel', serif" }}>
      
      <div className="relative z-10 container max-w-6xl mx-auto p-8">
        <div className="border-8 rounded-2xl p-8 shadow-2xl relative" style={{
            background: 'linear-gradient(145deg, #8b4513, #a0522d)',
            borderColor: '#654321',
            boxShadow: `0 0 30px rgba(212, 175, 55, 0.3), inset 0 0 20px rgba(0, 0, 0, 0.3)`
          }}>

          <div className="absolute -top-3 left-8 right-8 h-6 rounded-xl shadow-lg" style={{
              background: 'linear-gradient(45deg, #654321, #8b4513)',
              boxShadow: '0 4px 8px rgba(0, 0, 0, 0.3)'
            }}/>

          <div className="text-center mb-8">
            <h1 className="text-5xl font-bold mb-4 text-yellow-300" style={{
                fontFamily: "'Cinzel Decorative', serif",
                textShadow: '3px 3px 6px rgba(0, 0, 0, 0.7)'
              }}>VILLAGE NOTICE BOARD</h1>
            <p className="text-xl text-yellow-100 italic mb-6">Stonehaven - Opportunities for Bold Adventurers</p>

            <div className="flex justify-center gap-4 mb-6">
              <motion.button onClick={refreshQuests} disabled={isLoading} className="bg-gradient-to-br from-yellow-600 to-amber-700 text-amber-100  border-2 border-yellow-500 px-6 py-3 rounded-lg font-bold hover:from-yellow-500 hover:to-amber-600 transition-all duration-300 disabled:opacity-50 flex items-center gap-2"
                whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh Quests
              </motion.button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <h2 className="text-2xl font-bold mb-6 text-center text-yellow-300" style={{ 
                  fontFamily: "'Cinzel Decorative', serif",
                  textShadow: '2px 2px 4px rgba(0, 0, 0, 0.7)' 
                }}>🗞️ Available Quests</h2>
              
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin w-8 h-8 border-2 border-yellow-400 border-t-transparent rounded-full mx-auto mb-4"></div>
                  <p className="text-yellow-200">Loading quests...</p>
                </div>
              ) : availableQuests.length > 0 ? (
                <div className="space-y-6">
                  {availableQuests.map((quest, index) => (
                    <motion.div key={quest.id} initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }} className="bg-gradient-to-br from-yellow-100 to-amber-100 border-3 border-amber-700 rounded-xl p-6 shadow-lg relative cursor-pointer hover:shadow-2xl transition-all duration-300"
                      style={{ transform: `rotate(${index % 2 === 0 ? '-0.5deg' : '0.5deg'})`,
                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3), inset 0 0 10px rgba(139, 69, 19, 0.1)'}}
                      whileHover={{ scale: 1.02, rotate: 0,boxShadow: '0 6px 20px rgba(0, 0, 0, 0.4)' }}
                      onClick={() => setSelectedQuest(quest)}>

                      <div className="absolute -top-2 -right-2 text-2xl">📌</div>
                      <h3 className="text-xl font-bold mb-3 text-center text-red-800 uppercase" style={{ fontFamily: "'Cinzel Decorative', serif" }}>{quest.title}</h3>   
                      <p className="text-amber-900 mb-4 text-justify leading-relaxed">{quest.description}</p>
          
                      <div className="mb-4">
                        <span className="bg-red-800 text-yellow-100 px-3 py-1 rounded-full text-sm font-bold uppercase">{quest.type}</span>
                      </div>

                      <div className="border-t-2 border-amber-700 pt-4 flex justify-between items-center">
                        <div className="text-amber-800">
                          <div className="flex items-center gap-2">
                            <Coins className="w-5 h-5 text-yellow-600" />
                            <span className="font-bold text-yellow-700">
                              💰 {quest.reward?.gold || 0} gold
                            </span>
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <Award className="w-5 h-5 text-yellow-600" />
                            <span className="font-bold text-yellow-700">
                              ⭐ {quest.reward?.experience || 0} exp
                            </span>
                          </div>
                        </div>
                        
                        <motion.button onClick={(e) => {e.stopPropagation(); acceptQuest(quest);}}
                          disabled={state.isLoading} className="bg-gradient-to-br from-green-700 to-green-800 text-white px-4 py-2 rounded-lg font-bold hover:from-green-600 hover:to-green-700 transition-all duration-300 disabled:opacity-50" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                          Accept Quest
                        </motion.button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-amber-700 bg-amber-100/50 rounded-xl border-2 border-dashed border-amber-600">
                  <p className="text-lg italic">📜 No new quests available at this time.</p>
                  <p>Check back later or try refreshing!</p>
                </div>
              )}
            </div>

            <div>
              <h2 className="text-2xl font-bold mb-6 text-center text-yellow-300" style={{ fontFamily: "'Cinzel Decorative', serif", 
                textShadow: '2px 2px 4px rgba(0, 0, 0, 0.7)' }}>
                ⚔️ Active Quests
              </h2>
              
              {state.activeQuests.length > 0 ? (
                <div className="space-y-6">
                  {state.activeQuests.map((quest: Quest, index: number) => (
                    <motion.div key={`quest-${quest.id}-${index}`} initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }} className="bg-gradient-to-br from-yellow-100 to-amber-100 border-3 border-amber-700 rounded-xl p-6 shadow-lg relative"
                      style={{ transform: `rotate(${index % 2 === 0 ? '0.5deg' : '-0.5deg'})`,
                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3), inset 0 0 10px rgba(139, 69, 19, 0.1)'}}>

                      <h3 className="text-xl font-bold mb-3 text-center text-red-800 uppercase" style={{ fontFamily: "'Cinzel Decorative', serif" }}>{quest.title}</h3>
                      <p className="text-amber-900 mb-4 text-justify leading-relaxed">{quest.description}</p>

                      {quest.objectives && (
                        <div className="bg-black/20 rounded-lg p-4 mb-4">
                          <h4 className="text-yellow-700 font-bold mb-3">Progress:</h4>
                          <div className="space-y-2">
                            {quest.objectives.map((objective) => (
                              <div key={objective.id} className={`flex items-center gap-3 p-2 rounded ${objective.completed ? 'bg-green-200/20 border-l-3 border-green-600' : 'bg-yellow-200/20 border-l-3 border-yellow-600'}`}>
                                <span className="text-lg">
                                  {objective.completed ? '✅' : '⏳'}
                                </span>
                                <span className={`flex-grow text-sm ${objective.completed ? 'text-green-800' : 'text-amber-800'}`}>
                                  {objective.description}
                                  {objective.target && objective.target > 1 && (
                                    <span className="ml-2 font-bold">
                                      ({objective.progress || 0}/{objective.target})
                                    </span>
                                  )}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="border-t-2 border-amber-700 pt-4 flex justify-between items-center">
                        <div className="text-amber-800">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-yellow-700">
                              💰 {quest.reward?.gold || 0} gold
                            </span>
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="font-bold text-yellow-700">
                              ⭐ {quest.reward?.experience || 0} exp
                            </span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-amber-700 bg-amber-100/50 rounded-xl border-2 border-dashed border-amber-600">
                  <p className="text-lg italic">📋 No active quests.</p>
                  <p>Accept some quests to get started!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {selectedQuest && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            exit={{ opacity: 0 }} className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => setSelectedQuest(null)}>
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }} className="bg-gradient-to-br from-yellow-100 to-amber-100 border-8 border-amber-700  rounded-2xl p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto shadow-2xl relative" style={{ fontFamily: "'Cinzel', serif",
                boxShadow: '0 0 30px rgba(212, 175, 55, 0.5), inset 0 0 20px rgba(0, 0, 0, 0.1)'}}
              onClick={(e) => e.stopPropagation()}>

              <button onClick={() => setSelectedQuest(null)} className="absolute top-4 right-4 text-amber-800 hover:text-amber-600 transition-colors p-2 rounded-full hover:bg-amber-200/50">
                <X className="w-6 h-6" />
              </button>

              <div className="text-center mb-6">
                <h3 className="text-3xl font-bold text-red-800 uppercase mb-2" style={{ fontFamily: "'Cinzel Decorative', serif" }}>{selectedQuest.title}</h3>
                <span className="bg-red-800 text-yellow-100 px-4 py-2 rounded-full text-sm font-bold uppercase">{selectedQuest.type}</span>
              </div>

              <p className="text-amber-900 mb-8 leading-relaxed text-lg text-justify">{selectedQuest.description}</p>

              {selectedQuest.objectives && (
                <div className="mb-8">
                  <h4 className="text-xl font-bold text-yellow-700 mb-4" style={{ fontFamily: "'Cinzel Decorative', serif" }}>
                    Quest Objectives
                  </h4>
                  <div className="space-y-3">
                    {selectedQuest.objectives.map((objective) => (
                      <div key={objective.id} className="flex items-center gap-4 p-3 bg-amber-200/50 rounded-lg">
                        <CheckCircle className={`w-6 h-6 ${objective.completed ? 'text-green-600' : 'text-amber-600'}`}/>
                        <span className={`text-lg ${objective.completed ? 'text-green-800' : 'text-amber-800'}`}>
                          {objective.description}
                          {objective.target && objective.target > 1 && (
                            <span className="text-yellow-700 ml-3 font-semibold">
                              ({objective.progress || 0}/{objective.target})
                            </span>
                          )}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="mb-8 bg-amber-200/50 rounded-lg p-6">
                <h4 className="text-xl font-bold text-yellow-700 mb-4" style={{ fontFamily: "'Cinzel Decorative', serif" }}>Quest Rewards</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-3">
                    <Coins className="w-8 h-8 text-yellow-600" />
                    <div>
                      <span className="text-2xl font-bold text-yellow-700">
                        {selectedQuest.reward?.gold || 0}
                      </span>
                      <p className="text-amber-700">Gold</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Award className="w-8 h-8 text-yellow-600" />
                    <div>
                      <span className="text-2xl font-bold text-yellow-700">
                        {selectedQuest.reward?.experience || 0}
                      </span>
                      <p className="text-amber-700">Experience</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-4">
                <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={() => acceptQuest(selectedQuest)} disabled={state.isLoading} className="flex-1 bg-gradient-to-br from-green-700 to-green-800 text-white font-bold py-4 px-6 rounded-lg transition-all duration-300 hover:from-green-600 hover:to-green-700 disabled:opacity-50">
                  {state.isLoading ? 'Accepting...' : 'Accept Quest'}
                </motion.button>
                <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={() => setSelectedQuest(null)} className="px-6 py-4 border-2 border-amber-700 text-amber-700 rounded-lg hover:bg-amber-200/50 transition-all duration-300 font-bold">
                  Close
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default QuestLocation;
