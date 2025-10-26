// Scroll animation for hero
window.addEventListener('scroll', () => {
    const heroText = document.querySelector('.hero h2');
    heroText.style.opacity = 1 - window.scrollY / 400;
});

  const cards = document.querySelectorAll('.service-card');
  const revealOnScroll = () => {
    const triggerBottom = window.innerHeight * 0.85;
    cards.forEach(card => {
      const cardTop = card.getBoundingClientRect().top;
      if (cardTop < triggerBottom) {
        card.classList.add('show');
      }
    });
  };
  window.addEventListener('scroll', revealOnScroll);
  revealOnScroll();
