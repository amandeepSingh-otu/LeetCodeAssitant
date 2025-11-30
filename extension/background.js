const PANEL_PATH = 'popup.html';

function isLeetCodeProblem(url = '') {
  return /https?:\/\/leetcode\.com\/problems\//.test(url);
}


async function configurePanelForTab(tabId, url) {
  if (!chrome.sidePanel) return;

  const isLeetCode = isLeetCodeProblem(url);

 
  await chrome.sidePanel.setOptions({
    tabId,
    path: PANEL_PATH,
    enabled: isLeetCode
  });
}

chrome.runtime.onInstalled.addListener(() => {
  if (!chrome.sidePanel) return;
  chrome.sidePanel.setOptions({
    enabled: false
  });
});


chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' || changeInfo.url) {
    await configurePanelForTab(tabId, tab.url);
  }
});


chrome.tabs.onActivated.addListener(async ({ tabId }) => {
  const tab = await chrome.tabs.get(tabId);
  await configurePanelForTab(tabId, tab.url);
});


chrome.action.onClicked.addListener((tab) => {
  if (tab.windowId) {
    chrome.sidePanel.open({ windowId: tab.windowId });
  }
});