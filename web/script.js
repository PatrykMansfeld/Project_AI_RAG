const statusEl = document.getElementById('status');
const messagesEl = document.getElementById('messages');
const sourcesEl = document.getElementById('sources');
const questionEl = document.getElementById('question');
const sendBtn = document.getElementById('send');
const reindexBtn = document.getElementById('reindex');
// Selektory UI
const analyzeBtn = document.getElementById('analyze');
const analysisOut = document.getElementById('analysisOut');
const evalQaPathEl = document.getElementById('evalQaPath');
const evalRunBtn = document.getElementById('evalRun');
const evalOut = document.getElementById('evalOut');
const genTopicEl = document.getElementById('genTopic');
const genCountEl = document.getElementById('genCount');
const genMinWordsEl = document.getElementById('genMinWords');
const genStyleEl = document.getElementById('genStyle');
const genRunBtn = document.getElementById('genRun');
const genOut = document.getElementById('genOut');

function addMessage(text, cls) {
  const div = document.createElement('div');
  div.className = `message ${cls}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}
// Dodaje wiadomość do czatu

async function postJSON(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}
// POST JSON helper

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}
// GET JSON helper

reindexBtn.addEventListener('click', async () => {
  try {
    statusEl.textContent = 'Przebudowa indeksu...';
    reindexBtn.disabled = true;
    await postJSON('/api/index', {});
    statusEl.textContent = 'Indeks gotowy';
  } catch (e) {
    statusEl.textContent = 'Błąd przebudowy';
    console.error(e);
  } finally {
    reindexBtn.disabled = false;
  }
});
// Przebudowa indeksu

sendBtn.addEventListener('click', async () => {
  const q = questionEl.value.trim();
  if (!q) return;
  addMessage(q, 'user');
  questionEl.value = '';
  try {
    statusEl.textContent = 'Myślę...';
    const res = await postJSON('/api/chat', { question: q });
    addMessage(res.answer, 'assistant');
    sourcesEl.innerHTML = '';
    (res.sources || []).forEach(s => {
      const li = document.createElement('li');
      li.textContent = `${s.source} (chunk ${s.chunk_id})`;
      sourcesEl.appendChild(li);
    });
    statusEl.textContent = '';
  } catch (e) {
    addMessage('Błąd podczas odpowiedzi.', 'assistant');
    statusEl.textContent = '';
    console.error(e);
  }
});
// Obsługa czatu

questionEl.addEventListener('keydown', (ev) => {
  if (ev.key === 'Enter') sendBtn.click();
});
// Enter wysyła pytanie

analyzeBtn.addEventListener('click', async () => {
  try {
    statusEl.textContent = 'Analizuję korpus...';
    analyzeBtn.disabled = true;
    const stats = await getJSON('/api/analyze');
    analysisOut.textContent = JSON.stringify(stats, null, 2);
    statusEl.textContent = '';
  } catch (e) {
    analysisOut.textContent = 'Błąd analizy.';
    console.error(e);
    statusEl.textContent = '';
  } finally {
    analyzeBtn.disabled = false;
  }
});
// Analiza korpusu

evalRunBtn.addEventListener('click', async () => {
  const qaPath = evalQaPathEl.value.trim() || 'data/eval/qa.jsonl';
  try {
    statusEl.textContent = 'Uruchamiam ewaluację...';
    evalRunBtn.disabled = true;
    const res = await postJSON('/api/eval', { qa_path: qaPath });
    const summary = {
      accuracy: res.accuracy,
      count: res.count,
    };
    evalOut.textContent = JSON.stringify(summary, null, 2);
    statusEl.textContent = '';
  } catch (e) {
    evalOut.textContent = 'Błąd ewaluacji.';
    console.error(e);
    statusEl.textContent = '';
  } finally {
    evalRunBtn.disabled = false;
  }
});
// Ewaluacja QA

genRunBtn.addEventListener('click', async () => {
  const topic = genTopicEl.value.trim();
  const count = parseInt(genCountEl.value || '1', 10);
  const min_words = parseInt(genMinWordsEl.value || '400', 10);
  const style = genStyleEl.value.trim() || 'encyklopedyczny';
  if (!topic) return;
  try {
    statusEl.textContent = 'Generuję artykuły...';
    genRunBtn.disabled = true;
    const res = await postJSON('/api/generate', { topic, count, min_words, style });
    genOut.innerHTML = '';
    (res.generated || []).forEach(p => {
      const li = document.createElement('li');
      li.textContent = p;
      genOut.appendChild(li);
    });
    statusEl.textContent = '';
  } catch (e) {
    genOut.innerHTML = '<li>Błąd generowania.</li>';
    console.error(e);
    statusEl.textContent = '';
  } finally {
    genRunBtn.disabled = false;
  }
});
// Generowanie artykułów
