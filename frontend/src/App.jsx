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
import { genres, occasions, voiceTypes } from "./options";
import {
  createSong,
  createUser,
  deleteSong,
  getSongById,
  getCurrentUser,
  listSongsForUser,
  loginUser,
  logoutUser,
  setSessionUserId,
} from "./store";
import "./styles.css";

const BACKEND_BASE_URL = "http://127.0.0.1:8000";

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

  const refresh = () => setVersion((v) => v + 1);

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
      <Route path="/auth/google/callback" element={<GoogleCallbackPage onChange={refresh} />} />
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
              <button
                className="btn btn-ghost btn-sm"
                style={{ marginTop: 10 }}
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
          onClick={() => { window.location.href = `${BACKEND_BASE_URL}/auth/google/login/`; }}
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
  const ref = useRef(null);
  useGsapFadeUp(ref, [songs.length]);

  const filteredSongs = useMemo(() => {
    if (activeFilter === "all") return songs;
    return songs.filter((s) => s.status === activeFilter);
  }, [songs, activeFilter]);

  const filterItems = [
    { key: "all",        label: "All",        count: songs.length },
    { key: "ready",      label: "Ready",      count: songs.filter((s) => s.status === "ready").length },
    { key: "generating", label: "Generating", count: songs.filter((s) => s.status === "generating").length },
    { key: "failed",     label: "Failed",     count: songs.filter((s) => s.status === "failed").length },
  ];

  async function handleDelete(e, songId) {
    e.stopPropagation();
    if (!confirm("Delete this song?")) return;
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
      await createSong(currentUser.id, {
        title: detail.title,
        occasion: detail.occasion,
        genre: detail.genre,
        voice_type: detail.voice_type,
        custom_text: detail.custom_text || "",
      });
      setActiveFilter("generating");
      onSongsChange();
    } catch {
      alert("Could not regenerate this song. Please try again.");
    } finally {
      setRegeneratingId(null);
    }
  }

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
                  deleting={deletingId === song.id}
                  regenerating={regeneratingId === song.id}
                />
              ))}
            </div>
          )}
        </div>
      </main>
    </Shell>
  );
}

/* ─── Song Card ─────────────────────────────────────────────── */
function SongCard({ song, onClick, onDelete, onRegenerate, deleting, regenerating }) {
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

              {error && <div className="inline-error full-span">{error}</div>}

              <button className="btn btn-primary btn-lg full-span" type="submit">
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
  const navigate = useNavigate();
  const ref = useRef(null);

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

  async function handleDelete() {
    if (!confirm("Delete this song permanently?")) return;
    setDeleting(true);
    try {
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
      await createSong(currentUser.id, {
        title: song.title,
        occasion: song.occasion,
        genre: song.genre,
        voice_type: song.voice_type,
        custom_text: song.custom_text || "",
      });
      onChange();
      navigate("/library");
    } catch {
      alert("Could not regenerate this song.");
      setRegenerating(false);
    }
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

/* ─── Utility Functions ─────────────────────────────────────── */
function formatLabel(value) {
  if (!value) return "";
  return value.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}
