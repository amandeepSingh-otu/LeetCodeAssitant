// Inject a page-level script so we can access Monaco (content scripts run in an isolated world)
function injectPageScript() {
	const script = document.createElement('script');
	script.src = chrome.runtime.getURL('pageScript.js');
	script.onload = () => script.remove();
	document.documentElement.appendChild(script);
}

injectPageScript();

// Listen for code payload dispatched from pageScript.js
window.addEventListener('LC_ASSISTANT_CODE_EVENT', (e) => {
	const { code, slug, lang } = e.detail || {};
	console.log('[LeetCodeAssistant] Received code', { slug, lang, code });
	if (!code) {
		console.warn('[LeetCodeAssistant] No code retrieved via Monaco or DOM fallback.');
	}
	// After receiving code, fetch richer problem data via GraphQL
	if (slug) {
		fetchProblemData(slug).then((data) => {
			if (data) {
				console.log('[LeetCodeAssistant] Problem data', {
					title: data.title,
					difficulty: data.difficulty,
					likes: data.likes,
					dislikes: data.dislikes
				});
				// You can forward this to background or side panel as needed.
			}
		}).catch(err => console.error('[LeetCodeAssistant] GraphQL fetch failed', err));
	}
});

// Optionally request code again later (e.g., after user changes language)
function requestCodeRefresh() {
	window.dispatchEvent(new Event('LC_ASSISTANT_REQUEST_CODE'));
}

// Poll for language change or editor updates (simple heuristic)
let refreshAttempts = 0;
const refreshInterval = setInterval(() => {
	refreshAttempts += 1;
	if (refreshAttempts > 20) {
		clearInterval(refreshInterval);
		return;
	}
	requestCodeRefresh();
}, 5000);

// GraphQL query to get only title and full HTML description (content) by slug
async function fetchProblemData(slug) {
	const query = `query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    title\n    content\n  }\n}`;
	const res = await fetch('https://leetcode.com/graphql', {
		method: 'POST',
		headers: {
			'content-type': 'application/json'
		},
		body: JSON.stringify({ query, variables: { titleSlug: slug } })
	});
	const json = await res.json();
	if (!json?.data?.question) return null;
	const { title, content } = json.data.question;
	return { title, content };
}