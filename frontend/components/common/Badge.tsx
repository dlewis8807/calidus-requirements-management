import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'status' | 'priority' | 'type';
  color?: string;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  color,
  className = ''
}) => {
  const getColorClasses = () => {
    if (color) return color;

    const value = String(children).toLowerCase();

    // Status colors
    if (variant === 'status') {
      if (value === 'approved') return 'bg-green-100 text-green-800 border-green-200';
      if (value === 'draft') return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      if (value === 'under review' || value === 'under_review' || value === 'in_progress') return 'bg-blue-100 text-blue-800 border-blue-200';
      if (value === 'deprecated') return 'bg-gray-100 text-gray-800 border-gray-200';
      if (value === 'passed') return 'bg-green-100 text-green-800 border-green-200';
      if (value === 'failed') return 'bg-red-100 text-red-800 border-red-200';
      if (value === 'blocked') return 'bg-orange-100 text-orange-800 border-orange-200';
      if (value === 'pending') return 'bg-gray-100 text-gray-800 border-gray-200';
    }

    // Priority colors
    if (variant === 'priority') {
      if (value === 'critical') return 'bg-red-100 text-red-800 border-red-200';
      if (value === 'high') return 'bg-orange-100 text-orange-800 border-orange-200';
      if (value === 'medium') return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      if (value === 'low') return 'bg-blue-100 text-blue-800 border-blue-200';
      if (value === 'informational') return 'bg-gray-100 text-gray-800 border-gray-200';
    }

    // Type colors
    if (variant === 'type') {
      if (value.includes('aircraft') || value.includes('ahlr')) return 'bg-purple-100 text-purple-800 border-purple-200';
      if (value.includes('system')) return 'bg-blue-100 text-blue-800 border-blue-200';
      if (value.includes('technical')) return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      if (value.includes('certification')) return 'bg-green-100 text-green-800 border-green-200';
    }

    return 'bg-gray-100 text-gray-800 border-gray-200';
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getColorClasses()} ${className}`}>
      {children}
    </span>
  );
};

export default Badge;
