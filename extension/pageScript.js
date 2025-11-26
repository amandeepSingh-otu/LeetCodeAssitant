(function() {
  function getSlug() {
    const m = location.pathname.match(/problems\/([^\/]+)/);
    return m ? m[1] : null;
  }

  function getLanguage() {
    // Try to infer language from dropdown or tabs
    const selected = document.querySelector('[data-cy="language-select"] .ant-select-selection-item')
      || document.querySelector('[data-cy="lang-select"] [aria-selected="true"]')
      || document.querySelector('.ant-select-selection-item');
    return selected ? selected.textContent.trim() : null;
  }

  function getMonacoCode() {
    try {
      if (window.monaco && window.monaco.editor) {
        const model = window.monaco.editor.getModels()[0];
        if (model) return model.getValue();
      }
    } catch (e) {
      // swallow
    }
    return null;
  }

  function domFallback() {
    // Monaco renders tokens inside .view-lines; innerText concatenates lines
    const container = document.querySelector('.view-lines');
    if (container) return container.innerText;
    return null;
  }

  function collect() {
    const code = getMonacoCode() || domFallback();
    const slug = getSlug();
    const lang = getLanguage();
    window.dispatchEvent(new CustomEvent('LC_ASSISTANT_CODE_EVENT', {
      detail: { code, slug, lang }
    }));
  }

  // Poll until code loads or attempts exhausted
  let attempts = 0;
  const maxAttempts = 40; // ~20s at 500ms
  const poll = setInterval(() => {
    attempts++;
    if (getMonacoCode() || domFallback() || attempts >= maxAttempts) {
      clearInterval(poll);
      collect();
    }
  }, 500);

  // Allow explicit refresh from content script
  window.addEventListener('LC_ASSISTANT_REQUEST_CODE', collect);
})();
