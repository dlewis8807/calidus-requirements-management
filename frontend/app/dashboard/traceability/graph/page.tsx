'use client';

import React, { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { traceabilityAPI } from '@/lib/api';
import toast from 'react-hot-toast';
import cytoscape from 'cytoscape';
import fcose from 'cytoscape-fcose';

// Register the layout
if (typeof cytoscape !== 'undefined') {
  cytoscape.use(fcose);
}

interface GraphNode {
  id: string;
  label: string;
  title: string;
  type: string;
  status: string;
  priority: string;
  category: string;
  test_count: number;
  node_type: string;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  link_type: string;
  description?: string;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  total_nodes: number;
  total_edges: number;
}

export default function TraceabilityGraphPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [maxNodes, setMaxNodes] = useState(500);
  const [filterType, setFilterType] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [includeTests, setIncludeTests] = useState(false);
  const cyRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Fetch graph data
  const fetchGraphData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token') || localStorage.getItem('token') || localStorage.getItem('demo_token');
      if (!token) {
        router.push('/login');
        return;
      }

      const params: Record<string, any> = { max_nodes: maxNodes };
      if (filterType) params.type = filterType;
      if (filterStatus) params.status = filterStatus;
      if (includeTests) params.include_tests = true;

      const data = await traceabilityAPI.graph(params);
      setGraphData(data as GraphData);
    } catch (error: any) {
      console.error('Failed to fetch graph data:', error);
      toast.error('Failed to load traceability graph');
      if (error.message.includes('401') || error.message.includes('Unauthorized')) {
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphData();
  }, [maxNodes, filterType, filterStatus, includeTests]);

  // Initialize Cytoscape
  useEffect(() => {
    if (!graphData || !containerRef.current) return;

    // Destroy existing instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Type color mapping
    const getNodeColor = (type: string) => {
      switch (type) {
        case 'Aircraft_High_Level_Requirement':
          return '#3b82f6'; // blue
        case 'System_Requirement':
          return '#10b981'; // green
        case 'Technical_Specification':
          return '#f59e0b'; // amber
        case 'Certification_Requirement':
          return '#ef4444'; // red
        default:
          return '#6b7280'; // gray
      }
    };

    // Convert data to Cytoscape format
    const elements = [
      ...graphData.nodes.map(node => ({
        data: {
          id: node.id,
          label: node.label,
          title: node.title,
          type: node.type,
          status: node.status,
          priority: node.priority,
          category: node.category,
          test_count: node.test_count,
          node_type: node.node_type,
          color: getNodeColor(node.type)
        }
      })),
      ...graphData.edges.map(edge => ({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          link_type: edge.link_type
        }
      }))
    ];

    // Create Cytoscape instance
    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'background-color': 'data(color)',
            'color': '#fff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '10px',
            'width': '30px',
            'height': '30px',
            'text-wrap': 'wrap',
            'text-max-width': '80px'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#cbd5e1',
            'target-arrow-color': '#cbd5e1',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 1
          }
        },
        {
          selector: ':selected',
          style: {
            'background-color': '#8b5cf6',
            'line-color': '#8b5cf6',
            'target-arrow-color': '#8b5cf6',
            'border-width': 3,
            'border-color': '#8b5cf6'
          }
        }
      ],
      layout: {
        name: 'fcose',
        fit: true,
        padding: 30
      } as any,    });

    // Add event listeners
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const data = node.data();
      toast(`${data.label}: ${data.title.substring(0, 50)}...`, {
        duration: 3000,
        icon: 'ℹ️'
      });
    });

    cyRef.current = cy;

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [graphData]);

  // Control functions
  const zoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.2);
  const zoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const fit = () => cyRef.current?.fit();
  const center = () => cyRef.current?.center();

  if (loading) {
    return (
      <DashboardLayout title="Traceability Graph">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" text="Loading traceability graph..." />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Traceability Graph">
      <div className="space-y-4">
        {/* Controls */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex flex-wrap items-center gap-4">
            {/* Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Types</option>
                <option value="Aircraft_High_Level_Requirement">AHLR</option>
                <option value="System_Requirement">System</option>
                <option value="Technical_Specification">Technical</option>
                <option value="Certification_Requirement">Certification</option>
              </select>
            </div>

            {/* Max Nodes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Nodes</label>
              <select
                value={maxNodes}
                onChange={(e) => setMaxNodes(Number(e.target.value))}
                className="border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="100">100</option>
                <option value="500">500</option>
                <option value="1000">1000</option>
                <option value="2000">2000</option>
              </select>
            </div>

            {/* Include Tests */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="includeTests"
                checked={includeTests}
                onChange={(e) => setIncludeTests(e.target.checked)}
                className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="includeTests" className="text-sm font-medium text-gray-700">
                Include Test Cases
              </label>
            </div>

            {/* Zoom Controls */}
            <div className="flex items-center gap-2 ml-auto">
              <button
                onClick={zoomIn}
                className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-md text-sm font-medium"
              >
                Zoom In
              </button>
              <button
                onClick={zoomOut}
                className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-md text-sm font-medium"
              >
                Zoom Out
              </button>
              <button
                onClick={fit}
                className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-md text-sm font-medium"
              >
                Fit
              </button>
              <button
                onClick={center}
                className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-md text-sm font-medium"
              >
                Center
              </button>
            </div>
          </div>
        </div>

        {/* Stats */}
        {graphData && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="text-sm text-gray-600">Total Nodes</div>
              <div className="text-2xl font-bold text-gray-900">{graphData.total_nodes}</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="text-sm text-gray-600">Total Edges</div>
              <div className="text-2xl font-bold text-gray-900">{graphData.total_edges}</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="text-sm text-gray-600">Connectivity</div>
              <div className="text-2xl font-bold text-gray-900">
                {graphData.total_nodes > 0
                  ? ((graphData.total_edges / graphData.total_nodes) * 100).toFixed(1)
                  : 0}%
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="text-sm text-gray-600">Max Displayed</div>
              <div className="text-2xl font-bold text-gray-900">{maxNodes}</div>
            </div>
          </div>
        )}

        {/* Graph Container */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div
            ref={containerRef}
            className="w-full"
            style={{ height: '700px' }}
          />
        </div>

        {/* Legend */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Legend</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-blue-500"></div>
              <span className="text-sm text-gray-700">AHLR</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-green-500"></div>
              <span className="text-sm text-gray-700">System</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-amber-500"></div>
              <span className="text-sm text-gray-700">Technical</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-red-500"></div>
              <span className="text-sm text-gray-700">Certification</span>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
