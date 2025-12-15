export interface WebsetItem {
  id: string;
  name?: string;
  title?: string;
  type: string;
  description?: string;
  url?: string;
  
  // Company fields
  industry?: string;
  location?: string;
  logo_url?: string;
  
  // Person fields
  position?: string;
  company_name?: string;
  picture_url?: string;
  
  // Paper fields
  authors?: string[];
  publication?: string;
  year?: number;
  citations?: number;
  abstract?: string;
  
  // Article fields
  publisher?: string;
  date?: string;
  summary?: string;
  
  // Generic
  properties?: any;
  
  // Common
  evaluations?: Array<{
    criterion: string;
    satisfied: 'yes' | 'no' | 'unclear';
    reasoning?: string;
    references?: Array<{ title?: string; url: string; snippet?: string }>;
  }>;
  enrichments?: Record<string, any>;
}

export interface WebsetData {
  webset_id?: string;
  external_id?: string;
  query?: string;
  entity_type?: string;
  status?: string;
  search_status?: string;
  item_count?: number;
  items_found?: number;
  items_returned?: number;
  cost_deducted?: string;
  items?: WebsetItem[];
  item?: WebsetItem;
  // List websets response
  websets?: Array<{
    id: string;
    name?: string;
    status?: string;
    item_count?: number;
  }>;
  total?: number;
  limit?: number;
  next_cursor?: string;
  has_more?: boolean;
  // Live processing fields
  is_processing?: boolean;
  is_complete?: boolean;
  progress?: {
    found: number;
    analyzed: number;
    completion: number;
    time_left?: number | null;
  };
  message?: string;
  searches?: Array<{
    id: string;
    status: string;
    query: string;
    progress?: {
      found: number;
      completion: number;
    };
  }>;
  enrichments?: Array<{
    id: string;
    status: string;
    title?: string;
    description?: string;
  }>;
  monitors?: Array<{
    id: string;
    status: string;
    next_run?: string;
  }>;
  success?: boolean;
  timestamp?: string;
  created_at?: string;
  updated_at?: string;
}
