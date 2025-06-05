export interface Player {
  name: string;
  level: number;
  health: number;
  maxHealth: number;
  mana: number;
  maxMana: number;
  experience: number;
  gold: number;
  inventory: InventoryItem[];
  equippedItems: EquippedItems;
  stats: PlayerStats;
}

export interface PlayerStats {
  strength: number;
  dexterity: number;
  intelligence: number;
  vitality: number;
}

export interface InventoryItem {
  id: string;
  name: string;
  type: string;
  quantity: number;
  description?: string;
  value?: number;
  rarity?: string;
  stats?: Partial<PlayerStats>;
}

export interface EquippedItems {
  weapon?: InventoryItem;
  armor?: InventoryItem;
  accessory?: InventoryItem;
}

export interface Quest {
  id: string;
  title: string;
  description: string;
  objectives?: QuestObjective[];
  progress?: QuestObjective[];
  steps?: QuestStep[];
  completion_requirements?: string[];
  type?: string;
  difficulty?: string;
  contact?: string;
  reward_gold?: number;
  reward_exp?: number;
  requirements?: string[];
  completed_by?: string[];
  generated?: boolean;
  generated_at?: number;
  time_limit_hours?: number;
  status?: 'available' | 'active' | 'completed' | 'failed';
  reward?: QuestReward;
}

export interface QuestStep {
  action: string;
  location: string;
  description: string;
  completed: boolean;
  required_items?: string[];
  consumes_items?: string[];
}

export interface QuestObjective {
  id?: string;
  description: string;
  completed: boolean;
  progress?: number;
  target?: number;
  is_current?: boolean;
  missing_items?: string[];
}

export interface QuestReward {
  experience?: number;
  gold?: number;
  items?: InventoryItem[];
}

export interface DialogOption {
  id: string;
  text: string;
  action?: string;
}

export interface DialogMessage {
  speaker: string;
  text: string;
  options?: DialogOption[];
}

export interface Location {
  id: string;
  name: string;
  description: string;
  availableActions: string[];
  npcs?: NPC[];
}

export interface NPC {
  id: string;
  name: string;
  type: 'merchant' | 'questgiver' | 'guard' | 'innkeeper';
  inventory?: InventoryItem[];
}

export interface GameState {
  player: Player;
  currentLocation: string;
  activeQuests: Quest[];
  completedQuests: Quest[];
  dialogHistory: DialogMessage[];
  isLoading: boolean;
}
