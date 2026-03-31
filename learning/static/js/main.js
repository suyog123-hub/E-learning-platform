  const stars = document.querySelectorAll('#star-container .star');
  const ratingInput = document.getElementById('rating-value');

  stars.forEach(star => {
    star.addEventListener('click', () => {
      const val = +star.dataset.value;
      ratingInput.value = val;
      stars.forEach(s => {
        s.classList.toggle('active', +s.dataset.value <= val);
      });
    });

    star.addEventListener('mouseenter', () => {
      const val = +star.dataset.value;
      stars.forEach(s => {
        s.classList.toggle('active', +s.dataset.value <= val);
      });
    });

    star.addEventListener('mouseleave', () => {
      const saved = +ratingInput.value;
      stars.forEach(s => {
        s.classList.toggle('active', +s.dataset.value <= saved);
      });
    });
  });