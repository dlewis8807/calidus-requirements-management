import React, { useState } from 'react';
import { Modal } from '@/components/common/Modal';
import { Button } from '@/components/common/Button';
import type { TestCase } from '@/lib/types';
import toast from 'react-hot-toast';

interface ExecutionModalProps {
  testCase: TestCase | null;
  isOpen: boolean;
  onClose: () => void;
  onExecute: (id: number, data: { status: string; actual_results?: string; executed_by?: string }) => Promise<void>;
}

export const ExecutionModal: React.FC<ExecutionModalProps> = ({
  testCase,
  isOpen,
  onClose,
  onExecute,
}) => {
  const [status, setStatus] = useState<string>('passed');
  const [actualResults, setActualResults] = useState<string>('');
  const [executedBy, setExecutedBy] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testCase) return;

    setLoading(true);
    try {
      await onExecute(testCase.id, {
        status,
        actual_results: actualResults || undefined,
        executed_by: executedBy || undefined,
      });
      toast.success('Test case executed successfully');
      onClose();
      // Reset form
      setStatus('passed');
      setActualResults('');
      setExecutedBy('');
    } catch (error) {
      toast.error('Failed to execute test case');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (!testCase) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Execute Test Case: ${testCase.test_case_id}`} size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <h4 className="font-semibold text-gray-900 mb-2">Test Steps:</h4>
          <p className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-3 rounded">
            {testCase.test_steps}
          </p>
        </div>

        <div>
          <h4 className="font-semibold text-gray-900 mb-2">Expected Results:</h4>
          <p className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-3 rounded">
            {testCase.expected_results}
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Result Status <span className="text-red-500">*</span>
          </label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            required
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-[#3B7DDD] focus:ring-[#3B7DDD]"
          >
            <option value="passed">Passed</option>
            <option value="failed">Failed</option>
            <option value="blocked">Blocked</option>
            <option value="in_progress">In Progress</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Actual Results
          </label>
          <textarea
            value={actualResults}
            onChange={(e) => setActualResults(e.target.value)}
            rows={4}
            placeholder="Describe what actually happened during test execution..."
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-[#3B7DDD] focus:ring-[#3B7DDD]"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Executed By
          </label>
          <input
            type="text"
            value={executedBy}
            onChange={(e) => setExecutedBy(e.target.value)}
            placeholder="Your name or ID"
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-[#3B7DDD] focus:ring-[#3B7DDD]"
          />
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" loading={loading}>
            Save Results
          </Button>
        </div>
      </form>
    </Modal>
  );
};
