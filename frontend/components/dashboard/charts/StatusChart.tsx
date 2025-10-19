import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface StatusChartProps {
  data: Record<string, number>;
}

const STATUS_COLORS = {
  approved: '#10B981', // green
  draft: '#F59E0B', // yellow
  under_review: '#3B7DDD', // blue
  deprecated: '#6B7280', // gray
};

export const StatusChart: React.FC<StatusChartProps> = ({ data }) => {
  const chartData = Object.entries(data).map(([name, value]) => ({
    name: name.replace(/_/g, ' '),
    value,
    fill: STATUS_COLORS[name as keyof typeof STATUS_COLORS] || '#6B7280',
  }));

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Status Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#3B7DDD" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
