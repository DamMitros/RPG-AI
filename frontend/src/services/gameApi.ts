import api from '@/lib/api';
import { Player, Quest, InventoryItem, DialogMessage, QuestAction } from '@/types/game';

export const gameApi = {
  async getPlayer(): Promise<Player> {
    console.log('API: Fetching player data from /api/player...');
    try {
      const response = await api.get('/api/player');
      console.log('API: Raw response:', response);
      console.log('API: Response data:', response.data);
      console.log('API: Response data type:', typeof response.data);
      console.log('API: Response data stats:', (response.data as Player)?.stats);
      return response.data as Player;
    } catch (error) {
      console.error('API: Error fetching player:', error);
      throw error;
    }
  },

  async updatePlayer(player: Partial<Player>): Promise<Player> {
    const response = await api.put('/api/player', player);
    return response.data as Player;
  },

  async getLocation(locationId: string) {
    const response = await api.get(`/location/${locationId}`);
    return response.data as Record<string, unknown>;
  },

  async performLocationAction(locationId: string, action: string, data?: Record<string, unknown>) {
    const response = await api.post(`/location/${locationId}/action`, {
      action,
      ...data
    });
    return response.data as Record<string, unknown>;
  },

  async getQuests(): Promise<Quest[]> {
    const response = await api.get('/quest/list');
    return response.data as Quest[];
  },

  async getAvailableQuests() {
    const response = await api.get('/api/quests/available');
    return response.data as { quests: Quest[] };
  },

  async getActiveQuests(): Promise<Quest[]> {
    const response = await api.get('/api/quests/active');
    return (response.data as { quests: Quest[] }).quests;
  },

  async generateQuest(questType?: string) {
    const response = await api.post('/api/quests/generate', { quest_type: questType });
    return response.data as Quest;
  },

  async refreshQuests() {
    const response = await api.post('/api/quests/refresh');
    return response.data as { quests: Quest[] };
  },

  async acceptQuest(questId: string): Promise<Quest> {
    const response = await api.post(`/api/quests/${questId}/accept`);
    return response.data as Quest;
  },

  async abandonQuest(questId: string): Promise<boolean> {
    const response = await api.post(`/api/quests/${questId}/abandon`);
    return response.data as boolean;
  },

  async getQuestProgress(questId: string) {
    const response = await api.get(`/api/quests/${questId}/progress`);
    return response.data;
  },

  async getQuestActionsForLocation(location: string) {
    const response = await api.get(`/api/quests/actions/${location}`);
    return response.data as { actions: QuestAction[] };
  },

  async performQuestAction(action: string, location: string, questId?: string) {
    const response = await api.post('/api/quests/action', {
      action,
      location,
      quest_id: questId
    });
    return response.data as { success: boolean; message: string; quest_completed?: boolean; rewards?: Record<string, unknown>; player?: Player };
  },

  async completeQuest(questId: string): Promise<Quest> {
    const response = await api.post(`/quest/${questId}/complete`);
    return response.data as Quest;
  },

  async getInventory(): Promise<InventoryItem[]> {
    const response = await api.get('/inventory');
    return response.data as InventoryItem[];
  },

  async useItem(itemId: string) {
    const response = await api.post('/inventory/use', { item_id: itemId });
    return response.data as { success: boolean; message: string };
  },

  async craftItem(recipe: string, materials: string[]) {
    const response = await api.post('/inventory/craft', { recipe, materials });
    return response.data as { success: boolean; item?: InventoryItem };
  },

  async getMerchantInventory(): Promise<InventoryItem[]> {
    const response = await api.get('/merchant/inventory');
    return response.data as InventoryItem[];
  },

  async getShopItems() {
    console.log('API: Fetching shop items from /api/shop/items...');
    const response = await api.get('/api/shop/items');
    console.log('API: Shop items received:', response.data);
    return response.data;
  },

  async buyItem(itemId: string, quantity: number = 1) {
    console.log(`🌐 API: Buying ${quantity}x ${itemId}...`);
    const response = await api.post('/api/merchant/buy', {
      item_id: itemId,
      quantity
    });
    console.log('🌐 API: Buy response:', response.data);
    return response.data;
  },

  async sellItem(itemId: string, quantity: number = 1) {
    console.log(`🌐 API: Selling ${quantity}x ${itemId}...`);
    const response = await api.post('/api/merchant/sell', {
      item_id: itemId,
      quantity
    });
    console.log('🌐 API: Sell response:', response.data);
    return response.data;
  },

  async getSmithyRecipes() {
    console.log('API: Fetching smithy recipes from /api/smithy/recipes...');
    const response = await api.get('/api/smithy/recipes');
    console.log('API: Smithy recipes received:', response.data);
    return response.data;
  },

  async performAction(location: string, action: string, data?: Record<string, unknown>) {
    const response = await api.post('/api/action', {
      location,
      action,
      ...data
    });
    return response.data as { success: boolean; message: string; data?: Record<string, unknown> };
  },

  async sendMessage(sessionId: string, message: string, context?: Record<string, unknown>): Promise<DialogMessage> {
    const response = await api.post('/api/dialog', {
      session_id: sessionId,
      message,
      context
    });
    return response.data as DialogMessage;
  },

  async getDialogHistory(sessionId: string): Promise<DialogMessage[]> {
    const response = await api.get(`/api/dialog/${sessionId}/history`);
    return response.data as DialogMessage[];
  },

  async getConversationStats() {
    const response = await api.get('/api/conversation_stats');
    return response.data as Record<string, unknown>;
  },

  async getQualityReport() {
    const response = await api.get('/api/quality_report');
    return response.data as Record<string, unknown>;
  },

  async useInventoryItem(itemIndex: number) {
    const response = await api.post('/api/inventory/use', {
      itemId: itemIndex.toString()
    });
    return response.data as { success: boolean; message: string; data?: { player: Player } };
  },

  async unequipItem(slot: string) {
    const response = await api.post('/api/inventory/unequip', {
      equipment_slot: slot
    });
    return response.data as { success: boolean; message: string; data?: { player: Player } };
  },

  async refreshPlayerData(): Promise<Player> {
    return this.getPlayer();
  }
};
