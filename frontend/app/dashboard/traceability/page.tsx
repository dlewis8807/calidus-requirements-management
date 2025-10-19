'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Badge } from '@/components/common/Badge';
import RequirementModal from '@/components/RequirementModal';
import { traceabilityAPI } from '@/lib/api';
import type { TraceabilityReport, TraceabilityGap } from '@/lib/types';
import { ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export default function TraceabilityPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState<TraceabilityReport | null>(null);
  const [selectedRequirementId, setSelectedRequirementId] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const token = localStorage.getItem('token') || localStorage.getItem('demo_token');
        if (!token) {
          router.push('/login');
          return;
        }

        const data = await traceabilityAPI.report();
        setReport(data as TraceabilityReport);
      } catch (error: any) {
        console.error('Failed to fetch traceability report:', error);
        toast.error('Failed to load traceability report');
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
          router.push('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [router]);

  if (loading) {
    return (
      <DashboardLayout title="Traceability Matrix">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" text="Loading traceability report..." />
        </div>
      </DashboardLayout>
    );
  }

  if (!report) {
    return (
      <DashboardLayout title="Traceability Matrix">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">Failed to load traceability report</p>
        </div>
      </DashboardLayout>
    );
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-blue-600 bg-blue-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <DashboardLayout title="Traceability Matrix">
      <div className="space-y-6">
        {/* Action Buttons */}
        <div className="flex justify-end gap-3">
          <button
            onClick={() => router.push('/dashboard/traceability/graph')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
          >
            View Graph Visualization
          </button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Requirements</p>
                <p className="text-3xl font-bold text-gray-900">{report.total_requirements.toLocaleString()}</p>
              </div>
              <CheckCircleIcon className="h-12 w-12 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Trace Links</p>
                <p className="text-3xl font-bold text-gray-900">{report.total_trace_links.toLocaleString()}</p>
              </div>
              <CheckCircleIcon className="h-12 w-12 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Traceability Score</p>
                <p className="text-3xl font-bold text-[#3B7DDD]">{report.traceability_score.toFixed(1)}%</p>
              </div>
              <div className="w-full mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-[#3B7DDD] h-2 rounded-full"
                    style={{ width: `${report.traceability_score}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Gaps Found</p>
                <p className="text-3xl font-bold text-red-600">{report.traceability_gaps.length}</p>
              </div>
              <ExclamationTriangleIcon className="h-12 w-12 text-red-500" />
            </div>
          </div>
        </div>

        {/* Coverage Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Coverage Breakdown</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Requirements with Parents</span>
                  <span className="font-semibold">{report.requirements_with_parents.toLocaleString()}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${(report.requirements_with_parents / report.total_requirements) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Requirements with Children</span>
                  <span className="font-semibold">{report.requirements_with_children.toLocaleString()}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${(report.requirements_with_children / report.total_requirements) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Requirements with Tests</span>
                  <span className="font-semibold">{report.requirements_with_tests.toLocaleString()}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-500 h-2 rounded-full"
                    style={{ width: `${(report.requirements_with_tests / report.total_requirements) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Orphaned Requirements</span>
                  <span className="font-semibold text-red-600">{report.orphaned_requirements.toLocaleString()}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-red-500 h-2 rounded-full"
                    style={{ width: `${(report.orphaned_requirements / report.total_requirements) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Trace Links by Type</h3>
            <div className="space-y-3">
              {Object.entries(report.by_type).map(([type, count]) => {
                const percentage = report.total_trace_links > 0
                  ? (count / report.total_trace_links) * 100
                  : 0;
                return (
                  <div key={type}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700">{type.replace(/_/g, ' ')}</span>
                      <span className="font-semibold">{count}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-[#3B7DDD] h-2 rounded-full"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Traceability Gaps */}
        {report.traceability_gaps.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Traceability Gaps ({report.traceability_gaps.length})
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Requirement ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Gap Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Severity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {report.traceability_gaps.map((gap, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => setSelectedRequirementId(gap.requirement_identifier)}
                          className="text-[#3B7DDD] hover:text-[#2F66BD] hover:underline font-medium cursor-pointer"
                        >
                          {gap.requirement_identifier}
                        </button>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 max-w-md truncate">{gap.title}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge variant="type">{gap.type}</Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600 capitalize">
                          {gap.gap_type.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(gap.severity)}`}>
                          {gap.severity.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600 max-w-lg">{gap.description}</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Requirement Modal */}
      {selectedRequirementId && (
        <RequirementModal
          requirementId={selectedRequirementId}
          onClose={() => setSelectedRequirementId(null)}
          onRequirementClick={(reqId) => setSelectedRequirementId(reqId)}
        />
      )}
    </DashboardLayout>
  );
}
