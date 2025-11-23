// Header ticker animation
document.addEventListener('DOMContentLoaded', () => {
  const ticker = document.getElementById('ticker-track');
  
  if (ticker) {
    // The ticker animation is handled by CSS
    // This script could add interactivity like pause on hover
    ticker.addEventListener('mouseenter', () => {
      ticker.style.animationPlayState = 'paused';
    });
    
    ticker.addEventListener('mouseleave', () => {
      ticker.style.animationPlayState = 'running';
    });
  }
});

