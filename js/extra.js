document.addEventListener("DOMContentLoaded", function () {
  const viewSourceButton = document.querySelector('a[title="View source of this page"]');
  if (viewSourceButton) {
    viewSourceButton.style.display = 'none';
  }
});
