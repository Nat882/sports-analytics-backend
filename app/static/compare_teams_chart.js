document.addEventListener('DOMContentLoaded', () => {
  if (typeof teamData !== 'undefined' && teamData.length === 2) {
    const team1 = teamData[0];
    const team2 = teamData[1];

    const labels = ['PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK'];
    const team1Stats = [team1.PTS, team1.REB, team1.AST, team1.TOV, team1.STL, team1.BLK];
    const team2Stats = [team2.PTS, team2.REB, team2.AST, team2.TOV, team2.STL, team2.BLK];

    // Stacked Bar Chart 
    const ctxBar = document.getElementById('teamComparisonChart').getContext('2d');
    const stackedBarChart = new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: team1.TEAM_NAME,
            data: team1Stats,
            backgroundColor: 'rgba(255,99,132,0.6)',
            stack: 'Stack 0'
          },
          {
            label: team2.TEAM_NAME,
            data: team2Stats,
            backgroundColor: 'rgba(54,162,235,0.6)',
            stack: 'Stack 0'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,      // ← disable default aspect ratio
        plugins: {
          title: {
            display: true,
            text: 'Team Comparison (Stacked Bar Chart)'
          }
        },
        scales: {
          x: { stacked: true },
          y: { stacked: true, beginAtZero: true }
        }
      }
    });

    // ----- Radar Chart -----
    const ctxRadar = document.getElementById('radarChart').getContext('2d');
    const radarChart = new Chart(ctxRadar, {
      type: 'radar',
      data: {
        labels,
        datasets: [
          {
            label: team1.TEAM_NAME,
            data: team1Stats,
            fill: true,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            pointBackgroundColor: 'rgba(255, 99, 132, 1)'
          },
          {
            label: team2.TEAM_NAME,
            data: team2Stats,
            fill: true,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            pointBackgroundColor: 'rgba(54, 162, 235, 1)'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Team Comparison (Radar Chart)'
          }
        },
        scales: {
          r: { beginAtZero: true }
        }
      }
    });

    // ----- Doughnut Charts -----
    const ctxD1 = document.getElementById('team1Doughnut').getContext('2d');
    const ctxD2 = document.getElementById('team2Doughnut').getContext('2d');

    new Chart(ctxD1, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          label: team1.TEAM_NAME,
          data: team1Stats,
          backgroundColor: [
            'rgba(255,99,132,0.6)',
            'rgba(255,159,64,0.6)',
            'rgba(255,205,86,0.6)',
            'rgba(75,192,192,0.6)',
            'rgba(153,102,255,0.6)',
            'rgba(201,203,207,0.6)'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: `${team1.TEAM_NAME} Stat Breakdown`
          }
        }
      }
    });

    new Chart(ctxD2, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          label: team2.TEAM_NAME,
          data: team2Stats,
          backgroundColor: [
            'rgba(54,162,235,0.6)',
            'rgba(75,192,192,0.6)',
            'rgba(153,102,255,0.6)',
            'rgba(255,205,86,0.6)',
            'rgba(255,159,64,0.6)',
            'rgba(255,99,132,0.6)'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: `${team2.TEAM_NAME} Stat Breakdown`
          }
        }
      }
    });

    // ----- Toggle logic -----
    const selector = document.getElementById('chartType');
    const barCanvas = document.getElementById('teamComparisonChart');
    const radarCanvas = document.getElementById('radarChart');
    const doughnutContainer = document.getElementById('doughnutContainer');

    function showChart(type) {
      barCanvas.style.display       = type === 'bar'     ? 'block' : 'none';
      radarCanvas.style.display     = type === 'radar'   ? 'block' : 'none';
      doughnutContainer.style.display = type === 'doughnut' ? 'flex'  : 'none';
    }

    selector?.addEventListener('change', e => showChart(e.target.value));
    showChart('bar'); // default
  }
});
