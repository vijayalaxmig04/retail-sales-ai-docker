/* ==========================================
   RETAIL SALES DASHBOARD - CUSTOM JS
   ========================================== */

// Mobile navigation toggle
document.addEventListener('DOMContentLoaded', function() {
  const navToggle = document.getElementById('nav-toggle');
  const navMenu = document.getElementById('nav-menu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', function() {
      navToggle.classList.toggle('active');
      navMenu.classList.toggle('active');
    });

    // Close menu when a link is clicked
    const navLinks = navMenu.querySelectorAll('.app-nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', function() {
        navToggle.classList.remove('active');
        navMenu.classList.remove('active');
      });
    });
  }
});

// Toast notifications
function createToast(type, message) {
  const toastContainer = document.getElementById('toast-container');
  if (!toastContainer) return;

  const toastDiv = document.createElement('div');
  toastDiv.className = `app-toast ${type}`;
  toastDiv.setAttribute('role', 'status');
  toastDiv.setAttribute('aria-live', 'polite');
  toastDiv.innerHTML = `
    <div>${message}</div>
    <button class="app-toast-close" type="button" aria-label="Close notification">
      &times;
    </button>
  `;

  toastContainer.appendChild(toastDiv);

  // Auto-remove after 4 seconds
  const removeTimer = setTimeout(() => {
    removeToast(toastDiv);
  }, 4000);

  // Manual close button
  const closeBtn = toastDiv.querySelector('.app-toast-close');
  closeBtn.addEventListener('click', () => {
    clearTimeout(removeTimer);
    removeToast(toastDiv);
  });
}

function removeToast(toastDiv) {
  toastDiv.classList.add('removing');
  setTimeout(() => {
    toastDiv.remove();
  }, 300);
}

// Modal functionality
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
  if (event.target.classList.contains('app-modal')) {
    event.target.classList.remove('active');
    document.body.style.overflow = '';
  }
});

// Close modal with close button
document.addEventListener('click', function(event) {
  if (event.target.classList.contains('app-modal-close')) {
    const modal = event.target.closest('.app-modal');
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  }
});

// Add CSS for toast close button
const style = document.createElement('style');
style.textContent = `
  .app-toast-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: inherit;
    padding: 0;
    margin-left: auto;
    flex-shrink: 0;
  }
  
  .app-toast-close:hover {
    opacity: 0.7;
  }
`;
document.head.appendChild(style);

