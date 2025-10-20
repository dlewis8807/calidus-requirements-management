'use client';

import React, { useState, useEffect } from 'react';
import { RiskOverview as RiskOverviewComponent } from '@/components/risk/RiskOverview';
import { RiskCard } from '@/components/risk/RiskCard';
import { riskAPI } from '@/lib/api';
import { RiskOverview as RiskOverviewType, RequirementRisk, RiskLevel } from '@/lib/types';
import { AlertTriangle, Filter, X, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function RiskDashboardPage() {
  const router = useRouter();
  const [overview, setOverview] = useState<RiskOverviewType | null>(null);
  const [filteredRisks, setFilteredRisks] = useState<RequirementRisk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedRiskLevel, setSelectedRiskLevel] = useState<RiskLevel | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadRiskData();
  }, []);

  useEffect(() => {
    if (selectedRiskLevel) {
      loadFilteredRisks();
    } else if (overview) {
      setFilteredRisks(overview.top_risks);
    }
  }, [selectedRiskLevel]);

  const loadRiskData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await riskAPI.overview();
      setOverview(data);
      setFilteredRisks(data.top_risks);
    } catch (err: any) {
      setError(err.message || 'Failed to load risk data');
      console.error('Error loading risk data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadFilteredRisks = async () => {
    if (!selectedRiskLevel) return;

    try {
      const data = await riskAPI.requirements({
        risk_level: selectedRiskLevel,
        limit: 50,
      });
      setFilteredRisks(data);
    } catch (err: any) {
      console.error('Error loading filtered risks:', err);
    }
  };

  const handleRiskLevelClick = (level: RiskLevel) => {
    if (selectedRiskLevel === level) {
      // Clear filter if clicking the same level
      setSelectedRiskLevel(null);
    } else {
      setSelectedRiskLevel(level);
    }
  };

  const handleClearFilters = () => {
    setSelectedRiskLevel(null);
  };

  if (loading) {
    return (
      <div className="p-6 lg:p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 lg:p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800">
            <AlertTriangle className="w-5 h-5" />
            <span className="font-medium">Error loading risk data</span>
          </div>
          <p className="text-sm text-red-600 mt-1">{error}</p>
          <button
            onClick={loadRiskData}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="p-6 lg:p-8">
        <div className="text-center text-gray-500 py-12">
          <p>No risk data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8">
      <div className="space-y-6">
        {/* Back Button */}
        <div>
          <button
            onClick={() => router.push('/dashboard')}
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            Go back to Dashboard
          </button>
        </div>

        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Risk Assessment Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Comprehensive risk analysis across {overview.distribution.total} requirements
            </p>
          </div>
          <button
            onClick={loadRiskData}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Refresh Data
          </button>
        </div>

        {/* Risk Overview */}
        <RiskOverviewComponent overview={overview} onRiskLevelClick={handleRiskLevelClick} />

        {/* Risk Cards Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {selectedRiskLevel ? `${selectedRiskLevel} Risk Requirements` : 'Top Risk Requirements'}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {selectedRiskLevel
                  ? `Showing ${filteredRisks.length} requirements with ${selectedRiskLevel.toLowerCase()} risk level`
                  : `Top ${filteredRisks.length} highest risk requirements`}
              </p>
            </div>

            {selectedRiskLevel && (
              <button
                onClick={handleClearFilters}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
              >
                <X className="w-4 h-4" />
                Clear Filter
              </button>
            )}
          </div>

          {/* Risk Cards Grid */}
          {filteredRisks.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredRisks.map((requirement) => (
                <RiskCard
                  key={requirement.id}
                  requirement={requirement}
                  onClick={() => {
                    // Navigate to requirement detail
                    window.location.href = `/dashboard/requirements/${requirement.id}`;
                  }}
                />
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-12">
              <p>No requirements found with the selected filters</p>
            </div>
          )}
        </div>

        {/* Action Items Section */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-amber-900 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Recommended Actions
          </h3>
          <ul className="space-y-2 text-sm text-amber-800">
            {overview.untested_requirements > 0 && (
              <li className="flex items-start gap-2">
                <span className="font-semibold mt-0.5">•</span>
                <span>
                  <strong>{overview.untested_requirements} requirements</strong> have no test cases.
                  Consider creating test cases to reduce risk.
                </span>
              </li>
            )}
            {overview.orphaned_requirements > 0 && (
              <li className="flex items-start gap-2">
                <span className="font-semibold mt-0.5">•</span>
                <span>
                  <strong>{overview.orphaned_requirements} requirements</strong> have no traceability links.
                  Establish parent-child relationships to improve traceability.
                </span>
              </li>
            )}
            {overview.non_compliant_requirements > 0 && (
              <li className="flex items-start gap-2">
                <span className="font-semibold mt-0.5">•</span>
                <span>
                  <strong>{overview.non_compliant_requirements} requirements</strong> are non-compliant.
                  Review and address compliance issues immediately.
                </span>
              </li>
            )}
            {overview.critical_requirements > 0 && (
              <li className="flex items-start gap-2">
                <span className="font-semibold mt-0.5">•</span>
                <span>
                  <strong>{overview.critical_requirements} requirements</strong> have critical priority.
                  Focus testing and verification efforts on these items.
                </span>
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
