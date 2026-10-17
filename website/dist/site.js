const volumeButtons = [...document.querySelectorAll('[data-case]')];
const scenarioButtons = [...document.querySelectorAll('[data-scenario]')];

async function loadWalkthrough() {
  try {
    const response = await fetch('media/walkthrough.json');
    if (!response.ok) throw new Error('Recorded evidence unavailable.');
    const walkthrough = await response.json();
    let scenario = walkthrough.scenarios[0];
    let volume = 0;

    function render() {
      const row = scenario.rows[volume];
      for (const button of scenarioButtons) button.setAttribute('aria-pressed', String(button.dataset.scenario === scenario.id));
      for (const button of volumeButtons) button.setAttribute('aria-pressed', String(Number(button.dataset.case) === volume));
      document.getElementById('scenario-title').textContent = scenario.label;
      document.getElementById('scenario-verdict').textContent = scenario.screen.headline;
      document.getElementById('force-x').textContent = row.forces.x_uN.toFixed(3).replace('-', '−');
      const vertical = document.getElementById('force-z');
      vertical.textContent = (row.forces.z_uN > 0 ? '+' : '') + row.forces.z_uN.toFixed(3).replace('-', '−');
      vertical.classList.toggle('upward', row.forces.z_uN > 0);
      const heading = document.createElement('h3');
      heading.textContent = `${row.label} · ${row.input.volume_mm3 * 1000} nL`;
      const facts = document.createElement('p');
      facts.textContent = row.facts.slice(3).join(' ');
      const rule = document.createElement('p');
      const met = volume === 0 ? scenario.screen.reference_rule_met : scenario.screen.candidate_rule_met;
      rule.className = 'rule-status';
      rule.textContent = `Numerical fixture rule ${met ? 'met' : 'not met'}. Physical accuracy unqualified.`;
      document.getElementById('case-explanation').replaceChildren(heading, facts, rule);
      const capture = document.getElementById('scenario-capture');
      capture.src = `media/${scenario.id === 'gap-300' ? 'comparison-review' : 'changed-gap'}.jpg`;
      capture.alt = `Actual Board explorer capture at a ${scenario.held_gap_um} µm held gap, showing the exact native forces and numerical scope.`;
      document.getElementById('scenario-review').href = scenario.evidence_url;
    }

    for (const button of volumeButtons) button.addEventListener('click', () => { volume = Number(button.dataset.case); render(); });
    for (const button of scenarioButtons) button.addEventListener('click', () => {
      scenario = walkthrough.scenarios.find(item => item.id === button.dataset.scenario);
      render();
    });
    render();
  } catch {
    for (const button of [...volumeButtons, ...scenarioButtons]) button.disabled = true;
    const message = document.createElement('p');
    message.textContent = 'The saved 300 µm reference remains visible. Open either numerical review or download both scenarios to inspect the complete record.';
    document.getElementById('case-explanation').append(message);
  }
}

loadWalkthrough();
