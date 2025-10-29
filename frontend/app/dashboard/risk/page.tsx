'use client';

import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
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
      const typedData = data as RiskOverviewType;
      setOverview(typedData);
      setFilteredRisks(typedData.top_risks);
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
      setFilteredRisks(data as RequirementRisk[]);
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
      <DashboardLayout title="Risk Assessment">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout title="Risk Assessment">
        <div className="bg-red-50 border border-red-100 rounded-card-lg shadow-card p-8">
          <div className="flex items-center gap-3 text-red-800">
            <AlertTriangle className="w-6 h-6" />
            <span className="font-semibold text-lg">Error loading risk data</span>
          </div>
          <p className="text-sm text-red-600 mt-3">{error}</p>
          <button
            onClick={loadRiskData}
            className="mt-5 px-5 py-2.5 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors shadow-card font-semibold"
          >
            Retry
          </button>
        </div>
      </DashboardLayout>
    );
  }

  if (!overview) {
    return (
      <DashboardLayout title="Risk Assessment">
        <div className="bg-white rounded-card-lg shadow-card border border-gray-100 text-center text-gray-500 py-16">
          <p className="text-lg font-medium">No risk data available</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Risk Assessment">
      <div className="space-y-8">
        {/* Back Button */}
        <div>
          <button
            onClick={() => router.push('/dashboard')}
            className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-semibold transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-5 h-5" />
            Go back to Dashboard
          </button>
        </div>

        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Risk Assessment Dashboard</h1>
            <p className="text-gray-600 mt-2 text-base">
              Comprehensive risk analysis across {overview.distribution.total} requirements
            </p>
          </div>
          <button
            onClick={loadRiskData}
            className="px-5 py-2.5 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors shadow-card font-semibold"
          >
            Refresh Data
          </button>
        </div>

        {/* Risk Overview */}
        <RiskOverviewComponent overview={overview} onRiskLevelClick={handleRiskLevelClick} />

        {/* Risk Cards Section */}
        <div className="bg-white rounded-card-lg shadow-card border border-gray-100 p-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {selectedRiskLevel ? `${selectedRiskLevel} Risk Requirements` : 'Top Risk Requirements'}
              </h2>
              <p className="text-sm font-medium text-gray-600 mt-2">
                {selectedRiskLevel
                  ? `Showing ${filteredRisks.length} requirements with ${selectedRiskLevel.toLowerCase()} risk level`
                  : `Top ${filteredRisks.length} highest risk requirements`}
              </p>
            </div>

            {selectedRiskLevel && (
              <button
                onClick={handleClearFilters}
                className="flex items-center gap-2 px-5 py-2.5 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors font-semibold shadow-card"
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
            <div className="text-center text-gray-500 py-16">
              <p className="text-lg font-medium">No requirements found with the selected filters</p>
            </div>
          )}
        </div>

        {/* Action Items Section */}
        <div className="bg-amber-50 border border-amber-100 rounded-card-lg shadow-card p-8">
          <h3 className="text-xl font-bold text-amber-900 mb-6 flex items-center gap-3">
            <AlertTriangle className="w-6 h-6" />
            Recommended Actions
          </h3>
          <ul className="space-y-4 text-sm text-amber-800">
            {overview.untested_requirements > 0 && (
              <li className="flex items-start gap-3">
                <span className="font-bold mt-0.5">•</span>
                <span className="font-medium">
                  <strong className="font-bold">{overview.untested_requirements} requirements</strong> have no test cases.
                  Consider creating test cases to reduce risk.
                </span>
              </li>
            )}
            {overview.orphaned_requirements > 0 && (
              <li className="flex items-start gap-3">
                <span className="font-bold mt-0.5">•</span>
                <span className="font-medium">
                  <strong className="font-bold">{overview.orphaned_requirements} requirements</strong> have no traceability links.
                  Establish parent-child relationships to improve traceability.
                </span>
              </li>
            )}
            {overview.non_compliant_requirements > 0 && (
              <li className="flex items-start gap-3">
                <span className="font-bold mt-0.5">•</span>
                <span className="font-medium">
                  <strong className="font-bold">{overview.non_compliant_requirements} requirements</strong> are non-compliant.
                  Review and address compliance issues immediately.
                </span>
              </li>
            )}
            {overview.critical_requirements > 0 && (
              <li className="flex items-start gap-3">
                <span className="font-bold mt-0.5">•</span>
                <span className="font-medium">
                  <strong className="font-bold">{overview.critical_requirements} requirements</strong> have critical priority.
                  Focus testing and verification efforts on these items.
                </span>
              </li>
            )}
          </ul>
        </div>
      </div>
    </DashboardLayout>
  );
}
