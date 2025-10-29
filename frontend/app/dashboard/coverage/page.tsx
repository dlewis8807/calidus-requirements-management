'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { coverageAPI } from '@/lib/api';
import CoverageHeatmap from '@/components/coverage/CoverageHeatmap';
import CoverageGapList from '@/components/coverage/CoverageGapList';
import CoverageTrendChart from '@/components/coverage/CoverageTrendChart';
import TestSuggestions from '@/components/coverage/TestSuggestions';
import { ArrowUpIcon, ArrowDownIcon } from 'lucide-react';

interface CoverageAnalysis {
  overall: {
    total_requirements: number;
    covered_requirements: number;
    uncovered_requirements: number;
    coverage_percentage: number;
  };
  by_type: Record<string, any>;
  by_priority: Record<string, any>;
  heatmap: Record<string, Record<string, any>>;
  gaps: Array<{
    requirement_id: number;
    requirement_identifier: string;
    title: string;
    type: string;
    priority: string;
    status: string;
    regulatory: boolean;
    regulatory_document?: string;
  }>;
  trends: Array<{
    date: string;
    coverage_percentage: number;
    total_requirements: number;
    covered_requirements: number;
    total_gaps: number;
    critical_gaps: number;
  }>;
}

export default function CoverageDashboard() {
  const [coverage, setCoverage] = useState<CoverageAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedGap, setSelectedGap] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Map backend requirement types to display names
  const typeMapping: Record<string, string> = {
    'Aircraft_High_Level_Requirement': 'AHLR',
    'System_Requirement': 'System',
    'Technical_Specification': 'Technical',
    'Certification_Requirement': 'Certification'
  };

  useEffect(() => {
    loadCoverageAnalysis();
  }, []);

  const loadCoverageAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await coverageAPI.analyze();
      setCoverage(data as CoverageAnalysis);
    } catch (err: any) {
      console.error('Error loading coverage analysis:', err);
      setError(err.message || 'Failed to load coverage analysis');
    } finally {
      setLoading(false);
    }
  };

  const createSnapshot = async () => {
    try {
      await coverageAPI.createSnapshot();
      await loadCoverageAnalysis(); // Reload to get updated trends
    } catch (err: any) {
      console.error('Error creating snapshot:', err);
      setError(err.message || 'Failed to create snapshot');
    }
  };

  const getTrendIndicator = () => {
    if (!coverage?.trends || coverage.trends.length < 2) return null;

    const latest = coverage.trends[coverage.trends.length - 1].coverage_percentage;
    const previous = coverage.trends[coverage.trends.length - 2].coverage_percentage;
    const diff = latest - previous;

    if (Math.abs(diff) < 0.1) return null;

    return diff > 0 ? (
      <span className="flex items-center text-green-600 text-sm">
        <ArrowUpIcon className="w-4 h-4 mr-1" />
        +{diff.toFixed(1)}%
      </span>
    ) : (
      <span className="flex items-center text-red-600 text-sm">
        <ArrowDownIcon className="w-4 h-4 mr-1" />
        {diff.toFixed(1)}%
      </span>
    );
  };

  if (loading) {
    return (
      <DashboardLayout title="Test Coverage Analyzer">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Analyzing test coverage...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout title="Test Coverage Analyzer">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-semibold">Error</h3>
          <p className="text-red-600">{error}</p>
          <button
            onClick={loadCoverageAnalysis}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </DashboardLayout>
    );
  }

  if (!coverage) return null;

  const criticalGaps = coverage.gaps.filter(g => g.priority === 'Critical').length;

  return (
    <DashboardLayout title="Test Coverage Analyzer">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <p className="text-gray-600">
              Comprehensive analysis of test coverage across all requirements
            </p>
          </div>
        <button
          onClick={createSnapshot}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Create Snapshot
        </button>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Overall Coverage */}
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium opacity-90">Overall Coverage</h3>
            {getTrendIndicator()}
          </div>
          <p className="text-4xl font-bold mb-1">
            {coverage.overall.coverage_percentage.toFixed(1)}%
          </p>
          <p className="text-sm opacity-90">
            {coverage.overall.covered_requirements.toLocaleString()} / {coverage.overall.total_requirements.toLocaleString()} requirements
          </p>
        </div>

        {/* Uncovered Requirements */}
        <div className="bg-white rounded-lg p-6 shadow-lg border border-gray-200">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Uncovered Requirements</h3>
          <p className="text-4xl font-bold text-orange-600 mb-1">
            {coverage.overall.uncovered_requirements.toLocaleString()}
          </p>
          <p className="text-sm text-gray-500">Total gaps to address</p>
        </div>

        {/* Critical Gaps */}
        <div className="bg-white rounded-lg p-6 shadow-lg border border-gray-200">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Critical Gaps</h3>
          <p className="text-4xl font-bold text-red-600 mb-1">
            {criticalGaps}
          </p>
          <p className="text-sm text-gray-500">High priority issues</p>
        </div>

        {/* Coverage by Type */}
        <div className="bg-white rounded-lg p-6 shadow-lg border border-gray-200">
          <h3 className="text-sm font-medium text-gray-600 mb-3">Coverage by Type</h3>
          <div className="space-y-2">
            {Object.entries(coverage.by_type).map(([type, data]: [string, any]) => (
              <div key={type} className="flex justify-between items-center text-sm">
                <span className="text-gray-700">{typeMapping[type] || type}</span>
                <span className={`font-semibold ${
                  data.coverage_percentage >= 90 ? 'text-green-600' :
                  data.coverage_percentage >= 70 ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {data.coverage_percentage.toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Coverage Heatmap */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Coverage Heatmap (Type × Priority)
        </h2>
        <CoverageHeatmap data={coverage.heatmap} />
      </div>

      {/* Trend Chart */}
      {coverage.trends.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Coverage Trends
          </h2>
          <CoverageTrendChart trends={coverage.trends} />
        </div>
      )}

      {/* Gap List and Suggestions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gap List */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Coverage Gaps ({coverage.gaps.length})
          </h2>
          <CoverageGapList
            gaps={coverage.gaps}
            onSelectGap={setSelectedGap}
            selectedGap={selectedGap}
          />
        </div>

        {/* Test Suggestions */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Test Suggestions
          </h2>
          {selectedGap ? (
            <TestSuggestions requirementId={selectedGap} />
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>Select a gap from the list to see test suggestions</p>
            </div>
          )}
        </div>
      </div>
      </div>
    </DashboardLayout>
  );
}
