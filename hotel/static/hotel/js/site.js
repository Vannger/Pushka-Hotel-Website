// Room photos: the "show all" button and a full-screen viewer
// with arrows, keyboard and swipe. Without JavaScript every photo
// is listed and each one opens as a plain link.
(function () {
  var COLLAPSE_ABOVE = 9;

  var grid = document.querySelector("[data-gallery]");
  if (!grid) return;
  var links = Array.prototype.slice.call(grid.querySelectorAll("a[data-photo]"));

  var more = document.querySelector("[data-gallery-more]");
  if (more && links.length > COLLAPSE_ABOVE) {
    grid.classList.add("is-collapsed");
    more.hidden = false;
    more.addEventListener("click", function () {
      grid.classList.remove("is-collapsed");
      more.hidden = true;
    });
  }

  var box = document.querySelector("[data-lightbox]");
  if (!box || typeof box.showModal !== "function") return;
  var image = box.querySelector("[data-lightbox-image]");
  var count = box.querySelector("[data-lightbox-count]");
  var index = 0;

  function show(i) {
    index = (i + links.length) % links.length;
    var link = links[index];
    image.src = link.href;
    image.alt = link.querySelector("img").alt;
    count.textContent = index + 1 + " / " + links.length;
  }

  links.forEach(function (link, i) {
    link.addEventListener("click", function (event) {
      event.preventDefault();
      show(i);
      box.showModal();
    });
  });

  box.querySelector("[data-lightbox-prev]").addEventListener("click", function () { show(index - 1); });
  box.querySelector("[data-lightbox-next]").addEventListener("click", function () { show(index + 1); });
  box.querySelector("[data-lightbox-close]").addEventListener("click", function () { box.close(); });
  // A click on the dark area around the photo closes the viewer.
  box.addEventListener("click", function (event) {
    if (event.target === box) box.close();
  });
  box.addEventListener("keydown", function (event) {
    if (event.key === "ArrowLeft") show(index - 1);
    if (event.key === "ArrowRight") show(index + 1);
  });
  box.addEventListener("close", function () { image.removeAttribute("src"); });

  var startX = null;
  box.addEventListener("touchstart", function (event) { startX = event.touches[0].clientX; }, { passive: true });
  box.addEventListener("touchend", function (event) {
    if (startX === null) return;
    var dx = event.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 40) show(index + (dx < 0 ? 1 : -1));
    startX = null;
  });
})();
