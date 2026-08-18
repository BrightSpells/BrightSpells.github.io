(() => {
  const entries = Array.from(document.querySelectorAll("[data-media-entry]"));
  const archiveEntries = Array.from(document.querySelectorAll("[data-media-archive-entry]"));
  const buttons = Array.from(document.querySelectorAll("button[data-media-year]"));
  const counters = Array.from(document.querySelectorAll("[data-media-count]"));
  const detailList = document.querySelector("[data-media-detail-list]");
  const archiveList = document.querySelector("[data-media-archive-list]");
  const empty = document.querySelector("[data-media-empty]");

  if (!entries.length || !buttons.length) return;

  const availableYears = new Set(entries.map((entry) => entry.dataset.mediaYear));
  const requestedYear = window.location.hash.slice(1).toLowerCase();
  const initialYear = requestedYear === "all"
    ? "all"
    : availableYears.has(requestedYear)
    ? requestedYear
    : buttons.find((button) => button.dataset.mediaYear !== "all")?.dataset.mediaYear || "all";

  const showYear = (year, updateUrl = true) => {
    let visibleCount = 0;
    const typeCounts = { series: 0, film: 0, book: 0 };

    const showingArchive = year === "all";
    if (detailList) detailList.hidden = showingArchive;
    if (archiveList) archiveList.hidden = !showingArchive;

    entries.forEach((entry) => {
      const visible = !showingArchive && entry.dataset.mediaYear === year;
      entry.hidden = !visible;
      if (visible) {
        visibleCount += 1;
        if (entry.dataset.mediaType in typeCounts) typeCounts[entry.dataset.mediaType] += 1;
      }
    });

    if (showingArchive) {
      archiveEntries.forEach((entry) => {
        visibleCount += 1;
        if (entry.dataset.mediaType in typeCounts) typeCounts[entry.dataset.mediaType] += 1;
      });
    }

    buttons.forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.mediaYear === year));
    });
    counters.forEach((counter) => {
      counter.textContent = typeCounts[counter.dataset.mediaCount] || 0;
    });
    if (empty) empty.hidden = visibleCount !== 0;

    if (updateUrl) {
      const nextUrl = year === "all"
        ? `${window.location.pathname}${window.location.search}`
        : `${window.location.pathname}${window.location.search}#${year}`;
      window.history.replaceState(null, "", nextUrl);
    }
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => showYear(button.dataset.mediaYear));
  });
  showYear(initialYear, false);
})();
