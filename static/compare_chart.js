document.addEventListener('DOMContentLoaded', function () {
  if (typeof playersData !== 'undefined' && playersData.length === 2) {
    const player1 = playersData[0];
    const player2 = playersData[1];

    const labels = ['PTS', 'REB', 'AST', 'STL', 'BLK'];

    const player1Stats = [
      player1.PTS || 0,
      player1.REB || 0,
      player1.AST || 0,
      player1.STL || 0,
      player1.BLK || 0
    ];

    const player2Stats = [
      player2.PTS || 0,
      player2.REB || 0,
      player2.AST || 0,
      player2.STL || 0,
      player2.BLK || 0
    ];

    // Chart configs
    const ctxBar = document.getElementById('playerComparisonChart')?.getContext('2d');
    const ctxRadar = document.getElementById('radarChart')?.getContext('2d');
    const ctxLine = document.getElementById('lineChart')?.getContext('2d');

    // Bar Chart
    const barChart = new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels: labels.slice(0, 3), // PTS, REB, AST
        datasets: [
          {
            label: player1.PLAYER_NAME,
            data: player1Stats.slice(0, 3),
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
          },
          {
            label: player2.PLAYER_NAME,
            data: player2Stats.slice(0, 3),
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Player Comparison (Bar Chart)'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });

    // Radar Chart
    const radarChart = new Chart(ctxRadar, {
      type: 'radar',
      data: {
        labels: labels,
        datasets: [
          {
            label: player1.PLAYER_NAME,
            data: player1Stats,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            pointBackgroundColor: 'rgba(255, 99, 132, 1)'
          },
          {
            label: player2.PLAYER_NAME,
            data: player2Stats,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            pointBackgroundColor: 'rgba(54, 162, 235, 1)'
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Player Comparison (Radar Chart)'
          }
        },
        scales: {
          r: {
            beginAtZero: true
          }
        }
      }
    });

    // Line Chart
    const lineChart = new Chart(ctxLine, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: player1.PLAYER_NAME,
            data: player1Stats,
            borderColor: 'rgba(255, 99, 132, 1)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            fill: false,
            tension: 0.3
          },
          {
            label: player2.PLAYER_NAME,
            data: player2Stats,
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            fill: false,
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Player Comparison (Line Chart)'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });

    // Chart switcher
    const chartTypeSelector = document.getElementById('chartType');
    const barCanvas = document.getElementById('playerComparisonChart');
    const radarCanvas = document.getElementById('radarChart');
    const lineCanvas = document.getElementById('lineChart');

    function showChart(type) {
      barCanvas.style.display = type === 'bar' ? 'block' : 'none';
      radarCanvas.style.display = type === 'radar' ? 'block' : 'none';
      lineCanvas.style.display = type === 'line' ? 'block' : 'none';
    }

    chartTypeSelector?.addEventListener('change', function () {
      showChart(this.value);
    });

    // Show bar by default
    showChart('bar');
  } else {
    console.error("playersData is not defined or does not contain exactly 2 players.");
  }
});
