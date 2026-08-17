function _getDefaultPackeryOptions() {
  return {
    percentPosition: true,
    gutter: 5,
    resize: true,
  };
}

function _getPackeryOptions(nodeGallery) {
  const defaults = _getDefaultPackeryOptions();
  const {
    packeryGutter,
    packeryPercentPosition,
    packeryResize,
  } = nodeGallery.dataset;

  return {
    percentPosition:
      packeryPercentPosition !== undefined
        ? packeryPercentPosition === "true"
        : defaults.percentPosition,
    gutter:
      packeryGutter !== undefined ? parseInt(packeryGutter, 10) : defaults.gutter,
    resize:
      packeryResize !== undefined ? packeryResize === "true" : defaults.resize,
  };
}

(function initGalleries() {
  function initialize() {
    document.querySelectorAll(".gallery").forEach((nodeGallery) => {
      const packery = new Packery(
        nodeGallery,
        _getPackeryOptions(nodeGallery),
      );

      const relayout = () => packery.layout();

      nodeGallery.querySelectorAll("img").forEach((image) => {
        if (!image.complete) {
          image.addEventListener("load", relayout, { once: true });
          image.addEventListener("error", relayout, { once: true });
        }
      });

      if (document.fonts?.ready) {
        document.fonts.ready.then(relayout);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
