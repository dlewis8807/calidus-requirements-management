'use client';

import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, Lightbulb, ThumbsUp, ThumbsDown, Loader2, Target, Code, ClipboardCheck } from 'lucide-react';

interface RootCause {
  cause: string;
  likelihood: number;
  evidence: string[];
  affected_components: string[];
  regulatory_impact?: string;
}

interface Suggestion {
  priority: number;
  action: string;
  details: string;
  code_locations: string[];
  verification_steps: string[];
  estimated_effort_hours: number;
}

interface SuggestionsPanelProps {
  testCaseId: number;
  executionLog?: string;
  onAnalysisComplete?: (data: any) => void;
}

export function SuggestionsPanel({ testCaseId, executionLog = '', onAnalysisComplete }: SuggestionsPanelProps) {
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeFailure = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/test-cases/${testCaseId}/analyze`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          execution_log: executionLog || 'Test failed - no detailed log available'
        })
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data = await response.json();
      setAnalysis(data);

      if (onAnalysisComplete) {
        onAnalysisComplete(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze test failure');
      console.error('Failed to analyze:', err);
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (suggestionIndex: number, helpful: boolean) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`http://localhost:8000/api/test-cases/suggestions/${suggestionIndex}/feedback`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ helpful })
      });
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    }
  };

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-red-600" />
          <div>
            <h3 className="text-lg font-semibold text-red-900">Analysis Failed</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
        <button
          onClick={analyzeFailure}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
        >
          Retry Analysis
        </button>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <Lightbulb className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              🤖 Intelligent Failure Analysis
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Get AI-powered suggestions to help diagnose and fix this test failure.
              Our reasoning engine uses aerospace domain expertise and pattern matching
              to provide actionable insights.
            </p>
            <div className="flex flex-wrap gap-2 text-xs text-gray-500 mb-4">
              <span className="flex items-center gap-1 bg-white px-2 py-1 rounded">
                <CheckCircle className="w-3 h-3" /> Sub-100ms analysis
              </span>
              <span className="flex items-center gap-1 bg-white px-2 py-1 rounded">
                <CheckCircle className="w-3 h-3" /> Aerospace expertise
              </span>
            </div>
            <button
              onClick={analyzeFailure}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm font-medium"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Lightbulb className="w-4 h-4" />
                  Analyze Failure
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Failure Classification */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Target className="w-5 h-5 text-blue-600" />
            Failure Classification
          </h3>
          <span className="px-3 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full uppercase">
            {analysis.failure_type.replace(/_/g, ' ')}
          </span>
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="font-medium">Confidence:</span>
            <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-xs">
              <div
                className={`h-2 rounded-full ${
                  analysis.confidence_score > 0.7 ? 'bg-green-500' :
                  analysis.confidence_score > 0.5 ? 'bg-yellow-500' :
                  'bg-orange-500'
                }`}
                style={{ width: `${analysis.confidence_score * 100}%` }}
              />
            </div>
            <span className="font-medium text-gray-900">
              {(analysis.confidence_score * 100).toFixed(0)}%
            </span>
          </div>
          <p className="text-xs text-gray-500">
            {analysis.confidence_score > 0.7 ? 'High confidence - strong pattern match' :
             analysis.confidence_score > 0.5 ? 'Medium confidence - partial match' :
             'Low confidence - generic suggestions'}
          </p>
        </div>
      </div>

      {/* Root Causes */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-orange-600" />
          Root Cause Analysis
        </h3>

        <div className="space-y-4">
          {analysis.root_causes.map((cause: RootCause, index: number) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="flex items-center justify-center w-6 h-6 bg-orange-100 text-orange-800 text-xs font-bold rounded-full">
                      {index + 1}
                    </span>
                    <p className="text-sm font-semibold text-gray-900">{cause.cause}</p>
                  </div>

                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs text-gray-600">Likelihood:</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-1.5 max-w-xs">
                      <div
                        className={`h-1.5 rounded-full ${
                          cause.likelihood > 0.7 ? 'bg-red-500' :
                          cause.likelihood > 0.5 ? 'bg-orange-500' :
                          'bg-yellow-500'
                        }`}
                        style={{ width: `${cause.likelihood * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-900">
                      {(cause.likelihood * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Evidence */}
              {cause.evidence.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-gray-700 uppercase mb-2">Evidence:</p>
                  <ul className="space-y-1">
                    {cause.evidence.map((ev, i) => (
                      <li key={i} className="text-xs text-gray-600 flex items-start gap-2">
                        <span className="text-blue-500 mt-0.5">•</span>
                        <span>{ev}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Affected Components */}
              {cause.affected_components.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-gray-700 uppercase mb-2">
                    Affected Components:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {cause.affected_components.map((comp, i) => (
                      <span
                        key={i}
                        className="px-2 py-1 bg-blue-50 text-blue-800 text-xs rounded border border-blue-200"
                      >
                        {comp}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Regulatory Impact */}
              {cause.regulatory_impact && (
                <div className="mt-3 p-2 bg-orange-50 border border-orange-200 rounded">
                  <p className="text-xs font-semibold text-orange-900 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    Regulatory Impact:
                  </p>
                  <p className="text-xs text-orange-800 mt-1">{cause.regulatory_impact}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Suggestions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-yellow-600" />
          Suggested Actions
        </h3>

        <div className="space-y-4">
          {analysis.suggestions.map((suggestion: Suggestion, index: number) => (
            <div key={index} className="border border-blue-200 rounded-lg p-4 bg-blue-50">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-start gap-3 flex-1">
                  <span className="flex items-center justify-center w-8 h-8 bg-blue-600 text-white text-sm font-bold rounded-full flex-shrink-0">
                    {suggestion.priority}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-gray-900">{suggestion.action}</p>
                    <p className="text-xs text-gray-700 mt-1">{suggestion.details}</p>
                  </div>
                </div>
                <span className="text-xs text-gray-600 whitespace-nowrap ml-4">
                  ~{suggestion.estimated_effort_hours}h
                </span>
              </div>

              {/* Code Locations */}
              {suggestion.code_locations.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-gray-700 uppercase mb-2 flex items-center gap-1">
                    <Code className="w-3 h-3" />
                    Code Locations:
                  </p>
                  <div className="space-y-1">
                    {suggestion.code_locations.map((loc, i) => (
                      <code key={i} className="block text-xs bg-gray-900 text-gray-100 px-2 py-1 rounded font-mono">
                        {loc}
                      </code>
                    ))}
                  </div>
                </div>
              )}

              {/* Verification Steps */}
              {suggestion.verification_steps.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-gray-700 uppercase mb-2 flex items-center gap-1">
                    <ClipboardCheck className="w-3 h-3" />
                    Verification Steps:
                  </p>
                  <ol className="list-decimal list-inside space-y-1">
                    {suggestion.verification_steps.map((step, i) => (
                      <li key={i} className="text-xs text-gray-700">{step}</li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Feedback Buttons */}
              <div className="mt-4 pt-4 border-t border-blue-200 flex items-center justify-between">
                <p className="text-xs text-gray-600">Was this suggestion helpful?</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => submitFeedback(index, true)}
                    className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 text-xs rounded hover:bg-green-200 transition-colors"
                  >
                    <ThumbsUp className="w-3 h-3" />
                    Yes
                  </button>
                  <button
                    onClick={() => submitFeedback(index, false)}
                    className="flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 text-xs rounded hover:bg-red-200 transition-colors"
                  >
                    <ThumbsDown className="w-3 h-3" />
                    No
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Analysis Metadata */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between text-xs text-gray-600">
          <span>Analysis completed at {new Date().toLocaleString()}</span>
          <button
            onClick={analyzeFailure}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            Re-analyze
          </button>
        </div>
      </div>
    </div>
  );
}
