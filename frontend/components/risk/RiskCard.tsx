'use client';

import React from 'react';
import { RequirementRisk, RiskLevel } from '@/lib/types';
import { AlertTriangle, AlertCircle, Info, CheckCircle } from 'lucide-react';

interface RiskCardProps {
  requirement: RequirementRisk;
  onClick?: () => void;
}

export function RiskCard({ requirement, onClick }: RiskCardProps) {
  const { risk_score } = requirement;

  // Get risk level styling
  const getRiskColor = (level: RiskLevel): string => {
    switch (level) {
      case 'Critical':
        return '#8B0000'; // Dark red
      case 'High':
        return '#B45F06'; // Amber/orange
      case 'Medium':
        return '#4A5D23'; // Olive green
      case 'Low':
        return '#2D4F1E'; // Dark green
      default:
        return '#666666';
    }
  };

  const getRiskBgColor = (level: RiskLevel): string => {
    switch (level) {
      case 'Critical':
        return 'bg-red-50 border-red-200';
      case 'High':
        return 'bg-orange-50 border-orange-200';
      case 'Medium':
        return 'bg-yellow-50 border-yellow-200';
      case 'Low':
        return 'bg-green-50 border-green-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (level: RiskLevel) => {
    const color = getRiskColor(level);
    const iconProps = { className: 'w-5 h-5', style: { color } };

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

  const getScoreColor = (score: number): string => {
    if (score >= 76) return 'text-red-700 font-semibold';
    if (score >= 51) return 'text-orange-600 font-semibold';
    if (score >= 26) return 'text-yellow-700';
    return 'text-green-700';
  };

  const getTypeLabel = (type: string): string => {
    switch (type) {
      case 'Aircraft_High_Level_Requirement':
        return 'AHLR';
      case 'System_Requirement':
        return 'System';
      case 'Technical_Specification':
        return 'Technical';
      case 'Certification_Requirement':
        return 'Certification';
      default:
        return type;
    }
  };

  const riskColor = getRiskColor(risk_score.risk_level);
  const riskBgColor = getRiskBgColor(risk_score.risk_level);

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border-2 ${riskBgColor} p-6 transition-all hover:shadow-md ${
        onClick ? 'cursor-pointer' : ''
      }`}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-lg font-bold text-gray-900">{requirement.requirement_id}</h3>
            <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600">
              {getTypeLabel(requirement.type)}
            </span>
          </div>
          <p className="text-sm text-gray-600 line-clamp-2">{requirement.title}</p>
        </div>
        <div className="flex items-center gap-2">
          {getRiskIcon(risk_score.risk_level)}
          <span
            className="px-3 py-1 rounded-full text-sm font-medium text-white whitespace-nowrap"
            style={{ backgroundColor: riskColor }}
          >
            {risk_score.risk_level} Risk
          </span>
        </div>
      </div>

      {/* Risk Score Overview */}
      <div
        className={`mb-6 p-4 rounded-lg ${
          risk_score.risk_level === 'Critical'
            ? 'bg-red-50'
            : risk_score.risk_level === 'High'
            ? 'bg-orange-50'
            : risk_score.risk_level === 'Medium'
            ? 'bg-yellow-50'
            : 'bg-green-50'
        }`}
      >
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Overall Risk Score</span>
          <span className={`text-3xl font-bold ${getScoreColor(risk_score.total_risk_score)}`}>
            {risk_score.total_risk_score.toFixed(1)}
          </span>
        </div>
        <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
          <div
            className="h-2 rounded-full"
            style={{
              width: `${risk_score.total_risk_score}%`,
              backgroundColor: riskColor,
            }}
          />
        </div>
      </div>

      {/* Risk Factor Breakdown Table */}
      <div className="mb-6">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Risk Factor Breakdown</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-1 font-medium text-gray-600">Factor</th>
                <th className="text-right py-2 px-1 font-medium text-gray-600">Weight</th>
                <th className="text-right py-2 px-1 font-medium text-gray-600">Score</th>
                <th className="text-right py-2 px-1 font-medium text-gray-600">Impact</th>
              </tr>
            </thead>
            <tbody>
              {risk_score.factors.map((factor, index) => (
                <tr key={index} className="border-b border-gray-100">
                  <td className="py-2 px-1 text-gray-700">{factor.factor_name}</td>
                  <td className="text-right py-2 px-1 text-gray-600">{factor.weight.toFixed(0)}%</td>
                  <td className={`text-right py-2 px-1 ${getScoreColor(factor.score)}`}>
                    {factor.score.toFixed(0)}
                  </td>
                  <td className="text-right py-2 px-1 font-semibold text-gray-700">
                    {factor.impact.toFixed(1)}
                  </td>
                </tr>
              ))}
              {/* Total Row */}
              <tr className="bg-gray-50 font-bold">
                <td className="py-2 px-1 text-gray-900">Total Risk Score</td>
                <td className="text-right py-2 px-1 text-gray-900">100%</td>
                <td className="text-right py-2 px-1"></td>
                <td className={`text-right py-2 px-1 text-lg ${getScoreColor(risk_score.total_risk_score)}`}>
                  {risk_score.total_risk_score.toFixed(1)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          className="flex-1 px-4 py-2 rounded-md font-medium text-white transition-colors"
          style={{ backgroundColor: riskColor }}
          onClick={(e) => {
            e.stopPropagation();
            onClick?.();
          }}
        >
          View Risk Details
        </button>
        <button
          className="px-4 py-2 rounded-md font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
          onClick={(e) => {
            e.stopPropagation();
            // Handle action button click
          }}
        >
          Take Action
        </button>
      </div>
    </div>
  );
}
