// projections.js
document.addEventListener('DOMContentLoaded', async () => {
    const { players, allTeams, selectedTeam, mode } = window.PROJ_DATA;
  
    // 1) build combined data array
    const data = players.map(p => ({
      name: p.PLAYER_NAME,
      teamId: p.TEAM_ID,
      heur:  { PTS: p.PROJECTED_PTS, REB: p.PROJECTED_REB, AST: p.PROJECTED_AST },
      ml:    { PTS: 0, REB: 0, AST: 0 }  // ML only available for PTS
    }));
  
    // 2) fetch ML PTS projections
    await Promise.all(players.map((p, i) =>
      fetch(`/projections/api/player_projections_ml/${p.PLAYER_ID}`)
        .then(r => r.json().then(j => data[i].ml.PTS = j.PROJECTED_PTS_ML || 0))
        .catch(() => { /* leave as 0 */ })
    ));
  
    // 3) grab selectors
    const typeSel = document.getElementById('projTypeSelector');
    const teamSel = document.getElementById('teamSelector');
    const statSel = document.getElementById('statSelector');
  
    // 4) populate teamSelector
    teamSel.innerHTML = '<option value="all">All Teams</option>';
    allTeams.forEach(t => {
      const opt = new Option(t.abbreviation || t.full_name, t.id);
      if (t.id === selectedTeam) opt.selected = true;
      teamSel.append(opt);
    });
  
    // 5) setup Chart.js
    let currentStat = statSel.value;
    const ctx = document.getElementById('mlProjChart').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map(d => d.name),
        datasets: [
          {
            label: `Heuristic ${currentStat}`,
            data: data.map(d => d.heur[currentStat]),
            borderDash: [5,5],
            fill: false
          },
          {
            label: `ML ${currentStat}`,
            data: data.map(d => d.ml[currentStat]),
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top' },
          title:  { display: true, text: `${currentStat} Projection` },
          tooltip:{ mode: 'index', intersect: false }
        },
        interaction: { mode: 'nearest', axis: 'x', intersect: false },
        scales: {
          x: {
            title: { display: true, text: 'Player' },
            ticks: { autoSkip: false, maxRotation: 45, minRotation: 45 }
          },
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Projected Value' }
          }
        }
      }
    });
  
    // 6) unified update handler
    function updateChart() {
      const selTeam = teamSel.value;
      const selType = typeSel.value;
      const selStat = statSel.value;
      currentStat = selStat;
  
      // filter
      const filtered = data.filter(d =>
        selTeam === 'all' ? true : d.teamId === +selTeam
      );
  
      chart.data.labels = filtered.map(d => d.name);
      chart.data.datasets[0].data = filtered.map(d => d.heur[selStat]);
      chart.data.datasets[1].data = filtered.map(d => d.ml[selStat]);
  
      chart.data.datasets[0].hidden = (selType === 'ml');
      chart.data.datasets[1].hidden = (selType === 'heuristic');
  
      chart.data.datasets[0].label = `Heuristic ${selStat}`;
      chart.data.datasets[1].label = `ML ${selStat}`;
      chart.options.plugins.title.text = `${selStat} Projection`;
  
      chart.update();
    }
  
    // 7) wire up selectors
    typeSel.addEventListener('change', updateChart);
    teamSel.addEventListener('change', updateChart);
    statSel.addEventListener('change', updateChart);
  
    // 8) apply initial mode hiding
    updateChart();
  });
  