'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function Demo() {
  const [activeTab, setActiveTab] = useState<'upload' | 'analyze' | 'trace'>('upload');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-blue-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">C</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">CALIDUS Demo</h1>
                <p className="text-xs text-gray-500">Interactive Feature Preview</p>
              </div>
            </Link>
            <Link
              href="/login"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors text-sm"
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
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Import from ENOVIA
              </button>
              <button
                onClick={() => setActiveTab('analyze')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'analyze'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                AI Analysis
              </button>
              <button
                onClick={() => setActiveTab('trace')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'trace'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Traceability Matrix
              </button>
            </nav>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'upload' && (
          <div className="bg-white rounded-xl shadow-lg p-8 border border-blue-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Import from ENOVIA PLM</h2>
            <p className="text-gray-600 mb-6">
              Connect directly to ENOVIA PLM systems to import requirements, specifications, and traceability data
            </p>

            {/* ENOVIA Import Section - Primary */}
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
                        placeholder="ENOVIA Server URL (e.g., https://enovia.company.com)"
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <input
                        type="text"
                        placeholder="Workspace"
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                      />
                      <input
                        type="text"
                        placeholder="Project ID"
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                      />
                    </div>
                    <button className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      <span>Connect & Import from ENOVIA</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Document Upload Section - Secondary */}
            <div className="mb-6">
              <div className="flex items-center mb-4">
                <div className="flex-1 border-t border-gray-300"></div>
                <span className="px-4 text-sm text-gray-500 font-medium">OR</span>
                <div className="flex-1 border-t border-gray-300"></div>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-3">Upload Documents</h3>
              <p className="text-sm text-gray-600 mb-4">
                Alternatively, upload requirements documents directly for processing
              </p>

              <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-400 transition-colors cursor-pointer bg-gray-50">
                <svg className="mx-auto h-10 w-10 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <p className="mt-3 text-sm font-medium text-gray-700">
                  Drop files here or click to browse
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  Supported: DOCX, XLSX, PDF, CSV, JSON, XML (Max 50MB)
                </p>
              </div>
            </div>

            {/* Statistics */}
            <div className="mt-8 grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200">
                <div className="text-2xl font-bold text-blue-600 mb-1">15K+</div>
                <div className="text-sm text-gray-600">ENOVIA Objects Imported</div>
              </div>
              <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200">
                <div className="text-2xl font-bold text-green-600 mb-1">99.8%</div>
                <div className="text-sm text-gray-600">Traceability Preserved</div>
              </div>
              <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border border-purple-200">
                <div className="text-2xl font-bold text-purple-600 mb-1">&lt;3s</div>
                <div className="text-sm text-gray-600">Average Sync Time</div>
              </div>
            </div>

            {/* ENOVIA Features */}
            <div className="mt-6 grid md:grid-cols-2 gap-4">
              <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-sm font-semibold text-gray-900">Full Metadata Import</p>
                  <p className="text-xs text-gray-600">Preserves all ENOVIA attributes and relationships</p>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                <svg className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-sm font-semibold text-gray-900">Bi-directional Sync</p>
                  <p className="text-xs text-gray-600">Changes sync back to ENOVIA automatically</p>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-purple-50 rounded-lg">
                <svg className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-sm font-semibold text-gray-900">Version Control</p>
                  <p className="text-xs text-gray-600">Track requirement changes and revisions</p>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-orange-50 rounded-lg">
                <svg className="w-5 h-5 text-orange-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-sm font-semibold text-gray-900">Bulk Operations</p>
                  <p className="text-xs text-gray-600">Import thousands of requirements in seconds</p>
                </div>
              </div>
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
                      <span className="px-2 py-1 bg-blue-600 text-white text-xs font-semibold rounded">AHLR-001</span>
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
                      <span className="px-2 py-1 bg-yellow-600 text-white text-xs font-semibold rounded">SYS-042</span>
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
                      <span className="px-2 py-1 bg-purple-600 text-white text-xs font-semibold rounded">CERT-118</span>
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">AHLR-001</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">SYS-042, SYS-043</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">TC-101, TC-102</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        Complete
                      </span>
                    </td>
                  </tr>
                  <tr className="hover:bg-blue-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">AHLR-002</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">SYS-044</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">TC-103</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                        In Progress
                      </span>
                    </td>
                  </tr>
                  <tr className="hover:bg-blue-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">AHLR-003</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">SYS-045, SYS-046</td>
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
    </div>
  );
}
