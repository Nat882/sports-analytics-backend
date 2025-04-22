document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('gamesLink').addEventListener('click', () => {
      // Directly use the /games route
      window.location.href = "/games";
    });
});
