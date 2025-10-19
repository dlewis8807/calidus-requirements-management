import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

interface TestCoverageChartProps {
  totalRequirements: number;
  requirementsWithTests: number;
  coveragePercentage: number;
}

export const TestCoverageChart: React.FC<TestCoverageChartProps> = ({
  totalRequirements,
  requirementsWithTests,
  coveragePercentage,
}) => {
  const data = [
    {
      name: 'Tested',
      value: requirementsWithTests,
      fill: '#10B981',
    },
    {
      name: 'Untested',
      value: totalRequirements - requirementsWithTests,
      fill: '#EF4444',
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">Test Coverage</h3>
      <p className="text-3xl font-bold text-[#3B7DDD] mb-4">{coveragePercentage.toFixed(1)}%</p>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis dataKey="name" type="category" />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" radius={[0, 8, 8, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-600">Tested Requirements</p>
          <p className="text-lg font-semibold text-green-600">{requirementsWithTests.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-gray-600">Untested Requirements</p>
          <p className="text-lg font-semibold text-red-600">{(totalRequirements - requirementsWithTests).toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
};
