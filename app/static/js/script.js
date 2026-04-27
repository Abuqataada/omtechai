document.addEventListener('DOMContentLoaded', () => {
  const root = document.documentElement;
  const menuToggle = document.querySelector('.menu-toggle');
  const navLinks = document.querySelector('.nav-links');
  const themeToggle = document.querySelector('.theme-toggle');
  const themeIcon = document.querySelector('.theme-icon');
  const themeLabel = document.querySelector('.theme-label');
  const themeKey = 'omtechei-theme';

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    const isLight = theme === 'light';
    if (themeToggle) {
      themeToggle.setAttribute('aria-pressed', String(isLight));
    }
    if (themeIcon) {
      themeIcon.textContent = isLight ? '☾' : '☼';
    }
    if (themeLabel) {
      themeLabel.textContent = isLight ? 'Dark' : 'Bright';
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = root.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      localStorage.setItem(themeKey, next);
      applyTheme(next);
    });
  }

  const savedTheme = localStorage.getItem(themeKey);
  if (savedTheme) {
    applyTheme(savedTheme);
  } else {
    applyTheme(root.getAttribute('data-theme') || 'dark');
  }

  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      menuToggle.setAttribute('aria-expanded', String(isOpen));
    });
  }

  const revealTargets = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('show');
        }
      });
    }, { threshold: 0.12 });

    revealTargets.forEach((target) => observer.observe(target));
  } else {
    revealTargets.forEach((target) => target.classList.add('show'));
  }

  const contactForm = document.getElementById('contactForm');
  const contactStatus = document.getElementById('contactStatus');

  if (contactForm && contactStatus) {
    contactForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const submitButton = contactForm.querySelector('button[type="submit"]');
      const payload = Object.fromEntries(new FormData(contactForm).entries());

      submitButton.disabled = true;
      submitButton.textContent = 'Sending...';
      contactStatus.className = 'status-box';
      contactStatus.textContent = 'Submitting your inquiry...';

      try {
        const response = await fetch('/api/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || 'Something went wrong.');
        }

        contactStatus.className = 'status-box ok';
        contactStatus.textContent = data.message || 'Inquiry received.';
        contactForm.reset();
      } catch (error) {
        contactStatus.className = 'status-box err';
        contactStatus.textContent = error.message || 'Something went wrong.';
      } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Send inquiry';
      }
    });
  }
});
