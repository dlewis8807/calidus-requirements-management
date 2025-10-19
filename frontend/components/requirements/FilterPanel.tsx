'use client';

import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon, FunnelIcon } from '@heroicons/react/24/outline';
import type { RequirementFilter } from '@/lib/types';

interface FilterPanelProps {
  isOpen: boolean;
  onClose: () => void;
  filters: RequirementFilter;
  onFiltersChange: (filters: RequirementFilter) => void;
}

const CATEGORIES = [
  'FlightControl', 'Navigation', 'Propulsion', 'Avionics', 'Communication',
  'Safety', 'FuelSystem', 'LandingGear', 'Electrical', 'Hydraulic',
  'Environmental', 'Instrumentation', 'AutoPilot', 'WeatherRadar', 'TCAS'
];

export default function FilterPanel({ isOpen, onClose, filters, onFiltersChange }: FilterPanelProps) {
  const updateFilter = (key: keyof RequirementFilter, value: any) => {
    onFiltersChange({ ...filters, [key]: value || undefined, page: 1 });
  };

  const clearFilters = () => {
    onFiltersChange({
      page: 1,
      page_size: filters.page_size || 50,
    });
  };

  const hasActiveFilters = Object.keys(filters).some(
    key => !['page', 'page_size', 'sort_by', 'sort_order'].includes(key) && filters[key as keyof RequirementFilter]
  );

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-in-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in-out duration-300"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
              <Transition.Child
                as={Fragment}
                enter="transform transition ease-in-out duration-300"
                enterFrom="translate-x-full"
                enterTo="translate-x-0"
                leave="transform transition ease-in-out duration-300"
                leaveFrom="translate-x-0"
                leaveTo="translate-x-full"
              >
                <Dialog.Panel className="pointer-events-auto w-screen max-w-md">
                  <div className="flex h-full flex-col overflow-y-scroll bg-white shadow-xl">
                    {/* Header */}
                    <div className="bg-blue-600 px-4 py-6 sm:px-6" style={{ backgroundColor: '#3B7DDD' }}>
                      <div className="flex items-center justify-between">
                        <Dialog.Title className="text-lg font-semibold text-white flex items-center">
                          <FunnelIcon className="h-6 w-6 mr-2" />
                          Filter Requirements
                        </Dialog.Title>
                        <button
                          type="button"
                          className="rounded-md text-blue-100 hover:text-white focus:outline-none"
                          onClick={onClose}
                        >
                          <XMarkIcon className="h-6 w-6" />
                        </button>
                      </div>
                      {hasActiveFilters && (
                        <button
                          onClick={clearFilters}
                          className="mt-3 text-sm text-blue-100 hover:text-white underline"
                        >
                          Clear all filters
                        </button>
                      )}
                    </div>

                    {/* Filter Content */}
                    <div className="relative flex-1 px-4 py-6 sm:px-6 space-y-6">
                      {/* Type Filter */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Requirement Type
                        </label>
                        <select
                          value={filters.type || ''}
                          onChange={(e) => updateFilter('type', e.target.value)}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        >
                          <option value="">All Types</option>
                          <option value="Aircraft_High_Level_Requirement">AHLR</option>
                          <option value="System_Requirement">System Requirement</option>
                          <option value="Technical_Specification">Technical Specification</option>
                          <option value="Certification_Requirement">Certification Requirement</option>
                        </select>
                      </div>

                      {/* Status Filter */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Status
                        </label>
                        <select
                          value={filters.status || ''}
                          onChange={(e) => updateFilter('status', e.target.value)}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        >
                          <option value="">All Statuses</option>
                          <option value="draft">Draft</option>
                          <option value="approved">Approved</option>
                          <option value="under_review">Under Review</option>
                          <option value="deprecated">Deprecated</option>
                        </select>
                      </div>

                      {/* Priority Filter */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Priority
                        </label>
                        <select
                          value={filters.priority || ''}
                          onChange={(e) => updateFilter('priority', e.target.value)}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        >
                          <option value="">All Priorities</option>
                          <option value="Critical">Critical</option>
                          <option value="High">High</option>
                          <option value="Medium">Medium</option>
                          <option value="Low">Low</option>
                        </select>
                      </div>

                      {/* Category Filter */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Category
                        </label>
                        <select
                          value={filters.category || ''}
                          onChange={(e) => updateFilter('category', e.target.value)}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        >
                          <option value="">All Categories</option>
                          {CATEGORIES.map((cat) => (
                            <option key={cat} value={cat}>{cat}</option>
                          ))}
                        </select>
                      </div>

                      {/* Regulatory Document Filter */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Regulatory Document
                        </label>
                        <input
                          type="text"
                          value={filters.regulatory_document || ''}
                          onChange={(e) => updateFilter('regulatory_document', e.target.value)}
                          placeholder="e.g., 14 CFR Part 23"
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        />
                      </div>

                      {/* Search */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Search
                        </label>
                        <input
                          type="text"
                          value={filters.search || ''}
                          onChange={(e) => updateFilter('search', e.target.value)}
                          placeholder="Search in title and description"
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        />
                        <p className="mt-1 text-xs text-gray-500">
                          Search across requirement ID, title, and description
                        </p>
                      </div>
                    </div>

                    {/* Footer */}
                    <div className="border-t border-gray-200 px-4 py-4 sm:px-6">
                      <button
                        type="button"
                        onClick={onClose}
                        className="w-full rounded-md px-4 py-2 text-sm font-semibold text-white shadow-sm"
                        style={{ backgroundColor: '#3B7DDD' }}
                      >
                        Apply Filters
                      </button>
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
}
