// static/projections.js
document.addEventListener('DOMContentLoaded', async () => {
  const { players, allTeams, selectedTeam, mode } = window.PROJ_DATA;

  // 1) Build combined data array
  const data = players.map(p => ({
    name:   p.PLAYER_NAME,
    teamId: p.TEAM_ID,
    heur:   {
      PTS: p.PROJECTED_PTS,
      REB: p.PROJECTED_REB,
      AST: p.PROJECTED_AST
    },
    ml:     { PTS: 0, REB: 0, AST: 0 }
  }));

  // 2) Fetch ML projections in parallel
  await Promise.all(players.map((p, i) =>
    fetch(`/projections/api/player_projections_ml/${p.PLAYER_ID}`)
      .then(r => r.json())
      .then(j => { data[i].ml.PTS = j.PROJECTED_PTS_ML || 0; })
      .catch(() => { /* leave ml.PTS = 0 on error */ })
  ));

  // 3) Grab all of our controls
  const typeSel    = document.getElementById('projTypeSelector');
  const seasonSel  = document.getElementById('seasonSelector');
  const teamSel    = document.getElementById('teamSelector');
  const statSel    = document.getElementById('statSelector');

  // 4) Populate teamSelector
  teamSel.innerHTML = '<option value="all">All Teams</option>';
  allTeams.forEach(t => {
    const label = t.abbreviation || t.full_name || t.name;
    const opt   = new Option(label, t.id);
    if (t.id === selectedTeam) opt.selected = true;
    teamSel.append(opt);
  });

  // 5) Populate statSelector (from our heur keys)
  statSel.innerHTML = '';
  Object.keys(data[0].heur).forEach(stat => {
    statSel.append(new Option(stat, stat));
  });
  statSel.value = 'PTS';   // **force** default back to points

  // 6) Chart.js setup
  let currentStat = statSel.value;
  const ctx   = document.getElementById('mlProjChart').getContext('2d');
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels:   data.map(d => d.name),
      datasets: [
        {
          label:       `Heuristic ${currentStat}`,
          data:         data.map(d => d.heur[currentStat]),
          borderDash: [5,5],
          fill:        false,
          hidden:      (mode === 'ml')
        },
        {
          label:    `ML ${currentStat}`,
          data:      data.map(d => d.ml[currentStat]),
          fill:      false,
          hidden:    (mode === 'heuristic')
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

  // 7) Unified chart-update function
  function updateChart() {
    const selStat = statSel.value;
    const selTeam = teamSel.value;
    const selType = typeSel.value;

    // Filter by team
    const filtered = data.filter(d =>
      selTeam === 'all' ? true : d.teamId === +selTeam
    );

    // Update labels & data
    chart.data.labels               = filtered.map(d => d.name);
    chart.data.datasets[0].data     = filtered.map(d => d.heur[selStat]);
    chart.data.datasets[1].data     = filtered.map(d => d.ml[selStat]);
    chart.data.datasets[0].hidden   = (selType === 'ml');
    chart.data.datasets[1].hidden   = (selType === 'heuristic');
    chart.data.datasets[0].label    = `Heuristic ${selStat}`;
    chart.data.datasets[1].label    = `ML ${selStat}`;
    chart.options.plugins.title.text= `${selStat} Projection`;

    chart.update();
  }

  // 8) Wire up change events
  [ typeSel, teamSel, statSel ].forEach(el =>
    el.addEventListener('change', updateChart)
  );

  // 9) Season-selector: reload page with new season
  seasonSel.addEventListener('change', () => {
    const params = new URLSearchParams(window.location.search);
    params.set('season', seasonSel.value);
    // preserve team & mode if set
    params.set('team',   teamSel.value);
    params.set('mode',   typeSel.value);
    window.location.search = params.toString();
  });

  // 10) Initial render
  updateChart();
});
