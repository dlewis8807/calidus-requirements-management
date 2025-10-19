'use client';

import { useEffect, useState } from 'react';

interface TestCase {
  id: number;
  test_case_id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
}

interface TraceabilityLink {
  id: number;
  source_requirement_id: string | null;
  target_requirement_id: string | null;
  source_title: string | null;
  target_title: string | null;
  link_type: string;
  description: string | null;
}

interface RequirementDetails {
  id: number;
  requirement_id: string;
  type: string;
  category: string | null;
  title: string;
  description: string;
  priority: string;
  status: string;
  verification_method: string | null;
  regulatory_document: string | null;
  regulatory_section: string | null;
  regulatory_page: number | null;
  file_path: string | null;
  version: string;
  created_at: string;
  updated_at: string | null;
  test_cases: TestCase[];
  parent_traces: TraceabilityLink[];
  child_traces: TraceabilityLink[];
}

interface RequirementModalProps {
  requirementId: string;
  onClose: () => void;
  onRequirementClick?: (reqId: string) => void;
}

export default function RequirementModal({ requirementId, onClose, onRequirementClick }: RequirementModalProps) {
  const [requirement, setRequirement] = useState<RequirementDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRequirement = async () => {
      setLoading(true);
      setError(null);

      try {
        // Try multiple token locations (same as API client)
        const token = localStorage.getItem('access_token') ||
                     localStorage.getItem('token') ||
                     localStorage.getItem('demo_token');

        if (!token) {
          throw new Error('Authentication required. Please log in.');
        }

        const response = await fetch(`http://localhost:8000/api/requirements/by-req-id/${requirementId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('Authentication failed. Please log in again.');
          }
          if (response.status === 404) {
            throw new Error(`Requirement '${requirementId}' not found`);
          }
          throw new Error(`Failed to fetch requirement: ${response.statusText}`);
        }

        const data = await response.json();
        setRequirement(data);
      } catch (err) {
        console.error('Error fetching requirement:', err);
        setError(err instanceof Error ? err.message : 'Failed to load requirement');
      } finally {
        setLoading(false);
      }
    };

    fetchRequirement();
  }, [requirementId]);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved': return 'bg-green-100 text-green-700 border-green-200';
      case 'draft': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'under_review': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'deprecated': return 'bg-gray-100 text-gray-700 border-gray-200';
      case 'passed': return 'bg-green-100 text-green-700 border-green-200';
      case 'failed': return 'bg-red-100 text-red-700 border-red-200';
      case 'pending': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-700';
      case 'high': return 'bg-orange-100 text-orange-700';
      case 'medium': return 'bg-yellow-100 text-yellow-700';
      case 'low': return 'bg-blue-100 text-blue-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const handleRequirementClick = (reqId: string) => {
    if (onRequirementClick) {
      onRequirementClick(reqId);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">Requirement Details</h2>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-80px)] p-6">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <svg className="animate-spin h-10 w-10 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-sm text-red-700">{error}</span>
              </div>
            </div>
          )}

          {requirement && (
            <div className="space-y-6">
              {/* Basic Information */}
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <span className="px-3 py-1 bg-blue-600 text-white text-sm font-semibold rounded">
                    {requirement.requirement_id}
                  </span>
                  <span className={`px-3 py-1 text-sm font-semibold rounded ${getPriorityColor(requirement.priority)}`}>
                    {requirement.priority}
                  </span>
                  <span className={`px-3 py-1 text-sm font-semibold rounded border ${getStatusColor(requirement.status)}`}>
                    {requirement.status.replace('_', ' ')}
                  </span>
                  <span className="text-sm text-gray-500">v{requirement.version}</span>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{requirement.title}</h3>
                <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
                  <span className="px-2 py-1 bg-gray-100 rounded">{requirement.type.replace('_', ' ')}</span>
                  {requirement.category && (
                    <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded">{requirement.category}</span>
                  )}
                  {requirement.verification_method && (
                    <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded">Verified by: {requirement.verification_method}</span>
                  )}
                </div>
              </div>

              {/* Description */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Description</h4>
                <p className="text-gray-900">{requirement.description}</p>
              </div>

              {/* Regulatory Information */}
              {requirement.regulatory_document && (
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <h4 className="text-sm font-semibold text-blue-900 mb-2">Regulatory Source</h4>
                  <div className="space-y-1 text-sm">
                    <div><span className="font-medium text-gray-700">Document:</span> <span className="text-gray-900">{requirement.regulatory_document}</span></div>
                    {requirement.regulatory_section && (
                      <div><span className="font-medium text-gray-700">Section:</span> <span className="text-gray-900">{requirement.regulatory_section}</span></div>
                    )}
                    {requirement.regulatory_page && (
                      <div><span className="font-medium text-gray-700">Page:</span> <span className="text-gray-900">{requirement.regulatory_page}</span></div>
                    )}
                    {requirement.file_path && (
                      <div><span className="font-medium text-gray-700">Source File:</span> <span className="text-gray-600 text-xs break-all">{requirement.file_path}</span></div>
                    )}
                  </div>
                </div>
              )}

              {/* Test Cases */}
              {requirement.test_cases.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">Test Cases ({requirement.test_cases.length})</h4>
                  <div className="space-y-2">
                    {requirement.test_cases.map((tc) => (
                      <div key={tc.id} className="p-3 bg-green-50 rounded-lg border border-green-200">
                        <div className="flex items-start justify-between mb-1">
                          <div className="flex items-center space-x-2">
                            <span className="px-2 py-0.5 bg-green-600 text-white text-xs font-semibold rounded">
                              {tc.test_case_id}
                            </span>
                            <span className={`px-2 py-0.5 text-xs font-semibold rounded border ${getStatusColor(tc.status)}`}>
                              {tc.status}
                            </span>
                          </div>
                          <span className={`px-2 py-0.5 text-xs font-semibold rounded ${getPriorityColor(tc.priority)}`}>
                            {tc.priority}
                          </span>
                        </div>
                        <h5 className="text-sm font-semibold text-gray-900 mb-1">{tc.title}</h5>
                        <p className="text-xs text-gray-600">{tc.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Traceability Links */}
              {(requirement.parent_traces.length > 0 || requirement.child_traces.length > 0) && (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">Traceability</h4>

                  {requirement.parent_traces.length > 0 && (
                    <div className="mb-4">
                      <h5 className="text-sm font-semibold text-gray-700 mb-2">Parent Requirements ({requirement.parent_traces.length})</h5>
                      <div className="space-y-2">
                        {requirement.parent_traces.map((trace) => (
                          <div key={trace.id} className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                            <div className="flex items-center justify-between mb-1">
                              <button
                                onClick={() => trace.source_requirement_id && handleRequirementClick(trace.source_requirement_id)}
                                className="px-2 py-0.5 bg-purple-600 text-white text-xs font-semibold rounded hover:bg-purple-700 transition-colors"
                              >
                                {trace.source_requirement_id}
                              </button>
                              <span className="text-xs text-gray-500">{trace.link_type}</span>
                            </div>
                            <p className="text-sm text-gray-900">{trace.source_title}</p>
                            {trace.description && (
                              <p className="text-xs text-gray-600 mt-1">{trace.description}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {requirement.child_traces.length > 0 && (
                    <div>
                      <h5 className="text-sm font-semibold text-gray-700 mb-2">Child Requirements ({requirement.child_traces.length})</h5>
                      <div className="space-y-2">
                        {requirement.child_traces.map((trace) => (
                          <div key={trace.id} className="p-3 bg-indigo-50 rounded-lg border border-indigo-200">
                            <div className="flex items-center justify-between mb-1">
                              <button
                                onClick={() => trace.target_requirement_id && handleRequirementClick(trace.target_requirement_id)}
                                className="px-2 py-0.5 bg-indigo-600 text-white text-xs font-semibold rounded hover:bg-indigo-700 transition-colors"
                              >
                                {trace.target_requirement_id}
                              </button>
                              <span className="text-xs text-gray-500">{trace.link_type}</span>
                            </div>
                            <p className="text-sm text-gray-900">{trace.target_title}</p>
                            {trace.description && (
                              <p className="text-xs text-gray-600 mt-1">{trace.description}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Metadata */}
              <div className="pt-4 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Created:</span>
                    <span className="ml-2 text-gray-900">{new Date(requirement.created_at).toLocaleDateString()}</span>
                  </div>
                  {requirement.updated_at && (
                    <div>
                      <span className="text-gray-500">Updated:</span>
                      <span className="ml-2 text-gray-900">{new Date(requirement.updated_at).toLocaleDateString()}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
