// The landing page's trailer: muted and looping as the hero's background,
// and "Watch the trailer" plays it fullscreen from the start with sound and
// the browser's own controls. Leaving fullscreen puts it back as it was -
// muted, looping, no controls. With reduced motion asked for it stays on its
// poster until the button is pressed.
(function () {
  const video = document.getElementById("trailer");
  const button = document.getElementById("trailer-full");
  if (!video || !button) return;
  const still = window.matchMedia("(prefers-reduced-motion: reduce)");

  function background() {
    video.controls = false;
    video.muted = true;
    video.loop = true;
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
    if (element.webkitEnterFullscreen) return element.webkitEnterFullscreen();
    return Promise.reject(new Error("no fullscreen"));
  }

  button.addEventListener("click", () => {
    video.currentTime = 0;
    video.loop = false;
    video.muted = false;
    video.controls = true;
    video.play().catch(() => {});
    Promise.resolve(enterFullscreen(video)).catch(() => {
      // No fullscreen on offer: it plays in place with sound and controls.
    });
  });

  function onFullscreenChange() {
    if (!fullscreenElement()) background();
  }
  document.addEventListener("fullscreenchange", onFullscreenChange);
  document.addEventListener("webkitfullscreenchange", onFullscreenChange);
  video.addEventListener("webkitendfullscreen", background);

  button.hidden = false;
  still.addEventListener("change", background);
  background();
})();
