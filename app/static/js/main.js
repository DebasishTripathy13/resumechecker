// Progressive enhancement: the form works without JS; this adds drag-and-drop,
// a filename preview, a loading state, and animated score visuals.
(function () {
  "use strict";

  function initUpload() {
    var form = document.getElementById("upload-form");
    if (!form) return;

    var input = document.getElementById("resume");
    var dropzone = document.getElementById("dropzone");
    var label = document.getElementById("dropzone-text");
    var button = document.getElementById("submit-btn");

    function showFile() {
      var file = input.files && input.files[0];
      if (!file) return;
      label.textContent = file.name + " (" + Math.ceil(file.size / 1024) + " KB)";
      dropzone.classList.add("has-file");
    }

    input.addEventListener("change", showFile);

    ["dragenter", "dragover"].forEach(function (evt) {
      dropzone.addEventListener(evt, function (e) {
        e.preventDefault();
        dropzone.classList.add("dragging");
      });
    });
    ["dragleave", "drop"].forEach(function (evt) {
      dropzone.addEventListener(evt, function (e) {
        e.preventDefault();
        dropzone.classList.remove("dragging");
      });
    });
    dropzone.addEventListener("drop", function (e) {
      if (e.dataTransfer && e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        showFile();
      }
    });

    form.addEventListener("submit", function () {
      button.disabled = true;
      button.textContent = "Analyzing...";
    });
  }

  function initScores() {
    document.querySelectorAll("[data-score]").forEach(function (el) {
      var score = Math.max(0, Math.min(100, parseInt(el.dataset.score, 10) || 0));
      // Set via CSSOM so no inline style attributes are needed (keeps CSP strict).
      requestAnimationFrame(function () {
        el.style.setProperty("--score", score);
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initUpload();
    initScores();
  });
})();
