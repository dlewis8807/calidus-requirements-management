'use client';

import { useMemo } from 'react';

interface TrendPoint {
  date: string;
  coverage_percentage: number;
  total_requirements: number;
  covered_requirements: number;
  total_gaps: number;
  critical_gaps: number;
}

interface CoverageTrendChartProps {
  trends: TrendPoint[];
}

export default function CoverageTrendChart({ trends }: CoverageTrendChartProps) {
  const chartData = useMemo(() => {
    if (!trends || trends.length === 0) return null;

    const maxCoverage = Math.max(...trends.map(t => t.coverage_percentage));
    const minCoverage = Math.min(...trends.map(t => t.coverage_percentage));
    const maxGaps = Math.max(...trends.map(t => t.total_gaps));

    return {
      maxCoverage,
      minCoverage,
      maxGaps,
      range: maxCoverage - minCoverage,
    };
  }, [trends]);

  if (!chartData || trends.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No trend data available. Create snapshots to track coverage over time.
      </div>
    );
  }

  const getYPosition = (percentage: number) => {
    const chartHeight = 200;
    const padding = 20;
    const range = chartData.range || 10; // Minimum range of 10%
    const minValue = Math.max(0, chartData.minCoverage - 5);
    const maxValue = Math.min(100, chartData.maxCoverage + 5);
    const normalizedRange = maxValue - minValue;

    const y = chartHeight - padding - ((percentage - minValue) / normalizedRange) * (chartHeight - 2 * padding);
    return y;
  };

  const getXPosition = (index: number) => {
    const chartWidth = 800;
    const padding = 40;
    const step = (chartWidth - 2 * padding) / Math.max(trends.length - 1, 1);
    return padding + index * step;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const pathData = trends.map((trend, index) => {
    const x = getXPosition(index);
    const y = getYPosition(trend.coverage_percentage);
    return index === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
  }).join(' ');

  const areaPathData = `${pathData} L ${getXPosition(trends.length - 1)} 220 L ${getXPosition(0)} 220 Z`;

  // Calculate trend direction
  const firstValue = trends[0].coverage_percentage;
  const lastValue = trends[trends.length - 1].coverage_percentage;
  const trendDirection = lastValue - firstValue;

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="bg-blue-50 rounded-lg p-3">
          <div className="text-sm text-gray-600">Current Coverage</div>
          <div className="text-2xl font-bold text-blue-600">
            {lastValue.toFixed(1)}%
          </div>
        </div>
        <div className={`rounded-lg p-3 ${trendDirection >= 0 ? 'bg-green-50' : 'bg-red-50'}`}>
          <div className="text-sm text-gray-600">Trend</div>
          <div className={`text-2xl font-bold ${trendDirection >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trendDirection >= 0 ? '+' : ''}{trendDirection.toFixed(1)}%
          </div>
        </div>
        <div className="bg-orange-50 rounded-lg p-3">
          <div className="text-sm text-gray-600">Critical Gaps</div>
          <div className="text-2xl font-bold text-orange-600">
            {trends[trends.length - 1].critical_gaps}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-gray-50 rounded-lg p-4">
        <svg
          viewBox="0 0 800 250"
          className="w-full"
          style={{ maxHeight: '300px' }}
        >
          {/* Grid lines */}
          {[0, 25, 50, 75, 100].map(value => {
            const y = getYPosition(value);
            return (
              <g key={value}>
                <line
                  x1="40"
                  y1={y}
                  x2="760"
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                  strokeDasharray="4 4"
                />
                <text
                  x="25"
                  y={y + 5}
                  fontSize="12"
                  fill="#6b7280"
                  textAnchor="end"
                >
                  {value}%
                </text>
              </g>
            );
          })}

          {/* Area under curve */}
          <path
            d={areaPathData}
            fill="url(#coverageGradient)"
            opacity="0.3"
          />

          {/* Gradient definition */}
          <defs>
            <linearGradient id="coverageGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.1" />
            </linearGradient>
          </defs>

          {/* Main line */}
          <path
            d={pathData}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data points */}
          {trends.map((trend, index) => {
            const x = getXPosition(index);
            const y = getYPosition(trend.coverage_percentage);

            return (
              <g key={index}>
                {/* Point circle */}
                <circle
                  cx={x}
                  cy={y}
                  r="5"
                  fill="#3b82f6"
                  stroke="white"
                  strokeWidth="2"
                  className="hover:r-7 cursor-pointer transition-all"
                />

                {/* Date label */}
                <text
                  x={x}
                  y="240"
                  fontSize="11"
                  fill="#6b7280"
                  textAnchor="middle"
                  className="select-none"
                >
                  {formatDate(trend.date)}
                </text>

                {/* Hover tooltip group */}
                <g className="opacity-0 hover:opacity-100 transition-opacity pointer-events-none">
                  <rect
                    x={x - 60}
                    y={y - 70}
                    width="120"
                    height="55"
                    fill="#1f2937"
                    rx="6"
                    opacity="0.95"
                  />
                  <text
                    x={x}
                    y={y - 50}
                    fontSize="12"
                    fill="white"
                    textAnchor="middle"
                    fontWeight="bold"
                  >
                    {trend.coverage_percentage.toFixed(1)}%
                  </text>
                  <text
                    x={x}
                    y={y - 35}
                    fontSize="10"
                    fill="#d1d5db"
                    textAnchor="middle"
                  >
                    {trend.covered_requirements}/{trend.total_requirements}
                  </text>
                  <text
                    x={x}
                    y={y - 22}
                    fontSize="10"
                    fill="#fbbf24"
                    textAnchor="middle"
                  >
                    {trend.total_gaps} gaps
                  </text>
                </g>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-blue-600"></div>
          <span>Coverage Percentage</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-600 border-2 border-white"></div>
          <span>Snapshot Point</span>
        </div>
      </div>

      {/* Detailed Table */}
      <div className="mt-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Snapshot History</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-gray-700">Date</th>
                <th className="px-4 py-2 text-right font-medium text-gray-700">Coverage</th>
                <th className="px-4 py-2 text-right font-medium text-gray-700">Covered</th>
                <th className="px-4 py-2 text-right font-medium text-gray-700">Total</th>
                <th className="px-4 py-2 text-right font-medium text-gray-700">Gaps</th>
                <th className="px-4 py-2 text-right font-medium text-gray-700">Critical Gaps</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {trends.slice().reverse().map((trend, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-2 text-gray-900">
                    {new Date(trend.date).toLocaleString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </td>
                  <td className="px-4 py-2 text-right">
                    <span className={`font-semibold ${
                      trend.coverage_percentage >= 90 ? 'text-green-600' :
                      trend.coverage_percentage >= 70 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {trend.coverage_percentage.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-2 text-right text-gray-700">
                    {trend.covered_requirements.toLocaleString()}
                  </td>
                  <td className="px-4 py-2 text-right text-gray-700">
                    {trend.total_requirements.toLocaleString()}
                  </td>
                  <td className="px-4 py-2 text-right text-orange-600 font-medium">
                    {trend.total_gaps.toLocaleString()}
                  </td>
                  <td className="px-4 py-2 text-right text-red-600 font-bold">
                    {trend.critical_gaps}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
