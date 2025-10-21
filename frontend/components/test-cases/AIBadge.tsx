'use client';

import React from 'react';
import { Sparkles } from 'lucide-react';

interface AIBadgeProps {
  variant?: 'default' | 'minimal' | 'detailed';
  confidenceScore?: number;
  showConfidence?: boolean;
}

export function AIBadge({ variant = 'default', confidenceScore, showConfidence = false }: AIBadgeProps) {
  if (variant === 'minimal') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-purple-100 to-blue-100 text-purple-800 text-xs font-semibold rounded">
        <Sparkles className="w-3 h-3" />
        AI
      </span>
    );
  }

  if (variant === 'detailed' && confidenceScore !== undefined) {
    const confidenceColor =
      confidenceScore > 0.7 ? 'text-green-700 bg-green-50 border-green-200' :
      confidenceScore > 0.5 ? 'text-yellow-700 bg-yellow-50 border-yellow-200' :
      'text-orange-700 bg-orange-50 border-orange-200';

    return (
      <div className={`inline-flex items-center gap-2 px-3 py-1.5 border rounded-lg ${confidenceColor}`}>
        <Sparkles className="w-4 h-4" />
        <div className="flex flex-col">
          <span className="text-xs font-semibold">AI Generated</span>
          {showConfidence && (
            <span className="text-xs opacity-75">
              {(confidenceScore * 100).toFixed(0)}% confidence
            </span>
          )}
        </div>
      </div>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-gradient-to-r from-purple-500 to-blue-500 text-white text-xs font-semibold rounded-full shadow-sm">
      <Sparkles className="w-3.5 h-3.5" />
      AI Generated
    </span>
  );
}
