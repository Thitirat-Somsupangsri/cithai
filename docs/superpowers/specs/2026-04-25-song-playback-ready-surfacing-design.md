## Song Playback And Ready-State Surfacing

### Goal
Make it obvious where a generated song appears after completion and add direct playback for songs that already have a playable `audio_url`.

### Scope
- Frontend-only changes in the React app.
- No backend API changes.
- Use existing song payload fields, especially `status` and `audio_url`.

### Current Constraints
- Songs already appear in the personal library regardless of status.
- Only `ready` songs should be playable.
- The backend already returns `audio_url` for ready songs.
- The library already polls while songs are generating.

### Chosen Approach
Use explicit playback controls in the library and detail page, with one active player per page. When a song transitions from `generating` to `ready`, the library should make that completion visible and move the user toward the `Ready` view.

### Library Behavior
- Each ready song with an `audio_url` shows a `Play Song` button.
- Clicking `Play Song` starts playback for that song and changes the button to `Pause`.
- Only one song can play at a time within the library page.
- If another song is played, the previous one stops.
- If playback ends, the UI returns to the idle state.
- If the user is currently looking at the `Generating` tab and a song completes, the library automatically switches to the `Ready` tab.
- When at least one song has just completed, the library shows a short completion notice above the list.

### Song Detail Behavior
- A ready song with an `audio_url` shows a `Play Song` / `Pause` control.
- The detail page also shows a native audio player for scrubbing and replay.
- Generating and failed songs do not show playback controls.

### Messaging
- The library UI should explicitly indicate that completed generations appear in the `Ready` tab.
- The completion notice should be short and actionable, not a modal.

### Error Handling
- If the browser cannot start playback, show a small inline message on the current page.
- Playback errors do not change song status or backend data.

### Verification
- `npm run build` must pass.
- Ready songs render playback controls only when `audio_url` exists.
- A generating-to-ready transition changes the library presentation as designed.
