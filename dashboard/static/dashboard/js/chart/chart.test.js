import { ChartClass } from './chart.js';

// Mock the global Chart object used by Chart.js
global.Chart = jest.fn().mockImplementation(() => ({
  data: {
    datasets: [{ data: [50] }]
  },
  update: jest.fn()
}));

describe('ChartClass', () => {
  let chartInstance;

  beforeEach(() => {
    global.Chart.mockClear();
    // Create a mock canvas element to use in the tests
    document.body.innerHTML = `
      <canvas id="chart-canvas-1"></canvas>
    `;
    HTMLCanvasElement.prototype.getContext = jest.fn();
    chartInstance = new ChartClass(1, 50);
  });

  test('should create an instance of ChartClass', () => {
    expect(chartInstance).toBeInstanceOf(ChartClass);
  });

  test('should initialize chart with the given data', () => {
    expect(chartInstance.chart).toBeDefined();
    expect(global.Chart).toHaveBeenCalledTimes(1);
  });

  test('should update chart data correctly', () => {
    chartInstance.updateChart({ time_standing: 15, time_running: 20 });
    expect(chartInstance.chart.update).toHaveBeenCalled();
    expect(chartInstance.chart.data.datasets[0].data).toEqual([15, 20]);
  });
});