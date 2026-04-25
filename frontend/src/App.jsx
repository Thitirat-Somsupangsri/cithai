import { useEffect, useRef, useState, useMemo } from "react";
import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import { genders, genres, occasions, voiceTypes } from "./options";
import {
  createSong,
  createUser,
  deleteSong,
  downloadSong,
  getSongById,
  getCurrentUser,
  getProfile,
  createProfile,
  updateProfile,
  listSongsForUser,
  listShareLinks,
  createShareLink,
  deleteShareLink,
  resolveShareLink,
  loginUser,
  logoutUser,
  setSessionUserId,
} from "./store";
import "./styles.css";

const BACKEND_BASE_URL =
  typeof window === "undefined"
    ? "http://127.0.0.1:8000"
    : `${window.location.protocol}//${window.location.hostname}:8000`;

/* ─── GSAP helper (loaded via CDN) ────────────────────────── */
function useGsapFadeUp(ref, deps = []) {
  useEffect(() => {
    const gsap = window.gsap;
    if (!gsap || !ref.current) return;
    gsap.fromTo(
      ref.current.querySelectorAll(".fade-up"),
      { opacity: 0, y: 22 },
      { opacity: 1, y: 0, duration: 0.55, stagger: 0.08, ease: "power2.out" }
    );
  }, deps); // eslint-disable-line react-hooks/exhaustive-deps
}

function useAudioPlayback() {
  const audioRef = useRef(null);
  const [activeSongId, setActiveSongId] = useState(null);
  const [currentSong, setCurrentSong] = useState(null);
  const [playbackError, setPlaybackError] = useState("");

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return undefined;

    function handleEnded() {
      setActiveSongId(null);
    }

    function handleError() {
      setActiveSongId(null);
      setPlaybackError("This song could not be played.");
    }

    audio.addEventListener("ended", handleEnded);
    audio.addEventListener("error", handleError);

    return () => {
      audio.pause();
      audio.removeEventListener("ended", handleEnded);
      audio.removeEventListener("error", handleError);
    };
  }, []);

  async function playSong(song) {
    const audio = audioRef.current;
    const audioUrl = song?.audio_url || null;
    if (!audio || !audioUrl) return;

    setPlaybackError("");
    setCurrentSong(song);

    if (currentSong?.id !== song.id) {
      audio.src = audioUrl;
      audio.load();
    }

    try {
      await audio.play();
      setActiveSongId(song.id);
    } catch {
      setActiveSongId(null);
      setPlaybackError("Playback was blocked. Try pressing play again.");
    }
  }

  async function toggleSong(song) {
    const audio = audioRef.current;
    if (!audio || !song) return;

    if (currentSong?.id === song.id && !audio.paused) {
      audio.pause();
      setActiveSongId(null);
      return;
    }

    if (currentSong?.id === song.id && audio.paused) {
      try {
        await audio.play();
        setActiveSongId(song.id);
      } catch {
        setActiveSongId(null);
        setPlaybackError("Playback was blocked. Try pressing play again.");
      }
      return;
    }

    await playSong(song);
  }

  function stopPlayback() {
    const audio = audioRef.current;
    if (!audio) return;
    audio.pause();
    setActiveSongId(null);
  }

  function clearPlayback() {
    const audio = audioRef.current;
    if (!audio) return;
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
    setActiveSongId(null);
    setCurrentSong(null);
  }

  function seekBy(seconds) {
    const audio = audioRef.current;
    if (!audio) return;
    const duration = Number.isFinite(audio.duration) ? audio.duration : null;
    const nextTime = audio.currentTime + seconds;
    audio.currentTime = duration == null
      ? Math.max(0, nextTime)
      : Math.min(Math.max(0, nextTime), duration);
  }

  return {
    audioRef,
    activeSongId,
    currentSong,
    playbackError,
    clearPlayback,
    playSong,
    setActiveSongId,
    setPlaybackError,
    seekBy,
    stopPlayback,
    toggleSong,
  };
}

/* ─── App Root ──────────────────────────────────────────────── */
export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

function AppRoutes() {
  const [version, setVersion] = useState(0);
  const [currentUser, setCurrentUser] = useState(null);
  const [songs, setSongs] = useState([]);
  const [hydrated, setHydrated] = useState(false);
  const [startupError, setStartupError] = useState("");

  const refresh = () => {
    // Pause route protection until the latest session has been rehydrated.
    setHydrated(false);
    setVersion((v) => v + 1);
  };

  useEffect(() => {
    let active = true;
    async function hydrate() {
      try {
        const user = await getCurrentUser();
        if (!active) return;
        setStartupError("");
        if (!user) { setCurrentUser(null); setSongs([]); return; }
        setCurrentUser(user);
        const nextSongs = await listSongsForUser(user.id);
        if (!active) return;
        setSongs(nextSongs);
      } catch (err) {
        if (!active) return;
        setCurrentUser(null);
        setSongs([]);
        setStartupError(err.message || "Unable to reach the backend.");
      } finally {
        if (active) setHydrated(true);
      }
    }
    void hydrate();
    return () => { active = false; };
  }, [version]);

  /* Poll generating songs */
  useEffect(() => {
    if (!currentUser) return;
    if (!songs.some((s) => s.status === "generating")) return;
    const timer = setInterval(() => {
      void listSongsForUser(currentUser.id).then(setSongs).catch(() => {});
    }, 5000);
    return () => clearInterval(timer);
  }, [currentUser, songs]);

  if (!hydrated) return null;

  return (
    <Routes>
      <Route path="/" element={<Navigate to={currentUser ? "/library" : "/login"} replace />} />
      <Route path="/login" element={<LoginPage currentUser={currentUser} onChange={refresh} startupError={startupError} />} />
      <Route path="/create-user" element={<CreateUserPage currentUser={currentUser} onChange={refresh} startupError={startupError} />} />
      <Route path="/oauth/callback" element={<GoogleCallbackPage onChange={refresh} />} />
      <Route path="/library" element={
        <ProtectedRoute currentUser={currentUser}>
          <LibraryPage currentUser={currentUser} songs={songs} onLogout={refresh} onSongsChange={refresh} />
        </ProtectedRoute>
      } />
      <Route path="/create-song" element={
        <ProtectedRoute currentUser={currentUser}>
          <CreateSongPage currentUser={currentUser} onChange={refresh} />
        </ProtectedRoute>
      } />
      <Route path="/songs/:songId" element={
        <ProtectedRoute currentUser={currentUser}>
          <SongDetailPage currentUser={currentUser} onChange={refresh} />
        </ProtectedRoute>
      } />
      <Route path="/profile" element={
        <ProtectedRoute currentUser={currentUser}>
          <ProfilePage currentUser={currentUser} />
        </ProtectedRoute>
      } />
      <Route path="/s/:token" element={<ShareViewPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function ProtectedRoute({ currentUser, children }) {
  const location = useLocation();
  if (!currentUser) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return children;
}

/* ─── Shell & Nav ───────────────────────────────────────────── */
function Shell({ currentUser, onLogout, children }) {
  const navigate = useNavigate();

  function handleLogout() {
    logoutUser();
    onLogout?.();
    navigate("/login");
  }

  return (
    <div className="site-shell">
      {currentUser && (
        <nav className="topbar">
          <Link to="/library" className="brand-name">Cithai</Link>
          <div className="topnav">
            <Link to="/library">Library</Link>
          </div>
          <div className="profile-hover-card">
            <div className="user-avatar" tabIndex={0} aria-label="Profile menu">
              <span className="user-avatar-icon">
                <i className="icon-head" />
                <i className="icon-body" />
              </span>
            </div>
            <div className="profile-popover">
              <p className="eyebrow">Profile</p>
              <strong>{currentUser.username}</strong>
              <span>{currentUser.email}</span>
              <Link className="btn btn-ghost btn-sm" to="/profile" style={{ marginTop: 10, display: "block", textAlign: "center" }}>
                Edit Profile
              </Link>
              <button
                className="btn btn-ghost btn-sm"
                style={{ marginTop: 6 }}
                onClick={handleLogout}
              >
                Sign out
              </button>
            </div>
          </div>
        </nav>
      )}
      <div className="content-shell">
        {children}
      </div>
    </div>
  );
}

/* ─── Login ─────────────────────────────────────────────────── */
function LoginPage({ currentUser, onChange, startupError }) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [identifier, setIdentifier] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const ref = useRef(null);
  useGsapFadeUp(ref, []);

  if (currentUser) return <Navigate to="/library" replace />;

  const oauthError = searchParams.get("oauth_error");

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await loginUser(identifier);
      onChange();
      navigate("/library");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-layout" ref={ref}>
      <div className="auth-card fade-up">
        <p className="eyebrow">Welcome back</p>
        <h2>Sign in to Cithai</h2>
        <p className="subtitle">Your AI music studio awaits.</p>

        <form className="stack-form" onSubmit={handleSubmit} style={{ marginTop: 24 }}>
          <div className="field">
            <label className="field-label" htmlFor="identifier">Username or Email</label>
            <input
              id="identifier"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="melodymaker or artist@example.com"
              autoComplete="username"
              required
            />
          </div>
          {(startupError || oauthError || error) && (
            <div className="inline-error">{startupError || oauthError || error}</div>
          )}
          <button className="btn btn-primary btn-lg" type="submit" disabled={loading} style={{ marginTop: 4 }}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="divider">or</div>

        <button
          className="btn btn-ghost"
          style={{ width: "100%" }}
          onClick={() => {
            const frontendOrigin = encodeURIComponent(window.location.origin);
            window.location.href = `${BACKEND_BASE_URL}/auth/google/login/?frontend_origin=${frontendOrigin}`;
          }}
        >
          Continue with Google
        </button>

        <Link className="auth-link" to="/create-user">
          No account? <span>Create one</span>
        </Link>
      </div>
    </div>
  );
}

/* ─── Create User ───────────────────────────────────────────── */
function CreateUserPage({ currentUser, onChange, startupError }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const ref = useRef(null);
  useGsapFadeUp(ref, []);

  if (currentUser) return <Navigate to="/library" replace />;

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const user = await createUser(form);
      setSessionUserId(user.id);
      onChange();
      navigate("/library");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function set(key) {
    return (e) => setForm((prev) => ({ ...prev, [key]: e.target.value }));
  }

  return (
    <div className="auth-layout" ref={ref}>
      <div className="auth-card fade-up">
        <p className="eyebrow">Get started</p>
        <h2>Create your account</h2>
        <p className="subtitle">Join Cithai and start generating music.</p>

        <form className="stack-form" onSubmit={handleSubmit} style={{ marginTop: 24 }}>
          <div className="field">
            <label className="field-label" htmlFor="username">Username</label>
            <input
              id="username"
              value={form.username}
              onChange={set("username")}
              placeholder="melodymaker"
              autoComplete="username"
              required
            />
          </div>
          <div className="field">
            <label className="field-label" htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={form.email}
              onChange={set("email")}
              placeholder="artist@example.com"
              autoComplete="email"
              required
            />
          </div>
          {(startupError || error) && (
            <div className="inline-error">{startupError || error}</div>
          )}
          <button className="btn btn-primary btn-lg" type="submit" disabled={loading} style={{ marginTop: 4 }}>
            {loading ? "Creating…" : "Create account"}
          </button>
        </form>

        <Link className="auth-link" to="/login">
          Already have an account? <span>Sign in</span>
        </Link>
      </div>
    </div>
  );
}

/* ─── Google OAuth Callback ─────────────────────────────────── */
function GoogleCallbackPage({ onChange }) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const userId = searchParams.get("user_id");
    const oauthError = searchParams.get("oauth_error");
    if (userId) {
      setSessionUserId(userId);
      onChange();
      navigate("/library", { replace: true });
    } else if (oauthError) {
      navigate(`/login?oauth_error=${encodeURIComponent(oauthError)}`, { replace: true });
    } else {
      navigate("/login", { replace: true });
    }
  }, [navigate, onChange, searchParams]);

  return null;
}

/* ─── Library Page ──────────────────────────────────────────── */
function LibraryPage({ currentUser, songs, onLogout, onSongsChange }) {
  const navigate = useNavigate();
  const [activeFilter, setActiveFilter] = useState("all");
  const [deletingId, setDeletingId] = useState(null);
  const [regeneratingId, setRegeneratingId] = useState(null);
  const [completionNotice, setCompletionNotice] = useState("");
  const ref = useRef(null);
  const previousStatusesRef = useRef(new Map());
  const {
    audioRef,
    activeSongId,
    currentSong,
    playbackError,
    clearPlayback,
    playSong,
    seekBy,
    stopPlayback,
    toggleSong,
  } = useAudioPlayback();
  useGsapFadeUp(ref, [songs.length]);

  const playableSongs = useMemo(
    () => songs.filter((song) => song.status === "ready" && song.audio_url),
    [songs]
  );

  const [playerSnapshot, setPlayerSnapshot] = useState({ currentTime: 0, duration: 0 });

  const filteredSongs = useMemo(() => {
    if (activeFilter === "all") return songs;
    return songs.filter((s) => s.status === activeFilter);
  }, [songs, activeFilter]);

  useEffect(() => {
    const previousStatuses = previousStatusesRef.current;
    const completedSongs = songs.filter(
      (song) => previousStatuses.get(song.id) === "generating" && song.status === "ready"
    );

    if (completedSongs.length > 0) {
      const nextNotice =
        completedSongs.length === 1
          ? `"${completedSongs[0].title}" is ready. You can play it from the Ready tab.`
          : `${completedSongs.length} songs are ready. You can play them from the Ready tab.`;
      setCompletionNotice(nextNotice);
      if (activeFilter === "generating") {
        setActiveFilter("ready");
      }
    }

    previousStatusesRef.current = new Map(songs.map((song) => [song.id, song.status]));
  }, [activeFilter, songs]);

  const filterItems = [
    { key: "all",        label: "All",        count: songs.length },
    { key: "ready",      label: "Ready",      count: songs.filter((s) => s.status === "ready").length },
    { key: "generating", label: "Generating", count: songs.filter((s) => s.status === "generating").length },
    { key: "failed",     label: "Failed",     count: songs.filter((s) => s.status === "failed").length },
  ];

  async function handleDelete(e, songId) {
    e.stopPropagation();
    if (!confirm("Delete this song?")) return;
    if (activeSongId === songId) {
      clearPlayback();
    }
    setDeletingId(songId);
    try {
      await deleteSong(currentUser.id, songId);
      onSongsChange();
    } catch {
      alert("Could not delete the song. Please try again.");
    } finally {
      setDeletingId(null);
    }
  }

  async function handleRegenerate(e, songId) {
    e.stopPropagation();
    setRegeneratingId(songId);
    try {
      const detail = await getSongById(currentUser.id, songId);
      const regeneratedSong = await createSong(currentUser.id, {
        title: detail.title,
        occasion: detail.occasion,
        genre: detail.genre,
        voice_type: detail.voice_type,
        custom_text: detail.custom_text || "",
      });
      await deleteSong(currentUser.id, songId);
      setActiveFilter(regeneratedSong.status === "failed" ? "failed" : "generating");
      onSongsChange();
    } catch {
      alert("Could not regenerate this song. Please try again.");
    } finally {
      setRegeneratingId(null);
    }
  }

  async function handlePlayToggle(e, song) {
    e.stopPropagation();
    await toggleSong(song);
  }

  const currentSongIndex = currentSong
    ? playableSongs.findIndex((song) => song.id === currentSong.id)
    : -1;

  const hasPreviousSong = currentSongIndex > 0;
  const hasNextSong = currentSongIndex >= 0 && currentSongIndex < playableSongs.length - 1;

  async function handlePlayPrevious() {
    if (!hasPreviousSong) return;
    await playSong(playableSongs[currentSongIndex - 1]);
  }

  async function handlePlayNext() {
    if (!hasNextSong) {
      stopPlayback();
      return;
    }
    await playSong(playableSongs[currentSongIndex + 1]);
  }

  async function handleTrackEnded() {
    if (hasNextSong) {
      await playSong(playableSongs[currentSongIndex + 1]);
      return;
    }
    setPlayerSnapshot((snapshot) => ({ ...snapshot, currentTime: 0 }));
  }

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return undefined;

    function syncPlayerSnapshot() {
      setPlayerSnapshot({
        currentTime: audio.currentTime || 0,
        duration: Number.isFinite(audio.duration) ? audio.duration : 0,
      });
    }

    audio.addEventListener("timeupdate", syncPlayerSnapshot);
    audio.addEventListener("loadedmetadata", syncPlayerSnapshot);
    audio.addEventListener("pause", syncPlayerSnapshot);
    audio.addEventListener("play", syncPlayerSnapshot);

    return () => {
      audio.removeEventListener("timeupdate", syncPlayerSnapshot);
      audio.removeEventListener("loadedmetadata", syncPlayerSnapshot);
      audio.removeEventListener("pause", syncPlayerSnapshot);
      audio.removeEventListener("play", syncPlayerSnapshot);
    };
  }, [audioRef]);

  useEffect(() => {
    if (!currentSong) return;
    if (playableSongs.some((song) => song.id === currentSong.id)) return;
    clearPlayback();
    setPlayerSnapshot({ currentTime: 0, duration: 0 });
  }, [clearPlayback, currentSong, playableSongs]);

  const readyCount = songs.filter((s) => s.status === "ready").length;
  const generatingCount = songs.filter((s) => s.status === "generating").length;

  return (
    <Shell currentUser={currentUser} onLogout={onLogout}>
      <main className="library-layout" ref={ref}>
        <section className="library-hero fade-up">
          <div>
            <p className="eyebrow">Your Studio</p>
            <h1>{currentUser.username}&rsquo;s songs</h1>
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 12 }}>
            <div className="hero-stats">
              <div className="stat-chip"><strong>{songs.length}</strong> / 20 songs</div>
              {generatingCount > 0 && (
                <div className="stat-chip" style={{ color: "var(--primary)", borderColor: "rgba(255,77,141,0.25)" }}>
                  <strong>{generatingCount}</strong> generating
                </div>
              )}
            </div>
            <Link className="btn btn-primary" to="/create-song">+ Create Song</Link>
          </div>
        </section>

        <div className="songs-panel fade-up fade-up-delay-1">
          <div className="section-head">
            <h3>Song Library</h3>
            <p className="section-hint">Finished generations appear in <strong>Ready</strong>.</p>
          </div>

          <div className="filter-bar" role="tablist">
            {filterItems.map((item) => (
              <button
                key={item.key}
                role="tab"
                aria-selected={activeFilter === item.key}
                className={`filter-tab${activeFilter === item.key ? " active" : ""}`}
                onClick={() => setActiveFilter(item.key)}
              >
                {item.label} <strong>{item.count}</strong>
              </button>
            ))}
          </div>

          {completionNotice && (
            <div className="library-notice">
              <span>{completionNotice}</span>
              {activeFilter !== "ready" && (
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => setActiveFilter("ready")}
                >
                  View Ready
                </button>
              )}
            </div>
          )}

          {playbackError && (
            <div className="inline-error" style={{ marginBottom: 18 }}>
              {playbackError}
            </div>
          )}

          {filteredSongs.length === 0 ? (
            <div className="song-empty">
              <p style={{ fontSize: "2rem" }}>&#127925;</p>
              <p>
                {activeFilter === "all"
                  ? "No songs yet. Create your first one!"
                  : `No ${activeFilter} songs.`}
              </p>
            </div>
          ) : (
            <div className="song-grid">
              {filteredSongs.map((song) => (
                <SongCard
                  key={song.id}
                  song={song}
                  onClick={() => navigate(`/songs/${song.id}`)}
                  onDelete={(e) => handleDelete(e, song.id)}
                  onRegenerate={(e) => handleRegenerate(e, song.id)}
                  onPlayToggle={(e) => handlePlayToggle(e, song)}
                  isPlaying={activeSongId === song.id}
                  deleting={deletingId === song.id}
                  regenerating={regeneratingId === song.id}
                />
              ))}
            </div>
          )}

          <audio ref={audioRef} preload="none" hidden onEnded={() => { void handleTrackEnded(); }} />
        </div>

        {currentSong && (
          <div className="bottom-player fade-up">
            <div className="bottom-player-track">
              <p className="bottom-player-label">Now playing</p>
              <strong>{currentSong.title}</strong>
              <span>{formatDuration(playerSnapshot.currentTime)} / {formatDuration(playerSnapshot.duration || currentSong.duration || 0)}</span>
            </div>

            <div className="bottom-player-controls">
              <button
                type="button"
                className="player-icon-button"
                onClick={() => { void handlePlayPrevious(); }}
                disabled={!hasPreviousSong}
                aria-label="Previous song"
              >
                <span className="player-skip-icon player-skip-icon-backward" aria-hidden="true" />
              </button>
              <button
                type="button"
                className="player-icon-button"
                onClick={() => seekBy(-10)}
                aria-label="Back 10 seconds"
              >
                <span className="player-jump-label" aria-hidden="true">10</span>
              </button>
              <button
                type="button"
                className="player-icon-button player-icon-button-primary"
                onClick={() => { void toggleSong(currentSong); }}
                aria-label={activeSongId === currentSong.id ? "Pause song" : "Play song"}
              >
                <span className={activeSongId === currentSong.id ? "player-pause-icon" : "player-play-icon"} aria-hidden="true" />
              </button>
              <button
                type="button"
                className="player-icon-button"
                onClick={() => seekBy(10)}
                aria-label="Forward 10 seconds"
              >
                <span className="player-jump-label" aria-hidden="true">10</span>
              </button>
              <button
                type="button"
                className="player-icon-button"
                onClick={() => { void handlePlayNext(); }}
                disabled={!hasNextSong}
                aria-label="Next song"
              >
                <span className="player-skip-icon player-skip-icon-forward" aria-hidden="true" />
              </button>
            </div>
          </div>
        )}
      </main>
    </Shell>
  );
}

/* ─── Song Card ─────────────────────────────────────────────── */
function SongCard({ song, onClick, onDelete, onRegenerate, onPlayToggle, isPlaying, deleting, regenerating }) {
  const date = new Date(song.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  const statusLabel = song.status === "generating" ? "Generating" : song.status === "ready" ? "Ready" : "Failed";

  return (
    <article className="song-card" onClick={onClick} tabIndex={0} onKeyDown={(e) => e.key === "Enter" && onClick()}>
      <div className="song-card-header">
        <span className="song-title">{song.title}</span>
        <span className={`status-pill status-${song.status}`}>
          <span className="status-dot" />
          {statusLabel}
        </span>
      </div>

      {song.status === "generating" && (
        <div className="song-generating-row">
          <Waveform />
          <span className="song-generating-label">AI is composing…</span>
        </div>
      )}

      <div className="song-meta">
        {song.occasion && <span className="meta-tag">{formatLabel(song.occasion)}</span>}
        {song.genre    && <span className="meta-tag">{formatLabel(song.genre)}</span>}
        {song.voice_type && <span className="meta-tag">{formatLabel(song.voice_type)}</span>}
      </div>

      {song.description && song.status === "ready" && (
        <p className="song-description">{song.description}</p>
      )}

      <div className="song-card-footer">
        <span className="song-date">{date}</span>
        <div className="song-card-actions" onClick={(e) => e.stopPropagation()}>
          {song.duration > 0 && (
            <span className="duration-badge">{formatDuration(song.duration)}</span>
          )}
          {song.status === "ready" && song.audio_url && (
            <button
              type="button"
              className={`player-card-button ${isPlaying ? "is-playing" : ""}`}
              onClick={onPlayToggle}
              aria-label={isPlaying ? `Pause ${song.title}` : `Play ${song.title}`}
            >
              <span className={isPlaying ? "player-pause-icon" : "player-play-icon"} aria-hidden="true" />
              <span>{isPlaying ? "Pause" : "Play"}</span>
            </button>
          )}
          {song.status === "failed" && (
            <button
              className="btn btn-ghost btn-sm"
              onClick={onRegenerate}
              disabled={regenerating}
            >
              {regenerating ? "Regenerating…" : "Regenerate"}
            </button>
          )}
          <button
            className="btn btn-danger btn-sm"
            onClick={onDelete}
            disabled={deleting}
          >
            {deleting ? "…" : "Delete"}
          </button>
        </div>
      </div>
    </article>
  );
}

/* ─── Waveform Component ────────────────────────────────────── */
function Waveform() {
  return (
    <div className="waveform" aria-hidden="true">
      {Array.from({ length: 7 }).map((_, i) => (
        <div key={i} className="waveform-bar" />
      ))}
    </div>
  );
}

/* ─── Content Moderation ────────────────────────────────────── */
const BLOCKED_WORDS = [
  "hate", "kill", "murder", "rape", "fuck", "shit", "bitch", "bastard",
  "asshole", "damn", "cunt", "dick", "cock", "pussy", "nigger", "faggot",
  "whore", "slut", "retard", "nazi", "terrorist", "bomb", "suicide",
  "violence", "abuse", "porn", "explicit",
];

function checkModeration(...texts) {
  const lower = texts.join(" ").toLowerCase();
  return BLOCKED_WORDS.filter((w) => lower.includes(w));
}

/* ─── Create Song Page ──────────────────────────────────────── */
function CreateSongPage({ currentUser, onChange }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: "",
    occasion: "",
    genre: "",
    voice_type: "",
    custom_text: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const ref = useRef(null);
  useGsapFadeUp(ref, []);

  const flaggedWords = useMemo(
    () => checkModeration(form.title, form.custom_text),
    [form.title, form.custom_text]
  );

  function set(key) {
    return (e) => setForm((prev) => ({ ...prev, [key]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await createSong(currentUser.id, form);
      onChange();
      navigate("/library");
    } catch (err) {
      setError(err.message || "Failed to create song. Please try again.");
      setLoading(false);
    }
  }

  return (
    <Shell currentUser={currentUser}>
      <main className="form-layout" ref={ref}>
        <div className="form-card fade-up">
          <div className="form-card-head">
            <div>
              <p className="eyebrow">New Song</p>
              <h2>Create a song</h2>
              <p>Fill in the details and let AI compose your track.</p>
            </div>
            <Link className="btn btn-ghost btn-sm" to="/library">Back</Link>
          </div>

          {loading ? (
            <div className="generating-overlay">
              <div className="generating-visual">
                {Array.from({ length: 9 }).map((_, i) => (
                  <div key={i} className="gen-bar" />
                ))}
              </div>
              <div>
                <p className="generating-title">Composing your song…</p>
                <p className="generating-sub">AI is crafting your track. You&apos;ll see it in your library shortly.</p>
              </div>
            </div>
          ) : (
            <form className="song-form" onSubmit={handleSubmit}>
              <label className="full-span">
                <span>Song Title</span>
                <input
                  value={form.title}
                  onChange={set("title")}
                  placeholder="Birthday in Bangkok"
                  maxLength={120}
                  required
                />
              </label>

              <label>
                <span>Occasion</span>
                <select value={form.occasion} onChange={set("occasion")} required>
                  <option value="">Select occasion</option>
                  {occasions.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </label>

              <label>
                <span>Genre</span>
                <select value={form.genre} onChange={set("genre")} required>
                  <option value="">Select genre</option>
                  {genres.map((g) => (
                    <option key={g.value} value={g.value}>{g.label}</option>
                  ))}
                </select>
              </label>

              <label className="full-span">
                <span>Voice Type</span>
                <select value={form.voice_type} onChange={set("voice_type")} required>
                  <option value="">Select voice type</option>
                  {voiceTypes.map((v) => (
                    <option key={v.value} value={v.value}>{v.label}</option>
                  ))}
                </select>
              </label>

              <label className="full-span">
                <span>Custom Text <span style={{ color: "var(--muted)", fontWeight: 400 }}>(optional)</span></span>
                <textarea
                  rows={4}
                  value={form.custom_text}
                  onChange={set("custom_text")}
                  placeholder="Describe the mood, add lyric directions, dedicate to someone special…"
                  maxLength={600}
                />
                <p className="char-count">{form.custom_text.length} / 600</p>
              </label>

              {flaggedWords.length > 0 && (
                <div className="inline-error full-span">
                  <strong>Inappropriate content detected.</strong> Please remove the following word{flaggedWords.length > 1 ? "s" : ""}: {flaggedWords.map((w, i) => (
                    <span key={w}>
                      <mark style={{ background: "rgba(239,68,68,0.18)", color: "inherit", borderRadius: 3, padding: "0 3px" }}>{w}</mark>
                      {i < flaggedWords.length - 1 ? ", " : ""}
                    </span>
                  ))}
                </div>
              )}

              {error && <div className="inline-error full-span">{error}</div>}

              <button
                className="btn btn-primary btn-lg full-span"
                type="submit"
                disabled={flaggedWords.length > 0}
              >
                Generate Song
              </button>
            </form>
          )}
        </div>
      </main>
    </Shell>
  );
}

/* ─── Song Detail Page ──────────────────────────────────────── */
function SongDetailPage({ currentUser, onChange }) {
  const { songId } = useParams();
  const [song, setSong] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [shareLinks, setShareLinks] = useState([]);
  const [newLinkExpirationOption, setNewLinkExpirationOption] = useState("7_days");
  const [creatingLink, setCreatingLink] = useState(false);
  const [showShareForm, setShowShareForm] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const navigate = useNavigate();
  const ref = useRef(null);
  const {
    audioRef,
    activeSongId,
    playbackError,
    setActiveSongId,
    setPlaybackError,
    stopPlayback,
    toggleSong,
  } = useAudioPlayback();

  useEffect(() => {
    let active = true;
    setLoading(true);
    void getSongById(currentUser.id, songId)
      .then((data) => { if (active) { setSong(data); setLoading(false); } })
      .catch(() => { if (active) { setSong(null); setLoading(false); } });
    return () => { active = false; };
  }, [currentUser.id, songId]);

  useEffect(() => {
    if (!song || song.status !== "generating") return;
    const timer = setInterval(() => {
      void getSongById(currentUser.id, songId).then(setSong).catch(() => {});
    }, 5000);
    return () => clearInterval(timer);
  }, [currentUser.id, song, songId]);

  useGsapFadeUp(ref, [loading]);

  useEffect(() => {
    if (!song || song.status === "ready" || activeSongId !== song.id) return;
    stopPlayback();
  }, [activeSongId, song, stopPlayback]);

  async function handleDelete() {
    if (!confirm("Delete this song permanently?")) return;
    setDeleting(true);
    try {
      if (activeSongId === Number(songId)) {
        stopPlayback();
      }
      await deleteSong(currentUser.id, songId);
      onChange();
      navigate("/library");
    } catch {
      alert("Could not delete this song.");
      setDeleting(false);
    }
  }

  async function handleRegenerate() {
    if (!song) return;
    setRegenerating(true);
    try {
      const regeneratedSong = await createSong(currentUser.id, {
        title: song.title,
        occasion: song.occasion,
        genre: song.genre,
        voice_type: song.voice_type,
        custom_text: song.custom_text || "",
      });
      await deleteSong(currentUser.id, songId);
      onChange();
      navigate(`/songs/${regeneratedSong.id}`);
    } catch {
      alert("Could not regenerate this song.");
      setRegenerating(false);
    }
  }

  async function handlePlayToggle() {
    if (!song) return;
    setPlaybackError("");
    await toggleSong(song);
  }

  async function handleDownload() {
    if (!song) return;
    setDownloading(true);
    try { await downloadSong(song); } finally { setDownloading(false); }
  }

  function loadShareLinks() {
    listShareLinks(currentUser.id, songId).then(setShareLinks).catch(() => {});
  }

  useEffect(() => {
    if (song?.status === "ready") loadShareLinks();
  }, [song?.status]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleCreateLink(e) {
    e.preventDefault();
    setCreatingLink(true);
    try {
      const link = await createShareLink(currentUser.id, songId, newLinkExpirationOption);
      setShareLinks((prev) => [...prev, link]);
      setNewLinkExpirationOption("7_days");
      setShowShareForm(false);
    } catch (err) {
      alert(err.message || "Could not create share link.");
    } finally {
      setCreatingLink(false);
    }
  }

  async function handleDeleteLink(token) {
    if (!confirm("Delete this share link?")) return;
    try {
      await deleteShareLink(token);
      setShareLinks((prev) => prev.filter((l) => l.token !== token));
    } catch {
      alert("Could not delete share link.");
    }
  }

  function shareUrl(token) {
    return `${window.location.origin}/s/${token}`;
  }

  const date = song
    ? new Date(song.created_at).toLocaleString("en-US", {
        month: "long", day: "numeric", year: "numeric",
        hour: "2-digit", minute: "2-digit",
      })
    : null;

  return (
    <Shell currentUser={currentUser}>
      <main className="detail-layout" ref={ref}>
        <div className="detail-card fade-up">
          {loading ? (
            <div style={{ padding: "40px 0", textAlign: "center", color: "var(--muted)" }}>
              Loading…
            </div>
          ) : !song ? (
            <div style={{ padding: "40px 0", textAlign: "center" }}>
              <p style={{ color: "var(--muted)" }}>Song not found.</p>
              <Link className="btn btn-ghost btn-sm" to="/library" style={{ marginTop: 16, display: "inline-flex" }}>
                Back to Library
              </Link>
            </div>
          ) : (
            <>
              <div className="detail-header">
                <div className="detail-title-area">
                  <p className="eyebrow">Song Detail</p>
                  <h2>{song.title}</h2>
                  <div className="detail-status" style={{ marginTop: 10 }}>
                    <span className={`status-pill status-${song.status}`}>
                      <span className="status-dot" />
                      {song.status === "generating" ? "Generating" : song.status === "ready" ? "Ready" : "Failed"}
                    </span>
                    {song.duration > 0 && (
                      <span className="duration-badge" style={{ marginLeft: 10 }}>
                        {formatDuration(song.duration)}
                      </span>
                    )}
                  </div>
                </div>
                <Link className="btn btn-ghost btn-sm" to="/library">Back</Link>
              </div>

              {song.status === "generating" && (
                <div className="generating-overlay" style={{ padding: "40px 0" }}>
                  <div className="generating-visual">
                    {Array.from({ length: 9 }).map((_, i) => (
                      <div key={i} className="gen-bar" />
                    ))}
                  </div>
                  <p className="generating-title">AI is composing…</p>
                  <p className="generating-sub">This page refreshes automatically every 5 seconds.</p>
                </div>
              )}

              {song.status === "failed" && (
                <div className="inline-error" style={{ marginBottom: 20 }}>
                  {song.error_message || "Generation failed. Please try creating a new song."}
                </div>
              )}

              {playbackError && (
                <div className="inline-error" style={{ marginBottom: 20 }}>
                  {playbackError}
                </div>
              )}

              <div className="detail-grid">
                <div className="detail-cell">
                  <p className="detail-cell-label">Occasion</p>
                  <p className="detail-cell-value">{formatLabel(song.occasion) || "—"}</p>
                </div>
                <div className="detail-cell">
                  <p className="detail-cell-label">Genre</p>
                  <p className="detail-cell-value">{formatLabel(song.genre) || "—"}</p>
                </div>
                <div className="detail-cell">
                  <p className="detail-cell-label">Voice Type</p>
                  <p className="detail-cell-value">{formatLabel(song.voice_type) || "—"}</p>
                </div>
                <div className="detail-cell">
                  <p className="detail-cell-label">Provider</p>
                  <p className="detail-cell-value">{song.provider || "—"}</p>
                </div>
              </div>

              {song.custom_text && (
                <div className="detail-section">
                  <p className="detail-section-label">Your Directions</p>
                  <p>{song.custom_text}</p>
                </div>
              )}

              {song.description && song.status === "ready" && (
                <div className="detail-section">
                  <p className="detail-section-label">Generated Description</p>
                  <p>{song.description}</p>
                </div>
              )}

              {song.status === "ready" && song.audio_url && (
                <div className="detail-section">
                  <p className="detail-section-label">Playback</p>
                  <div className="detail-player">
                    <button className={`btn ${activeSongId === song.id ? "btn-ghost" : "btn-primary"}`} onClick={handlePlayToggle}>
                      {activeSongId === song.id ? "Pause" : "Play Song"}
                    </button>
                    <audio
                      ref={audioRef}
                      controls
                      preload="none"
                      src={song.audio_url}
                      onPlay={() => setActiveSongId(song.id)}
                      onPause={() => {
                        if (!audioRef.current?.ended) {
                          setActiveSongId(null);
                        }
                      }}
                    />
                  </div>
                </div>
              )}

              {song.status === "ready" && song.audio_url && (
                <div className="detail-section">
                  <p className="detail-section-label">Download</p>
                  <button className="btn btn-ghost" onClick={handleDownload} disabled={downloading}>
                    {downloading ? "Downloading…" : "Download MP3"}
                  </button>
                </div>
              )}

              {song.status === "ready" && (
                <div className="detail-section">
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
                    <p className="detail-section-label" style={{ marginBottom: 0 }}>Share Links</p>
                    <button className="btn btn-ghost btn-sm" onClick={() => setShowShareForm((v) => !v)}>
                      {showShareForm ? "Cancel" : "+ New Link"}
                    </button>
                  </div>

                  {showShareForm && (
                    <form onSubmit={handleCreateLink} style={{ display: "flex", gap: 8, marginBottom: 12, alignItems: "center" }}>
                      <select
                        value={newLinkExpirationOption}
                        onChange={(e) => setNewLinkExpirationOption(e.target.value)}
                        style={{ flex: 1, borderRadius: "var(--radius-sm)", border: "1px solid var(--line)", padding: "6px 10px", background: "var(--bg)" }}
                      >
                        <option value="7_days">7 days</option>
                        <option value="1_month">1 month</option>
                      </select>
                      <button className="btn btn-primary btn-sm" type="submit" disabled={creatingLink}>
                        {creatingLink ? "Creating…" : "Create"}
                      </button>
                    </form>
                  )}

                  {shareLinks.length === 0 ? (
                    <p style={{ color: "var(--muted)", fontSize: "0.85rem" }}>No share links yet.</p>
                  ) : (
                    <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 8 }}>
                      {shareLinks.map((link) => (
                        <li key={link.token} style={{ display: "flex", alignItems: "center", gap: 8, background: "var(--bg-soft)", borderRadius: "var(--radius-sm)", padding: "8px 12px" }}>
                          <span style={{ flex: 1, fontSize: "0.8rem", color: "var(--text-2)", wordBreak: "break-all" }}>
                            {shareUrl(link.token)}
                          </span>
                          <span style={{ fontSize: "0.75rem", color: link.is_valid ? "var(--success)" : "var(--danger)", whiteSpace: "nowrap" }}>
                            {link.is_valid ? `Expires ${link.expiration_date}` : "Expired"}
                          </span>
                          <button
                            className="btn btn-ghost btn-sm"
                            onClick={() => { navigator.clipboard.writeText(shareUrl(link.token)); }}
                          >
                            Copy
                          </button>
                          <button className="btn btn-danger btn-sm" onClick={() => handleDeleteLink(link.token)}>
                            Delete
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              <div className="detail-section">
                <p className="detail-section-label">Created</p>
                <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>{date}</p>
              </div>

              <div className="detail-actions">
                {song.status === "failed" && (
                  <button
                    className="btn btn-ghost"
                    onClick={handleRegenerate}
                    disabled={regenerating}
                  >
                    {regenerating ? "Regenerating…" : "Regenerate Song"}
                  </button>
                )}
                <button
                  className="btn btn-danger"
                  onClick={handleDelete}
                  disabled={deleting}
                >
                  {deleting ? "Deleting…" : "Delete Song"}
                </button>
              </div>
            </>
          )}
        </div>
      </main>
    </Shell>
  );
}

/* ─── Profile Page ──────────────────────────────────────────── */
function ProfilePage({ currentUser }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ gender: "", birthday: "" });
  const [error, setError] = useState("");
  const ref = useRef(null);
  useGsapFadeUp(ref, [loading]);

  useEffect(() => {
    setLoading(true);
    getProfile(currentUser.id)
      .then((p) => { setProfile(p); setForm({ gender: p.gender, birthday: p.birthday }); })
      .catch(() => setProfile(null))
      .finally(() => setLoading(false));
  }, [currentUser.id]);

  function set(key) {
    return (e) => setForm((prev) => ({ ...prev, [key]: e.target.value }));
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      let saved;
      if (profile) {
        saved = await updateProfile(currentUser.id, form);
      } else {
        saved = await createProfile(currentUser.id, form);
      }
      setProfile(saved);
      setForm({ gender: saved.gender, birthday: saved.birthday });
      setEditing(false);
    } catch (err) {
      setError(err.message || "Could not save profile.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Shell currentUser={currentUser}>
      <main className="form-layout" ref={ref}>
        <div className="form-card fade-up">
          <div className="form-card-head">
            <div>
              <p className="eyebrow">Account</p>
              <h2>Your Profile</h2>
            </div>
            <Link className="btn btn-ghost btn-sm" to="/library">Back</Link>
          </div>

          {loading ? (
            <p style={{ color: "var(--muted)" }}>Loading…</p>
          ) : !profile || editing ? (
            <form className="song-form" onSubmit={handleSave}>
              <label className="full-span">
                <span>Username</span>
                <input value={currentUser.username} disabled style={{ opacity: 0.5 }} />
              </label>
              <label className="full-span">
                <span>Email</span>
                <input value={currentUser.email} disabled style={{ opacity: 0.5 }} />
              </label>
              <label>
                <span>Gender</span>
                <select value={form.gender} onChange={set("gender")} required>
                  <option value="">Select gender</option>
                  {genders.map((g) => (
                    <option key={g.value} value={g.value}>{g.label}</option>
                  ))}
                </select>
              </label>
              <label>
                <span>Birthday</span>
                <input type="date" value={form.birthday} onChange={set("birthday")} required />
              </label>
              {error && <div className="inline-error full-span">{error}</div>}
              <div className="full-span" style={{ display: "flex", gap: 8 }}>
                <button className="btn btn-primary" type="submit" disabled={saving}>
                  {saving ? "Saving…" : profile ? "Save Changes" : "Create Profile"}
                </button>
                {profile && (
                  <button className="btn btn-ghost" type="button" onClick={() => { setEditing(false); setError(""); }}>
                    Cancel
                  </button>
                )}
              </div>
            </form>
          ) : (
            <div className="detail-grid">
              <div className="detail-cell">
                <p className="detail-cell-label">Username</p>
                <p className="detail-cell-value">{currentUser.username}</p>
              </div>
              <div className="detail-cell">
                <p className="detail-cell-label">Email</p>
                <p className="detail-cell-value">{currentUser.email}</p>
              </div>
              <div className="detail-cell">
                <p className="detail-cell-label">Gender</p>
                <p className="detail-cell-value">{formatLabel(profile.gender)}</p>
              </div>
              <div className="detail-cell">
                <p className="detail-cell-label">Birthday</p>
                <p className="detail-cell-value">{profile.birthday}</p>
              </div>
              <div className="full-span" style={{ marginTop: 8 }}>
                <button className="btn btn-primary" onClick={() => setEditing(true)}>Edit Profile</button>
              </div>
            </div>
          )}
        </div>
      </main>
    </Shell>
  );
}

/* ─── Share View Page (public) ──────────────────────────────── */
function ShareViewPage() {
  const { token } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { audioRef, activeSongId, setActiveSongId, toggleSong } = useAudioPlayback();
  const ref = useRef(null);
  useGsapFadeUp(ref, [loading]);

  useEffect(() => {
    resolveShareLink(token)
      .then(setData)
      .catch((err) => setError(err.message || "Link not found or expired."))
      .finally(() => setLoading(false));
  }, [token]);

  const mockSong = data ? { id: data.song_id, audio_url: data.audio_url, provider: data.provider } : null;

  return (
    <div className="auth-layout" ref={ref}>
      <div className="auth-card fade-up" style={{ maxWidth: 500 }}>
        <p className="eyebrow">Shared Song</p>
        {loading ? (
          <p style={{ color: "var(--muted)" }}>Loading…</p>
        ) : error ? (
          <p style={{ color: "var(--danger)" }}>{error}</p>
        ) : (
          <>
            <h2 style={{ marginBottom: 4 }}>{data.title}</h2>
            {data.description && <p style={{ color: "var(--muted)", marginBottom: 12 }}>{data.description}</p>}
            {data.duration > 0 && (
              <p style={{ color: "var(--muted)", fontSize: "0.85rem", marginBottom: 12 }}>
                {formatDuration(data.duration)}
              </p>
            )}
            {data.audio_url && (
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                <button
                  className={`btn ${activeSongId === data.song_id ? "btn-ghost" : "btn-primary"}`}
                  onClick={() => toggleSong(mockSong)}
                >
                  {activeSongId === data.song_id ? "Pause" : "Play Song"}
                </button>
                <audio
                  ref={audioRef}
                  controls
                  preload="none"
                  src={data.audio_url}
                  onPlay={() => setActiveSongId(data.song_id)}
                  onPause={() => { if (!audioRef.current?.ended) setActiveSongId(null); }}
                />
              </div>
            )}
            <p style={{ color: "var(--muted)", fontSize: "0.8rem", marginTop: 16 }}>
              Link expires: {data.expiration_date}
            </p>
          </>
        )}
      </div>
    </div>
  );
}

/* ─── Utility Functions ─────────────────────────────────────── */
function formatLabel(value) {
  if (!value) return "";
  return value.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatDuration(seconds) {
  const safeSeconds = Number.isFinite(seconds) ? Math.max(0, Math.floor(seconds)) : 0;
  const m = Math.floor(safeSeconds / 60);
  const s = safeSeconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}
