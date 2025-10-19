'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import toast from 'react-hot-toast';

interface Conflict {
  type: string;
  severity: string;
  description: string;
  source?: any;
  target?: any;
  requirements?: any[];
}

export default function ConflictsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [conflicts, setConflicts] = useState<any>(null);

  useEffect(() => {
    fetchConflicts();
  }, []);

  const fetchConflicts = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token') || localStorage.getItem('token') || localStorage.getItem('demo_token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await fetch('http://localhost:8000/api/traceability/conflicts', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setConflicts(data);
      } else {
        toast.error('Failed to load conflicts data');
      }
    } catch (error: any) {
      console.error('Failed to fetch conflicts:', error);
      toast.error('Failed to load conflicts');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout title="Requirement Conflicts & Inconsistencies">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" text="Analyzing requirements for conflicts..." />
        </div>
      </DashboardLayout>
    );
  }

  const totalConflicts = conflicts?.total_conflicts || 0;
  const explicitConflicts = conflicts?.conflicts?.explicit || [];
  const priorityIssues = conflicts?.conflicts?.priority_inconsistencies || [];
  const duplicates = conflicts?.conflicts?.potential_duplicates || [];

  return (
    <DashboardLayout title="Requirement Conflicts & Inconsistencies">
      <div className="space-y-6">
        {/* Header with Summary */}
        <div className="bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Conflict Detection Analysis</h2>
              <p className="mt-2 text-gray-600">
                Automated detection of requirement conflicts, inconsistencies, and potential duplicates
              </p>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-red-600">{totalConflicts}</div>
              <div className="text-sm text-gray-600">Total Issues Detected</div>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow-sm border-l-4 border-red-500 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Explicit Conflicts</p>
                <p className="mt-1 text-2xl font-bold text-red-600">{explicitConflicts.length}</p>
                <p className="mt-1 text-xs text-gray-500">High Severity</p>
              </div>
              <svg className="w-12 h-12 text-red-200" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border-l-4 border-orange-500 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Priority Inconsistencies</p>
                <p className="mt-1 text-2xl font-bold text-orange-600">{priorityIssues.length}</p>
                <p className="mt-1 text-xs text-gray-500">Medium Severity</p>
              </div>
              <svg className="w-12 h-12 text-orange-200" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
              </svg>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border-l-4 border-yellow-500 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Potential Duplicates</p>
                <p className="mt-1 text-2xl font-bold text-yellow-600">{duplicates.length}</p>
                <p className="mt-1 text-xs text-gray-500">Low Severity</p>
              </div>
              <svg className="w-12 h-12 text-yellow-200" fill="currentColor" viewBox="0 0 20 20">
                <path d="M7 9a2 2 0 012-2h6a2 2 0 012 2v6a2 2 0 01-2 2H9a2 2 0 01-2-2V9z" />
                <path d="M5 3a2 2 0 00-2 2v6a2 2 0 002 2V5h8a2 2 0 00-2-2H5z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Explicit Conflicts */}
        {explicitConflicts.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200 bg-red-50">
              <h3 className="text-lg font-semibold text-red-900">🚨 Explicit Conflicts ({explicitConflicts.length})</h3>
              <p className="text-sm text-red-700 mt-1">Requirements that directly conflict with each other</p>
            </div>
            <div className="p-6 space-y-4">
              {explicitConflicts.map((conflict: any, index: number) => (
                <div key={index} className="border border-red-200 rounded-lg p-4 bg-red-50">
                  <div className="flex items-start justify-between mb-3">
                    <span className="px-3 py-1 bg-red-600 text-white text-xs font-semibold rounded-full">
                      HIGH SEVERITY
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="border-l-4 border-red-500 pl-4">
                      <div className="text-sm font-semibold text-gray-900">{conflict.source?.requirement_id}</div>
                      <div className="text-sm text-gray-800 mt-1">{conflict.source?.title}</div>
                      <div className="mt-2 flex gap-2">
                        <span className="px-2 py-1 bg-white text-xs font-medium text-gray-900 rounded border border-gray-200">{conflict.source?.priority}</span>
                        <span className="px-2 py-1 bg-white text-xs font-medium text-gray-900 rounded border border-gray-200">{conflict.source?.status}</span>
                      </div>
                    </div>
                    <div className="border-l-4 border-red-500 pl-4">
                      <div className="text-sm font-semibold text-gray-900">{conflict.target?.requirement_id}</div>
                      <div className="text-sm text-gray-800 mt-1">{conflict.target?.title}</div>
                      <div className="mt-2 flex gap-2">
                        <span className="px-2 py-1 bg-white text-xs font-medium text-gray-900 rounded border border-gray-200">{conflict.target?.priority}</span>
                        <span className="px-2 py-1 bg-white text-xs font-medium text-gray-900 rounded border border-gray-200">{conflict.target?.status}</span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 p-3 bg-white rounded border border-red-200">
                    <div className="text-xs font-semibold text-gray-700 uppercase">Conflict Description</div>
                    <div className="text-sm text-gray-900 mt-1 leading-relaxed">{conflict.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Priority Inconsistencies */}
        {priorityIssues.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200 bg-orange-50">
              <h3 className="text-lg font-semibold text-orange-900">⚠️ Priority Inconsistencies ({priorityIssues.length})</h3>
              <p className="text-sm text-orange-700 mt-1">Requirements in the same category with inconsistent prioritization</p>
            </div>
            <div className="p-6 space-y-4">
              {priorityIssues.map((issue: any, index: number) => (
                <div key={index} className="border border-orange-200 rounded-lg p-4 bg-orange-50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="px-3 py-1 bg-orange-500 text-white text-xs font-semibold rounded-full">
                      MEDIUM SEVERITY
                    </span>
                    <span className="text-sm text-gray-600">{issue.count} requirements affected</span>
                  </div>
                  <div className="text-sm font-semibold text-gray-900 mb-2">{issue.description}</div>
                  <div className="grid grid-cols-2 gap-4 mt-3">
                    <div>
                      <div className="text-xs font-semibold text-gray-700 uppercase">Category</div>
                      <div className="text-sm font-medium text-gray-900">{issue.category}</div>
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-gray-700 uppercase">Verification Method</div>
                      <div className="text-sm font-medium text-gray-900">{issue.verification_method}</div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="text-xs font-semibold text-gray-700 uppercase mb-2">Detected Priorities:</div>
                    <div className="flex flex-wrap gap-2">
                      {issue.priorities?.map((priority: string, idx: number) => (
                        <span key={idx} className="px-2 py-1 bg-white border border-orange-300 text-xs font-medium text-gray-900 rounded">
                          {priority}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Potential Duplicates */}
        {duplicates.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200 bg-yellow-50">
              <h3 className="text-lg font-semibold text-yellow-900">📋 Potential Duplicates ({duplicates.length})</h3>
              <p className="text-sm text-yellow-700 mt-1">Requirements with similar titles that may be duplicates</p>
            </div>
            <div className="p-6 space-y-4">
              {duplicates.slice(0, 10).map((dup: any, index: number) => (
                <div key={index} className="border border-yellow-200 rounded-lg p-4 bg-yellow-50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="px-3 py-1 bg-yellow-500 text-white text-xs font-semibold rounded-full">
                      LOW SEVERITY
                    </span>
                    <span className="text-sm text-gray-600">{dup.count} similar requirements</span>
                  </div>
                  <div className="text-sm font-medium text-gray-900 mb-3">{dup.description}</div>
                  <div className="space-y-2">
                    {dup.requirements?.slice(0, 3).map((req: any, idx: number) => (
                      <div key={idx} className="flex items-start gap-3 p-2 bg-white rounded border border-yellow-200">
                        <div className="text-xs font-semibold text-blue-600">{req.requirement_id}</div>
                        <div className="flex-1 text-xs text-gray-800">{req.title}</div>
                        <div className="text-xs px-2 py-1 bg-gray-100 text-gray-800 font-medium rounded">{req.type}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Conflicts Found */}
        {totalConflicts === 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-8 text-center">
            <svg className="w-16 h-16 text-green-500 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <h3 className="text-xl font-semibold text-green-900">No Conflicts Detected</h3>
            <p className="mt-2 text-green-700">All requirements appear to be consistent and conflict-free.</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
