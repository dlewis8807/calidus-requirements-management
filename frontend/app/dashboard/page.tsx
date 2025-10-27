'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { requirementsAPI, testCasesAPI, traceabilityAPI } from '@/lib/api';
import type { RequirementStats, TestCaseStats, TraceabilityReport } from '@/lib/types';

export default function DashboardPage() {
  const [reqStats, setReqStats] = useState<RequirementStats | null>(null);
  const [testStats, setTestStats] = useState<TestCaseStats | null>(null);
  const [traceReport, setTraceReport] = useState<TraceabilityReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [reqData, testData, traceData] = await Promise.all([
          requirementsAPI.stats(),
          testCasesAPI.stats(),
          traceabilityAPI.report(),
        ]);
        setReqStats(reqData as any);
        setTestStats(testData as any);
        setTraceReport(traceData as any);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <DashboardLayout title="Dashboard">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout title="Dashboard">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Dashboard">
      <div className="space-y-8">
        {/* Welcome Section */}
        <div className="bg-white rounded-card-lg shadow-card border border-gray-100 p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Welcome back, Admin!</h2>
          <p className="text-gray-600">Here&apos;s what&apos;s happening with your requirements today.</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total Requirements */}
          <div className="bg-white rounded-card shadow-card border border-gray-100 p-8 hover:shadow-card-hover transition-shadow">
            <div className="flex items-center justify-between mb-6">
              <div className="p-3 bg-blue-50 rounded-xl">
                <svg className="w-6 h-6 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            <h3 className="text-4xl font-bold text-gray-900 mb-2">
              {reqStats?.total_requirements.toLocaleString()}
            </h3>
            <p className="text-sm font-medium text-gray-600">Total Requirements</p>
            <div className="mt-4 flex items-center text-xs font-medium text-green-600">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clipRule="evenodd" />
              </svg>
              <span>100% imported</span>
            </div>
          </div>

          {/* Test Coverage */}
          <div className="bg-white rounded-card shadow-card border border-gray-100 p-8 hover:shadow-card-hover transition-shadow">
            <div className="flex items-center justify-between mb-6">
              <div className="p-3 bg-green-50 rounded-xl">
                <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <h3 className="text-4xl font-bold text-gray-900 mb-2">
              {reqStats?.coverage_percentage}%
            </h3>
            <p className="text-sm font-medium text-gray-600">Test Coverage</p>
            <div className="mt-4">
              <div className="w-full bg-gray-100 rounded-full h-2.5">
                <div
                  className="bg-gradient-to-r from-chart-teal to-green-500 h-2.5 rounded-full transition-all duration-500"
                  style={{ width: `${reqStats?.coverage_percentage}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Test Cases */}
          <div className="bg-white rounded-card shadow-card border border-gray-100 p-8 hover:shadow-card-hover transition-shadow">
            <div className="flex items-center justify-between mb-6">
              <div className="p-3 bg-purple-50 rounded-xl">
                <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
            </div>
            <h3 className="text-4xl font-bold text-gray-900 mb-2">
              {testStats?.total_test_cases.toLocaleString()}
            </h3>
            <p className="text-sm font-medium text-gray-600">Total Test Cases</p>
            <div className="mt-4 flex items-center text-xs font-medium text-green-600">
              <span>{testStats?.pass_rate.toFixed(1)}% pass rate</span>
            </div>
          </div>

          {/* Traceability Score */}
          <div className="bg-white rounded-card shadow-card border border-gray-100 p-8 hover:shadow-card-hover transition-shadow">
            <div className="flex items-center justify-between mb-6">
              <div className="p-3 bg-amber-50 rounded-xl">
                <svg className="w-6 h-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
            <h3 className="text-4xl font-bold text-gray-900 mb-2">
              {traceReport?.traceability_score.toFixed(1)}%
            </h3>
            <p className="text-sm font-medium text-gray-600">Traceability Health</p>
            <div className="mt-4 flex items-center text-xs font-medium text-amber-600">
              <span>{traceReport?.orphaned_requirements} orphaned</span>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Requirements by Type */}
          <div className="bg-white rounded-card-lg shadow-card border border-gray-100 p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-6">Requirements by Type</h3>
            <div className="space-y-4">
              {reqStats && Object.entries(reqStats.by_type).map(([type, count]) => {
                const percentage = (count / reqStats.total_requirements) * 100;
                const colors: Record<string, string> = {
                  'Aircraft_High_Level_Requirement': 'from-chart-sky to-primary-500',
                  'System_Requirement': 'from-chart-teal to-green-500',
                  'Technical_Specification': 'from-chart-lavender to-purple-500',
                  'Certification_Requirement': 'from-chart-amber to-orange-500',
                };
                return (
                  <div key={type}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-semibold text-gray-800">
                        {type.replace(/_/g, ' ')}
                      </span>
                      <span className="text-sm font-bold text-gray-900">{count.toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2.5">
                      <div
                        className={`bg-gradient-to-r ${colors[type] || 'bg-gray-600'} h-2.5 rounded-full transition-all duration-500`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Requirements by Status */}
          <div className="bg-white rounded-card-lg shadow-card border border-gray-100 p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-6">Requirements by Status</h3>
            <div className="space-y-4">
              {reqStats && Object.entries(reqStats.by_status).map(([status, count]) => {
                const percentage = (count / reqStats.total_requirements) * 100;
                const colors: Record<string, string> = {
                  'approved': 'from-chart-teal to-green-500',
                  'draft': 'from-chart-amber to-yellow-500',
                  'under_review': 'from-chart-sky to-blue-500',
                  'deprecated': 'bg-gray-400',
                };
                return (
                  <div key={status}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-semibold text-gray-800 capitalize">
                        {status.replace(/_/g, ' ')}
                      </span>
                      <span className="text-sm font-bold text-gray-900">{count.toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2.5">
                      <div
                        className={`bg-gradient-to-r ${colors[status] || 'bg-gray-600'} h-2.5 rounded-full transition-all duration-500`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-card-lg shadow-card border border-gray-100 p-8 hover:shadow-card-hover transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-2">With Traceability</p>
                <p className="text-3xl font-bold text-gray-900">
                  {traceReport?.requirements_with_parents.toLocaleString()}
                </p>
              </div>
              <div className="p-4 bg-blue-50 rounded-xl">
                <svg className="w-7 h-7 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-card-lg shadow-card border border-gray-100 p-8 hover:shadow-card-hover transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-2">Automated Tests</p>
                <p className="text-3xl font-bold text-gray-900">
                  {testStats?.total_automated.toLocaleString()}
                </p>
              </div>
              <div className="p-4 bg-green-50 rounded-xl">
                <svg className="w-7 h-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-card-lg shadow-card border border-gray-100 p-8 hover:shadow-card-hover transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-2">Trace Links</p>
                <p className="text-3xl font-bold text-gray-900">
                  {traceReport?.total_trace_links.toLocaleString()}
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-xl">
                <svg className="w-7 h-7 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
