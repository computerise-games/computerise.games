// The landing page's trailer: muted and looping as the hero's background,
// and "Watch the trailer" plays it fullscreen from the start with sound and
// the browser's own controls. Leaving fullscreen puts it back as it was -
// muted, looping, no controls. With reduced motion asked for it stays on its
// poster until the button is pressed.
(function () {
  const video = document.getElementById("trailer");
  const button = document.getElementById("trailer-full");
  const qualityControl = document.querySelector(".trailer-quality");
  const quality = document.getElementById("trailer-quality");
  if (!video || !button || !qualityControl || !quality) return;
  const still = window.matchMedia("(prefers-reduced-motion: reduce)");
  let pendingRestore = null;
  let pendingSeek = null;

  function background() {
    video.controls = false;
    video.muted = true;
    video.loop = true;
    button.hidden = false;
    qualityControl.hidden = true;
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
    if (video.webkitEnterFullscreen) {
      qualityControl.hidden = true;
      return video.webkitEnterFullscreen();
    }
    return Promise.reject(new Error("no fullscreen"));
  }

  quality.addEventListener("change", () => {
    const source = quality.value;
    if (!source) return;
    const nextSource = new URL(source, document.baseURI).href;
    if (video.currentSrc === nextSource) return;

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
  });

  button.addEventListener("click", () => {
    button.hidden = true;
    video.currentTime = 0;
    video.loop = false;
    video.muted = false;
    video.controls = true;
    video.play().catch(() => {});
    Promise.resolve(enterFullscreen(video.parentElement)).then(() => {
      if (fullscreenElement() === video.parentElement) qualityControl.hidden = false;
    }).catch(() => {
      button.hidden = false;
      qualityControl.hidden = true;
    });
  });

  function onFullscreenChange() {
    qualityControl.hidden = fullscreenElement() !== video.parentElement;
    if (!fullscreenElement()) background();
  }
  document.addEventListener("fullscreenchange", onFullscreenChange);
  document.addEventListener("webkitfullscreenchange", onFullscreenChange);
  video.addEventListener("webkitendfullscreen", background);

  button.hidden = false;
  still.addEventListener("change", background);
  background();
})();
