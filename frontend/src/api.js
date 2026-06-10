const TOKEN_KEY = "auth_token";

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = tokenStore.get();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    throw new ApiError("Sin conexión al servidor. Revisa tu internet.", 0);
  }

  if (response.status === 204) return null;

  let data;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    if (response.status === 401 && auth) {
      tokenStore.clear();
      window.dispatchEvent(new Event("auth:logout"));
    }
    const message =
      (data && (data.detail || data.message)) ||
      `Error ${response.status}. Intenta de nuevo.`;
    throw new ApiError(message, response.status);
  }

  return data;
}

export const api = {
  login: (email, password) =>
    request("/api/auth/login", {
      method: "POST",
      body: { email, password },
      auth: false,
    }),
  me: () => request("/api/auth/me"),
  changePassword: (current_password, new_password) =>
    request("/api/auth/change-password", {
      method: "POST",
      body: { current_password, new_password },
    }),

  listUsers: () => request("/api/users"),
  createUser: (email, temporary_password, is_admin = false) =>
    request("/api/users", {
      method: "POST",
      body: { email, temporary_password, is_admin },
    }),
  deleteUser: (id) => request(`/api/users/${id}`, { method: "DELETE" }),

  getPains: () => request("/api/catalogs/pains"),
  getFormats: () => request("/api/catalogs/formats"),

  getContext: () => request("/api/context"),
  updateContext: (data) =>
    request("/api/context", { method: "PUT", body: data }),

  generate: (payload) =>
    request("/api/content/generate", { method: "POST", body: payload }),
};
