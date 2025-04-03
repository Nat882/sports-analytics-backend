document.addEventListener('DOMContentLoaded', function() {
    // Ensure that playersData exists and contains exactly 2 players.
    if (typeof playersData !== 'undefined' && playersData.length === 2) {
      var player1 = playersData[0];
      var player2 = playersData[1];
  
      // ----- Bar Chart -----
      // Define the labels for the bar chart.
      var barLabels = ['PTS', 'REB', 'AST'];
      
      // Extract the per-game stats from each player for the bar chart.
      var player1BarStats = [player1.PTS, player1.REB, player1.AST];
      var player2BarStats = [player2.PTS, player2.REB, player2.AST];
  
      // Get the canvas for the bar chart.
      var barCanvas = document.getElementById('playerComparisonChart');
      if (barCanvas) {
        var ctxBar = barCanvas.getContext('2d');
        var barChart = new Chart(ctxBar, {
          type: 'bar',
          data: {
            labels: barLabels,
            datasets: [
              {
                label: player1.PLAYER_NAME,
                data: player1BarStats,
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
              },
              {
                label: player2.PLAYER_NAME,
                data: player2BarStats,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
              }
            ]
          },
          options: {
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Per-Game Averages'
                }
              }
            },
            plugins: {
              title: {
                display: true,
                text: 'Player Comparison (Bar Chart)'
              }
            }
          }
        });
      } else {
        console.error("Canvas element with id 'playerComparisonChart' not found.");
      }
  
      // ----- Radar Chart -----
      // Define the labels for the radar chart.
      var radarLabels = ['PTS', 'REB', 'AST', 'STL', 'BLK'];
      
      // Extract stats for the radar chart. If some stats don't exist, default to 0.
      var player1RadarStats = [
        player1.PTS || 0,
        player1.REB || 0,
        player1.AST || 0,
        player1.STL || 0,
        player1.BLK || 0
      ];
      var player2RadarStats = [
        player2.PTS || 0,
        player2.REB || 0,
        player2.AST || 0,
        player2.STL || 0,
        player2.BLK || 0
      ];
  
      // Get the canvas for the radar chart.
      var radarCanvas = document.getElementById('radarChart');
      if (radarCanvas) {
        var ctxRadar = radarCanvas.getContext('2d');
        var radarChart = new Chart(ctxRadar, {
          type: 'radar',
          data: {
            labels: radarLabels,
            datasets: [
              {
                label: player1.PLAYER_NAME,
                data: player1RadarStats,
                fill: true,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                pointBackgroundColor: 'rgba(255, 99, 132, 1)'
              },
              {
                label: player2.PLAYER_NAME,
                data: player2RadarStats,
                fill: true,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                pointBackgroundColor: 'rgba(54, 162, 235, 1)'
              }
            ]
          },
          options: {
            scales: {
              r: {
                beginAtZero: true
              }
            },
            plugins: {
              title: {
                display: true,
                text: 'Player Comparison (Radar Chart)'
              }
            }
          }
        });
      } else {
        console.error("Canvas element with id 'radarChart' not found.");
      }
    } else {
      console.error("playersData is not defined or does not contain exactly 2 players.");
    }
  });
  