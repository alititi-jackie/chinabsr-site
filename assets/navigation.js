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

function enablePhotoViewer() {
  if (typeof HTMLDialogElement === 'undefined') return;
  const dialog = document.createElement('dialog');
  dialog.className = 'photo-viewer';
  dialog.setAttribute('aria-label', '查看大图');
  dialog.innerHTML = '<button type="button" class="viewer-close">关闭</button><figure><picture><img alt=""></picture><figcaption></figcaption></figure>';
  document.body.append(dialog);
  const close = dialog.querySelector('button');
  const fullImage = dialog.querySelector('img');
  const caption = dialog.querySelector('figcaption');
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });

  function openImage(image, credit) {
    fullImage.src = image.currentSrc || image.src;
    fullImage.alt = image.alt;
    fullImage.parentElement.classList.toggle('archive-photo', Boolean(image.closest('.archive-photo, .slides')));
    caption.textContent = credit || image.alt;
    dialog.showModal();
    close.focus();
  }

  function addTrigger(image) {
    const media = image.closest('picture') || image;
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'view-image';
    trigger.setAttribute('aria-label', '查看大图：' + image.alt);
    trigger.setAttribute('aria-haspopup', 'dialog');
    media.replaceWith(trigger);
    trigger.append(media);
    trigger.addEventListener('click', () => openImage(image, image.closest('figure')?.querySelector('figcaption')?.textContent));
  }

  for (const link of document.querySelectorAll('a.card')) {
    const image = link.querySelector('img');
    if (!image) continue;
    const card = document.createElement('article');
    card.className = link.className;
    const media = image.closest('picture') || image;
    link.replaceWith(card);
    card.append(media, link);
    link.className = 'card-story';
    addTrigger(image);
  }
  document.querySelectorAll('.article figure img').forEach(addTrigger);
  const controls = document.querySelector('.hero .nav');
  if (controls) {
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.textContent = '查看大图';
    trigger.setAttribute('aria-haspopup', 'dialog');
    controls.append(trigger);
    trigger.addEventListener('click', () => {
      const active = document.querySelector('.slides img.active');
      if (active) openImage(active, active.dataset.caption);
    });
  }
}
enablePhotoViewer();
