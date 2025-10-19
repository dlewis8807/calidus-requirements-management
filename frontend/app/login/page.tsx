'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function Login() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        // Store both for compatibility
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('token', data.access_token);
        router.push('/dashboard');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
      }
    } catch (err) {
      setError('Failed to connect to server. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemoAccount = (role: 'admin' | 'engineer' | 'viewer') => {
    const credentials = {
      admin: { username: 'admin', password: 'demo2024' },
      engineer: { username: 'engineer', password: 'engineer2024' },
      viewer: { username: 'viewer', password: 'viewer2024' },
    };
    setUsername(credentials[role].username);
    setPassword(credentials[role].password);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block mb-4">
            <img src="/images/CLS-AEROSPACE-LOGO.svg" alt="CALIDUS Aerospace" className="h-20 mx-auto" />
          </Link>
          <p className="text-calidus-gray mt-2">Requirements Management Platform</p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-calidus-silver-light">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Sign In</h2>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                placeholder="Enter your username"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                placeholder="Enter your password"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 text-white rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              style={{backgroundColor: loading ? '#88898D' : '#3B7DDD'}}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Demo Accounts */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm font-medium text-gray-700 mb-3">Try Demo Accounts:</p>
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => fillDemoAccount('admin')}
                className="px-3 py-2 rounded-lg text-xs font-medium transition-colors border"
                style={{backgroundColor: '#EBF3FE', color: '#3B7DDD', borderColor: '#3B7DDD'}}
              >
                Admin
              </button>
              <button
                onClick={() => fillDemoAccount('engineer')}
                className="px-3 py-2 rounded-lg text-xs font-medium transition-colors border"
                style={{backgroundColor: '#EBF3FE', color: '#3B7DDD', borderColor: '#3B7DDD'}}
              >
                Engineer
              </button>
              <button
                onClick={() => fillDemoAccount('viewer')}
                className="px-3 py-2 rounded-lg text-xs font-medium transition-colors border"
                style={{backgroundColor: '#EBF3FE', color: '#3B7DDD', borderColor: '#3B7DDD'}}
              >
                Viewer
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-3 text-center">
              Click a role to auto-fill credentials
            </p>
          </div>

          {/* Register Link */}
          <div className="mt-6 text-center text-sm text-gray-600">
            Don&apos;t have an account?{' '}
            <Link href="/register" className="text-blue-600 font-medium hover:text-blue-700">
              Sign up
            </Link>
          </div>
        </div>

        {/* Back to Home */}
        <div className="text-center mt-6">
          <Link href="/" className="text-sm text-gray-600 hover:text-gray-900">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
