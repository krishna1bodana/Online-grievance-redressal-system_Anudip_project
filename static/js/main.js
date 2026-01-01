/* =========================
   GRIEVANCE STATUS REFRESH
========================= */

function normalizeStatus(status) {
    return status
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '-');
}

function refreshGrievanceStatus(grievanceId) {
    const statusLabel = document.getElementById('current-status');
    const historyList = document.getElementById('status-history-list');

    if (!statusLabel || !grievanceId) return;

    statusLabel.style.opacity = '0.6';

    fetch(`/api/grievance-status/${grievanceId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response error');
            }
            return response.json();
        })
        .then(data => {
            const normalizedStatus = normalizeStatus(data.status);

            statusLabel.textContent = data.status;

            statusLabel.className = `status-badge status-${normalizedStatus}`;
            statusLabel.style.opacity = '1';

            if (historyList && Array.isArray(data.history)) {
                historyList.innerHTML = '';

                data.history.forEach(item => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <strong>${item.old_status}</strong>
                        →
                        <strong>${item.new_status}</strong>
                        <small>(${new Date(item.changed_at).toLocaleString()})</small>
                    `;
                    historyList.appendChild(li);
                });
            }
        })
        .catch(error => {
            console.error('Status refresh failed:', error);
            statusLabel.style.opacity = '1';
        });
}

/* =========================
   SLA COUNTDOWN TIMER
========================= */

function startSlaCountdown() {
    const container = document.getElementById('grievance-detail-container');
    if (!container) return;

    const dueDateStr = container.dataset.due;
    const timerEl = document.getElementById('sla-timer');

    if (!dueDateStr || !timerEl) return;

    const dueDate = new Date(dueDateStr);

    function updateTimer() {
        const now = new Date();
        const diffMs = dueDate - now;

        if (diffMs <= 0) {
            timerEl.textContent = 'Overdue';
            timerEl.style.color = 'red';
            return;
        }

        const totalSeconds = Math.floor(diffMs / 1000);
        const days = Math.floor(totalSeconds / (3600 * 24));
        const hours = Math.floor((totalSeconds % (3600 * 24)) / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);

        timerEl.textContent = `${days}d ${hours}h ${minutes}m`;

        // Color logic
        if (days >= 2) {
            timerEl.style.color = 'green';
        } else {
            timerEl.style.color = 'orange';
        }
    }

    updateTimer();
    setInterval(updateTimer, 1000);
}

/* =========================
   AUTO INIT ON DETAIL PAGE
========================= */

document.addEventListener('DOMContentLoaded', () => {
    const detailView = document.getElementById('grievance-detail-container');
    if (!detailView) return;

    const grievanceId = detailView.dataset.id;
    if (!grievanceId) return;

    refreshGrievanceStatus(grievanceId);
    startSlaCountdown();

    setInterval(() => {
        refreshGrievanceStatus(grievanceId);
    }, 30000);
});
function markRead(notificationId) {
    fetch(`/notifications/read/${notificationId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

// CSRF helper (Django-safe)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

/* =========================
   END OF FILE
========================= */
