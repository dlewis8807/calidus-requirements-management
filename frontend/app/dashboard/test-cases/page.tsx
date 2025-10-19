'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import Badge from '@/components/common/Badge';
import Pagination from '@/components/common/Pagination';
import RequirementModal from '@/components/RequirementModal';
import { testCasesAPI } from '@/lib/api';
import type { TestCase, TestCaseFilter, TestCasesListResponse } from '@/lib/types';
import {
  FunnelIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  PlayIcon,
} from '@heroicons/react/24/outline';

export default function TestCasesPage() {
  const [data, setData] = useState<TestCasesListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<TestCaseFilter>({
    page: 1,
    page_size: 50,
    sort_by: 'created_at',
    sort_order: 'desc',
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedRequirementId, setSelectedRequirementId] = useState<string | null>(null);

  useEffect(() => {
    fetchTestCases();
  }, [filters]);

  const fetchTestCases = async () => {
    try {
      setLoading(true);
      const response = await testCasesAPI.list(filters as any);
      setData(response as TestCasesListResponse);
    } catch (error) {
      console.error('Error fetching test cases:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (page: number) => {
    setFilters({ ...filters, page });
  };

  const handlePageSizeChange = (pageSize: number) => {
    setFilters({ ...filters, page_size: pageSize, page: 1 });
  };

  const getStatusBadge = (status: string) => {
    // Always return "status" variant for status badges
    return 'status' as const;
  };

  const getPriorityBadge = (priority: string) => {
    // Always return "priority" variant for priority badges
    return 'priority' as const;
  };

  const activeFilterCount = Object.keys(filters).filter(
    key => !['page', 'page_size', 'sort_by', 'sort_order'].includes(key) && filters[key as keyof TestCaseFilter]
  ).length;

  return (
    <DashboardLayout title="Test Cases">
      <div className="space-y-4">
        {/* Header Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Test Cases</h2>
            <p className="mt-1 text-sm text-gray-600">
              Manage and execute test cases
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <FunnelIcon className="h-5 w-5 mr-2 text-gray-400" />
              Filters
              {activeFilterCount > 0 && (
                <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full">
                  {activeFilterCount}
                </span>
              )}
            </button>
            <Link
              href="/dashboard/test-cases/new"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white shadow-sm hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2"
              style={{ backgroundColor: '#3B7DDD' }}
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              New Test Case
            </Link>
          </div>
        </div>

        {/* Filter Bar (Inline) */}
        {showFilters && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value as any, page: 1 })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  <option value="">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="passed">Passed</option>
                  <option value="failed">Failed</option>
                  <option value="blocked">Blocked</option>
                  <option value="in_progress">In Progress</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Priority
                </label>
                <select
                  value={filters.priority || ''}
                  onChange={(e) => setFilters({ ...filters, priority: e.target.value as any, page: 1 })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  <option value="">All Priorities</option>
                  <option value="Critical">Critical</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Automation
                </label>
                <select
                  value={filters.automated !== undefined ? filters.automated.toString() : ''}
                  onChange={(e) => setFilters({
                    ...filters,
                    automated: e.target.value === '' ? undefined : e.target.value === 'true',
                    page: 1
                  })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  <option value="">All Tests</option>
                  <option value="true">Automated</option>
                  <option value="false">Manual</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Search
                </label>
                <input
                  type="text"
                  value={filters.search || ''}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
                  placeholder="Search test cases..."
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                />
              </div>
            </div>

            {activeFilterCount > 0 && (
              <div className="mt-3 flex items-center justify-between">
                <span className="text-sm text-gray-600">
                  {activeFilterCount} filter{activeFilterCount > 1 ? 's' : ''} active
                </span>
                <button
                  onClick={() => setFilters({
                    page: 1,
                    page_size: 50,
                    sort_by: 'created_at',
                    sort_order: 'desc',
                  })}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Clear all filters
                </button>
              </div>
            )}
          </div>
        )}

        {/* Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : data && data.test_cases.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Test ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Title
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Priority
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Requirement
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {data.test_cases.map((testCase) => (
                      <tr key={testCase.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Link
                            href={`/dashboard/test-cases/${testCase.id}`}
                            className="text-sm font-medium text-blue-600 hover:text-blue-800"
                          >
                            {testCase.test_case_id}
                          </Link>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900 max-w-md truncate">
                            {testCase.title}
                          </div>
                          {testCase.automated && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 mt-1">
                              Automated
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge variant={getStatusBadge(testCase.status)}>
                            {testCase.status}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge variant={getPriorityBadge(testCase.priority)}>
                            {testCase.priority}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {testCase.test_type}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {testCase.requirement_id_str ? (
                            <button
                              onClick={() => setSelectedRequirementId(testCase.requirement_id_str || null)}
                              className="text-sm text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
                            >
                              {testCase.requirement_id_str}
                            </button>
                          ) : (
                            <span className="text-sm text-gray-400">No requirement</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end space-x-2">
                            <button
                              className="text-green-600 hover:text-green-900"
                              title="Execute Test"
                            >
                              <PlayIcon className="h-5 w-5" />
                            </button>
                            <Link
                              href={`/dashboard/test-cases/${testCase.id}`}
                              className="text-blue-600 hover:text-blue-900"
                              title="View"
                            >
                              <EyeIcon className="h-5 w-5" />
                            </Link>
                            <button
                              className="text-gray-600 hover:text-gray-900"
                              title="Edit"
                            >
                              <PencilIcon className="h-5 w-5" />
                            </button>
                            <button
                              className="text-red-600 hover:text-red-900"
                              title="Delete"
                            >
                              <TrashIcon className="h-5 w-5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <Pagination
                currentPage={data.page}
                totalPages={Math.ceil(data.total / data.page_size)}
                pageSize={data.page_size}
                totalItems={data.total}
                onPageChange={handlePageChange}
                onPageSizeChange={handlePageSizeChange}
              />
            </>
          ) : (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No test cases found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {activeFilterCount > 0
                  ? 'Try adjusting your filters'
                  : 'Get started by creating a new test case'}
              </p>
            </div>
          )}
        </div>
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
