const analyzeBtn = document.getElementById('analyze');
const BASE = 'http://127.0.0.1:8000'; // your Django backend

analyzeBtn.addEventListener('click', async () => {
  const raw = document.getElementById('bulk').value;

  let tasks = [];
  try {
    tasks = JSON.parse(raw);
  } catch (e) {
    alert('Invalid JSON format');
    return;
  }

  const strategy = document.getElementById('strategy').value;

  const response = await fetch(`${BASE}/api/tasks/analyze/?strategy=${strategy}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tasks)
  });

  const data = await response.json();

  const out = document.getElementById('output');
  out.innerHTML = '';

  data.forEach(task => {
    const div = document.createElement('div');
    div.className = 'task';

    let level = 'low';
    if (task.score > 0.8) level = 'high';
    else if (task.score > 0.4) level = 'medium';
    div.classList.add(level);

    div.innerHTML = `
      <strong>${task.title}</strong> — Score: ${task.score}<br>
      ${task.reason}<br>
      <small>Due: ${task.due_date || 'N/A'} | Effort: ${task.estimated_hours} hrs | Importance: ${task.importance}</small>
    `;

    out.appendChild(div);
  });
});
