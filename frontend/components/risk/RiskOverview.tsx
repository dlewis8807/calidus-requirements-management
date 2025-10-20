'use client';

import React from 'react';
import { RiskOverview as RiskOverviewType, RiskLevel } from '@/lib/types';
import { AlertTriangle, AlertCircle, Info, CheckCircle, TrendingUp, FileWarning, TestTube, GitBranch, FileX } from 'lucide-react';

interface RiskOverviewProps {
  overview: RiskOverviewType;
  onRiskLevelClick?: (level: RiskLevel) => void;
}

export function RiskOverview({ overview, onRiskLevelClick }: RiskOverviewProps) {
  const { distribution, average_risk_score } = overview;

  const getRiskColor = (level: RiskLevel): string => {
    switch (level) {
      case 'Critical':
        return '#8B0000';
      case 'High':
        return '#B45F06';
      case 'Medium':
        return '#4A5D23';
      case 'Low':
        return '#2D4F1E';
      default:
        return '#666666';
    }
  };

  const getRiskIcon = (level: RiskLevel, className = 'w-5 h-5') => {
    const color = getRiskColor(level);
    const iconProps = { className, style: { color } };

    switch (level) {
      case 'Critical':
        return <AlertTriangle {...iconProps} />;
      case 'High':
        return <AlertCircle {...iconProps} />;
      case 'Medium':
        return <Info {...iconProps} />;
      case 'Low':
        return <CheckCircle {...iconProps} />;
      default:
        return <Info {...iconProps} />;
    }
  };

  const getRiskPercentage = (count: number): number => {
    return distribution.total > 0 ? (count / distribution.total) * 100 : 0;
  };

  const getAverageScoreColor = (score: number): string => {
    if (score >= 76) return 'text-red-700';
    if (score >= 51) return 'text-orange-600';
    if (score >= 26) return 'text-yellow-700';
    return 'text-green-700';
  };

  return (
    <div className="space-y-6">
      {/* Overall Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Average Risk Score */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Average Risk Score</p>
              <p className={`text-3xl font-bold ${getAverageScoreColor(average_risk_score)}`}>
                {average_risk_score.toFixed(1)}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-gray-400" />
          </div>
        </div>

        {/* Critical Requirements */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Critical Priority</p>
              <p className="text-3xl font-bold text-red-700">{overview.critical_requirements}</p>
            </div>
            <FileWarning className="w-8 h-8 text-gray-400" />
          </div>
        </div>

        {/* Untested Requirements */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Untested</p>
              <p className="text-3xl font-bold text-orange-600">{overview.untested_requirements}</p>
            </div>
            <TestTube className="w-8 h-8 text-gray-400" />
          </div>
        </div>

        {/* Orphaned Requirements */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Orphaned</p>
              <p className="text-3xl font-bold text-amber-600">{overview.orphaned_requirements}</p>
            </div>
            <GitBranch className="w-8 h-8 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Risk Distribution */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>

        {/* Risk Level Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {(['Critical', 'High', 'Medium', 'Low'] as RiskLevel[]).map((level) => {
            const count = distribution[level.toLowerCase() as keyof typeof distribution] as number;
            const percentage = getRiskPercentage(count);
            const color = getRiskColor(level);

            return (
              <div
                key={level}
                className="border-2 rounded-lg p-4 cursor-pointer transition-all hover:shadow-md"
                style={{ borderColor: color }}
                onClick={() => onRiskLevelClick?.(level)}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-gray-700">{level}</span>
                  {getRiskIcon(level, 'w-5 h-5')}
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold" style={{ color }}>
                    {count}
                  </span>
                  <span className="text-sm text-gray-500">({percentage.toFixed(1)}%)</span>
                </div>
                <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full transition-all"
                    style={{
                      width: `${percentage}%`,
                      backgroundColor: color,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Pie Chart Visualization */}
        <div className="flex items-center justify-center">
          <svg width="300" height="300" viewBox="0 0 300 300" className="drop-shadow-sm">
            {/* Background circle */}
            <circle cx="150" cy="150" r="120" fill="none" stroke="#e5e7eb" strokeWidth="60" />

            {/* Pie slices */}
            {(() => {
              let currentAngle = -90; // Start from top
              const slices = ['critical', 'high', 'medium', 'low'].map((level) => {
                const count = distribution[level as keyof typeof distribution] as number;
                const percentage = getRiskPercentage(count);
                const angle = (percentage / 100) * 360;
                const startAngle = currentAngle;
                const endAngle = currentAngle + angle;

                // Calculate arc path
                const startRad = (startAngle * Math.PI) / 180;
                const endRad = (endAngle * Math.PI) / 180;
                const x1 = 150 + 120 * Math.cos(startRad);
                const y1 = 150 + 120 * Math.sin(startRad);
                const x2 = 150 + 120 * Math.cos(endRad);
                const y2 = 150 + 120 * Math.sin(endRad);
                const largeArc = angle > 180 ? 1 : 0;

                currentAngle = endAngle;

                return {
                  path: `M 150 150 L ${x1} ${y1} A 120 120 0 ${largeArc} 1 ${x2} ${y2} Z`,
                  color: getRiskColor(level.charAt(0).toUpperCase() + level.slice(1) as RiskLevel),
                  percentage,
                };
              });

              return slices.map((slice, index) => (
                slice.percentage > 0 && (
                  <path
                    key={index}
                    d={slice.path}
                    fill={slice.color}
                    opacity="0.8"
                    className="hover:opacity-100 transition-opacity"
                  />
                )
              ));
            })()}

            {/* Center circle for donut effect */}
            <circle cx="150" cy="150" r="70" fill="white" />

            {/* Center text */}
            <text
              x="150"
              y="140"
              textAnchor="middle"
              className="text-sm font-medium fill-gray-600"
            >
              Total
            </text>
            <text
              x="150"
              y="165"
              textAnchor="middle"
              className="text-2xl font-bold fill-gray-900"
            >
              {distribution.total}
            </text>
          </svg>
        </div>
      </div>
    </div>
  );
}
