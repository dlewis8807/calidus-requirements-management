'use client';

import { useState } from 'react';
import Link from 'next/link';
import RequirementModal from '@/components/RequirementModal';
import AskAhmedModal from '@/components/chat/AskAhmedModal';

// Types for our data
interface Requirement {
  id: number;
  requirement_id: string;
  type: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  category?: string;
}

interface RequirementsResponse {
  total: number;
  page: number;
  page_size: number;
  requirements: Requirement[];
}

interface StatsResponse {
  total_requirements: number;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  total_with_tests: number;
  coverage_percentage: number;
}

export default function Demo() {
  const [activeTab, setActiveTab] = useState<'upload' | 'analyze' | 'trace'>('upload');
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [importProgress, setImportProgress] = useState(0);

  // Modal state
  const [selectedRequirementId, setSelectedRequirementId] = useState<string | null>(null);
  const [isAhmedOpen, setIsAhmedOpen] = useState(false);

  // ENOVIA form state
  const [enoviaUrl, setEnoviaUrl] = useState('https://enovia.calidus.aero');
  const [workspace, setWorkspace] = useState('Aircraft_Development');
  const [projectId, setProjectId] = useState('CALIDUS-2024');

  const handleRequirementClick = (requirementId: string) => {
    setSelectedRequirementId(requirementId);
  };

  const handleCloseModal = () => {
    setSelectedRequirementId(null);
  };

  const handleEnoviaConnect = async () => {
    setIsConnecting(true);
    setConnectionError(null);
    setImportProgress(0);

    try {
      // Simulate connection delay
      await new Promise(resolve => setTimeout(resolve, 800));
      setImportProgress(10);

      // Get authentication token (simulating ENOVIA authentication)
      let token: string | null = localStorage.getItem('demo_token');

      if (!token) {
        // Login with demo admin credentials to get token
        const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: 'admin',
            password: 'demo2024'
          })
        });

        if (!loginResponse.ok) {
          throw new Error('Failed to authenticate with ENOVIA server');
        }

        const loginData = await loginResponse.json();
        token = loginData.access_token as string;
        if (token) {
          localStorage.setItem('demo_token', token);
        }
      }

      setImportProgress(20);

      // Fetch statistics from our backend (simulating ENOVIA connection)
      const statsResponse = await fetch('http://localhost:8000/api/requirements/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!statsResponse.ok) {
        throw new Error('Failed to connect to ENOVIA server');
      }

      const statsData: StatsResponse = await statsResponse.json();
      setStats(statsData);
      setImportProgress(50);

      // Simulate data transfer
      await new Promise(resolve => setTimeout(resolve, 1000));
      setImportProgress(75);

      // Fetch sample requirements
      const reqResponse = await fetch('http://localhost:8000/api/requirements?page=1&page_size=20', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!reqResponse.ok) {
        throw new Error('Failed to import requirements from ENOVIA');
      }

      const reqData: RequirementsResponse = await reqResponse.json();
      setRequirements(reqData.requirements);
      setImportProgress(100);

      // Mark as connected
      setIsConnected(true);
    } catch (error) {
      console.error('ENOVIA connection error:', error);
      setConnectionError(error instanceof Error ? error.message : 'Connection failed');
    } finally {
      setIsConnecting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved': return 'bg-green-100 text-green-700 border-green-200';
      case 'draft': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'under_review': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'deprecated': return 'bg-gray-100 text-gray-700 border-gray-200';
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-calidus-silver-light">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center">
              <img src="/images/CLS-AEROSPACE-LOGO.svg" alt="CALIDUS Aerospace" className="h-14" />
            </Link>
            <Link
              href="/login"
              className="px-4 py-2 text-white rounded-lg font-semibold transition-colors text-sm"
              style={{backgroundColor: '#3B7DDD'}}
            >
              Sign In
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('upload')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'upload'
                    ? 'border-calidus-blue'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                style={activeTab === 'upload' ? {color: '#3B7DDD'} : {}}
              >
                Import from ENOVIA
              </button>
              <button
                onClick={() => setActiveTab('analyze')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'analyze'
                    ? 'border-calidus-blue'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                style={activeTab === 'analyze' ? {color: '#3B7DDD'} : {}}
              >
                AI Analysis
              </button>
              <button
                onClick={() => setActiveTab('trace')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'trace'
                    ? 'border-calidus-blue'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                style={activeTab === 'trace' ? {color: '#3B7DDD'} : {}}
              >
                Traceability Matrix
              </button>
            </nav>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            {/* ENOVIA Import Section */}
            <div className="bg-white rounded-xl shadow-lg p-8 border border-blue-100">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Import from ENOVIA PLM</h2>
              <p className="text-gray-600 mb-6">
                Connect directly to ENOVIA PLM systems to import requirements, specifications, and traceability data
              </p>

              {/* ENOVIA Connection Form */}
              <div className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-300">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                      </svg>
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">ENOVIA 3DEXPERIENCE Connection</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Seamlessly import requirements from ENOVIA PLM with full traceability and metadata preservation
                    </p>

                    <div className="space-y-3">
                      <div className="flex items-center space-x-3">
                        <input
                          type="text"
                          value={enoviaUrl}
                          onChange={(e) => setEnoviaUrl(e.target.value)}
                          placeholder="ENOVIA Server URL (e.g., https://enovia.company.com)"
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                          disabled={isConnecting}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <input
                          type="text"
                          value={workspace}
                          onChange={(e) => setWorkspace(e.target.value)}
                          placeholder="Workspace"
                          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                          disabled={isConnecting}
                        />
                        <input
                          type="text"
                          value={projectId}
                          onChange={(e) => setProjectId(e.target.value)}
                          placeholder="Project ID"
                          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                          disabled={isConnecting}
                        />
                      </div>

                      {/* Progress Bar */}
                      {isConnecting && (
                        <div className="space-y-2">
                          <div className="w-full bg-gray-200 rounded-full h-2.5">
                            <div
                              className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
                              style={{ width: `${importProgress}%` }}
                            ></div>
                          </div>
                          <p className="text-sm text-gray-600 text-center">
                            {importProgress < 30 && "Connecting to ENOVIA server..."}
                            {importProgress >= 30 && importProgress < 60 && "Fetching requirement metadata..."}
                            {importProgress >= 60 && importProgress < 90 && "Importing requirements and traceability..."}
                            {importProgress >= 90 && "Finalizing import..."}
                          </p>
                        </div>
                      )}

                      {/* Error Message */}
                      {connectionError && (
                        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                          <div className="flex items-center space-x-2">
                            <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                            <span className="text-sm text-red-700">{connectionError}</span>
                          </div>
                        </div>
                      )}

                      {/* Success Message */}
                      {isConnected && stats && (
                        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                          <div className="flex items-center space-x-2 mb-2">
                            <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span className="text-sm font-semibold text-green-700">Successfully connected to ENOVIA!</span>
                          </div>
                          <p className="text-sm text-green-600">
                            Imported {stats.total_requirements.toLocaleString()} requirements with {stats.coverage_percentage}% test coverage
                          </p>
                        </div>
                      )}

                      {/* Connect Button */}
                      <button
                        onClick={handleEnoviaConnect}
                        disabled={isConnecting}
                        className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
                      >
                        {isConnecting ? (
                          <>
                            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span>Connecting...</span>
                          </>
                        ) : (
                          <>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                            </svg>
                            <span>{isConnected ? 'Reconnect to ENOVIA' : 'Connect & Import from ENOVIA'}</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Display Statistics */}
              {stats && (
                <div className="mt-8 space-y-6">
                  <h3 className="text-lg font-semibold text-gray-900">Import Summary</h3>

                  <div className="grid md:grid-cols-4 gap-4">
                    <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200">
                      <div className="text-2xl font-bold text-blue-600 mb-1">{stats.total_requirements.toLocaleString()}</div>
                      <div className="text-sm text-gray-600">Total Requirements</div>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200">
                      <div className="text-2xl font-bold text-green-600 mb-1">{stats.total_with_tests.toLocaleString()}</div>
                      <div className="text-sm text-gray-600">With Test Cases</div>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border border-purple-200">
                      <div className="text-2xl font-bold text-purple-600 mb-1">{stats.coverage_percentage}%</div>
                      <div className="text-sm text-gray-600">Test Coverage</div>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg border border-orange-200">
                      <div className="text-2xl font-bold text-orange-600 mb-1">{Object.keys(stats.by_type).length}</div>
                      <div className="text-sm text-gray-600">Requirement Types</div>
                    </div>
                  </div>

                  {/* Requirements by Type */}
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="p-4 bg-white rounded-lg border border-gray-200">
                      <h4 className="text-sm font-semibold text-gray-700 mb-3">By Type</h4>
                      <div className="space-y-2">
                        {Object.entries(stats.by_type).map(([type, count]) => (
                          <div key={type} className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">{type}</span>
                            <span className="text-sm font-semibold text-gray-900">{count.toLocaleString()}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="p-4 bg-white rounded-lg border border-gray-200">
                      <h4 className="text-sm font-semibold text-gray-700 mb-3">By Status</h4>
                      <div className="space-y-2">
                        {Object.entries(stats.by_status).map(([status, count]) => (
                          <div key={status} className="flex items-center justify-between">
                            <span className="text-sm text-gray-600 capitalize">{status.replace('_', ' ')}</span>
                            <span className="text-sm font-semibold text-gray-900">{count.toLocaleString()}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Display Sample Requirements */}
              {requirements.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Sample Requirements (Showing 20 of {stats?.total_requirements.toLocaleString()})</h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {requirements.map((req) => (
                      <div key={req.id} className="p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-colors">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleRequirementClick(req.requirement_id)}
                              className="px-2 py-1 bg-blue-600 text-white text-xs font-semibold rounded hover:bg-blue-700 transition-colors cursor-pointer"
                            >
                              {req.requirement_id}
                            </button>
                            <span className={`px-2 py-1 text-xs font-semibold rounded ${getPriorityColor(req.priority)}`}>
                              {req.priority}
                            </span>
                            <span className={`px-2 py-1 text-xs font-semibold rounded border ${getStatusColor(req.status)}`}>
                              {req.status.replace('_', ' ')}
                            </span>
                          </div>
                          <span className="text-xs text-gray-500">{req.type}</span>
                        </div>
                        <h4 className="text-sm font-semibold text-gray-900 mb-1">{req.title}</h4>
                        <p className="text-xs text-gray-600 line-clamp-2">{req.description}</p>
                        {req.category && (
                          <div className="mt-2">
                            <span className="text-xs text-gray-500">Category: </span>
                            <span className="text-xs font-medium text-blue-600">{req.category}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analyze' && (
          <div className="bg-white rounded-xl shadow-lg p-8 border border-blue-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">AI-Powered Requirement Analysis</h2>
            <p className="text-gray-600 mb-6">
              Automatic classification, compliance checking, and gap analysis
            </p>

            <div className="space-y-4">
              <div className="p-6 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <button
                        onClick={() => handleRequirementClick('AHLR-001')}
                        className="px-2 py-1 bg-blue-600 text-white text-xs font-semibold rounded hover:bg-blue-700 transition-colors cursor-pointer"
                      >
                        AHLR-001
                      </button>
                      <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded">DO-178C</span>
                    </div>
                    <p className="text-gray-900 font-medium mb-2">
                      The system shall provide redundant flight control systems with automatic failover capability
                    </p>
                    <div className="flex items-center space-x-4 text-sm">
                      <span className="text-gray-600">Level: <strong>A (Critical)</strong></span>
                      <span className="text-gray-600">Status: <strong className="text-green-600">Compliant</strong></span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                      <span className="text-2xl font-bold text-green-600">98%</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-6 bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-lg border border-yellow-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <button
                        onClick={() => handleRequirementClick('SYS-042')}
                        className="px-2 py-1 bg-yellow-600 text-white text-xs font-semibold rounded hover:bg-yellow-700 transition-colors cursor-pointer"
                      >
                        SYS-042
                      </button>
                      <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs font-semibold rounded">UAE GCAA</span>
                    </div>
                    <p className="text-gray-900 font-medium mb-2">
                      Aircraft navigation systems must maintain accuracy within specified tolerances
                    </p>
                    <div className="flex items-center space-x-4 text-sm">
                      <span className="text-gray-600">Level: <strong>B (Major)</strong></span>
                      <span className="text-gray-600">Status: <strong className="text-yellow-600">Needs Review</strong></span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center">
                      <span className="text-2xl font-bold text-yellow-600">76%</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-6 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg border border-purple-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <button
                        onClick={() => handleRequirementClick('CERT-118')}
                        className="px-2 py-1 bg-purple-600 text-white text-xs font-semibold rounded hover:bg-purple-700 transition-colors cursor-pointer"
                      >
                        CERT-118
                      </button>
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded">FAA</span>
                    </div>
                    <p className="text-gray-900 font-medium mb-2">
                      All safety-critical software shall undergo independent verification and validation
                    </p>
                    <div className="flex items-center space-x-4 text-sm">
                      <span className="text-gray-600">Level: <strong>A (Critical)</strong></span>
                      <span className="text-gray-600">Status: <strong className="text-green-600">Verified</strong></span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
                      <span className="text-2xl font-bold text-purple-600">100%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Ask Ahmed AI Assistant Section */}
            <div className="mt-8 p-8 bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 rounded-xl border-2 border-indigo-200 shadow-lg">
              <div className="flex items-start space-x-6">
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    Need Predictive Analysis?
                  </h3>
                  <p className="text-gray-700 mb-4 leading-relaxed">
                    Ask Ahmed, our AI-powered requirements assistant, can help you perform deep predictive analysis on any requirement.
                    Get instant insights on compliance risk, test coverage gaps, regulatory conflicts, and impact analysis.
                  </p>
                  <div className="space-y-2 mb-6">
                    <div className="flex items-start space-x-2">
                      <svg className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm text-gray-700">Predict compliance risks before they become issues</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <svg className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm text-gray-700">Identify test coverage gaps and suggest test cases</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <svg className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm text-gray-700">Analyze impact of requirement changes across the system</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <svg className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm text-gray-700">Get regulatory guidance for FAA, EASA, and UAE GCAA standards</span>
                    </div>
                  </div>
                  <button
                    onClick={() => setIsAhmedOpen(true)}
                    className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl space-x-3"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                    <span>Ask Ahmed for Predictive Analysis</span>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </button>
                  <p className="text-xs text-gray-500 mt-3">
                    Try asking: &quot;What are the highest risk requirements?&quot; or &quot;Which requirements have incomplete test coverage?&quot;
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trace' && (
          <div className="bg-white rounded-xl shadow-lg p-8 border border-blue-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Traceability Matrix</h2>
            <p className="text-gray-600 mb-6">
              Automated bidirectional traceability across all requirement levels
            </p>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      High-Level Req
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      System Req
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Test Case
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  <tr className="hover:bg-blue-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleRequirementClick('AHLR-001')}
                        className="text-blue-600 hover:text-blue-800 hover:underline font-semibold cursor-pointer"
                      >
                        AHLR-001
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleRequirementClick('SYS-042')}
                        className="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
                      >
                        SYS-042
                      </button>
                      {', '}
                      <button
                        onClick={() => handleRequirementClick('SYS-043')}
                        className="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
                      >
                        SYS-043
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">TC-101, TC-102</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        Complete
                      </span>
                    </td>
                  </tr>
                  <tr className="hover:bg-blue-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleRequirementClick('AHLR-002')}
                        className="text-blue-600 hover:text-blue-800 hover:underline font-semibold cursor-pointer"
                      >
                        AHLR-002
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleRequirementClick('SYS-044')}
                        className="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
                      >
                        SYS-044
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">TC-103</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                        In Progress
                      </span>
                    </td>
                  </tr>
                  <tr className="hover:bg-blue-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleRequirementClick('AHLR-003')}
                        className="text-blue-600 hover:text-blue-800 hover:underline font-semibold cursor-pointer"
                      >
                        AHLR-003
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleRequirementClick('SYS-045')}
                        className="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
                      >
                        SYS-045
                      </button>
                      {', '}
                      <button
                        onClick={() => handleRequirementClick('SYS-046')}
                        className="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
                      >
                        SYS-046
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">-</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                        Gap Detected
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="mt-6 grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="text-2xl font-bold text-green-600 mb-1">847</div>
                <div className="text-sm text-gray-600">Complete Traces</div>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="text-2xl font-bold text-yellow-600 mb-1">23</div>
                <div className="text-sm text-gray-600">In Progress</div>
              </div>
              <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                <div className="text-2xl font-bold text-red-600 mb-1">12</div>
                <div className="text-sm text-gray-600">Gaps Detected</div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Requirement Modal */}
      {selectedRequirementId && (
        <RequirementModal
          requirementId={selectedRequirementId}
          onClose={handleCloseModal}
          onRequirementClick={handleRequirementClick}
        />
      )}

      {/* Ask Ahmed Modal */}
      <AskAhmedModal
        isOpen={isAhmedOpen}
        onClose={() => setIsAhmedOpen(false)}
      />
    </div>
  );
}
