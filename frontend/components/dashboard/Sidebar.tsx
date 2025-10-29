'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import {
  HomeIcon,
  DocumentTextIcon,
  BeakerIcon,
  ArrowsRightLeftIcon,
  UserGroupIcon,
  Cog6ToothIcon,
  ArrowLeftOnRectangleIcon,
  ExclamationTriangleIcon,
  ShieldExclamationIcon,
  BoltIcon,
  ChartBarIcon,
  ChevronDownIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavItem {
  name: string;
  href?: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  adminOnly?: boolean;
  children?: Array<{
    name: string;
    href: string;
    icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  }>;
}

const navigation: NavItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  {
    name: 'Requirements',
    href: '/dashboard/requirements',
    icon: DocumentTextIcon,
    children: [
      { name: 'Impact Analysis', href: '/dashboard/impact-analysis', icon: BoltIcon },
      { name: 'Conflicts', href: '/dashboard/conflicts', icon: ExclamationTriangleIcon },
      { name: 'Compliance', href: '/dashboard/compliance', icon: DocumentTextIcon },
    ]
  },
  {
    name: 'Test Cases',
    href: '/dashboard/test-cases',
    icon: BeakerIcon,
    children: [
      { name: 'Coverage', href: '/dashboard/coverage', icon: ChartBarIcon },
    ]
  },
  { name: 'Traceability', href: '/dashboard/traceability', icon: ArrowsRightLeftIcon },
  { name: 'Risk Assessment', href: '/dashboard/risk', icon: ShieldExclamationIcon },
  { name: 'Users', href: '/dashboard/admin/users', icon: UserGroupIcon, adminOnly: true },
  { name: 'Settings', href: '/dashboard/settings', icon: Cog6ToothIcon },
];

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  // Auto-expand parent items if child is active
  useState(() => {
    const expanded: string[] = [];
    navigation.forEach(item => {
      if (item.children) {
        const hasActiveChild = item.children.some(child =>
          pathname === child.href || pathname?.startsWith(child.href + '/')
        );
        if (hasActiveChild) {
          expanded.push(item.name);
        }
      }
    });
    setExpandedItems(expanded);
  });

  const toggleExpanded = (itemName: string) => {
    setExpandedItems(prev =>
      prev.includes(itemName)
        ? prev.filter(name => name !== itemName)
        : [...prev, itemName]
    );
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('demo_token');
    window.location.href = '/login';
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 z-20 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 z-30 h-full w-64 bg-white border-r border-gray-200
          transform transition-transform duration-300 ease-in-out lg:translate-x-0
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-20 px-6 border-b border-gray-200">
            <Link href="/dashboard" className="flex items-center">
              <img
                src="/images/CLS-AEROSPACE-LOGO.svg"
                alt="CALIDUS"
                className="h-20"
              />
            </Link>
            <button
              onClick={onClose}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = item.href && (pathname === item.href || pathname?.startsWith(item.href + '/'));
              const isExpanded = expandedItems.includes(item.name);
              const hasChildren = item.children && item.children.length > 0;

              return (
                <div key={item.name}>
                  {/* Parent Item */}
                  <div className="flex items-center">
                    {item.href ? (
                      <Link
                        href={item.href}
                        className={`
                          flex items-center flex-1 px-4 py-3 text-sm font-medium rounded-lg transition-colors
                          ${isActive && !hasChildren
                            ? 'bg-blue-50 text-blue-600'
                            : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                          }
                        `}
                        style={isActive && !hasChildren ? { backgroundColor: '#EBF3FE', color: '#3B7DDD' } : {}}
                      >
                        <item.icon
                          className={`mr-3 h-5 w-5 ${isActive && !hasChildren ? 'text-blue-600' : 'text-gray-400'}`}
                          style={isActive && !hasChildren ? { color: '#3B7DDD' } : {}}
                        />
                        {item.name}
                        {item.adminOnly && (
                          <span className="ml-auto px-2 py-0.5 text-xs font-semibold bg-orange-100 text-orange-700 rounded">
                            Admin
                          </span>
                        )}
                      </Link>
                    ) : (
                      <div className="flex items-center flex-1 px-4 py-3 text-sm font-medium text-gray-700">
                        <item.icon className="mr-3 h-5 w-5 text-gray-400" />
                        {item.name}
                      </div>
                    )}

                    {/* Expand/Collapse Button */}
                    {hasChildren && (
                      <button
                        onClick={() => toggleExpanded(item.name)}
                        className="p-2 hover:bg-gray-100 rounded transition-colors"
                      >
                        {isExpanded ? (
                          <ChevronDownIcon className="h-4 w-4 text-gray-500" />
                        ) : (
                          <ChevronRightIcon className="h-4 w-4 text-gray-500" />
                        )}
                      </button>
                    )}
                  </div>

                  {/* Child Items */}
                  {hasChildren && isExpanded && (
                    <div className="ml-6 mt-1 space-y-1">
                      {item.children!.map((child) => {
                        const isChildActive = pathname === child.href || pathname?.startsWith(child.href + '/');
                        return (
                          <Link
                            key={child.name}
                            href={child.href}
                            className={`
                              flex items-center px-4 py-2 text-sm rounded-lg transition-colors
                              ${isChildActive
                                ? 'bg-blue-50 text-blue-600 font-medium'
                                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                              }
                            `}
                            style={isChildActive ? { backgroundColor: '#EBF3FE', color: '#3B7DDD' } : {}}
                          >
                            <child.icon
                              className={`mr-3 h-4 w-4 ${isChildActive ? 'text-blue-600' : 'text-gray-400'}`}
                              style={isChildActive ? { color: '#3B7DDD' } : {}}
                            />
                            {child.name}
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </nav>

          {/* User info & Logout */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center mb-3">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <span className="text-blue-600 font-semibold text-sm">AD</span>
                </div>
              </div>
              <div className="ml-3 flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">Admin User</p>
                <p className="text-xs text-gray-500 truncate">admin@calidus.aero</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeftOnRectangleIcon className="mr-3 h-5 w-5 text-gray-400" />
              Logout
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
