'use client';

import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { impactAnalysisAPI, requirementsAPI } from '@/lib/api';
import { ImpactAnalysisResult, ImpactAnalysisReport, ChangeRequest, Requirement } from '@/lib/types';
import {
  ArrowLeft,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Users,
  FileText,
  Clock,
  CheckCircle2,
  XCircle,
  GitBranch,
  Target,
  Search,
} from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function ImpactAnalysisPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // State for analysis
  const [requirementId, setRequirementId] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<Requirement[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [analysis, setAnalysis] = useState<ImpactAnalysisResult | null>(null);
  const [analyzingId, setAnalyzingId] = useState<number | null>(null);

  // State for recent reports
  const [recentReports, setRecentReports] = useState<ImpactAnalysisReport[]>([]);
  const [changeRequests, setChangeRequests] = useState<ChangeRequest[]>([]);

  useEffect(() => {
    loadRecentData();
  }, []);

  // Close search results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('#searchQuery') && !target.closest('.search-results')) {
        setShowSearchResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Search requirements as user types
  useEffect(() => {
    const searchRequirements = async () => {
      if (!searchQuery || searchQuery.trim().length < 2) {
        setSearchResults([]);
        setShowSearchResults(false);
        return;
      }

      try {
        const results: any = await requirementsAPI.list({
          search: searchQuery,
          limit: 10,
        });

        // Handle both array response and paginated response
        const reqArray = Array.isArray(results) ? results : (results.requirements || []);
        setSearchResults(reqArray);
        setShowSearchResults(reqArray.length > 0);
      } catch (err: any) {
        console.error('Error searching requirements:', err);
        setSearchResults([]);
      }
    };

    const debounce = setTimeout(searchRequirements, 300);
    return () => clearTimeout(debounce);
  }, [searchQuery]);

  const loadRecentData = async () => {
    try {
      const [reports, requests]: [any, any] = await Promise.all([
        impactAnalysisAPI.listReports({ limit: 10 }),
        impactAnalysisAPI.listChangeRequests({ limit: 10 }),
      ]);
      setRecentReports(reports);
      setChangeRequests(requests);
    } catch (err: any) {
      console.error('Error loading recent data:', err);
    }
  };

  const handleSelectRequirement = (req: Requirement) => {
    setRequirementId(req.id.toString());
    setSearchQuery(req.requirement_id);
    setShowSearchResults(false);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!requirementId || !requirementId.trim()) {
      setError('Please select a requirement first');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Convert requirement ID string to number
      const reqId = parseInt(requirementId);
      if (isNaN(reqId)) {
        setError('Invalid requirement ID. Please select a requirement from the search results.');
        return;
      }

      setAnalyzingId(reqId);
      const result = await impactAnalysisAPI.analyze(reqId);
      setAnalysis(result as ImpactAnalysisResult);
      loadRecentData(); // Refresh recent reports
    } catch (err: any) {
      setError(err.message || 'Failed to analyze impact');
      console.error('Error analyzing impact:', err);
    } finally {
      setLoading(false);
      setAnalyzingId(null);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return 'text-red-700 bg-red-100 border-red-300';
      case 'HIGH':
        return 'text-orange-700 bg-orange-100 border-orange-300';
      case 'MEDIUM':
        return 'text-yellow-700 bg-yellow-100 border-yellow-300';
      case 'LOW':
        return 'text-green-700 bg-green-100 border-green-300';
      default:
        return 'text-gray-700 bg-gray-100 border-gray-300';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'APPROVED':
        return 'text-green-700 bg-green-100 border-green-300';
      case 'REJECTED':
        return 'text-red-700 bg-red-100 border-red-300';
      case 'PENDING':
        return 'text-yellow-700 bg-yellow-100 border-yellow-300';
      case 'IMPLEMENTED':
        return 'text-blue-700 bg-blue-100 border-blue-300';
      default:
        return 'text-gray-700 bg-gray-100 border-gray-300';
    }
  };

  return (
    <DashboardLayout title="Impact Analysis">
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
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Impact Analysis</h1>
          <p className="text-gray-600 mt-1">
            Analyze the ripple effects of requirement changes
          </p>
        </div>

        {/* Analyzer Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Analyze Requirement Impact</h2>

          <div className="flex gap-4">
            <div className="flex-1 relative">
              <label htmlFor="searchQuery" className="block text-sm font-medium text-gray-700 mb-2">
                Search Requirement
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="searchQuery"
                  type="text"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    if (e.target.value.trim().length < 2) {
                      setRequirementId('');
                    }
                  }}
                  placeholder="Search by ID (e.g., AHLR-001) or title..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && requirementId) {
                      handleAnalyze();
                    }
                  }}
                  onFocus={() => {
                    if (searchResults.length > 0) {
                      setShowSearchResults(true);
                    }
                  }}
                />
              </div>

              {/* Search Results Dropdown */}
              {showSearchResults && searchResults.length > 0 && (
                <div className="search-results absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                  {searchResults.map((req) => (
                    <button
                      key={req.id}
                      onClick={() => handleSelectRequirement(req)}
                      className="w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors border-b border-gray-100 last:border-0"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-gray-900">{req.requirement_id}</div>
                          <div className="text-sm text-gray-600 truncate">{req.title}</div>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700">
                              {req.type}
                            </span>
                            <span className="text-xs px-2 py-0.5 rounded bg-purple-100 text-purple-700">
                              {req.priority}
                            </span>
                          </div>
                        </div>
                        <div className="text-xs text-gray-500">ID: {req.id}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {searchQuery && searchResults.length === 0 && searchQuery.trim().length >= 2 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg p-4 text-center text-gray-500 text-sm">
                  No requirements found matching &quot;{searchQuery}&quot;
                </div>
              )}
            </div>
            <div className="flex items-end">
              <button
                onClick={handleAnalyze}
                disabled={loading || !requirementId}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Analyzing...' : 'Analyze Impact'}
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center gap-2 text-red-800">
                <AlertTriangle className="w-5 h-5" />
                <span className="font-medium">{error}</span>
              </div>
            </div>
          )}

          {requirementId && searchQuery && !error && (
            <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="text-sm text-blue-800">
                <span className="font-medium">Selected:</span> {searchQuery} (ID: {requirementId})
              </div>
            </div>
          )}
        </div>

        {/* Analysis Results */}
        {analysis && (
          <div className="space-y-6">
            {/* Risk Score Card */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Risk Assessment</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-gray-900">{analysis.risk_score.score.toFixed(1)}</div>
                  <div className="text-sm text-gray-600 mt-1">Risk Score</div>
                  <div className={`mt-2 px-3 py-1 rounded-full text-sm font-medium inline-block border ${getRiskColor(analysis.risk_score.level)}`}>
                    {analysis.risk_score.level}
                  </div>
                </div>

                <div className="text-center">
                  <div className="text-3xl font-bold text-gray-900">{analysis.stats.total_affected}</div>
                  <div className="text-sm text-gray-600 mt-1">Affected Requirements</div>
                  <div className="text-xs text-gray-500 mt-2">
                    ↑ {analysis.stats.upstream_count} | ↓ {analysis.stats.downstream_count}
                  </div>
                </div>

                <div className="text-center">
                  <div className="text-3xl font-bold text-gray-900">{analysis.affected_test_cases.length}</div>
                  <div className="text-sm text-gray-600 mt-1">Affected Test Cases</div>
                </div>

                <div className="text-center">
                  <div className="text-3xl font-bold text-gray-900">{analysis.estimated_effort_hours.toFixed(1)}</div>
                  <div className="text-sm text-gray-600 mt-1">Estimated Hours</div>
                </div>
              </div>

              {/* Risk Factors */}
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Risk Factors</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                  {Object.entries(analysis.risk_score.factors).map(([factor, value]) => (
                    <div key={factor} className="bg-gray-50 rounded-lg p-3">
                      <div className="text-xs text-gray-600 capitalize">{factor}</div>
                      <div className="text-lg font-semibold text-gray-900">{(value as unknown as number).toFixed(0)}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Impact Tree */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Upstream Dependencies */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  <h2 className="text-xl font-semibold text-gray-900">Upstream ({analysis.stats.upstream_count})</h2>
                </div>

                {analysis.upstream.length > 0 ? (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {analysis.upstream.map((node, idx) => (
                      <div
                        key={idx}
                        className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                        style={{ marginLeft: `${node.depth * 12}px` }}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-gray-900 truncate">{node.requirement_id}</div>
                            <div className="text-sm text-gray-600 truncate">{node.title}</div>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700">{node.type}</span>
                              <span className="text-xs px-2 py-0.5 rounded bg-purple-100 text-purple-700">{node.priority}</span>
                              {node.regulatory && (
                                <span className="text-xs px-2 py-0.5 rounded bg-red-100 text-red-700">Regulatory</span>
                              )}
                            </div>
                          </div>
                          <div className="text-xs text-gray-500">Depth: {node.depth}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    <Target className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                    <p>No upstream dependencies</p>
                  </div>
                )}
              </div>

              {/* Downstream Impacts */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <TrendingDown className="w-5 h-5 text-green-600" />
                  <h2 className="text-xl font-semibold text-gray-900">Downstream ({analysis.stats.downstream_count})</h2>
                </div>

                {analysis.downstream.length > 0 ? (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {analysis.downstream.map((node, idx) => (
                      <div
                        key={idx}
                        className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                        style={{ marginLeft: `${node.depth * 12}px` }}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-gray-900 truncate">{node.requirement_id}</div>
                            <div className="text-sm text-gray-600 truncate">{node.title}</div>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700">{node.type}</span>
                              <span className="text-xs px-2 py-0.5 rounded bg-purple-100 text-purple-700">{node.priority}</span>
                              {node.regulatory && (
                                <span className="text-xs px-2 py-0.5 rounded bg-red-100 text-red-700">Regulatory</span>
                              )}
                              {node.test_case_count > 0 && (
                                <span className="text-xs px-2 py-0.5 rounded bg-green-100 text-green-700">
                                  {node.test_case_count} tests
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="text-xs text-gray-500">Depth: {node.depth}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    <GitBranch className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                    <p>No downstream impacts</p>
                  </div>
                )}
              </div>
            </div>

            {/* Recommendations & Regulatory */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recommendations */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5" />
                  Recommendations
                </h3>
                {analysis.recommendations.length > 0 ? (
                  <ul className="space-y-2">
                    {analysis.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-blue-800">
                        <span className="font-semibold mt-0.5">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-blue-700">No specific recommendations</p>
                )}
              </div>

              {/* Regulatory Implications */}
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-amber-900 mb-4 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Regulatory Implications
                </h3>
                {analysis.regulatory_implications.length > 0 ? (
                  <ul className="space-y-2">
                    {analysis.regulatory_implications.map((impl, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-amber-800">
                        <span className="font-semibold mt-0.5">•</span>
                        <span>{impl}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-amber-700">No regulatory implications detected</p>
                )}
              </div>
            </div>

            {/* Explanation */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Risk Score Explanation</h3>
              <p className="text-sm text-gray-700">{analysis.risk_score.explanation}</p>
            </div>
          </div>
        )}

        {/* Recent Reports & Change Requests */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Reports */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Recent Reports</h2>
              <FileText className="w-5 h-5 text-gray-400" />
            </div>

            {recentReports.length > 0 ? (
              <div className="space-y-3">
                {recentReports.map((report) => (
                  <div
                    key={report.id}
                    className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => setAnalyzingId(report.requirement_id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900">Req #{report.requirement_id}</div>
                        <div className="text-sm text-gray-600">{report.stats.total_affected} affected</div>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-medium border ${getRiskColor(report.risk_level)}`}>
                        {report.risk_level}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <FileText className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                <p>No recent reports</p>
              </div>
            )}
          </div>

          {/* Change Requests */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Change Requests</h2>
              <Users className="w-5 h-5 text-gray-400" />
            </div>

            {changeRequests.length > 0 ? (
              <div className="space-y-3">
                {changeRequests.map((request) => (
                  <div
                    key={request.id}
                    className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium text-gray-900 truncate">{request.title}</div>
                      <div className={`px-2 py-1 rounded text-xs font-medium border ${getStatusColor(request.status)}`}>
                        {request.status}
                      </div>
                    </div>
                    <div className="text-sm text-gray-600 truncate">{request.description}</div>
                    <div className="text-xs text-gray-500 mt-1">Req #{request.requirement_id}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <Users className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                <p>No change requests</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
