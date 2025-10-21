'use client';

import { useEffect, useState } from 'react';
import { coverageAPI } from '@/lib/api';
import { CheckCircle, XCircle, Lightbulb, TrendingUp } from 'lucide-react';

interface Suggestion {
  type: string;
  title: string;
  steps: string[];
  expected_results: string[];
  confidence: number;
  reasoning: string;
}

interface TestSuggestionsProps {
  requirementId: number;
}

export default function TestSuggestions({ requirementId }: TestSuggestionsProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSuggestions();
  }, [requirementId]);

  const loadSuggestions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await coverageAPI.suggestions(requirementId);
      setSuggestions(data);
    } catch (err: any) {
      console.error('Error loading suggestions:', err);
      setError(err.message || 'Failed to load suggestions');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600 bg-green-100';
    if (confidence >= 0.7) return 'text-blue-600 bg-blue-100';
    if (confidence >= 0.5) return 'text-yellow-600 bg-yellow-100';
    return 'text-orange-600 bg-orange-100';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.9) return 'Very High';
    if (confidence >= 0.7) return 'High';
    if (confidence >= 0.5) return 'Medium';
    return 'Low';
  };

  const getTestTypeColor = (type: string) => {
    switch (type) {
      case 'Unit': return 'bg-blue-100 text-blue-800';
      case 'Integration': return 'bg-purple-100 text-purple-800';
      case 'System': return 'bg-green-100 text-green-800';
      case 'Acceptance': return 'bg-indigo-100 text-indigo-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-sm text-gray-600">Generating suggestions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-red-800 font-semibold mb-1">Error</h3>
        <p className="text-red-600 text-sm">{error}</p>
        <button
          onClick={loadSuggestions}
          className="mt-2 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (suggestions.length === 0) {
    return (
      <div className="text-center py-8">
        <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-2" />
        <p className="text-gray-700 font-medium">All test types covered!</p>
        <p className="text-sm text-gray-500 mt-1">
          This requirement has adequate test coverage
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start gap-2">
        <Lightbulb className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
        <div className="text-sm text-blue-800">
          <strong>AI-Generated Suggestions</strong>
          <p className="text-blue-700 mt-1">
            Based on requirement characteristics, we recommend adding {suggestions.length} test{suggestions.length > 1 ? 's' : ''}.
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {suggestions.map((suggestion, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow bg-white"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 text-xs font-medium rounded ${getTestTypeColor(suggestion.type)}`}>
                  {suggestion.type} Test
                </span>
                <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(suggestion.confidence)}`}>
                  <TrendingUp className="w-3 h-3" />
                  {getConfidenceLabel(suggestion.confidence)} ({(suggestion.confidence * 100).toFixed(0)}%)
                </div>
              </div>
            </div>

            {/* Title */}
            <h4 className="font-semibold text-gray-900 mb-2">
              {suggestion.title}
            </h4>

            {/* Reasoning */}
            <div className="bg-gray-50 rounded-lg p-3 mb-3">
              <p className="text-sm text-gray-700">
                <strong className="text-gray-900">Why:</strong> {suggestion.reasoning}
              </p>
            </div>

            {/* Test Steps */}
            <div className="mb-3">
              <h5 className="text-sm font-semibold text-gray-900 mb-2">Suggested Steps:</h5>
              <ol className="space-y-1">
                {suggestion.steps.map((step, stepIndex) => (
                  <li key={stepIndex} className="text-sm text-gray-700 flex gap-2">
                    <span className="text-gray-400 font-medium">{stepIndex + 1}.</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
            </div>

            {/* Expected Results */}
            <div className="mb-4">
              <h5 className="text-sm font-semibold text-gray-900 mb-2">Expected Results:</h5>
              <ul className="space-y-1">
                {suggestion.expected_results.map((result, resultIndex) => (
                  <li key={resultIndex} className="text-sm text-gray-700 flex gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>{result}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-3 border-t border-gray-200">
              <button
                onClick={() => {
                  // TODO: Implement accept suggestion
                  console.log('Accept suggestion:', suggestion);
                }}
                className="flex-1 px-3 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-1"
              >
                <CheckCircle className="w-4 h-4" />
                Accept & Create Test
              </button>
              <button
                onClick={() => {
                  // TODO: Implement reject suggestion
                  console.log('Reject suggestion:', suggestion);
                }}
                className="px-3 py-2 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300 transition-colors flex items-center justify-center gap-1"
              >
                <XCircle className="w-4 h-4" />
                Dismiss
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Footer */}
      <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-600">
        <p>
          <strong className="text-gray-900">{suggestions.length}</strong> suggestion{suggestions.length > 1 ? 's' : ''} generated
          • Average confidence: <strong className="text-gray-900">
            {((suggestions.reduce((sum, s) => sum + s.confidence, 0) / suggestions.length) * 100).toFixed(0)}%
          </strong>
        </p>
      </div>
    </div>
  );
}
