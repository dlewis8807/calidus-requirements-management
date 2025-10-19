'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { StatCard } from '@/components/dashboard/StatCard';
import { complianceAPI } from '@/lib/api';
import { ComplianceStats, RegulationCoverage, ComplianceGap } from '@/lib/types';
import toast from 'react-hot-toast';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

export default function CompliancePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<ComplianceStats | null>(null);
  const [gaps, setGaps] = useState<ComplianceGap[]>([]);
  const [selectedAuthority, setSelectedAuthority] = useState<string>('all');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token') || localStorage.getItem('token') || localStorage.getItem('demo_token');
      if (!token) {
        router.push('/login');
        return;
      }

      const [statsData, gapsData] = await Promise.all([
        complianceAPI.stats(),
        complianceAPI.gaps({ limit: 10 })
      ]);

      setStats(statsData as ComplianceStats);
      setGaps((gapsData as any).unmapped_requirements || []);
    } catch (error: any) {
      console.error('Failed to fetch compliance data:', error);
      toast.error('Failed to load compliance data');
      if (error.message.includes('401') || error.message.includes('credentials')) {
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout title="Compliance Dashboard">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" text="Loading compliance data..." />
        </div>
      </DashboardLayout>
    );
  }

  if (!stats) {
    return (
      <DashboardLayout title="Compliance Dashboard">
        <div className="text-center py-12">
          <p className="text-gray-500">No compliance data available</p>
        </div>
      </DashboardLayout>
    );
  }

  // Prepare chart data
  const authorityData = Object.entries(stats.by_authority).map(([name, value]) => ({
    name,
    value
  })).filter(item => item.value > 0);

  const regulationData = Object.entries(stats.by_regulation)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);

  const COLORS = ['#3B7DDD', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <DashboardLayout title="Compliance Dashboard">
      <div className="space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-xs font-medium text-gray-600 uppercase tracking-wider">Total Requirements</p>
            <p className="mt-2 text-2xl font-bold text-gray-900">{stats.total_requirements.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-xs font-medium text-gray-600 uppercase tracking-wider">Mapped Requirements</p>
            <p className="mt-2 text-2xl font-bold text-green-600">{stats.mapped_requirements.toLocaleString()}</p>
            <p className="mt-1 text-xs text-gray-500">{stats.coverage_percentage.toFixed(1)}% coverage</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-xs font-medium text-gray-600 uppercase tracking-wider">Unmapped Requirements</p>
            <p className="mt-2 text-2xl font-bold text-orange-600">{stats.unmapped_requirements.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-xs font-medium text-gray-600 uppercase tracking-wider">Regulations</p>
            <p className="mt-2 text-2xl font-bold text-purple-600">{stats.regulations_count}</p>
            <p className="mt-1 text-xs text-gray-500">{stats.sections_count} sections</p>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* By Authority Pie Chart */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Coverage by Authority</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={authorityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }: any) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {authorityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Top Regulations Bar Chart */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Top 10 Regulations</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={regulationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3B7DDD" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Compliance Gaps Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Compliance Gaps (Top 10)</h3>
            <p className="text-sm text-gray-500 mt-1">Requirements without regulatory mapping</p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Requirement ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {gaps.slice(0, 10).map((gap, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                      {gap.requirement_id}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {gap.requirement_title?.substring(0, 60)}...
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {gap.requirement_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        gap.priority === 'Critical' ? 'bg-red-100 text-red-800' :
                        gap.priority === 'High' ? 'bg-orange-100 text-orange-800' :
                        gap.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {gap.priority}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
