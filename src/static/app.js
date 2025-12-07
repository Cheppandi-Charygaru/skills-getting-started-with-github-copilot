document.addEventListener('DOMContentLoaded', () => {
  // Activities will be fetched from the backend API
  let activities = [];

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
      node.querySelector('.activity-desc').textContent = act.description;
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
          const span = document.createElement('span');
          span.className = 'participant-item';
          span.textContent = p;
          const deleteBtn = document.createElement('button');
          deleteBtn.className = 'delete-btn';
          deleteBtn.textContent = '✕';
          deleteBtn.type = 'button';
          deleteBtn.setAttribute('aria-label', `Remove ${p}`);
          deleteBtn.addEventListener('click', async () => {
            try {
              const response = await fetch(`/activities/${encodeURIComponent(act.name)}/unregister?email=${encodeURIComponent(p)}`, {
                method: 'POST'
              });
              if (!response.ok) {
                showMessage('Failed to remove participant.', 'error');
                return;
              }
              showMessage(`Removed ${p} from ${act.name}.`, 'success');
              await fetchActivities();
            } catch (err) {
              console.error('Error removing participant:', err);
              showMessage('Failed to remove participant.', 'error');
            }
          });
          li.appendChild(span);
          li.appendChild(deleteBtn);
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
      opt.value = act.name;
      opt.textContent = `${act.name} (${act.participants.length})`;
      selectEl.appendChild(opt);
    });
  }

  async function fetchActivities() {
    try {
      const response = await fetch('/activities');
      if (!response.ok) throw new Error('Failed to fetch activities');
      const data = await response.json();
      activities = Object.entries(data).map(([name, info]) => ({
        name,
        description: info.description,
        schedule: info.schedule,
        max_participants: info.max_participants,
        participants: info.participants
      }));
      renderActivities();
      populateSelect();
    } catch (err) {
      console.error('Error fetching activities:', err);
      showMessage('Failed to load activities.', 'error');
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim().toLowerCase();
    const activityName = selectEl.value;
    if (!email || !activityName) {
      showMessage('Please enter an email and choose an activity.', 'error');
      return;
    }

    const act = activities.find(a => a.name === activityName);
    if (!act) {
      showMessage('Selected activity not found.', 'error');
      return;
    }

    if (act.participants.includes(email)) {
      showMessage('This email is already signed up for that activity.', 'info');
      return;
    }

    try {
      const response = await fetch(`/activities/${encodeURIComponent(activityName)}/signup?email=${encodeURIComponent(email)}`, {
        method: 'POST'
      });
      if (!response.ok) {
        const errorData = await response.json();
        showMessage(errorData.detail || 'Failed to sign up.', 'error');
        return;
      }
      
      showMessage(`Signed up ${email} for ${activityName}.`, 'success');
      form.reset();
      await fetchActivities();
    } catch (err) {
      console.error('Error signing up:', err);
      showMessage('Failed to sign up for activity.', 'error');
    }
  });

  function showMessage(text, type = 'info') {
    messageEl.className = '';
    messageEl.classList.add(type === 'success' ? 'msg-success' : type === 'error' ? 'msg-error' : 'msg-info');
    messageEl.textContent = text;
    messageEl.style.display = 'block';
    setTimeout(() => (messageEl.style.display = 'none'), 4000);
  }

  // Fetch activities on page load
  fetchActivities();
});
