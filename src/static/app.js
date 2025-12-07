document.addEventListener('DOMContentLoaded', () => {
  // Sample activities data with participants arrays
  const activities = [
    { id: 'chess', name: 'Chess Club', desc: 'Strategy, tournaments and fun.', participants: ['alice@mergington.edu'] },
    { id: 'robotics', name: 'Robotics Team', desc: 'Build and program robots.', participants: [] },
    { id: 'drama', name: 'Drama Club', desc: 'Acting, improv, and stagecraft.', participants: ['bob@mergington.edu', 'carol@mergington.edu'] },
  ];

  const listEl = document.getElementById('activities-list');
  const template = document.getElementById('activity-template');
  const selectEl = document.getElementById('activity');
  const form = document.getElementById('signup-form');
  const emailInput = document.getElementById('email');
  const messageEl = document.getElementById('message');

  function renderActivities() {
    listEl.innerHTML = '';
    activities.forEach(act => {
      const node = template.content.cloneNode(true);
      node.querySelector('.activity-name').textContent = act.name;
      node.querySelector('.activity-desc').textContent = act.desc;
      node.querySelector('.activity-meta').textContent = `${act.participants.length} participant${act.participants.length === 1 ? '' : 's'}`;

      const ul = node.querySelector('.participants-list');
      const noParticipants = node.querySelector('.no-participants');
      ul.innerHTML = '';
      if (act.participants.length === 0) {
        noParticipants.style.display = 'block';
      } else {
        noParticipants.style.display = 'none';
        act.participants.forEach(p => {
          const li = document.createElement('li');
          li.textContent = p;
          ul.appendChild(li);
        });
      }

      listEl.appendChild(node);
    });
  }

  function populateSelect() {
    // keep the placeholder option, then append options
    // remove old options except first placeholder
    while (selectEl.options.length > 1) selectEl.remove(1);
    activities.forEach(act => {
      const opt = document.createElement('option');
      opt.value = act.id;
      opt.textContent = `${act.name} (${act.participants.length})`;
      selectEl.appendChild(opt);
    });
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = emailInput.value.trim().toLowerCase();
    const activityId = selectEl.value;
    if (!email || !activityId) {
      showMessage('Please enter an email and choose an activity.', 'error');
      return;
    }

    const act = activities.find(a => a.id === activityId);
    if (!act) {
      showMessage('Selected activity not found.', 'error');
      return;
    }

    if (act.participants.includes(email)) {
      showMessage('This email is already signed up for that activity.', 'info');
      return;
    }

    act.participants.push(email);
    renderActivities();
    populateSelect();
    showMessage(`Signed up ${email} for ${act.name}.`, 'success');
    form.reset();
  });

  function showMessage(text, type = 'info') {
    messageEl.className = '';
    messageEl.classList.add(type === 'success' ? 'msg-success' : type === 'error' ? 'msg-error' : 'msg-info');
    messageEl.textContent = text;
    messageEl.style.display = 'block';
    setTimeout(() => (messageEl.style.display = 'none'), 4000);
  }

  // initial render
  renderActivities();
  populateSelect();
});
