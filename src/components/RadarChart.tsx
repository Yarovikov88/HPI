import React from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js';
import { Radar } from 'react-chartjs-2';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

export interface RadarItem { name: string; value: number }
export interface RadarChartProps { data: RadarItem[] }

export const RadarChart: React.FC<RadarChartProps> = ({ data }) => {
  const chartData = {
    labels: data && Array.isArray(data) ? data.map(i => i.name) : [],
    datasets: [
      {
        label: 'Баланс по сферам',
        data: data && Array.isArray(data) ? data.map(i => i.value) : [],
        backgroundColor: 'rgba(79, 114, 180, 0.18)',
        borderColor: '#4f72b4',
        pointBackgroundColor: '#0a2463',
        pointBorderColor: '#fff',
      }
    ]
  };
  const options = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { r: { suggestedMin: 0, suggestedMax: 10, ticks: { stepSize: 2, color: '#4f72b4' }, grid: { color: 'rgba(79,114,180,0.2)' }, angleLines: { color: 'rgba(79,114,180,0.2)' } } }
  } as const;
  return <Radar data={chartData} options={options} />;
}; 