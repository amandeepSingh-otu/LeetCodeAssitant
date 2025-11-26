const PANEL_PATH = 'popup.html';

function isLeetCodeProblem(url = '') {
  return /https?:\/\/leetcode\.com\/problems\//.test(url);
}

async function configurePanelForTab(tabId, enabled, windowId) {
  if (!chrome.sidePanel) return;
  try {
    await chrome.sidePanel.setOptions({
      tabId,
      path: PANEL_PATH,
      enabled,
    });
    if (enabled && windowId) {
      await chrome.sidePanel.open({ windowId });
    }
  } catch (err) {
    console.warn('Failed to configure side panel', err);
  }
}

chrome.runtime.onInstalled.addListener(() => {
  if (!chrome.sidePanel) return;
  chrome.sidePanel.setOptions({
    enabled: false,
    path: PANEL_PATH,
  });
});

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (!chrome.sidePanel) return;
  if (!changeInfo.status && !changeInfo.url) return;
  const url = changeInfo.url || tab?.url || '';
  const enabled = isLeetCodeProblem(url);
  await configurePanelForTab(tabId, enabled, enabled ? tab?.windowId : undefined);
});

chrome.tabs.onActivated.addListener(async ({ tabId }) => {
  if (!chrome.sidePanel) return;
  try {
    const tab = await chrome.tabs.get(tabId);
    const enabled = isLeetCodeProblem(tab?.url || '');
    await configurePanelForTab(tabId, enabled, enabled ? tab.windowId : undefined);
  } catch (err) {
    console.warn('Failed to handle tab activation', err);
  }
});

chrome.action.onClicked.addListener(async (tab) => {
  if (!chrome.sidePanel || !tab?.windowId) {
    return;
  }
  await chrome.sidePanel.open({ windowId: tab.windowId });
});
