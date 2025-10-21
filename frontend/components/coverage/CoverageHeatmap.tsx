'use client';

import { useState } from 'react';

interface HeatmapCell {
  total: number;
  covered: number;
  uncovered: number;
  coverage_percentage: number;
}

interface CoverageHeatmapProps {
  data: Record<string, Record<string, HeatmapCell>>;
}

export default function CoverageHeatmap({ data }: CoverageHeatmapProps) {
  const [hoveredCell, setHoveredCell] = useState<{type: string; priority: string} | null>(null);

  // Map backend requirement types to display names
  const typeMapping: Record<string, string> = {
    'Aircraft_High_Level_Requirement': 'AHLR',
    'System_Requirement': 'System',
    'Technical_Specification': 'Technical',
    'Certification_Requirement': 'Certification'
  };

  // Get actual types from data keys
  const backendTypes = Object.keys(data);
  const types = backendTypes.map(t => typeMapping[t] || t);
  const priorities = ['Critical', 'High', 'Medium', 'Low'];

  const getColorClass = (percentage: number) => {
    if (percentage >= 90) return 'bg-green-500';
    if (percentage >= 75) return 'bg-green-400';
    if (percentage >= 60) return 'bg-yellow-400';
    if (percentage >= 40) return 'bg-orange-400';
    if (percentage >= 20) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getTextColor = (percentage: number) => {
    return percentage >= 40 ? 'text-white' : 'text-gray-900';
  };

  return (
    <div className="overflow-x-auto">
      <div className="inline-block min-w-full">
        <table className="min-w-full border-collapse">
          <thead>
            <tr>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b-2 border-gray-300">
                Type / Priority
              </th>
              {priorities.map(priority => (
                <th
                  key={priority}
                  className="px-4 py-3 text-center text-sm font-semibold text-gray-700 border-b-2 border-gray-300"
                >
                  {priority}
                </th>
              ))}
              <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700 border-b-2 border-gray-300">
                Type Total
              </th>
            </tr>
          </thead>
          <tbody>
            {backendTypes.map((backendType, typeIndex) => {
              const displayType = types[typeIndex];
              const typeData = data[backendType] || {};
              const typeTotals = priorities.reduce((acc, priority) => {
                const cell = typeData[priority];
                if (cell) {
                  acc.total += cell.total;
                  acc.covered += cell.covered;
                }
                return acc;
              }, { total: 0, covered: 0 });
              const typePercentage = typeTotals.total > 0
                ? (typeTotals.covered / typeTotals.total) * 100
                : 0;

              return (
                <tr key={backendType} className="border-b border-gray-200">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {displayType}
                  </td>
                  {priorities.map(priority => {
                    const cell = typeData[priority];
                    const percentage = cell?.coverage_percentage || 0;
                    const isHovered = hoveredCell?.type === backendType && hoveredCell?.priority === priority;

                    return (
                      <td
                        key={priority}
                        className="px-2 py-2 text-center relative"
                        onMouseEnter={() => setHoveredCell({ type: backendType, priority })}
                        onMouseLeave={() => setHoveredCell(null)}
                      >
                        <div
                          className={`
                            ${getColorClass(percentage)}
                            ${getTextColor(percentage)}
                            rounded-lg p-3 transition-all duration-200
                            ${isHovered ? 'scale-105 shadow-lg' : 'shadow'}
                            cursor-pointer
                          `}
                        >
                          <div className="font-bold text-lg">
                            {percentage.toFixed(0)}%
                          </div>
                          <div className="text-xs opacity-90">
                            {cell?.covered || 0}/{cell?.total || 0}
                          </div>
                        </div>

                        {/* Tooltip */}
                        {isHovered && cell && (
                          <div className="absolute z-10 left-1/2 -translate-x-1/2 top-full mt-2 bg-gray-900 text-white px-3 py-2 rounded-lg shadow-xl text-xs whitespace-nowrap">
                            <div className="font-semibold mb-1">{displayType} - {priority}</div>
                            <div>Total: {cell.total}</div>
                            <div>Covered: {cell.covered}</div>
                            <div>Uncovered: {cell.uncovered}</div>
                            <div>Coverage: {cell.coverage_percentage.toFixed(1)}%</div>
                            <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45"></div>
                          </div>
                        )}
                      </td>
                    );
                  })}
                  <td className="px-4 py-3 text-center">
                    <div className="font-semibold text-gray-900">
                      {typePercentage.toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-500">
                      {typeTotals.covered}/{typeTotals.total}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {/* Legend */}
        <div className="mt-6 flex items-center justify-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-red-500 rounded"></div>
            <span className="text-gray-700">0-20%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-orange-500 rounded"></div>
            <span className="text-gray-700">20-40%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-orange-400 rounded"></div>
            <span className="text-gray-700">40-60%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-yellow-400 rounded"></div>
            <span className="text-gray-700">60-75%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-green-400 rounded"></div>
            <span className="text-gray-700">75-90%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-green-500 rounded"></div>
            <span className="text-gray-700">90-100%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
