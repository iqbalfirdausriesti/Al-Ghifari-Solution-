(function () {
  "use strict";

  // 1. SLIDER FLASH SALE: AUTO-SLIDE PELAN + TOMBOL KIRI/KANAN
  function initFlashSaleSlider() {
    const row = document.getElementById("row");
    if (!row || row.dataset.agsReady) return;
    row.dataset.agsReady = "true";

    const wrap = document.createElement("div");
    wrap.className = "ags-row-wrap";
    row.parentNode.insertBefore(wrap, row);
    wrap.appendChild(row);

    const prevBtn = document.createElement("button");
    prevBtn.type = "button";
    prevBtn.className = "ags-row-arr l";
    prevBtn.setAttribute("aria-label", "Geser kiri");
    prevBtn.innerHTML = "&#10094;";

    const nextBtn = document.createElement("button");
    nextBtn.type = "button";
    nextBtn.className = "ags-row-arr r";
    nextBtn.setAttribute("aria-label", "Geser kanan");
    nextBtn.innerHTML = "&#10095;";

    wrap.appendChild(prevBtn);
    wrap.appendChild(nextBtn);

    let paused = false;
    let resumeTimer = null;
    const speed = 0.55; // Kecepatan geser pelan otomatis

    function pauseFor(ms) {
      paused = true;
      clearTimeout(resumeTimer);
      resumeTimer = setTimeout(() => {
        paused = false;
      }, ms);
    }

    row.addEventListener("mouseenter", () => { paused = true; });
    row.addEventListener("mouseleave", () => { paused = false; });
    row.addEventListener("touchstart", () => { paused = true; }, { passive: true });
    row.addEventListener("touchend", () => { pauseFor(1500); });
    row.addEventListener("wheel", () => { pauseFor(1500); }, { passive: true });

    prevBtn.addEventListener("click", () => {
      pauseFor(1400);
      row.scrollBy({ left: -240, behavior: "smooth" });
    });

    nextBtn.addEventListener("click", () => {
      pauseFor(1400);
      row.scrollBy({ left: 240, behavior: "smooth" });
    });

    function autoSlide() {
      if (!paused && row.offsetParent !== null && row.scrollWidth > row.clientWidth) {
        row.scrollLeft += speed;
        if (row.scrollLeft + row.clientWidth >= row.scrollWidth - 2) {
          row.scrollLeft = 0;
        }
      }
      requestAnimationFrame(autoSlide);
    }

    requestAnimationFrame(autoSlide);
  }

  // 2. AUDIO VIDEO IKLAN: AUTO-NYALA SAAT MASUK, AUTO-MATI SAAT KELUAR
  function initVideoAutoAudio() {
    const vview = document.getElementById("vview");
    const soundBtn = document.getElementById("vsn");
    const tip = document.getElementById("vtp");
    if (!vview || !soundBtn || vview.dataset.agsAudioReady) return;
    vview.dataset.agsAudioReady = "true";

    let isSectionVisible = false;
    let manuallyMuted = false;

    function getActiveVideo() {
      const activeSlide = vview.querySelector(".vs-s.on video");
      return activeSlide || vview.querySelector("video");
    }

    function syncSoundUI(isOn) {
      const icon = document.getElementById("vsi");
      if (icon) {
        icon.innerHTML = isOn
          ? '<path d="M11 5L6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 010 7M18.5 5.5a9 9 0 010 13"/>'
          : '<path d="M11 5L6 9H3v6h3l5 4z"/><path d="M16 9l5 6M21 9l-5 6"/>';
      }
      soundBtn.classList.toggle("hint", !isOn);
      if (tip) tip.classList.toggle("off", isOn);
    }

    // Tetap dukung klik tombol sound manual (#vsn)
    soundBtn.addEventListener("click", () => {
      setTimeout(() => {
        const vid = getActiveVideo();
        if (!vid) return;
        manuallyMuted = vid.muted;
        syncSoundUI(!vid.muted);
      }, 20);
    });

    async function turnAudioOn() {
      isSectionVisible = true;
      const vid = getActiveVideo();
      if (!vid) return;

      if (manuallyMuted) {
        vid.muted = true;
        vid.play().catch(() => {});
        syncSoundUI(false);
        return;
      }

      vid.muted = false;
      try {
        await vid.play();
        syncSoundUI(true);
      } catch (err) {
        // Fallback kebijakan autoplay browser: nyala otomatis saat sentuhan/klik pertama di area video
        vid.muted = true;
        vid.play().catch(() => {});
        syncSoundUI(false);

        const unlockOnGesture = () => {
          if (isSectionVisible && !manuallyMuted) {
            const currentVid = getActiveVideo();
            if (currentVid) {
              currentVid.muted = false;
              currentVid.play().catch(() => {});
              syncSoundUI(true);
            }
          }
          document.removeEventListener("pointerdown", unlockOnGesture);
        };
        document.addEventListener("pointerdown", unlockOnGesture, { once: true });
      }
    }

    function turnAudioOff() {
      isSectionVisible = false;
      vview.querySelectorAll("video").forEach((v) => {
        v.muted = true;
        v.pause();
      });
      syncSoundUI(false);
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && entry.intersectionRatio >= 0.45) {
            turnAudioOn();
          } else {
            turnAudioOff();
          }
        });
      },
      { threshold: [0, 0.45] }
    );

    observer.observe(vview);

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        turnAudioOff();
      } else if (isSectionVisible && !manuallyMuted) {
        turnAudioOn();
      }
    });
  }

  function boot() {
    initFlashSaleSlider();
    initVideoAutoAudio();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();