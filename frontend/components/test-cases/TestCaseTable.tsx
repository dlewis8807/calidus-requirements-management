import React from 'react';
import Link from 'next/link';
import { Badge } from '@/components/common/Badge';
import { Button } from '@/components/common/Button';
import type { TestCase } from '@/lib/types';
import { PlayIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';

interface TestCaseTableProps {
  testCases: TestCase[];
  onExecute?: (testCase: TestCase) => void;
}

export const TestCaseTable: React.FC<TestCaseTableProps> = ({ testCases, onExecute }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Test ID
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Priority
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Requirement
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Executed
              </th>
              <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {testCases.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                  No test cases found.
                </td>
              </tr>
            ) : (
              testCases.map((test) => (
                <tr key={test.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-medium text-gray-900">{test.test_case_id}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-md truncate">{test.title}</div>
                    {test.automated && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 mt-1">
                        Automated
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge variant="status">{test.status}</Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge variant="priority">{test.priority}</Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {test.requirement_id_str ? (
                      <Link
                        href={`/dashboard/requirements/${test.requirement_id}`}
                        className="text-[#3B7DDD] hover:text-[#2F66BD] text-sm"
                      >
                        {test.requirement_id_str}
                      </Link>
                    ) : (
                      <span className="text-sm text-gray-500">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {test.execution_date
                      ? format(new Date(test.execution_date), 'MMM dd, yyyy')
                      : 'Never'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    {onExecute && (
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => onExecute(test)}
                        className="inline-flex items-center"
                      >
                        <PlayIcon className="h-4 w-4 mr-1" />
                        Execute
                      </Button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
