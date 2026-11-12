(function () {
  const audio = document.getElementById("quran-audio");
  if (!audio) return;
  const title = document.getElementById("player-title");
  const status = document.getElementById("player-status");
  const toggle = document.getElementById("player-toggle");
  const reciter = document.getElementById("reciter-select");
  const prev = document.getElementById("player-prev");
  const next = document.getElementById("player-next");
  let playlist = [];
  let index = 0;
  let playing = false;

  function audioUrl(item) {
    return "https://cdn.islamic.network/quran/audio/128/" + encodeURIComponent(reciter.value) + "/" + item.global + ".mp3";
  }
  function loadCurrent(autoplay) {
    if (!playlist.length || !playlist[index]) return;
    const item = playlist[index];
    audio.src = audioUrl(item);
    title.textContent = "Surah " + item.surah + " · Ayah " + item.verse;
    status.textContent = "Reciter: " + reciter.options[reciter.selectedIndex].text;
    if (autoplay) {
      audio.play().then(() => { playing = true; toggle.textContent = "Ⅱ"; })
        .catch(() => { playing = false; toggle.textContent = "▶"; status.textContent = "Audio could not start. Check your connection and try again."; });
    }
  }
  function start(items, startIndex) {
    playlist = items;
    index = Math.max(0, startIndex || 0);
    loadCurrent(true);
  }
  document.querySelectorAll(".verse-play").forEach((button) => {
    button.addEventListener("click", () => {
      const current = {global: Number(button.dataset.globalAyah), surah: Number(button.dataset.surah), verse: Number(button.dataset.verse)};
      const all = Array.isArray(window.QURAN_PLAYLIST) ? window.QURAN_PLAYLIST : [current];
      const found = all.findIndex((item) => item.global === current.global);
      start(found >= 0 ? all : [current], found >= 0 ? found : 0);
    });
  });
  const fullSurah = document.getElementById("play-surah");
  if (fullSurah) fullSurah.addEventListener("click", () => {
    if (Array.isArray(window.QURAN_PLAYLIST) && window.QURAN_PLAYLIST.length) start(window.QURAN_PLAYLIST, 0);
  });
  toggle.addEventListener("click", () => {
    if (!playlist.length) { const first = document.querySelector(".verse-play"); if (first) first.click(); return; }
    if (audio.paused) audio.play().catch(() => {});
    else audio.pause();
  });
  audio.addEventListener("play", () => { playing = true; toggle.textContent = "Ⅱ"; });
  audio.addEventListener("pause", () => { playing = false; toggle.textContent = "▶"; });
  audio.addEventListener("ended", () => {
    if (index < playlist.length - 1) { index += 1; loadCurrent(true); }
    else { playing = false; toggle.textContent = "▶"; status.textContent = "Finished."; }
  });
  prev.addEventListener("click", () => { if (playlist.length && index > 0) { index -= 1; loadCurrent(true); } });
  next.addEventListener("click", () => { if (playlist.length && index < playlist.length - 1) { index += 1; loadCurrent(true); } });
  reciter.addEventListener("change", () => { if (playlist.length) loadCurrent(playing); });
})();