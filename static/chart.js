// document.addEventListener('DOMContentLoaded', function() {
//     // Ensure that playersData exists and contains exactly 2 players.
//     if (typeof playersData !== 'undefined' && playersData.length === 2) {
//       var player1 = playersData[0];
//       var player2 = playersData[1];
  
//       // Define the labels (adjust these based on the data you have).
//       // For example, we use points (PTS), rebounds (REB), assists (AST),
//       // steals (STL), and blocks (BLK) if available.
//       var labels = ['PTS', 'REB', 'AST', 'STL', 'BLK'];
  
//       // For this example, if your data does not include STL or BLK,
//       // you might want to default them to 0. For instance:
//       var player1Stats = [
//         player1.PTS || 0, 
//         player1.REB || 0, 
//         player1.AST || 0, 
//         player1.STL || 0, 
//         player1.BLK || 0
//       ];
//       var player2Stats = [
//         player2.PTS || 0, 
//         player2.REB || 0, 
//         player2.AST || 0, 
//         player2.STL || 0, 
//         player2.BLK || 0
//       ];
  
//       // ----- Create the Radar Chart -----
//       var radarCanvas = document.getElementById('radarChart');
//       if (radarCanvas) {
//         var radarCtx = radarCanvas.getContext('2d');
//         var radarChart = new Chart(radarCtx, {
//           type: 'radar',
//           data: {
//             labels: labels,
//             datasets: [
//               {
//                 label: player1.PLAYER_NAME,
//                 data: player1Stats,
//                 fill: true,
//                 backgroundColor: 'rgba(255, 99, 132, 0.2)',
//                 borderColor: 'rgba(255, 99, 132, 1)',
//                 pointBackgroundColor: 'rgba(255, 99, 132, 1)'
//               },
//               {
//                 label: player2.PLAYER_NAME,
//                 data: player2Stats,
//                 fill: true,
//                 backgroundColor: 'rgba(54, 162, 235, 0.2)',
//                 borderColor: 'rgba(54, 162, 235, 1)',
//                 pointBackgroundColor: 'rgba(54, 162, 235, 1)'
//               }
//             ]
//           },
//           options: {
//             scales: {
//               r: {
//                 beginAtZero: true,
//               }
//             },
//             plugins: {
//               title: {
//                 display: true,
//                 text: 'Player Performance Radar Chart'
//               }
//             }
//           }
//         });
//       } else {
//         console.error("Canvas element with id 'radarChart' not found.");
//       }
  
//       // ----- Create the Bar Chart -----
//       var barCanvas = document.getElementById('barChart');
//       if (barCanvas) {
//         var barCtx = barCanvas.getContext('2d');
//         var barChart = new Chart(barCtx, {
//           type: 'bar',
//           data: {
//             labels: labels,
//             datasets: [
//               {
//                 label: player1.PLAYER_NAME,
//                 data: player1Stats,
//                 backgroundColor: 'rgba(255, 99, 132, 0.5)'
//               },
//               {
//                 label: player2.PLAYER_NAME,
//                 data: player2Stats,
//                 backgroundColor: 'rgba(54, 162, 235, 0.5)'
//               }
//             ]
//           },
//           options: {
//             scales: {
//               y: {
//                 beginAtZero: true,
//                 title: {
//                   display: true,
//                   text: 'Per-Game Averages'
//                 }
//               }
//             },
//             plugins: {
//               title: {
//                 display: true,
//                 text: 'Player Performance Bar Chart'
//               }
//             }
//           }
//         });
//       } else {
//         console.error("Canvas element with id 'barChart' not found.");
//       }
//     } else {
//       console.error("playersData is not defined or does not contain exactly 2 players.");
//     }
//   });
  