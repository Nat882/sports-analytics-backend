document.addEventListener('DOMContentLoaded', () => {
  const gamesLink = document.getElementById('gamesLink');
  if (gamesLink) {
    gamesLink.addEventListener('click', () => {
      // Redirects to the Flask route for games
      window.location.href = "/games"; // or use a data attribute for more flexibility
    });
  }
});
