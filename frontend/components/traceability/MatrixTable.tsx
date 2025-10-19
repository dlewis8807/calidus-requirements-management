import React from 'react';
import Link from 'next/link';
import { Badge } from '@/components/common/Badge';

interface TraceLink {
  id: number;
  source_requirement_id: string;
  source_title: string;
  target_requirement_id: string;
  target_title: string;
  link_type: string;
}

interface MatrixTableProps {
  traceLinks: TraceLink[];
}

export const MatrixTable: React.FC<MatrixTableProps> = ({ traceLinks }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Source Requirement
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Link Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Target Requirement
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {traceLinks.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-6 py-12 text-center text-gray-500">
                  No trace links found.
                </td>
              </tr>
            ) : (
              traceLinks.map((link) => (
                <tr key={link.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-[#3B7DDD]">
                      {link.source_requirement_id}
                    </div>
                    <div className="text-sm text-gray-500 truncate max-w-xs">
                      {link.source_title}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge variant="default">
                      {link.link_type.replace(/_/g, ' ')}
                    </Badge>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-[#3B7DDD]">
                      {link.target_requirement_id}
                    </div>
                    <div className="text-sm text-gray-500 truncate max-w-xs">
                      {link.target_title}
                    </div>
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
