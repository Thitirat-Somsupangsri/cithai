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

export async function getProfile(userId) {
  return request(`/users/${userId}/profile/`);
}

export async function createProfile(userId, payload) {
  return request(`/users/${userId}/profile/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateProfile(userId, payload) {
  return request(`/users/${userId}/profile/`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function listShareLinks(userId, songId) {
  const payload = await request(`/users/${userId}/songs/${songId}/share-links/`);
  return payload.share_links || [];
}

export async function createShareLink(userId, songId, expiration_date) {
  return request(`/users/${userId}/songs/${songId}/share-links/`, {
    method: "POST",
    body: JSON.stringify({ expiration_date }),
  });
}

export async function deleteShareLink(token) {
  return request(`/share-links/${token}/`, { method: "DELETE" });
}

export async function resolveShareLink(token) {
  return request(`/share-links/${token}/`);
}

export async function downloadSong(song) {
  const url = song.audio_url;
  if (!url) return;
  try {
    const resp = await fetch(url);
    const blob = await resp.blob();
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = `${song.title || "song"}.mp3`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(blobUrl);
  } catch {
    window.open(url, "_blank", "noopener");
  }
}
