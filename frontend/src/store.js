async function request(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
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
    const error = new Error(payload.error || "Request failed.");
    Object.assign(error, payload);
    error.status = response.status;
    throw error;
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

export async function loginUser(identifier, password = "") {
  const payload = await request("/auth/session/login/", {
    method: "POST",
    body: JSON.stringify({ identifier, password }),
  });
  return payload.user || null;
}

export async function changePassword(userId, currentPassword, newPassword) {
  return request(`/users/${userId}/change-password/`, {
    method: "POST",
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });
}

export async function logoutUser() {
  return request("/auth/session/logout/", { method: "POST" });
}

export async function getCurrentUser() {
  try {
    const payload = await request("/auth/session/me/");
    return payload.user || null;
  } catch (err) {
    if (err.status === 401) return null;
    throw err;
  }
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

export async function cancelSong(userId, songId) {
  return request(`/users/${userId}/songs/${songId}/`, {
    method: "PUT",
    body: JSON.stringify({ action: "cancel" }),
  });
}

export async function regenerateSong(userId, songId) {
  return request(`/users/${userId}/songs/${songId}/`, {
    method: "PUT",
    body: JSON.stringify({ action: "regenerate" }),
  });
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

export async function createShareLink(userId, songId, expirationOption = "7_days") {
  return request(`/users/${userId}/songs/${songId}/share-links/`, {
    method: "POST",
    body: JSON.stringify({ expiration_option: expirationOption }),
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
