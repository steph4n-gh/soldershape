const buttons = [...document.querySelectorAll('[data-case]')];
async function loadRecordedCase() {
  try {
    const response = await fetch('media/evidence/review.json');
    if (!response.ok) throw new Error('Recorded evidence unavailable.');
    const review = await response.json();
    function select(index) {
      const row = review.rows[index];
      for (const button of buttons) button.setAttribute('aria-pressed', String(Number(button.dataset.case) === index));
      document.getElementById('force-x').textContent = row.forces.x_uN.toFixed(3).replace('-', '−');
      const vertical = document.getElementById('force-z');
      vertical.textContent = (row.forces.z_uN > 0 ? '+' : '') + row.forces.z_uN.toFixed(3).replace('-', '−');
      vertical.classList.toggle('upward', row.forces.z_uN > 0);
      const heading = document.createElement('h3'); heading.textContent = `${row.label} · ${row.input.volume_mm3 * 1000} nL`;
      const facts = document.createElement('p'); facts.textContent = row.facts.slice(3).join(' ');
      document.getElementById('case-explanation').replaceChildren(heading, facts);
    }
    for (const button of buttons) button.addEventListener('click', () => select(Number(button.dataset.case)));
    select(0);
  } catch {
    for (const button of buttons) button.disabled = true;
    const message = document.createElement('p'); message.textContent = 'The saved reference remains visible. Open the numerical review or download the example to inspect both recorded cases.';
    document.getElementById('case-explanation').append(message);
  }
}
loadRecordedCase();
