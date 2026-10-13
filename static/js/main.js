// Vcart Vanilla JS Utilities
document.addEventListener('DOMContentLoaded', () => {
  // Mobile drawer menu toggle
  const mobileBtn = document.getElementById('mobileMenuBtn');
  const mobileDrawer = document.getElementById('mobileDrawer');

  if (mobileBtn && mobileDrawer) {
    mobileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isExpanded = mobileBtn.getAttribute('aria-expanded') === 'true';
      mobileBtn.setAttribute('aria-expanded', !isExpanded);
      mobileDrawer.classList.toggle('open');
    });

    // Close mobile drawer when clicking outside
    document.addEventListener('click', (e) => {
      if (!mobileDrawer.contains(e.target) && !mobileBtn.contains(e.target)) {
        mobileDrawer.classList.remove('open');
        mobileBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Auto-dismiss alert notifications after 4.5 seconds
  const flashAlerts = document.querySelectorAll('.flash-alert, .alert');
  if (flashAlerts.length > 0) {
    setTimeout(() => {
      flashAlerts.forEach(alert => {
        alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-8px)';
        setTimeout(() => alert.remove(), 400);
      });
    }, 4500);
  }
});
