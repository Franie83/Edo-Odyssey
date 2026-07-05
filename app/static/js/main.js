// EDO ODYSSEY — Main JavaScript

// Auto-dismiss flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('#flash-container .alert').forEach(el => {
      const bsAlert = new bootstrap.Alert(el);
      bsAlert.close();
    });
  }, 5000);

  // Init tooltips
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });

  // Admin sidebar mobile toggle
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.admin-sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('show'));
  }

  // Countdown timer
  document.querySelectorAll('[data-countdown]').forEach(el => {
    const target = new Date(el.dataset.countdown).getTime();
    const update = () => {
      const now = Date.now();
      const diff = target - now;
      if (diff <= 0) { el.innerHTML = '<span class="text-muted">Event Started!</span>'; return; }
      const d = Math.floor(diff / 86400000);
      const h = Math.floor((diff % 86400000) / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      const s = Math.floor((diff % 60000) / 1000);
      const box = n => `<div class="countdown-box text-center"><div class="countdown-num">${String(n).padStart(2,'0')}</div></div>`;
      el.innerHTML = `${box(d)}<div class="countdown-sep text-gold fw-bold">:</div>${box(h)}<div class="countdown-sep text-gold fw-bold">:</div>${box(m)}<div class="countdown-sep text-gold fw-bold">:</div>${box(s)}`;
    };
    update();
    setInterval(update, 1000);
  });

  // Star rating interactive
  document.querySelectorAll('.star-select').forEach(container => {
    const stars = container.querySelectorAll('[data-star]');
    const input = container.querySelector('input[type=hidden]');
    stars.forEach(star => {
      star.addEventListener('mouseover', () => {
        stars.forEach(s => s.classList.toggle('text-gold', parseInt(s.dataset.star) <= parseInt(star.dataset.star)));
      });
      star.addEventListener('click', () => {
        if (input) input.value = star.dataset.star;
        stars.forEach(s => s.classList.toggle('active-star', parseInt(s.dataset.star) <= parseInt(star.dataset.star)));
      });
    });
    container.addEventListener('mouseleave', () => {
      const val = input ? parseInt(input.value) : 0;
      stars.forEach(s => s.classList.toggle('text-gold', parseInt(s.dataset.star) <= val));
    });
  });

  // Google Maps embeds (placeholder)
  document.querySelectorAll('.map-placeholder').forEach(el => {
    const lat = el.dataset.lat;
    const lng = el.dataset.lng;
    const name = el.dataset.name || 'Location';
    el.innerHTML = `
      <div class="d-flex align-items-center justify-content-center h-100 bg-blue-100 rounded" style="min-height:280px">
        <div class="text-center p-3">
          <i class="bi bi-geo-alt-fill text-gold" style="font-size:2.5rem"></i>
          <p class="mt-2 fw-semibold text-blue">${name}</p>
          <p class="small text-muted">Lat: ${lat} | Lng: ${lng}</p>
          <a href="https://www.google.com/maps?q=${lat},${lng}" target="_blank" class="btn btn-sm btn-blue mt-2">
            <i class="bi bi-map me-1"></i>Open in Google Maps
          </a>
        </div>
      </div>`;
  });
});

// Confirm delete
function confirmDelete(form, name) {
  if (confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`)) {
    form.submit();
  }
}

// Copy to clipboard
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied to clipboard!', 'success');
  });
}

function showToast(message, type='info') {
  const container = document.getElementById('toast-container') || (() => {
    const c = document.createElement('div');
    c.id = 'toast-container';
    c.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999';
    document.body.appendChild(c);
    return c;
  })();
  const toast = document.createElement('div');
  toast.className = `toast show align-items-center text-white bg-${type === 'success' ? 'success' : 'primary'} border-0`;
  toast.innerHTML = `<div class="d-flex"><div class="toast-body">${message}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="this.parentElement.parentElement.remove()"></button></div>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}
