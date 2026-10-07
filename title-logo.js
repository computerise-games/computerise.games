// The game's main-menu NEW WORLDS title (ui/title_logo.gd in the game repo):
// two baked layers - lettering plus the orbit's far half, and the orbit's
// near half - with Terra's loading loop turning between them as the O, and
// the player's ship riding that orbit. Drawn at a whole-number pixel scale
// so the pixel grid never smears; the layers hold FACTOR texels per art px.
(function () {
  const FACTOR = 3;
  const FPS = 25;
  const LOOP_FRAMES = 161;
  const LOOP_COLS = 13;
  const LOOP_CELL = 165;
  const TERRA_OFFSET = [285, 5];
  const ORBIT_CENTER = [312, 32];
  const ORBIT_RADII = [52, 11];
  const ORBIT_TILT = -Math.PI / 20;
  const ORBIT_PHASE = 0.6;

  const canvas = document.getElementById("title-logo");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const still = window.matchMedia("(prefers-reduced-motion: reduce)");

  function load(src) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });
  }

  Promise.all(
    ["back", "front", "loop", "ship"].map((k) => load(canvas.dataset[k]))
  ).then(([back, front, loop, ship]) => {
    const nativeW = back.naturalWidth / FACTOR;
    const nativeH = back.naturalHeight / FACTOR;
    let scale = 1;

    function layout() {
      const dpr = window.devicePixelRatio || 1;
      const room = canvas.parentElement.clientWidth * dpr;
      scale = Math.max(1, Math.min(4, Math.floor(room / nativeW)));
      canvas.width = nativeW * scale;
      canvas.height = nativeH * scale;
      canvas.style.width = canvas.width / dpr + "px";
      canvas.style.height = canvas.height / dpr + "px";
      ctx.imageSmoothingEnabled = false;
    }

    function rotate([x, y], a) {
      const c = Math.cos(a), s = Math.sin(a);
      return [x * c - y * s, x * s + y * c];
    }

    function drawShip(t) {
      const local = rotate([ORBIT_RADII[0] * Math.cos(t), ORBIT_RADII[1] * Math.sin(t)], ORBIT_TILT);
      const vel = rotate([-ORBIT_RADII[0] * Math.sin(t), ORBIT_RADII[1] * Math.cos(t)], ORBIT_TILT);
      const at = [Math.round(ORBIT_CENTER[0] + local[0]), Math.round(ORBIT_CENTER[1] + local[1])];
      // The sprite's nose points up (-Y).
      const heading = Math.atan2(vel[1], vel[0]) + Math.PI / 2;
      ctx.setTransform(1, 0, 0, 1, at[0] * scale, at[1] * scale);
      ctx.rotate(heading);
      ctx.scale(scale / FACTOR, scale / FACTOR);
      ctx.drawImage(ship, -ship.naturalWidth / 2, -ship.naturalHeight / 2);
    }

    function draw(frame) {
      // One lap of the orbit per turn of the globe, so the loop stays in step.
      const t = (2 * Math.PI * frame) / LOOP_FRAMES + ORBIT_PHASE;
      const farSide = Math.sin(t) <= 0;
      const k = scale / FACTOR;

      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.setTransform(k, 0, 0, k, 0, 0);
      ctx.drawImage(back, 0, 0);
      if (farSide) drawShip(t);
      ctx.setTransform(k, 0, 0, k, 0, 0);
      ctx.drawImage(
        loop,
        (frame % LOOP_COLS) * LOOP_CELL, Math.floor(frame / LOOP_COLS) * LOOP_CELL,
        LOOP_CELL, LOOP_CELL,
        TERRA_OFFSET[0] * FACTOR, TERRA_OFFSET[1] * FACTOR,
        LOOP_CELL, LOOP_CELL
      );
      ctx.drawImage(front, 0, 0);
      if (!farSide) drawShip(t);
    }

    // The loop has 25 frames a second, so the canvas is redrawn only when the
    // frame changes, not on every display refresh. It stops altogether while
    // the title is off-screen or the tab hidden, and picks up where it left
    // off rather than jumping ahead.
    let elapsed = 0;
    let last = null;
    let shown = -1;
    let onScreen = true;
    let running = false;

    function frameNow() {
      return Math.floor(elapsed * FPS) % LOOP_FRAMES;
    }

    function tick(now) {
      if (!active()) {
        running = false;
        last = null;
        return;
      }
      if (last !== null) elapsed += Math.min(now - last, 250) / 1000;
      last = now;
      const frame = frameNow();
      if (frame !== shown) {
        shown = frame;
        draw(frame);
      }
      requestAnimationFrame(tick);
    }

    function active() {
      return onScreen && !document.hidden && !still.matches;
    }

    function wake() {
      if (active() && !running) {
        running = true;
        requestAnimationFrame(tick);
      }
    }

    layout();
    draw(frameNow());
    window.addEventListener("resize", () => {
      layout();
      draw(shown = frameNow());
    });
    document.addEventListener("visibilitychange", wake);
    still.addEventListener("change", wake);
    if ("IntersectionObserver" in window) {
      new IntersectionObserver((entries) => {
        onScreen = entries[entries.length - 1].isIntersecting;
        wake();
      }).observe(canvas);
    }
    wake();
  });
})();
