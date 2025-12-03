document.addEventListener('DOMContentLoaded', () => {
  const BACKEND_URL = "http://127.0.0.1:8000"; 
  const MAX_HINTS = 10;
  const chatWindow = document.getElementById('chatWindow');
  const status = document.getElementById('status');
  const hintsLeftDisplay = document.getElementById('hintsLeftDisplay');

  const getHintBtn = document.getElementById('getHint');
  const moreHintBtn = document.getElementById('moreHint');
  const complexityBtn = document.getElementById('getComplexity');
  const edgeCaseBtn = document.getElementById('getEdgeCase');
  const giveUpBtn = document.getElementById('giveUpBtn');


   const provideCodeToggle = document.getElementById('hideCodeToggle');
  if (!provideCodeToggle) {
      console.warn("WARNING: 'hideCodeToggle' element not found in HTML. Code generation option will default to false.");
  }

  // --- State Variables ---
  let hintsLeft = MAX_HINTS;
  

  let chatHistory = []; 


  updateHintDisplay();


  function addMessage(role, text) {
    const el = document.createElement('div');
    el.className = `chat-msg ${role}`;
    el.innerHTML = text.replace(/\n/g, '<br>'); 
    chatWindow.appendChild(el);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    chatHistory.push({
        role: role,
        content: text
    });
  }


  function updateHintDisplay() {
    hintsLeftDisplay.textContent = `${hintsLeft} Hints Left`;

    if (hintsLeft <= 0) {
      toggleButtons(false);
      if (giveUpBtn) giveUpBtn.style.display = 'block';
      if (status) status.textContent = 'Out of hints!';
      addMessage('assistant', 'You are out of hints! Try to solve it, or click "I Give Up" to see the solution.');
    }
  }

  function toggleButtons(enable) {
    const buttons = [getHintBtn, moreHintBtn, complexityBtn, edgeCaseBtn];
    buttons.forEach(btn => {
      if (btn) btn.disabled = !enable;
    });
  }


  function getTabContext() {
    return new Promise(async (resolve, reject) => {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab) {
        reject("No active tab found.");
        return;
      }

      chrome.tabs.sendMessage(tab.id, { action: "getProblemContext" }, (response) => {
        if (chrome.runtime.lastError) {
          reject("Please refresh the LeetCode page.");
        } else if (!response) {
          reject("No response from page script.");
        } else {
          resolve(response);
        }
      });
    });
  }

  async function handleRequest(endpointType, userMessage) {
    if (hintsLeft <= 0 && endpointType !== 'solution') return;

    addMessage('user', userMessage);
    if (status) status.textContent = 'Analyzing...';

    try {
      
      const context = await getTabContext();
      const { code, slug, lang, problem } = context;

      if (!slug) throw new Error("Could not find problem slug.");
      
     
      const wantCode = provideCodeToggle ? provideCodeToggle.checked : false;

      let payload = {
        slug: String(slug),
        description: problem ? String(problem.content) : "Description unavailable",
        solution: code ? String(code) : "", 
      };

  
      
      if (endpointType === 'hint') {
         payload.chat_history = chatHistory; 
         payload.provide_code = wantCode ? "true" : "false"; 
      } 

    
      let route = "/hint/get_hint"; 
      if (endpointType === 'complexity') route = "/hint/task_complexity";
      if (endpointType === 'edgecase') route = "/hint/generate_edge_cases";
      if (endpointType === 'solution') route = "/solution"; 

    
      const res = await fetch(`${BACKEND_URL}${route}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error(`Backend Error: ${res.status}`);
      
      const data = await res.json();
      
   
      const reply = data.message || data.hint || data.analysis || JSON.stringify(data);
      
      
      addMessage('assistant', reply); 
      
      if (status) status.textContent = 'Ready';

 
      if (endpointType !== 'solution') {
        hintsLeft--;
        updateHintDisplay();
      } else {
        toggleButtons(false);
        if (giveUpBtn) giveUpBtn.disabled = true;
        if (status) status.textContent = 'Solution revealed.';
      }

    } catch (err) {
      addMessage('assistant', `Error: ${err.message}`);
      if (status) status.textContent = 'Error';
    }
  }


  if (getHintBtn) getHintBtn.addEventListener('click', () => handleRequest('hint', 'Give me a hint.'));
  

  if (moreHintBtn) moreHintBtn.addEventListener('click', () => handleRequest('hint', 'I need more hint.'));
  
  if (complexityBtn) complexityBtn.addEventListener('click', () => handleRequest('complexity', 'Analyze the complexity.'));
  if (edgeCaseBtn) edgeCaseBtn.addEventListener('click', () => handleRequest('edgecase', 'What are the edge cases?'));
  
  if (giveUpBtn) {
    giveUpBtn.addEventListener('click', () => {
      if (confirm("Are you sure? This will show the solution and use your remaining hints.")) {
        handleRequest('solution', 'I give up. Show me the solution.');
      }
    });
  }
});