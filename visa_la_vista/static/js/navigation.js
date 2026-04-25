// Navigation functionality
(function() {
  'use strict';

  // Get all navigation links
  const navLinks = document.querySelectorAll('[data-nav]');
  const pages = document.querySelectorAll('.page');
  const footer = document.getElementById('footer');

  // Navigate to a specific page
  function navigateTo(pageName) {
    // Update pages visibility
    pages.forEach(page => {
      if (page.id === `${pageName}-page`) {
        page.classList.add('active');
      } else {
        page.classList.remove('active');
      }
    });

    // Update nav links active state
    navLinks.forEach(link => {
      if (link.getAttribute('data-nav') === pageName) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });

    // Hide footer on chat page
    if (pageName === 'chat') {
      footer.style.display = 'none';
    } else {
      footer.style.display = 'block';
    }

    // Scroll to top
    window.scrollTo(0, 0);
  }

  // Add click event listeners to navigation links
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const page = link.getAttribute('data-nav');
      navigateTo(page);
    });
  });

  // Initialize - show home page by default
  navigateTo('home');
})();
