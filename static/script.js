
const form = document.getElementById('analyzeForm');
const resultsEl = document.getElementById('results');
const summaryEl = document.getElementById('summary');
const engineBox = document.getElementById('engineBox');

fetch('/api/health')
  .then(r => r.json())
  // .then(data => engineBox.textContent = `Similarity Engine: ${data.engine}`)
  .catch(() => engineBox.textContent = 'Engine: unknown');

function tags(items, cls='') {
  if (!items || items.length === 0) return '<span class="tag">None</span>';
  return items.slice(0, 18).map(x => `<span class="tag ${cls}">${escapeHtml(x)}</span>`).join('');
}

function bars(scores) {
  return Object.entries(scores).map(([k, v]) => `
    <div>
      <div class="bar-label"><span>${k}</span><span>${v}%</span></div>
      <div class="bar"><span style="width:${v}%"></span></div>
    </div>
  `).join('');
}

function escapeHtml(str) {
  return String(str).replace(/[&<>'"]/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;'}[c]));
}

function render(data) {
  const ranking = data.ranking || [];
  summaryEl.classList.remove('hidden');
  summaryEl.innerHTML = `
    <div class="summary-card">Candidates<b>${data.total_candidates}</b></div>
    <div class="summary-card">JD Skills Found<b>${data.jd_summary.required_skills.length}</b></div>
    <div class="summary-card">JD Min Experience<b>${data.jd_summary.min_experience_years || 0} yrs</b></div>
  `;
  resultsEl.innerHTML = ranking.map(r => `
    <article class="card result-card">
      <div class="result-header">
        <div>
          <div class="rank">Rank #${r.rank}</div>
          <div class="file">${escapeHtml(r.file_name)}</div>
          <span class="badge">${escapeHtml(r.recommendation)}</span>
          <div>Detected Domain: <b>${escapeHtml(r.resume_domain.best_domain)}</b> (${Math.round((r.resume_domain.confidence || 0) * 100)}%)</div>
          <div>Experience: <b>${r.resume_info.experience.years}</b> years </div>
        </div>
        <div class="score-ring">${r.score}%</div>
      </div>

      <div class="grid">
        <div class="panel">
          <h3>Component Scores</h3>
          <div class="bars">${bars(r.scoring.component_scores)}</div>
        </div>
        <div class="panel">
          <h3>Semantic Similarities</h3>
          <div class="bars">${bars(r.similarities)}</div>
        </div>
        <div class="panel">
          <h3>Matched Skills (${r.scoring.matched_skill_count})</h3>
          <div class="tags">${tags(r.scoring.matched_skills)}</div>
        </div>
        <div class="panel">
          <h3>Missing Skills (${r.scoring.missing_skill_count})</h3>
          <div class="tags">${tags(r.scoring.missing_skills, 'missing')}</div>
        </div>
      </div>
    </article>
  `).join('');
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  resultsEl.innerHTML = '<div class="card result-card">Analyzing... Please keep this window open.</div>';
  summaryEl.classList.add('hidden');
  const formData = new FormData(form);
  try {
    const response = await fetch('/api/analyze', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Analysis failed');
    render(data);
  } catch (err) {
    resultsEl.innerHTML = `<div class="error">${escapeHtml(err.message)}</div>`;
  }
});
