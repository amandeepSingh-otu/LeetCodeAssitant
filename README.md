## LeetCode Assistant Extension

### Code & Problem Data Collection

Because Chrome extension content scripts run in an isolated world, they cannot directly access page-level variables like `monaco`. LeetCode also sets a strict CSP that blocks inline script injection (no `unsafe-inline`).

We work around this by:
1. Declaring `pageScript.js` as a `web_accessible_resource` in `manifest.json`.
2. Injecting it as a normal `<script src="chrome-extension://...">` tag from `content.js` (permitted by CSP).
3. Having `pageScript.js` poll for the Monaco editor or DOM fallback and dispatch a custom event `LC_ASSISTANT_CODE_EVENT` with `{ code, slug, lang }`.
4. The content script listens for that event and then makes a GraphQL request to `https://leetcode.com/graphql` to fetch richer problem metadata (title, difficulty, likes, dislikes, full HTML content).

### Refreshing Code
`content.js` periodically dispatches `LC_ASSISTANT_REQUEST_CODE` which `pageScript.js` listens to in order to re-send updated code (e.g., after language changes).

### GraphQL Query Used
```
query questionData($titleSlug: String!) {
	question(titleSlug: $titleSlug) {
		title
		content
		difficulty
		likes
		dislikes
	}
}
```

### Fallback Behavior
If Monaco is not yet available, we attempt a DOM fallback by reading `.view-lines` text. This may lose formatting but still returns the current editor content.

### Notes
Avoid adding inline scripts or using `eval`—they will be blocked by CSP. All dynamic logic should reside in `pageScript.js` and communicate via `CustomEvent`.

