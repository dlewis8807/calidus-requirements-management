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
                Document Upload
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
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Document Upload & Processing</h2>
            <p className="text-gray-600 mb-6">
              Upload aerospace requirements documents in various formats for AI-powered analysis
            </p>

            <div className="border-2 border-dashed border-blue-300 rounded-xl p-12 text-center hover:border-blue-500 transition-colors cursor-pointer bg-blue-50">
              <svg className="mx-auto h-12 w-12 text-blue-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <p className="mt-4 text-sm font-medium text-gray-900">
                Drop files here or click to browse
              </p>
              <p className="mt-2 text-xs text-gray-500">
                Supported: DOCX, XLSX, PDF, CSV, JSON, XML (Max 50MB)
              </p>
            </div>

            <div className="mt-8 grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="text-2xl font-bold text-blue-600 mb-1">10+</div>
                <div className="text-sm text-gray-600">File Formats</div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="text-2xl font-bold text-green-600 mb-1">15K+</div>
                <div className="text-sm text-gray-600">Requirements Processed</div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="text-2xl font-bold text-purple-600 mb-1">&lt;5s</div>
                <div className="text-sm text-gray-600">Average Processing Time</div>
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
