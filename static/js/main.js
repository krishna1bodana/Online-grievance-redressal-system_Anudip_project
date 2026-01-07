/* ==========================================================================
   GLOBAL UTILITIES & LOADER
   ========================================================================== */

const initLoader = () => {
    const loader = document.getElementById("loader");
    if (!loader) return;

    // Hide loader on initial page load
    window.addEventListener("load", () => {
        loader.style.opacity = "0";
        setTimeout(() => loader.style.display = "none", 300);
    });

    // Use event delegation for all internal links (future-proof)
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;

        const href = link.getAttribute('href');
        if (
            href &&
            !href.startsWith('#') &&
            !link.target &&
            !e.ctrlKey &&
            !e.metaKey
        ) {
            loader.style.display = "flex";
            loader.style.opacity = "1";
        }
    });
};

/* ==========================================================================
   DJANGO CSRF TOKEN HELPER
   ========================================================================== */

const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie) {
        document.cookie.split(';').forEach(cookie => {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(
                    trimmed.substring(name.length + 1)
                );
            }
        });
    }
    return cookieValue;
};

/* ==========================================================================
   NOTIFICATIONS LOGIC (AJAX)
   ========================================================================== */

const initNotifications = () => {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.mark-read-btn');
        if (!btn) return;

        e.preventDefault();

        const notifId = btn.dataset.id;
        const url = btn.dataset.url;
        const card = document.getElementById(`notification-${notifId}`);

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(res => res.json())
        .then(data => {
            // ✅ FIXED: matches Django response
            if (data.success) {
                if (card) {
                    card.classList.remove('border-primary', 'unread');
                }
                btn.outerHTML =
                    '<span class="badge bg-light text-muted border rounded-pill px-3 py-2">' +
                    '<i class="fas fa-check-double me-1"></i> Seen</span>';
            }
        })
        .catch(err => console.error('Notification error:', err));
    });
};

/* ==========================================================================
   SLA TIMER & STATUS REFRESH
   ========================================================================== */

const startSlaCountdown = () => {
    const container = document.getElementById('grievance-detail-container');
    const timerEl = document.getElementById('sla-timer');

    if (!container || !timerEl || !container.dataset.due) return;

    const dueDate = new Date(container.dataset.due).getTime();
    const wrapper = timerEl.closest('.sla-wrapper') || timerEl.parentElement;

    const updateTimer = () => {
        const now = Date.now();
        const diff = dueDate - now;

        if (diff <= 0) {
            timerEl.textContent = 'SLA BREACHED';
            if (wrapper) {
                wrapper.classList.add('text-danger', 'bg-danger-subtle');
            }
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
        const mins = Math.floor((diff / (1000 * 60)) % 60);

        timerEl.textContent = `${days}d ${hours}h ${mins}m`;
    };

    updateTimer();
    setInterval(updateTimer, 60000);
};

/* ==========================================================================
   DASHBOARD FEATURES (Search)
   ========================================================================== */

const initDashboardSearch = () => {
    const searchInput = document.getElementById('dashboardSearch');
    if (!searchInput) return;

    searchInput.addEventListener('input', function () {
        const value = this.value.toLowerCase();
        document.querySelectorAll('.grievance-card').forEach(card => {
            card.style.display =
                card.textContent.toLowerCase().includes(value) ? '' : 'none';
        });
    });
};

/* ==========================================================================
   INITIALIZATION
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initLoader();
    initNotifications();
    startSlaCountdown();
    initDashboardSearch();
     initCounters();

    // Bootstrap form validation
    document.querySelectorAll('.needs-validation').forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});
/* ==========================================================================
   COUNTER ANIMATION (Public Dashboard)
   ========================================================================== */

const initCounters = () => {
    const counters = document.querySelectorAll('.counter');
    if (!counters.length) return;

    counters.forEach(counter => {
        const target = parseInt(counter.dataset.target || 0, 10);
        if (isNaN(target) || target <= 0) return;

        let current = 0;
        const duration = 1200; // total animation time (ms)
        const stepTime = Math.max(Math.floor(duration / target), 20);

        const updateCounter = () => {
            current += Math.ceil(target / 60);
            if (current >= target) {
                counter.textContent = target;
            } else {
                counter.textContent = current;
                setTimeout(updateCounter, stepTime);
            }
        };

        // Start animation slightly delayed for smooth UX
        setTimeout(updateCounter, 300);
    });
};

/* ==========================================================================
   END OF FILE
   ========================================================================== */