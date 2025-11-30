chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  
  if (request.action === 'getProblemContext') {
    
    
    const handleCodeReceived = async (e) => {

      window.removeEventListener('LC_ASSISTANT_CODE_EVENT', handleCodeReceived);
      
      const { code, slug, lang } = e.detail;

     
      let problemData = null;
      if (slug) {
        problemData = await fetchProblemData(slug);
      }

    
      sendResponse({
        code: code,
        slug: slug,
        lang: lang,
        problem: problemData
      });
    };

  
    window.addEventListener('LC_ASSISTANT_CODE_EVENT', handleCodeReceived);

   
    window.dispatchEvent(new CustomEvent('LC_ASSISTANT_REQUEST_CODE'));

    
    return true; 
  }
});


async function fetchProblemData(slug) {
  const query = `
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        title
        content
        difficulty
      }
    }
  `;
  try {
    const res = await fetch('https://leetcode.com/graphql', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ query, variables: { titleSlug: slug } })
    });
    const json = await res.json();
    return json?.data?.question || null;
  } catch (err) {
    return null;
  }
}