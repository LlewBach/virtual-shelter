export class ChartClass {
  constructor(id) {
    this.chartCanvas = document.querySelector(`#chart-canvas-${id}`);
    if (!this.chartCanvas) return;

    this.ctx = this.chartCanvas.getContext('2d');

    this.chart = new Chart(this.ctx, {
      type: 'pie',
      data: {
        labels: ['Time Standing', 'Time Running'],
        datasets: [{
          label: 'Time Spent in States',
          data: [0, 0],
          backgroundColor: ['rgba(54, 162, 235, 0.6)', 'rgba(255, 99, 132, 0.6)'],
          borderColor: ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: false
      }
    });
  }
  updateChart(data) {
    if (!this.chart) return;

    this.chart.data.datasets[0].data = [data.time_standing, data.time_running];
    this.chart.update();
  }
}