// Carousel interaction placeholder for future enhancement

// Scroll parallax effect
window.addEventListener('scroll', () => {
  const hero = document.getElementById('hero');
  if(hero) {
    const scrollAmount = window.pageYOffset * 0.5;
    hero.style.backgroundPosition = `center ${scrollAmount}px`;
  }
});

// Enhanced scroll animations
window.addEventListener('scroll', function() {
  const elements = document.querySelectorAll('[data-scroll]');
  const windowHeight = window.innerHeight;
  elements.forEach(el => {
    let elementTop = el.getBoundingClientRect().top;
    if (elementTop < windowHeight * 0.85) {
      el.classList.add('visible');
    }
  });
});