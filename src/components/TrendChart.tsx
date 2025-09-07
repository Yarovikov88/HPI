import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import type { ChartOptions } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  ChartDataLabels
);

export type TrendPoint = { date: string; hpi: number };

export interface TrendChartProps {
  points: TrendPoint[];
  compact?: boolean;
  height?: number;
  yMin?: number;
  yMax?: number;
  yStep?: number;
  label?: string;
}

export const TrendChart: React.FC<TrendChartProps> = ({
  points,
  compact = false,
  height,
  yMin = 0,
  yMax = 100,
  yStep = 10,
  label = 'HPI',
}) => {
  const labels = points && Array.isArray(points) ? points.map(p => new Date(p.date).toLocaleDateString('ru-RU')) : [];
  const data = {
    labels,
    datasets: [
      {
        label,
        data: points && Array.isArray(points) ? points.map(p => p.hpi) : [],
        borderColor: '#4f72b4',
        backgroundColor: 'rgba(79, 114, 180, 0.15)',
        pointBackgroundColor: '#0a2463',
        pointBorderColor: '#ffffff',
        tension: 0.25,
        pointRadius: compact ? 3 : 4,
        pointHoverRadius: compact ? 4 : 5,
      },
    ],
  };
  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: compact ? false : true,
    plugins: {
      legend: { position: 'bottom', display: compact ? false : true },
      title: { display: false, text: 'Динамика HPI' },
      datalabels: compact
        ? { display: false }
        : {
            align: 'top',
            anchor: 'end',
            color: '#0a2463',
            backgroundColor: 'rgba(255,255,255,0.9)',
            borderRadius: 4,
            padding: 4,
            formatter: (value: number) => Number(value).toFixed(1),
            font: { weight: 700 },
          },
    },
    scales: {
      y: { min: yMin, max: yMax, ticks: { stepSize: yStep } },
    },
  };
  const wrapperStyle = compact && height ? { height: `${height}px` } : compact ? { height: '160px' } : undefined;
  return (
    <div style={wrapperStyle}>
      <Line data={data} options={options} />
    </div>
  );
}; 