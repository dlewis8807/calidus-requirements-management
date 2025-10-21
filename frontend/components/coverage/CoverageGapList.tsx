'use client';

import { useState, useMemo } from 'react';
import { AlertCircle, Filter, Download } from 'lucide-react';

interface Gap {
  requirement_id: number;
  requirement_identifier: string;
  title: string;
  type: string;
  priority: string;
  status: string;
  regulatory: boolean;
  regulatory_document?: string;
}

interface CoverageGapListProps {
  gaps: Gap[];
  onSelectGap: (id: number) => void;
  selectedGap: number | null;
}

export default function CoverageGapList({ gaps, onSelectGap, selectedGap }: CoverageGapListProps) {
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [regulatoryFilter, setRegulatoryFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const filteredGaps = useMemo(() => {
    return gaps.filter(gap => {
      if (typeFilter !== 'all' && gap.type !== typeFilter) return false;
      if (priorityFilter !== 'all' && gap.priority !== priorityFilter) return false;
      if (regulatoryFilter === 'yes' && !gap.regulatory) return false;
      if (regulatoryFilter === 'no' && gap.regulatory) return false;
      if (searchTerm && !gap.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
          !gap.requirement_identifier.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }
      return true;
    });
  }, [gaps, typeFilter, priorityFilter, regulatoryFilter, searchTerm]);

  const exportToCSV = () => {
    const headers = ['ID', 'Title', 'Type', 'Priority', 'Status', 'Regulatory', 'Document'];
    const rows = filteredGaps.map(gap => [
      gap.requirement_identifier,
      gap.title,
      gap.type,
      gap.priority,
      gap.status,
      gap.regulatory ? 'Yes' : 'No',
      gap.regulatory_document || ''
    ]);

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `coverage-gaps-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'High': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'Low': return 'bg-blue-100 text-blue-800 border-blue-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'AHLR': return 'bg-purple-100 text-purple-800';
      case 'System': return 'bg-blue-100 text-blue-800';
      case 'Technical': return 'bg-green-100 text-green-800';
      case 'Certification': return 'bg-indigo-100 text-indigo-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const types = ['all', ...Array.from(new Set(gaps.map(g => g.type)))];
  const priorities = ['all', ...Array.from(new Set(gaps.map(g => g.priority)))];

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-3 py-2 rounded-lg flex items-center gap-2 transition-colors ${
              showFilters ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Filter className="w-4 h-4" />
            Filters
          </button>
          <span className="text-sm text-gray-600">
            Showing {filteredGaps.length} of {gaps.length} gaps
          </span>
        </div>
        <button
          onClick={exportToCSV}
          className="px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          Export CSV
        </button>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-gray-50 rounded-lg p-4 space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type
              </label>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {types.map(type => (
                  <option key={type} value={type}>
                    {type === 'all' ? 'All Types' : type}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {priorities.map(priority => (
                  <option key={priority} value={priority}>
                    {priority === 'all' ? 'All Priorities' : priority}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Regulatory
              </label>
              <select
                value={regulatoryFilter}
                onChange={(e) => setRegulatoryFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All</option>
                <option value="yes">Regulatory Only</option>
                <option value="no">Non-Regulatory Only</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by ID or title..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => {
                setTypeFilter('all');
                setPriorityFilter('all');
                setRegulatoryFilter('all');
                setSearchTerm('');
              }}
              className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              Clear Filters
            </button>
          </div>
        </div>
      )}

      {/* Gap List */}
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredGaps.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No gaps found matching the current filters</p>
          </div>
        ) : (
          filteredGaps.map(gap => (
            <div
              key={gap.requirement_id}
              onClick={() => onSelectGap(gap.requirement_id)}
              className={`
                p-4 rounded-lg border-2 transition-all cursor-pointer
                ${selectedGap === gap.requirement_id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-md'
                }
              `}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-sm font-semibold text-gray-900">
                      {gap.requirement_identifier}
                    </span>
                    {gap.regulatory && (
                      <span className="px-2 py-0.5 text-xs bg-indigo-100 text-indigo-800 rounded-full">
                        Regulatory
                      </span>
                    )}
                  </div>
                  <h4 className="text-sm text-gray-900 line-clamp-2">
                    {gap.title}
                  </h4>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded border ${getPriorityColor(gap.priority)}`}>
                  {gap.priority}
                </span>
              </div>

              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 text-xs font-medium rounded ${getTypeColor(gap.type)}`}>
                  {gap.type}
                </span>
                {gap.regulatory_document && (
                  <span className="text-xs text-gray-600">
                    {gap.regulatory_document}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
