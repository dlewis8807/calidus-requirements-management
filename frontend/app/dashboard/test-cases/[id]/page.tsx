'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import Badge from '@/components/common/Badge';
import { SuggestionsPanel } from '@/components/test-cases/SuggestionsPanel';
import { testCasesAPI } from '@/lib/api';
import {
  ArrowLeftIcon,
  ClockIcon,
  UserIcon,
  BeakerIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlayIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';

export default function TestCaseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const testCaseId = parseInt(params.id as string);

  const [testCase, setTestCase] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Only fetch if we have a valid ID
    if (!isNaN(testCaseId) && testCaseId > 0) {
      fetchTestCase();
    } else {
      setError('Invalid test case ID');
      setLoading(false);
    }
  }, [testCaseId]);

  const fetchTestCase = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/test-cases/${testCaseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch test case');
      }

      const data = await response.json();
      setTestCase(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching test case:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    return 'status' as const;
  };

  const getPriorityBadgeVariant = (priority: string) => {
    return 'priority' as const;
  };

  if (loading) {
    return (
      <DashboardLayout title="Test Case Details">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !testCase) {
    return (
      <DashboardLayout title="Test Case Details">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-800">{error || 'Test case not found'}</p>
          <button
            onClick={() => router.back()}
            className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            ← Go back
          </button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title={testCase.test_case_id}>
      <div className="space-y-6">
        {/* Back Button */}
        <button
          onClick={() => router.back()}
          className="flex items-center text-sm text-gray-600 hover:text-gray-900"
        >
          <ArrowLeftIcon className="w-4 h-4 mr-2" />
          Back to Test Cases
        </button>

        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold text-gray-900">{testCase.test_case_id}</h1>
                <Badge variant={getStatusBadgeVariant(testCase.status)} label={testCase.status} />
                <Badge variant={getPriorityBadgeVariant(testCase.priority)} label={testCase.priority} />
              </div>
              <h2 className="text-lg text-gray-700 mb-4">{testCase.title}</h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="flex items-center gap-2 text-gray-600">
                  <BeakerIcon className="w-4 h-4" />
                  <span className="font-medium">Type:</span>
                  <span>{testCase.test_type}</span>
                </div>
                {testCase.execution_date && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <ClockIcon className="w-4 h-4" />
                    <span className="font-medium">Executed:</span>
                    <span>{new Date(testCase.execution_date).toLocaleDateString()}</span>
                  </div>
                )}
                {testCase.executed_by && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <UserIcon className="w-4 h-4" />
                    <span className="font-medium">By:</span>
                    <span>{testCase.executed_by}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Description */}
        {testCase.description && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <DocumentTextIcon className="w-5 h-5 text-gray-600" />
              Description
            </h3>
            <p className="text-gray-700 whitespace-pre-wrap">{testCase.description}</p>
          </div>
        )}

        {/* Test Steps */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <PlayIcon className="w-5 h-5 text-blue-600" />
            Test Steps
          </h3>
          <ol className="space-y-2">
            {JSON.parse(testCase.test_steps || '[]').map((step: string, index: number) => (
              <li key={index} className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-semibold">
                  {index + 1}
                </span>
                <span className="text-gray-700">{step}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Expected vs Actual Results */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <CheckCircleIcon className="w-5 h-5 text-green-600" />
              Expected Results
            </h3>
            <ul className="space-y-2">
              {JSON.parse(testCase.expected_results || '[]').map((result: string, index: number) => (
                <li key={index} className="flex gap-2 text-gray-700">
                  <span className="text-green-500">✓</span>
                  <span>{result}</span>
                </li>
              ))}
            </ul>
          </div>

          {testCase.actual_results && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <XCircleIcon className={`w-5 h-5 ${(testCase.status === 'FAILED' || testCase.status === 'failed') ? 'text-red-600' : 'text-green-600'}`} />
                Actual Results
              </h3>
              <ul className="space-y-2">
                {JSON.parse(testCase.actual_results || '[]').map((result: string, index: number) => (
                  <li key={index} className="flex gap-2 text-gray-700">
                    <span className={(testCase.status === 'FAILED' || testCase.status === 'failed') ? 'text-red-500' : 'text-green-500'}>
                      {(testCase.status === 'FAILED' || testCase.status === 'failed') ? '✗' : '✓'}
                    </span>
                    <span>{result}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* AI Suggestions Panel - Only show for failed tests */}
        {(testCase.status === 'FAILED' || testCase.status === 'failed') && (
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-4">Intelligent Failure Analysis</h3>
            <SuggestionsPanel
              testCaseId={testCaseId}
              executionLog={testCase.actual_results || testCase.description}
            />
          </div>
        )}

        {/* Metadata */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div>
              <span className="font-medium">Created:</span> {new Date(testCase.created_at).toLocaleString()}
            </div>
            {testCase.updated_at && (
              <div>
                <span className="font-medium">Updated:</span> {new Date(testCase.updated_at).toLocaleString()}
              </div>
            )}
            {testCase.execution_duration && (
              <div>
                <span className="font-medium">Duration:</span> {testCase.execution_duration}s
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
