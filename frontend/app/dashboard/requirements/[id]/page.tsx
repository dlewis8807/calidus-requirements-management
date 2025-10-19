'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import Badge from '@/components/common/Badge';
import RequirementModal from '@/components/RequirementModal';
import { requirementsAPI, traceabilityAPI } from '@/lib/api';
import type { Requirement, TestCase } from '@/lib/types';

interface TraceabilityMatrix {
  parent_requirements: Requirement[];
  child_requirements: Requirement[];
  test_cases: TestCase[];
}
import {
  ArrowLeftIcon,
  PencilIcon,
  TrashIcon,
  DocumentTextIcon,
  BeakerIcon,
  ArrowsRightLeftIcon,
} from '@heroicons/react/24/outline';

export default function RequirementDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [requirement, setRequirement] = useState<Requirement | null>(null);
  const [traceMatrix, setTraceMatrix] = useState<TraceabilityMatrix | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRequirementId, setSelectedRequirementId] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchRequirement();
    }
  }, [id]);

  const fetchRequirement = async () => {
    try {
      setLoading(true);
      setError(null);
      const [reqData, traceData] = await Promise.all([
        requirementsAPI.get(parseInt(id)),
        traceabilityAPI.matrix(parseInt(id)),
      ]);
      setRequirement(reqData as any);
      setTraceMatrix(traceData as any);
    } catch (err) {
      console.error('Error fetching requirement:', err);
      setError(err instanceof Error ? err.message : 'Failed to load requirement');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = () => {
    return 'status' as const;
  };

  const getPriorityBadge = () => {
    return 'priority' as const;
  };

  const getTypeBadge = (type: string) => {
    const colors: Record<string, string> = {
      Aircraft_High_Level_Requirement: 'bg-blue-100 text-blue-700 border-blue-200',
      System_Requirement: 'bg-green-100 text-green-700 border-green-200',
      Technical_Specification: 'bg-purple-100 text-purple-700 border-purple-200',
      Certification_Requirement: 'bg-orange-100 text-orange-700 border-orange-200',
    };
    return colors[type] || 'bg-gray-100 text-gray-700 border-gray-200';
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      Aircraft_High_Level_Requirement: 'AHLR',
      System_Requirement: 'System Requirement',
      Technical_Specification: 'Technical Specification',
      Certification_Requirement: 'Certification Requirement',
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <DashboardLayout title="Loading...">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !requirement) {
    return (
      <DashboardLayout title="Error">
        <div className="text-center py-12">
          <p className="text-red-600">{error || 'Requirement not found'}</p>
          <Link
            href="/dashboard/requirements"
            className="mt-4 inline-flex items-center text-blue-600 hover:text-blue-800"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Back to Requirements
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title={requirement.requirement_id}>
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-3">
                <Link
                  href="/dashboard/requirements"
                  className="text-gray-400 hover:text-gray-600"
                >
                  <ArrowLeftIcon className="h-5 w-5" />
                </Link>
                <h1 className="text-2xl font-bold text-gray-900">
                  {requirement.requirement_id}
                </h1>
                <Badge variant="status">
                  {requirement.status.replace('_', ' ')}
                </Badge>
                <Badge variant="priority">
                  {requirement.priority}
                </Badge>
              </div>
              <h2 className="text-lg text-gray-700 mb-2">{requirement.title}</h2>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded border ${getTypeBadge(requirement.type)}`}>
                  {getTypeLabel(requirement.type)}
                </span>
                {requirement.category && (
                  <span>Category: {requirement.category}</span>
                )}
                <span>Version: {requirement.version}</span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <PencilIcon className="h-5 w-5 mr-2" />
                Edit
              </button>
              <button
                className="inline-flex items-center px-4 py-2 border border-red-300 rounded-lg text-sm font-medium text-red-700 bg-white hover:bg-red-50"
              >
                <TrashIcon className="h-5 w-5 mr-2" />
                Delete
              </button>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Description */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <DocumentTextIcon className="h-5 w-5 mr-2 text-gray-400" />
                Description
              </h3>
              <div className="text-gray-700 whitespace-pre-wrap">
                {requirement.description}
              </div>
            </div>

            {/* Regulatory Information */}
            {requirement.regulatory_document && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Regulatory Linkage
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      Document
                    </label>
                    <p className="text-gray-900">{requirement.regulatory_document}</p>
                  </div>
                  {requirement.regulatory_section && (
                    <div>
                      <label className="block text-sm font-medium text-gray-500 mb-1">
                        Section
                      </label>
                      <p className="text-gray-900">{requirement.regulatory_section}</p>
                    </div>
                  )}
                  {requirement.regulatory_page && (
                    <div>
                      <label className="block text-sm font-medium text-gray-500 mb-1">
                        Page
                      </label>
                      <p className="text-gray-900">{requirement.regulatory_page}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Traceability */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <ArrowsRightLeftIcon className="h-5 w-5 mr-2 text-gray-400" />
                Traceability
              </h3>

              {/* Parent Requirements */}
              {traceMatrix && traceMatrix.parent_requirements.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">
                    Parent Requirements ({traceMatrix.parent_requirements.length})
                  </h4>
                  <div className="space-y-2">
                    {traceMatrix.parent_requirements.map((parent) => (
                      <button
                        key={parent.id}
                        onClick={() => setSelectedRequirementId(parent.requirement_id)}
                        className="w-full block p-3 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-300 transition-colors cursor-pointer text-left"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-blue-600">
                              {parent.requirement_id}
                            </p>
                            <p className="text-sm text-gray-600 mt-1">
                              {parent.title}
                            </p>
                          </div>
                          <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded border ${getTypeBadge(parent.type)}`}>
                            {getTypeLabel(parent.type)}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Child Requirements */}
              {traceMatrix && traceMatrix.child_requirements.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-3">
                    Child Requirements ({traceMatrix.child_requirements.length})
                  </h4>
                  <div className="space-y-2">
                    {traceMatrix.child_requirements.map((child) => (
                      <button
                        key={child.id}
                        onClick={() => setSelectedRequirementId(child.requirement_id)}
                        className="w-full block p-3 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-300 transition-colors cursor-pointer text-left"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-blue-600">
                              {child.requirement_id}
                            </p>
                            <p className="text-sm text-gray-600 mt-1">
                              {child.title}
                            </p>
                          </div>
                          <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded border ${getTypeBadge(child.type)}`}>
                            {getTypeLabel(child.type)}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* No Traceability */}
              {traceMatrix &&
               traceMatrix.parent_requirements.length === 0 &&
               traceMatrix.child_requirements.length === 0 && (
                <p className="text-sm text-gray-500 text-center py-4">
                  No traceability links found
                </p>
              )}
            </div>

            {/* Test Cases */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <BeakerIcon className="h-5 w-5 mr-2 text-gray-400" />
                  Test Cases ({traceMatrix?.test_cases.length || 0})
                </h3>
                <button
                  className="inline-flex items-center px-3 py-1.5 border border-transparent rounded-md text-sm font-medium text-white shadow-sm hover:opacity-90"
                  style={{ backgroundColor: '#3B7DDD' }}
                >
                  Add Test Case
                </button>
              </div>

              {traceMatrix && traceMatrix.test_cases.length > 0 ? (
                <div className="space-y-2">
                  {traceMatrix.test_cases.map((testCase: any) => (
                    <Link
                      key={testCase.id}
                      href={`/dashboard/test-cases/${testCase.id}`}
                      className="block p-3 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-300 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-blue-600">
                            {testCase.test_case_id}
                          </p>
                          <p className="text-sm text-gray-600 mt-1">
                            {testCase.title}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="status">
                            {testCase.status}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {testCase.is_automated ? 'Automated' : 'Manual'}
                          </span>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 text-center py-4">
                  No test cases linked to this requirement
                </p>
              )}
            </div>
          </div>

          {/* Right Column - Metadata */}
          <div className="space-y-6">
            {/* Details Card */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Details</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">
                    Priority
                  </label>
                  <Badge variant="priority">
                    {requirement.priority}
                  </Badge>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">
                    Status
                  </label>
                  <Badge variant="status">
                    {requirement.status.replace('_', ' ')}
                  </Badge>
                </div>

                {requirement.verification_method && (
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      Verification Method
                    </label>
                    <p className="text-sm text-gray-900">
                      {requirement.verification_method}
                    </p>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">
                    Version
                  </label>
                  <p className="text-sm text-gray-900">{requirement.version}</p>
                </div>

                {requirement.file_path && (
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      Source File
                    </label>
                    <p className="text-sm text-gray-900 font-mono break-all">
                      {requirement.file_path}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Statistics Card */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistics</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Test Cases</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {traceMatrix?.test_cases.length || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Parent Links</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {traceMatrix?.parent_requirements.length || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Child Links</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {traceMatrix?.child_requirements.length || 0}
                  </span>
                </div>
              </div>
            </div>

            {/* Metadata Card */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Metadata</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <label className="block text-gray-500 mb-1">Created</label>
                  <p className="text-gray-900">
                    {new Date(requirement.created_at).toLocaleString()}
                  </p>
                </div>
                {requirement.updated_at && (
                  <div>
                    <label className="block text-gray-500 mb-1">Updated</label>
                    <p className="text-gray-900">
                      {new Date(requirement.updated_at).toLocaleString()}
                    </p>
                  </div>
                )}
                {requirement.revision_notes && (
                  <div>
                    <label className="block text-gray-500 mb-1">Revision Notes</label>
                    <p className="text-gray-900">{requirement.revision_notes}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
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
