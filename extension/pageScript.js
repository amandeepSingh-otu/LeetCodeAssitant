function getSlug() {
  const path = window.location.pathname;
  const match = path.match(/problems\/([^\/]+)/);
  return match && match[1] ? match[1] : null;
}


window.addEventListener('LC_ASSISTANT_REQUEST_CODE', () => {
  
  let code = null;
  let lang = 'unknown';
  
  try {
    const editor = window.monaco?.editor?.getModels()?.[0];
    if (editor) {
      code = editor.getValue();
      lang = editor.getLanguageId();
    }
  } catch (e) {
    console.error('Monaco access error:', e);
  }

  const slug = getSlug();

  window.dispatchEvent(new CustomEvent('LC_ASSISTANT_CODE_EVENT', {
    detail: { code, slug, lang }
  }));
});