// Types mirroring the backend Pydantic schemas.

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  auth_provider: string;
  created_at: string;
}

export type DeviceType =
  | "browser" | "windows" | "linux" | "raspberry_pi" | "android_tv"
  | "fire_tv" | "samsung_tv" | "lg_tv" | "tablet" | "other";

export type DisplayStatus = "online" | "offline" | "unpaired";

export interface Display {
  id: number;
  user_id: number;
  name: string;
  device_type: DeviceType;
  status: DisplayStatus;
  group: string | null;
  pairing_code: string | null;
  last_seen: string | null;
  current_layout_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface GridConfig {
  columns: number;
  rows: number;
  gap: number;
}

export interface Widget {
  id: number;
  layout_id: number;
  widget_type: string;
  config: Record<string, unknown>;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  created_at: string;
  updated_at: string;
}

export interface Layout {
  id: number;
  user_id: number;
  name: string;
  theme: string;
  grid_config: GridConfig;
  created_at: string;
  updated_at: string;
}

export interface LayoutDetail extends Layout {
  widgets: Widget[];
}

export interface DisplayPlayerView {
  display: Display;
  layout: LayoutDetail | null;
}

export interface WidgetCatalogEntry {
  type: string;
  name: string;
  category: string;
  description: string;
  icon: string;
  tags: string[];
  default_width: number;
  default_height: number;
  min_width: number;
  min_height: number;
  default_config: Record<string, unknown>;
  config_schema: Record<string, unknown>;
}

export interface Template {
  id: number;
  user_id: number | null;
  name: string;
  description: string | null;
  category: string;
  is_system: boolean;
  definition: {
    theme: string;
    grid_config: GridConfig;
    widgets: Array<Omit<Widget, "id" | "layout_id" | "created_at" | "updated_at">>;
  };
  created_at: string;
}

export interface DashboardStats {
  total_displays: number;
  online_displays: number;
  total_layouts: number;
  widget_count: number;
  recent_activity: Array<Record<string, unknown>>;
}

export interface AIBuildResponse {
  name: string;
  theme: string;
  grid_config: GridConfig;
  widgets: Array<Omit<Widget, "id" | "layout_id" | "created_at" | "updated_at">>;
  layout_id: number | null;
  source: string;
}
