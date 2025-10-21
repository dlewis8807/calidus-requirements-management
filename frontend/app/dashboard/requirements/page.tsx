'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import FilterPanel from '@/components/requirements/FilterPanel';
import Pagination from '@/components/common/Pagination';
import Badge from '@/components/common/Badge';
import RequirementModal from '@/components/RequirementModal';
import { requirementsAPI } from '@/lib/api';
import type { Requirement, RequirementFilter, RequirementsListResponse } from '@/lib/types';
import {
  FunnelIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';

export default function RequirementsPage() {
  const [data, setData] = useState<RequirementsListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterPanelOpen, setFilterPanelOpen] = useState(false);
  const [selectedRequirementId, setSelectedRequirementId] = useState<string | null>(null);
  const [filters, setFilters] = useState<RequirementFilter>({
    page: 1,
    page_size: 50,
    sort_by: 'created_at',
    sort_order: 'desc',
  });

  useEffect(() => {
    fetchRequirements();
  }, [filters]);

  const fetchRequirements = async () => {
    try {
      setLoading(true);
      const response = await requirementsAPI.list(filters as any);
      setData(response as RequirementsListResponse);
    } catch (error) {
      console.error('Error fetching requirements:', error);
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

  const getTypeBadge = (type: string) => {
    const colors: Record<string, string> = {
      AHLR: 'bg-blue-100 text-blue-700 border-blue-200',
      SYSTEM: 'bg-green-100 text-green-700 border-green-200',
      TECHNICAL: 'bg-purple-100 text-purple-700 border-purple-200',
      CERTIFICATION: 'bg-orange-100 text-orange-700 border-orange-200',
      // Legacy support
      Aircraft_High_Level_Requirement: 'bg-blue-100 text-blue-700 border-blue-200',
      System_Requirement: 'bg-green-100 text-green-700 border-green-200',
      Technical_Specification: 'bg-purple-100 text-purple-700 border-purple-200',
      Certification_Requirement: 'bg-orange-100 text-orange-700 border-orange-200',
    };
    return colors[type] || 'bg-gray-100 text-gray-700 border-gray-200';
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      AHLR: 'AHLR',
      SYSTEM: 'System',
      TECHNICAL: 'Technical',
      CERTIFICATION: 'Certification',
      // Legacy support
      Aircraft_High_Level_Requirement: 'AHLR',
      System_Requirement: 'System',
      Technical_Specification: 'Technical',
      Certification_Requirement: 'Certification',
    };
    return labels[type] || type;
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      DRAFT: 'Draft',
      APPROVED: 'Approved',
      UNDER_REVIEW: 'Under Review',
      DEPRECATED: 'Deprecated',
      // Legacy support
      draft: 'Draft',
      approved: 'Approved',
      under_review: 'Under Review',
      deprecated: 'Deprecated',
    };
    return labels[status] || status.replace('_', ' ');
  };

  const activeFilterCount = Object.keys(filters).filter(
    key => !['page', 'page_size', 'sort_by', 'sort_order'].includes(key) && filters[key as keyof RequirementFilter]
  ).length;

  return (
    <DashboardLayout title="Requirements">
      <div className="space-y-4">
        {/* Header Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Requirements</h2>
            <p className="mt-1 text-sm text-gray-600">
              Manage and track all project requirements
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setFilterPanelOpen(true)}
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
              href="/dashboard/requirements/new"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white shadow-sm hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2"
              style={{ backgroundColor: '#3B7DDD' }}
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              New Requirement
            </Link>
          </div>
        </div>

        {/* Active Filters */}
        {activeFilterCount > 0 && (
          <div className="flex items-center space-x-2 flex-wrap">
            <span className="text-sm text-gray-600">Active filters:</span>
            {filters.type && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-md text-sm bg-blue-100 text-blue-700">
                Type: {getTypeLabel(filters.type)}
                <button
                  onClick={() => setFilters({ ...filters, type: undefined })}
                  className="ml-1.5 text-blue-500 hover:text-blue-700"
                >
                  ×
                </button>
              </span>
            )}
            {filters.status && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-md text-sm bg-blue-100 text-blue-700">
                Status: {getStatusLabel(filters.status)}
                <button
                  onClick={() => setFilters({ ...filters, status: undefined })}
                  className="ml-1.5 text-blue-500 hover:text-blue-700"
                >
                  ×
                </button>
              </span>
            )}
            {filters.priority && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-md text-sm bg-blue-100 text-blue-700">
                Priority: {filters.priority}
                <button
                  onClick={() => setFilters({ ...filters, priority: undefined })}
                  className="ml-1.5 text-blue-500 hover:text-blue-700"
                >
                  ×
                </button>
              </span>
            )}
            {filters.category && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-md text-sm bg-blue-100 text-blue-700">
                Category: {filters.category}
                <button
                  onClick={() => setFilters({ ...filters, category: undefined })}
                  className="ml-1.5 text-blue-500 hover:text-blue-700"
                >
                  ×
                </button>
              </span>
            )}
            {filters.search && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-md text-sm bg-blue-100 text-blue-700">
                Search: &quot;{filters.search}&quot;
                <button
                  onClick={() => setFilters({ ...filters, search: undefined })}
                  className="ml-1.5 text-blue-500 hover:text-blue-700"
                >
                  ×
                </button>
              </span>
            )}
          </div>
        )}

        {/* Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : data && data.requirements.length > 0 ? (
            <>
              <div className="overflow-x-auto max-w-full">
                <table className="w-full divide-y divide-gray-200 table-fixed">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="w-32 px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Requirement ID
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Title
                      </th>
                      <th className="w-28 px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="w-28 px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="w-24 px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Priority
                      </th>
                      <th className="w-20 px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tests
                      </th>
                      <th className="w-28 px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {data.requirements.map((req) => (
                      <tr key={req.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 whitespace-nowrap">
                          <button
                            onClick={() => setSelectedRequirementId(req.requirement_id)}
                            className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
                          >
                            {req.requirement_id}
                          </button>
                        </td>
                        <td className="px-4 py-3">
                          <div className="text-sm text-gray-900 truncate" title={req.title}>
                            {req.title}
                          </div>
                          {req.category && (
                            <div className="text-xs text-gray-500 mt-1 truncate" title={req.category}>
                              {req.category}
                            </div>
                          )}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded border ${getTypeBadge(req.type)}`}>
                            {getTypeLabel(req.type)}
                          </span>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <Badge variant={getStatusBadge(req.status)}>
                            {getStatusLabel(req.status)}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <Badge variant={getPriorityBadge(req.priority)}>
                            {req.priority}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                          {req.test_case_count || 0}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end space-x-1">
                            <Link
                              href={`/dashboard/requirements/${req.id}`}
                              className="text-blue-600 hover:text-blue-900 p-1"
                              title="View"
                            >
                              <EyeIcon className="h-4 w-4" />
                            </Link>
                            <button
                              className="text-gray-600 hover:text-gray-900 p-1"
                              title="Edit"
                            >
                              <PencilIcon className="h-4 w-4" />
                            </button>
                            <button
                              className="text-red-600 hover:text-red-900 p-1"
                              title="Delete"
                            >
                              <TrashIcon className="h-4 w-4" />
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
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No requirements found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {activeFilterCount > 0
                  ? 'Try adjusting your filters'
                  : 'Get started by creating a new requirement'}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Filter Panel */}
      <FilterPanel
        isOpen={filterPanelOpen}
        onClose={() => setFilterPanelOpen(false)}
        filters={filters}
        onFiltersChange={setFilters}
      />

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
