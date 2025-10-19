'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function Home() {
  const [apiStatus, setApiStatus] = useState<'loading' | 'healthy' | 'error'>('loading');
  const [apiInfo, setApiInfo] = useState<any>(null);

  useEffect(() => {
    const checkAPI = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          setApiStatus('healthy');
          const infoResponse = await fetch('http://localhost:8000/');
          const data = await infoResponse.json();
          setApiInfo(data);
        } else {
          setApiStatus('error');
        }
      } catch (error) {
        setApiStatus('error');
      }
    };

    checkAPI();
    const interval = setInterval(checkAPI, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-calidus-silver-light">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center">
              <img src="/images/CLS-AEROSPACE-LOGO.svg" alt="CALIDUS Aerospace" className="h-14" />
            </Link>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${apiStatus === 'healthy' ? 'bg-green-500' : apiStatus === 'error' ? 'bg-red-500' : 'bg-yellow-500'} animate-pulse`}></div>
              <span className="text-sm text-gray-600">
                {apiStatus === 'healthy' ? 'API Online' : apiStatus === 'error' ? 'API Offline' : 'Checking...'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            AI-Powered Requirements Management for Aerospace
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Streamline compliance with UAE GCAA, FAA, EASA, DO-178C, and AS9100 regulations
          </p>
          <div className="flex justify-center gap-4">
            <Link
              href="/demo"
              className="px-6 py-3 text-white rounded-lg font-semibold transition-colors shadow-lg hover:shadow-xl hover:bg-[#2C5DBB]"
              style={{backgroundColor: '#3B7DDD'}}
            >
              Try Interactive Demo
            </Link>
            <Link
              href="/login"
              className="px-6 py-3 bg-white rounded-lg font-semibold hover:bg-gray-50 transition-colors border-2"
              style={{color: '#3B7DDD', borderColor: '#3B7DDD'}}
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-6 rounded-xl shadow-lg border border-calidus-silver-light hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4" style={{backgroundColor: '#EBF3FE'}}>
              <svg className="w-6 h-6" style={{color: '#3B7DDD'}} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Document Processing</h3>
            <p className="text-gray-600">
              Extract and analyze requirements from Word, Excel, PDF, and structured data files
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg border border-calidus-silver-light hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4" style={{backgroundColor: '#C8C9CD'}}>
              <svg className="w-6 h-6" style={{color: '#3B7DDD'}} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Compliance Tracking</h3>
            <p className="text-gray-600">
              Automatic verification against DO-178C, AS9100, FAA, EASA, and UAE GCAA standards
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg border border-calidus-silver-light hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4" style={{backgroundColor: '#EBF3FE'}}>
              <svg className="w-6 h-6" style={{color: '#3B7DDD'}} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">AI-Powered Insights</h3>
            <p className="text-gray-600">
              Smart requirement classification, gap analysis, and traceability matrix generation
            </p>
          </div>
        </div>

        {/* Stats Section */}
        <div className="bg-white rounded-xl shadow-lg border border-calidus-silver-light p-8 mb-16">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold mb-2" style={{color: '#3B7DDD'}}>15,000+</div>
              <div className="text-calidus-gray">Requirements Managed</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2" style={{color: '#3B7DDD'}}>99.9%</div>
              <div className="text-calidus-gray">Compliance Accuracy</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2" style={{color: '#A8A9AD'}}>10+</div>
              <div className="text-calidus-gray">File Formats Supported</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2" style={{color: '#A8A9AD'}}>24/7</div>
              <div className="text-calidus-gray">AI Assistant Available</div>
            </div>
          </div>
        </div>

        {/* API Status Section */}
        {apiInfo && (
          <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl p-6 border border-calidus-silver-light">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-white rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">Application</div>
                <div className="font-semibold text-gray-900">{apiInfo.app}</div>
              </div>
              <div className="bg-white rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">Version</div>
                <div className="font-semibold text-gray-900">{apiInfo.version}</div>
              </div>
              <div className="bg-white rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">Status</div>
                <div className="font-semibold text-green-600 capitalize">{apiInfo.status}</div>
              </div>
              <div className="bg-white rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">API Endpoint</div>
                <div className="font-mono text-xs text-gray-900">http://localhost:8000</div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-calidus-silver-light mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-calidus-gray text-sm">
            <p className="mb-2 font-semibold" style={{color: '#3B7DDD'}}>CALIDUS | AEROSPACE</p>
            <p className="text-xs text-calidus-silver-dark">
              Requirements Management & Traceability Assistant
            </p>
            <p className="text-xs text-calidus-silver-dark mt-2">
              Compliant with DO-178C, AS9100, FAA, EASA, and UAE GCAA regulations
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
