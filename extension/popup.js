document.addEventListener('DOMContentLoaded', () => {
  const getHintBtn = document.getElementById('getHint');
  const moreHintBtn = document.getElementById('moreHint');
  const similarBtn = document.getElementById('similarQuestion');
  const status = document.getElementById('status');
  const chatWindow = document.getElementById('chatWindow');
  const toggle = document.getElementById('hideCodeToggle');
  const hideCodeLabel = document.getElementById('hideCodeLabel');

  const chatHistory = [];
  const SIMILAR_QUESTIONS = [
    'Two Sum (Easy)',
    'Valid Parentheses (Easy)',
    'Merge Two Sorted Lists (Medium)',
    'Longest Substring Without Repeating (Medium)',
    'Word Ladder (Hard)'
  ];
  let similarIndex = 0;
  let cachedProblemContext = null;
  let problemContextSent = false;

  function setStatus(text) {
    status.textContent = text;
  }

  function updateToggleLabel() {
    hideCodeLabel.textContent = toggle.checked ? 'On' : 'Off';
  }

  function friendlyError(message) {
    const lower = message?.toLowerCase() || '';
    if (lower.includes('inject content script')) {
      return 'Reload the coding tab, then try again.';
    }
    if (lower.includes('no active tab')) {
      return 'Focus the tab you want help with.';
    }
    return message;
  }

  function addMessage(role, text) {
    const el = document.createElement('div');
    el.className = `chat-msg ${role}`;
    el.textContent = text;
    chatWindow.querySelector('.chat-placeholder')?.remove();
    chatWindow.appendChild(el);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    chatHistory.push({ role, text });
  }

  async function fetchProblemContext() {
    try {
      cachedProblemContext = await sendMessageToActiveTab({ action: 'getProblemContext' });
      return cachedProblemContext;
    } catch (err) {
      console.warn('Failed to fetch problem context', err);
      return null;
    }
  }

  async function captureDomSnapshot() {
    try {
      await sendMessageToActiveTab({ action: 'inspectFlexLayout' });
    } catch (err) {
      console.warn('Failed to capture DOM snapshot', err);
    }
  }

  async function ensureContentScript(tabId) {
    if (!chrome?.scripting) return false;
    try {
      await chrome.scripting.executeScript({ target: { tabId }, files: ['content.js'] });
      return true;
    } catch (err) {
      console.error('Failed to inject content script', err);
      return false;
    }
  }

  async function sendMessageToActiveTab(message) {
    if (!chrome?.tabs) {
      throw new Error('Chrome APIs unavailable in this context');
    }
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const tab = tabs?.[0];
    if (!tab) {
      throw new Error('No active tab');
    }

    const send = () => new Promise((resolve, reject) => {
      chrome.tabs.sendMessage(tab.id, message, (resp) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve(resp);
        }
      });
    });

    try {
      return await send();
    } catch (err) {
      if (err?.message?.includes('Receiving end')) {
        const injected = await ensureContentScript(tab.id);
        if (!injected) {
          throw new Error('Could not inject content script');
        }
        return await send();
      }
      throw err;
    }
  }

  async function requestHint(kind) {
    const verb = kind === 'more' ? 'Requesting follow-up hint' : 'Requesting hint';
    setStatus(`${verb}...`);
    addMessage('user', kind === 'more' ? 'Give me another hint.' : 'Give me a hint.');
    addMessage('assistant', 'Working on a hint...');

    let problemPayload = null;
    if (!problemContextSent) {
      const context = cachedProblemContext || await fetchProblemContext();
      if (context) {
        problemPayload = context;
        problemContextSent = true;
      }
    }

    try {
      const response = await sendMessageToActiveTab({
        action: 'run',
        kind,
        hideCode: toggle.checked,
        history: chatHistory.slice(-4),
        problem: problemPayload || undefined,
      });
      const text = response?.status || 'Highlight complete.';
      setStatus('Done');
      chatWindow.lastElementChild.textContent = text;
    } catch (err) {
      const message = friendlyError(err?.message || String(err));
      setStatus(message);
      chatWindow.lastElementChild.textContent = '⚠️ ' + message;
    }
  }

  getHintBtn.addEventListener('click', async () => {
    await captureDomSnapshot();
    await requestHint('first');
  });
  moreHintBtn.addEventListener('click', () => requestHint('more'));
  similarBtn.addEventListener('click', () => {
    const question = SIMILAR_QUESTIONS[similarIndex % SIMILAR_QUESTIONS.length];
    similarIndex += 1;
    addMessage('user', 'Show me a similar question I solved.');
    addMessage('assistant', `Try revisiting: ${question}.`);
    setStatus('Shared a similar question.');
  });

  toggle.addEventListener('change', updateToggleLabel);
  updateToggleLabel();
});
