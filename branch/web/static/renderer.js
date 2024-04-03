document.addEventListener('DOMContentLoaded', () => {
  const minButton = document.getElementById('minButton');
  const maxButton = document.getElementById('maxButton');
  const closeButton = document.getElementById('closeButton');

  if (minButton) {
    minButton.addEventListener('click', () => {
      window.electronAPI.minimizeWindow();
    });
  }

  if (maxButton) {
    maxButton.addEventListener('click', () => {
      window.electronAPI.maximizeWindow();
    });
  }

  if (closeButton) {
    closeButton.addEventListener('click', () => {
      window.electronAPI.closeWindow();
    });
  }
});

if (window.electronAPI) {
  window.isElectron = true;
}