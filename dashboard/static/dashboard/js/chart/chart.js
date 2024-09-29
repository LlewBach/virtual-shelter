export class ChartClass {
  constructor(id, initialSatiation) {
    this.chartCanvas = document.querySelector(`#chart-canvas-${id}`);
    if (!this.chartCanvas) return;

    this.ctx = this.chartCanvas.getContext('2d');

    this.chart = new Chart(this.ctx, {
      type: 'bar',
      data: {
        labels: ['Satiation'], // A single label for the bar
        datasets: [{
          label: 'Satiation Level',
          data: [initialSatiation],
          backgroundColor: 'rgba(75, 192, 192, 0.6)', // Optional: Bar color
          borderColor: 'rgba(75, 192, 192, 1)', // Optional: Bar border color
          borderWidth: 1
        }]
      },
      options: {
        responsive: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100 // Assuming the satiation level ranges from 0 to 100
          }
        }
      }
    });
  }
  updateChart(data) {
    if (!this.chart) return;  // gonna delete

    this.chart.data.datasets[0].data = [data.satiation];
    this.chart.update();
  }
}