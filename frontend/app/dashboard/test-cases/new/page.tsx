'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { testCasesAPI } from '@/lib/api';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';

export default function NewTestCasePage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    test_case_id: '',
    title: '',
    description: '',
    test_type: 'Unit',
    priority: 'Medium',
    requirement_id: '',
    expected_result: '',
    automated: false,
    test_steps: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      // Create the test case
      await testCasesAPI.create({
        ...formData,
        status: 'Pending',
      });

      // Redirect to test cases list
      router.push('/dashboard/test-cases');
    } catch (err: any) {
      console.error('Error creating test case:', err);
      setError(err.message || 'Failed to create test case. Please try again.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="/dashboard/test-cases"
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-2" />
          Back to Test Cases
        </Link>
        <h1 className="text-4xl font-bold text-gray-900">Create New Test Case</h1>
        <p className="mt-2 text-gray-600">Add a new test case to verify requirements</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-card-lg shadow-card border border-gray-100 p-8">
        <div className="space-y-6">
          {/* Test Case ID */}
          <div>
            <label htmlFor="test_case_id" className="block text-sm font-medium text-gray-700 mb-2">
              Test Case ID <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="test_case_id"
              name="test_case_id"
              required
              value={formData.test_case_id}
              onChange={handleChange}
              placeholder="e.g., TC-001234"
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="mt-1 text-xs text-gray-500">Unique identifier for this test case</p>
          </div>

          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="title"
              name="title"
              required
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g., Verify flight control system response time"
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              id="description"
              name="description"
              required
              value={formData.description}
              onChange={handleChange}
              rows={4}
              placeholder="Detailed description of what this test case verifies..."
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Test Type */}
            <div>
              <label htmlFor="test_type" className="block text-sm font-medium text-gray-700 mb-2">
                Test Type <span className="text-red-500">*</span>
              </label>
              <select
                id="test_type"
                name="test_type"
                required
                value={formData.test_type}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="Unit">Unit</option>
                <option value="Integration">Integration</option>
                <option value="System">System</option>
                <option value="Acceptance">Acceptance</option>
              </select>
            </div>

            {/* Priority */}
            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
                Priority <span className="text-red-500">*</span>
              </label>
              <select
                id="priority"
                name="priority"
                required
                value={formData.priority}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>

          {/* Requirement ID */}
          <div>
            <label htmlFor="requirement_id" className="block text-sm font-medium text-gray-700 mb-2">
              Linked Requirement ID
            </label>
            <input
              type="number"
              id="requirement_id"
              name="requirement_id"
              value={formData.requirement_id}
              onChange={handleChange}
              placeholder="e.g., 123 (database ID)"
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="mt-1 text-xs text-gray-500">The database ID of the requirement this test verifies</p>
          </div>

          {/* Test Steps */}
          <div>
            <label htmlFor="test_steps" className="block text-sm font-medium text-gray-700 mb-2">
              Test Steps
            </label>
            <textarea
              id="test_steps"
              name="test_steps"
              value={formData.test_steps}
              onChange={handleChange}
              rows={6}
              placeholder="1. Step one&#10;2. Step two&#10;3. Step three..."
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Expected Result */}
          <div>
            <label htmlFor="expected_result" className="block text-sm font-medium text-gray-700 mb-2">
              Expected Result <span className="text-red-500">*</span>
            </label>
            <textarea
              id="expected_result"
              name="expected_result"
              required
              value={formData.expected_result}
              onChange={handleChange}
              rows={3}
              placeholder="What should happen when this test passes..."
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Automated Checkbox */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="automated"
              name="automated"
              checked={formData.automated}
              onChange={handleChange}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="automated" className="ml-2 block text-sm text-gray-900">
              This is an automated test
            </label>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-8 flex items-center justify-end space-x-4 pt-6 border-t border-gray-200">
          <Link
            href="/dashboard/test-cases"
            className="px-6 py-3 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50 transition-colors font-semibold"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors font-semibold shadow-card hover:shadow-card-hover disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Creating...' : 'Create Test Case'}
          </button>
        </div>
      </form>
    </div>
  );
}
