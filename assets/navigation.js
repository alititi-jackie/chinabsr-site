const shareButton = document.getElementById('share');
shareButton.hidden = false;
let statusTimer;
shareButton.addEventListener('click', async () => {
  const url = location.href;
  const status = document.getElementById('share-status');
  try {
    if (navigator.share) {
      await navigator.share({title:document.title,url});
    } else {
      await navigator.clipboard.writeText(url);
      status.textContent = '链接已复制';
      clearTimeout(statusTimer);
      statusTimer = setTimeout(() => { status.textContent = ''; }, 2000);
    }
  } catch (error) {
    if (error.name !== 'AbortError') window.prompt('复制网址', url);
  }
});
