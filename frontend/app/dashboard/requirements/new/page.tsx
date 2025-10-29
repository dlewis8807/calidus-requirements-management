'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { requirementsAPI } from '@/lib/api';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

export default function NewRequirementPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | string[] | null>(null);
  const [formData, setFormData] = useState({
    requirement_id: '',
    title: '',
    description: '',
    type: 'System_Requirement',
    status: 'draft',
    priority: 'Medium',
    category: '',
    verification_method: 'Test',
    regulatory_document: '',
    regulatory_section: '',
    regulatory_page: '',
    version: '1.0',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Convert regulatory_page to number if provided
      const payload = {
        ...formData,
        regulatory_page: formData.regulatory_page ? parseInt(formData.regulatory_page) : null,
      };

      await requirementsAPI.create(payload as any);
      router.push('/dashboard/requirements');
    } catch (err: any) {
      console.error('Error creating requirement:', err);

      // Parse error message - handle both string errors and validation error arrays
      let errorMessage: string | string[] = 'Failed to create requirement';

      // Check if the error has a data property (from our API client)
      if (err.data?.detail) {
        if (Array.isArray(err.data.detail)) {
          // FastAPI validation errors
          errorMessage = err.data.detail.map((e: any) =>
            `${e.loc?.slice(1).join(' > ') || 'Error'}: ${e.msg}`
          );
        } else {
          errorMessage = err.data.detail;
        }
      } else if (err.message) {
        // Fallback to error message
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout title="New Requirement">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-4">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5 text-gray-600" />
          </button>
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Create New Requirement</h2>
            <p className="mt-2 text-base text-gray-600">
              Add a new requirement to the system
            </p>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-card p-4">
            {Array.isArray(error) ? (
              <div>
                <p className="text-sm font-semibold text-red-800 mb-2">Validation Errors:</p>
                <ul className="list-disc list-inside space-y-1">
                  {error.map((err, index) => (
                    <li key={index} className="text-sm text-red-700">{err}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <p className="text-sm text-red-700">{error}</p>
            )}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-card-lg shadow-card border border-gray-100 p-8">
          <div className="space-y-6">
            {/* Requirement ID and Version */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="requirement_id" className="block text-sm font-semibold text-gray-900 mb-2">
                  Requirement ID *
                </label>
                <input
                  type="text"
                  id="requirement_id"
                  name="requirement_id"
                  required
                  value={formData.requirement_id}
                  onChange={handleChange}
                  placeholder="e.g., SYS-00001"
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label htmlFor="version" className="block text-sm font-semibold text-gray-900 mb-2">
                  Version *
                </label>
                <input
                  type="text"
                  id="version"
                  name="version"
                  required
                  value={formData.version}
                  onChange={handleChange}
                  placeholder="e.g., 1.0"
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Title */}
            <div>
              <label htmlFor="title" className="block text-sm font-semibold text-gray-900 mb-2">
                Title *
              </label>
              <input
                type="text"
                id="title"
                name="title"
                required
                value={formData.title}
                onChange={handleChange}
                placeholder="Enter requirement title"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-semibold text-gray-900 mb-2">
                Description *
              </label>
              <textarea
                id="description"
                name="description"
                required
                rows={4}
                value={formData.description}
                onChange={handleChange}
                placeholder="Enter detailed requirement description"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Type, Status, Priority */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label htmlFor="type" className="block text-sm font-semibold text-gray-900 mb-2">
                  Type *
                </label>
                <select
                  id="type"
                  name="type"
                  required
                  value={formData.type}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="Aircraft_High_Level_Requirement">AHLR</option>
                  <option value="System_Requirement">System</option>
                  <option value="Technical_Specification">Technical</option>
                  <option value="Certification_Requirement">Certification</option>
                </select>
              </div>
              <div>
                <label htmlFor="status" className="block text-sm font-semibold text-gray-900 mb-2">
                  Status *
                </label>
                <select
                  id="status"
                  name="status"
                  required
                  value={formData.status}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="draft">Draft</option>
                  <option value="under_review">Under Review</option>
                  <option value="approved">Approved</option>
                  <option value="deprecated">Deprecated</option>
                </select>
              </div>
              <div>
                <label htmlFor="priority" className="block text-sm font-semibold text-gray-900 mb-2">
                  Priority *
                </label>
                <select
                  id="priority"
                  name="priority"
                  required
                  value={formData.priority}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="Critical">Critical</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>
            </div>

            {/* Category and Verification Method */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="category" className="block text-sm font-semibold text-gray-900 mb-2">
                  Category
                </label>
                <input
                  type="text"
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  placeholder="e.g., FlightControl, Structures"
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label htmlFor="verification_method" className="block text-sm font-semibold text-gray-900 mb-2">
                  Verification Method *
                </label>
                <select
                  id="verification_method"
                  name="verification_method"
                  required
                  value={formData.verification_method}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="Test">Test</option>
                  <option value="Analysis">Analysis</option>
                  <option value="Inspection">Inspection</option>
                  <option value="Demonstration">Demonstration</option>
                </select>
              </div>
            </div>

            {/* Regulatory Information */}
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Regulatory Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label htmlFor="regulatory_document" className="block text-sm font-semibold text-gray-900 mb-2">
                    Regulatory Document
                  </label>
                  <input
                    type="text"
                    id="regulatory_document"
                    name="regulatory_document"
                    value={formData.regulatory_document}
                    onChange={handleChange}
                    placeholder="e.g., 14 CFR Part 23"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label htmlFor="regulatory_section" className="block text-sm font-semibold text-gray-900 mb-2">
                    Section
                  </label>
                  <input
                    type="text"
                    id="regulatory_section"
                    name="regulatory_section"
                    value={formData.regulatory_section}
                    onChange={handleChange}
                    placeholder="e.g., §23.143"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label htmlFor="regulatory_page" className="block text-sm font-semibold text-gray-900 mb-2">
                    Page
                  </label>
                  <input
                    type="number"
                    id="regulatory_page"
                    name="regulatory_page"
                    value={formData.regulatory_page}
                    onChange={handleChange}
                    placeholder="e.g., 42"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={() => router.back()}
                className="px-5 py-2.5 border border-gray-300 rounded-xl text-sm font-semibold text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-5 py-2.5 border border-transparent rounded-xl text-sm font-semibold text-white shadow-card hover:shadow-card-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all bg-primary-500 hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating...' : 'Create Requirement'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
}
