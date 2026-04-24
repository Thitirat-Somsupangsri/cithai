const SESSION_KEY = "cithai_front_session_user_id";

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  let payload = {};
  try {
    payload = await response.json();
  } catch {
    payload = { error: "Invalid server response." };
  }

  if (!response.ok) {
    throw new Error(payload.error || "Request failed.");
  }

  return payload;
}

export async function listUsers() {
  const payload = await request("/users/");
  return payload.users || [];
}

export async function createUser(payload) {
  return request("/users/", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function loginUser(identifier) {
  const normalized = identifier.trim().toLowerCase();
  const users = await listUsers();
  const user = users.find(
    (item) => item.username.toLowerCase() === normalized || item.email.toLowerCase() === normalized
  );
  if (!user) {
    throw new Error("User not found.");
  }
  setSessionUserId(user.id);
  return user;
}

export function logoutUser() {
  localStorage.removeItem(SESSION_KEY);
}

export function getSessionUserId() {
  const raw = localStorage.getItem(SESSION_KEY);
  return raw ? Number(raw) : null;
}

export function setSessionUserId(userId) {
  localStorage.setItem(SESSION_KEY, String(userId));
}

export async function getCurrentUser() {
  const userId = getSessionUserId();
  if (!userId) return null;
  const users = await listUsers();
  return users.find((user) => user.id === userId) || null;
}

export async function listSongsForUser(userId) {
  const payload = await request(`/users/${userId}/songs/`);
  return payload.songs || [];
}

export async function getSongById(userId, songId) {
  return request(`/users/${userId}/songs/${songId}/`);
}

export async function createSong(userId, payload) {
  return request(`/users/${userId}/songs/`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function deleteSong(userId, songId) {
  return request(`/users/${userId}/songs/${songId}/`, { method: "DELETE" });
}
