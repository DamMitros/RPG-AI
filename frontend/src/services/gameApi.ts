import api from '@/lib/api';
import { Player, Quest, InventoryItem, DialogMessage } from '@/types/game';

export const gameApi = {
  async getPlayer(): Promise<Player> {
    console.log('API: Fetching player data from /api/player...');
    const response = await api.get('/api/player');
    console.log('API: Player data received:', response.data);
    return response.data as Player;
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

  async acceptQuest(questId: string): Promise<Quest> {
    const response = await api.post(`/quest/${questId}/accept`);
    return response.data as Quest;
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

  async refreshPlayerData(): Promise<Player> {
    return this.getPlayer();
  }
};
