// Photo gallery: thumbnails, previous/next buttons, arrow keys and swipe.
(function () {
  document.querySelectorAll("[data-gallery]").forEach(function (gallery) {
    var main = gallery.querySelector("[data-gallery-main]");
    var thumbs = Array.prototype.slice.call(gallery.querySelectorAll("[data-gallery-thumb]"));
    var count = gallery.querySelector("[data-gallery-count]");
    if (!main || thumbs.length < 2) return;
    var index = 0;

    function show(i) {
      index = (i + thumbs.length) % thumbs.length;
      var link = thumbs[index];
      main.src = link.getAttribute("href");
      main.alt = link.getAttribute("data-alt");
      thumbs.forEach(function (thumb, j) {
        if (j === index) thumb.setAttribute("aria-current", "true");
        else thumb.removeAttribute("aria-current");
      });
      if (count) count.textContent = index + 1 + " / " + thumbs.length;
    }

    thumbs.forEach(function (link, i) {
      link.addEventListener("click", function (event) {
        event.preventDefault();
        show(i);
      });
    });
    gallery.querySelector("[data-gallery-prev]").addEventListener("click", function () { show(index - 1); });
    gallery.querySelector("[data-gallery-next]").addEventListener("click", function () { show(index + 1); });
    gallery.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") show(index - 1);
      if (event.key === "ArrowRight") show(index + 1);
    });

    var startX = null;
    main.addEventListener("touchstart", function (event) { startX = event.touches[0].clientX; }, { passive: true });
    main.addEventListener("touchend", function (event) {
      if (startX === null) return;
      var dx = event.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) show(index + (dx < 0 ? 1 : -1));
      startX = null;
    });

    gallery.classList.add("is-ready");
  });
})();
