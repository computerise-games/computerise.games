// The landing page's trailer: muted and looping as the hero's background,
// with quality picked from the browser's network estimate. "Watch the trailer"
// plays it fullscreen from the start with sound and native video controls.
(function () {
  const video = document.getElementById("trailer");
  const button = document.getElementById("trailer-full");
  if (!video || !button) return;
  const still = window.matchMedia("(prefers-reduced-motion: reduce)");
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  const sources = {
    low: "video/new-worlds-trailer-720p30.mp4",
    standard: "video/new-worlds-trailer-1080p30.mp4",
    high: "video/new-worlds-trailer.mp4",
  };
  const qualityRank = new Map([
    [sources.low, 0],
    [sources.standard, 1],
    [sources.high, 2],
  ]);
  let pendingRestore = null;
  let pendingSeek = null;
  let stallTimer = null;
  let qualityLimit = 2;

  function preferredSource() {
    if (!connection) return sources.low;
    if (connection.saveData) return sources.low;
    if (Number.isFinite(connection.downlink)) {
      if (connection.downlink < 2.5) return sources.low;
      if (connection.downlink < 5) return sources.standard;
      return sources.high;
    }
    if (connection.effectiveType === "slow-2g" || connection.effectiveType === "2g") {
      return sources.low;
    }
    if (connection.effectiveType === "3g") return sources.low;
    if (connection.effectiveType === "4g") return sources.high;
    return sources.standard;
  }

  function clearStallTimer() {
    if (stallTimer !== null) {
      clearTimeout(stallTimer);
      stallTimer = null;
    }
  }

  function downgradeAfterStall() {
    clearStallTimer();
    const stalledAt = video.currentTime;
    stallTimer = window.setTimeout(() => {
      stallTimer = null;
      if (
        video.paused ||
        video.currentTime - stalledAt >= 0.25
      ) return;

      const currentSource = new URL(video.currentSrc, document.baseURI).pathname.slice(1);
      const currentRank = qualityRank.get(currentSource);
      if (currentRank === undefined || currentRank === 0) return;
      qualityLimit = currentRank - 1;
      updateSource();
    }, 5000);
  }

  function updateSource() {
    const requestedSource = preferredSource();
    const requestedRank = qualityRank.get(requestedSource) ?? 0;
    const source = [...qualityRank.entries()]
      .find(([, rank]) => rank === Math.min(requestedRank, qualityLimit))?.[0]
      ?? sources.low;
    const nextSource = new URL(source, document.baseURI).href;
    if (video.currentSrc === nextSource || video.src === nextSource) return;

    clearStallTimer();
    const time = video.currentTime;
    const resume = !video.paused;
    if (pendingRestore) video.removeEventListener("loadedmetadata", pendingRestore);
    if (pendingSeek) video.removeEventListener("seeked", pendingSeek);
    pendingRestore = () => {
      pendingRestore = null;
      const targetTime = Number.isFinite(video.duration) ? Math.min(time, video.duration) : 0;
      if (Math.abs(video.currentTime - targetTime) < 0.01) {
        if (resume) video.play().catch(() => {});
        return;
      }
      pendingSeek = () => {
        pendingSeek = null;
        if (resume) video.play().catch(() => {});
      };
      video.addEventListener("seeked", pendingSeek, { once: true });
      video.currentTime = targetTime;
    };
    video.addEventListener("loadedmetadata", pendingRestore, { once: true });
    video.src = source;
    video.load();
  }

  function background() {
    video.controls = false;
    video.muted = true;
    video.loop = true;
    button.hidden = false;
    updateSource();
    if (still.matches) {
      video.pause();
    } else {
      video.play().catch(() => {});
    }
  }

  function fullscreenElement() {
    return document.fullscreenElement || document.webkitFullscreenElement || null;
  }

  function enterFullscreen(element) {
    if (element.requestFullscreen) return element.requestFullscreen();
    if (element.webkitRequestFullscreen) return element.webkitRequestFullscreen();
    // iOS Safari: only the video itself can go fullscreen.
    if (video.webkitEnterFullscreen) return video.webkitEnterFullscreen();
    return Promise.reject(new Error("no fullscreen"));
  }

  button.addEventListener("click", () => {
    button.hidden = true;
    video.currentTime = 0;
    video.loop = false;
    video.muted = false;
    video.controls = true;
    updateSource();
    video.play().catch(() => {});
    Promise.resolve(enterFullscreen(video)).catch(() => {
      button.hidden = false;
    });
  });

  function onFullscreenChange() {
    if (!fullscreenElement()) background();
  }
  document.addEventListener("fullscreenchange", onFullscreenChange);
  document.addEventListener("webkitfullscreenchange", onFullscreenChange);
  video.addEventListener("webkitendfullscreen", background);
  video.addEventListener("waiting", downgradeAfterStall);
  video.addEventListener("stalled", downgradeAfterStall);
  video.addEventListener("playing", clearStallTimer);

  button.hidden = false;
  still.addEventListener("change", background);
  if (connection && connection.addEventListener) {
    connection.addEventListener("change", updateSource);
  } else if (connection) {
    connection.onchange = updateSource;
  }
  background();
})();
