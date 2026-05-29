import type {
  AIBuildResponse, DashboardStats, Display, DisplayPlayerView,
  Layout, LayoutDetail, Template, TokenPair, User, Widget, WidgetCatalogEntry,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const V1 = `${API_URL}/api/v1`;

const ACCESS_KEY = "tc_access";
const REFRESH_KEY = "tc_refresh";

export const tokenStore = {
  get access() {
    return typeof window === "undefined" ? null : localStorage.getItem(ACCESS_KEY);
  },
  get refresh() {
    return typeof window === "undefined" ? null : localStorage.getItem(REFRESH_KEY);
  },
  set(pair: TokenPair) {
    localStorage.setItem(ACCESS_KEY, pair.access_token);
    localStorage.setItem(REFRESH_KEY, pair.refresh_token);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function refreshTokens(): Promise<boolean> {
  const refresh = tokenStore.refresh;
  if (!refresh) return false;
  const res = await fetch(`${V1}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refresh }),
  });
  if (!res.ok) return false;
  tokenStore.set(await res.json());
  return true;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  retry = true,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  const access = tokenStore.access;
  if (access) headers.set("Authorization", `Bearer ${access}`);

  const res = await fetch(`${V1}${path}`, { ...options, headers });

  if (res.status === 401 && retry && (await refreshTokens())) {
    return request<T>(path, options, false);
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  // --- auth ---
  register: (email: string, password: string, full_name?: string) =>
    request<TokenPair>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
    }),
  login: (email: string, password: string) =>
    request<TokenPair>("/auth/login/json", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<User>("/auth/me"),
  logout: () => request<{ detail: string }>("/auth/logout", { method: "POST" }),

  // --- dashboard ---
  dashboardStats: () => request<DashboardStats>("/dashboard/stats"),

  // --- displays ---
  listDisplays: () => request<Display[]>("/displays"),
  createDisplay: (body: Partial<Display>) =>
    request<Display>("/displays", { method: "POST", body: JSON.stringify(body) }),
  updateDisplay: (id: number, body: Partial<Display>) =>
    request<Display>(`/displays/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteDisplay: (id: number) =>
    request<void>(`/displays/${id}`, { method: "DELETE" }),
  assignLayout: (id: number, layout_id: number | null) =>
    request<Display>(`/displays/${id}/assign`, {
      method: "POST",
      body: JSON.stringify({ layout_id }),
    }),
  playerView: (id: number) => request<DisplayPlayerView>(`/displays/${id}/player`),
  heartbeat: (id: number) =>
    request<{ detail: string }>(`/displays/${id}/heartbeat`, { method: "POST" }),

  // --- layouts ---
  listLayouts: () => request<Layout[]>("/layouts"),
  getLayout: (id: number) => request<LayoutDetail>(`/layouts/${id}`),
  createLayout: (body: Partial<Layout>) =>
    request<LayoutDetail>("/layouts", { method: "POST", body: JSON.stringify(body) }),
  updateLayout: (id: number, body: Partial<Layout>) =>
    request<LayoutDetail>(`/layouts/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteLayout: (id: number) => request<void>(`/layouts/${id}`, { method: "DELETE" }),
  cloneLayout: (id: number) =>
    request<LayoutDetail>(`/layouts/${id}/clone`, { method: "POST" }),

  // --- widgets ---
  widgetCatalog: () =>
    request<{ widgets: WidgetCatalogEntry[] }>("/widgets/catalog"),
  addWidget: (layoutId: number, body: Partial<Widget>) =>
    request<Widget>(`/layouts/${layoutId}/widgets`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  updateWidget: (layoutId: number, widgetId: number, body: Partial<Widget>) =>
    request<Widget>(`/layouts/${layoutId}/widgets/${widgetId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  deleteWidget: (layoutId: number, widgetId: number) =>
    request<void>(`/layouts/${layoutId}/widgets/${widgetId}`, { method: "DELETE" }),

  // --- templates ---
  listTemplates: () => request<Template[]>("/templates"),
  instantiateTemplate: (id: number, name?: string) =>
    request<LayoutDetail>(`/templates/${id}/instantiate`, {
      method: "POST",
      body: JSON.stringify({ name }),
    }),

  // --- AI ---
  aiBuild: (prompt: string, theme?: string, save = true) =>
    request<AIBuildResponse>("/ai/build", {
      method: "POST",
      body: JSON.stringify({ prompt, theme, save }),
    }),
};

export { ApiError };
