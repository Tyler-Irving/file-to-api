export interface Dataset {
  id: string;
  slug: string;
  name: string;
  original_filename: string;
  row_count: number;
  status: 'processing' | 'ready' | 'error';
  error_message?: string;
  created_at: string;
  api_url: string;
  docs_url: string;
  api_key?: string; // Only present on creation (full key)
  columns: DatasetColumn[];
}

export interface DatasetColumn {
  id?: number;
  name: string;
  field_name: string;
  data_type: 'text' | 'integer' | 'float' | 'boolean' | 'date' | 'datetime';
  nullable: boolean;
  sample_values: any[];
  position: number;
}

export interface APIKey {
  id: string;
  prefix: string;
  name: string;
  created_at: string;
  is_active: boolean;
  full_key?: string; // Only present on creation
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface DataRecord {
  id: number;
  [key: string]: any;
}
