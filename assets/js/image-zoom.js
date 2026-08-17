(() => {
  const MARGIN = 24;
  const overlay = document.createElement("div");
  overlay.className = "pixel-zoom-overlay";
  overlay.hidden = true;
  overlay.setAttribute("role", "dialog");
  overlay.setAttribute("aria-modal", "true");
  overlay.setAttribute("aria-label", "Full-resolution image viewer");

  const status = document.createElement("span");
  status.className = "pixel-zoom-status";
  status.textContent = "Loading full-resolution image…";
  overlay.append(status);
  document.body.append(overlay);

  let zoomedImage = null;
  let previousOverflow = "";

  function viewportSize() {
    const viewport = window.visualViewport;
    return {
      width: viewport ? viewport.width : window.innerWidth,
      height: viewport ? viewport.height : window.innerHeight,
      offsetLeft: viewport ? viewport.offsetLeft : 0,
      offsetTop: viewport ? viewport.offsetTop : 0,
    };
  }

  function sizeImage() {
    if (!zoomedImage || !zoomedImage.naturalWidth || !zoomedImage.naturalHeight) return;

    const viewport = viewportSize();
    const pixelRatio = Math.max(window.devicePixelRatio || 1, 1);

    // One source pixel should cover at most one physical display pixel. Large
    // images are reduced to fit the viewport; small images are never upscaled.
    const nativeWidth = zoomedImage.naturalWidth / pixelRatio;
    const nativeHeight = zoomedImage.naturalHeight / pixelRatio;
    const availableWidth = Math.max(viewport.width - MARGIN * 2, 1);
    const availableHeight = Math.max(viewport.height - MARGIN * 2, 1);
    const scale = Math.min(1, availableWidth / nativeWidth, availableHeight / nativeHeight);

    zoomedImage.style.width = `${Math.round(nativeWidth * scale * 100) / 100}px`;
    zoomedImage.style.height = `${Math.round(nativeHeight * scale * 100) / 100}px`;
    overlay.style.left = `${viewport.offsetLeft}px`;
    overlay.style.top = `${viewport.offsetTop}px`;
    overlay.style.width = `${viewport.width}px`;
    overlay.style.height = `${viewport.height}px`;
  }

  function closeZoom() {
    if (overlay.hidden) return;
    overlay.hidden = true;
    overlay.classList.remove("is-open", "is-loading");
    zoomedImage?.remove();
    zoomedImage = null;
    document.documentElement.style.overflow = previousOverflow;
  }

  function openZoom(sourceImage) {
    const source = sourceImage.dataset.zoomSrc || sourceImage.currentSrc || sourceImage.src;
    if (!source) return;

    closeZoom();
    zoomedImage = new Image();
    zoomedImage.className = "pixel-zoom-image";
    zoomedImage.alt = sourceImage.alt || "";
    zoomedImage.decoding = "async";

    overlay.hidden = false;
    overlay.classList.add("is-open", "is-loading");
    previousOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = "hidden";

    zoomedImage.addEventListener("load", () => {
      if (!zoomedImage) return;
      sizeImage();
      overlay.append(zoomedImage);
      overlay.classList.remove("is-loading");
    }, { once: true });

    zoomedImage.addEventListener("error", closeZoom, { once: true });
    zoomedImage.src = source;
  }

  document.addEventListener("click", (event) => {
    if (event.target === overlay || event.target === zoomedImage) {
      closeZoom();
      return;
    }

    const image = event.target.closest?.("img:not(.nozoom)");
    if (!image) return;
    event.preventDefault();
    openZoom(image);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeZoom();
  });

  window.addEventListener("resize", sizeImage);
  window.visualViewport?.addEventListener("resize", sizeImage);
  window.visualViewport?.addEventListener("scroll", sizeImage);
})();
