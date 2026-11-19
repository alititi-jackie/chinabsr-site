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

// Match the genealogy site's scroll threshold and floating control.
const floatingNavigation = document.createElement('div');
floatingNavigation.className = 'nav-buttons';
const topButton = document.createElement('button');
topButton.type = 'button';
topButton.hidden = true;
topButton.setAttribute('aria-label', '返回顶部');
topButton.title = '返回顶部';
topButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 7-7 7 7"/><path d="M12 19V5"/></svg>';
floatingNavigation.append(topButton);
document.body.append(floatingNavigation);
function updateTopButton() {
  topButton.hidden = window.scrollY <= 900;
}
window.addEventListener('scroll', updateTopButton, {passive:true});
updateTopButton();
topButton.addEventListener('click', () => {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  window.scrollTo({top:0, behavior:reduceMotion ? 'instant' : 'smooth'});
});
