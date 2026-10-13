// The header's Share button: the device's own share sheet where there is one
// (phones, mostly), or the page's link copied to the clipboard.
(function () {
  const button = document.getElementById("share");
  if (!button) return;
  const label = button.getAttribute("aria-label");
  function said(text) {
    button.dataset.said = text;
    button.setAttribute("aria-label", text);
    setTimeout(() => {
      delete button.dataset.said;
      button.setAttribute("aria-label", label);
    }, 1800);
  }
  button.addEventListener("click", async () => {
    const data = { title: document.title, url: location.href.split("#")[0] };
    if (navigator.share) {
      try {
        await navigator.share(data);
      } catch (e) {
        // Dismissed, most likely - nothing to say.
      }
      return;
    }
    try {
      await navigator.clipboard.writeText(data.url);
      said("Link copied");
    } catch (e) {
      prompt("Copy this link:", data.url);
    }
  });
})();
