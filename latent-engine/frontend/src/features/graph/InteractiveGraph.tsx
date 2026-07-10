import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';

export default function InteractiveGraph() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [graphMode, setGraphMode] = useState<'knowledge' | 'reasoning' | 'execution'>('knowledge');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    let cy: cytoscape.Core;

    const fetchGraph = async () => {
      setLoading(true);
      try {
        const res = await fetch(`http://localhost:8000/api/v1/graph/latest`);
        const data = await res.json();

        const elements = [
          ...data.nodes.map((n: any) => ({ data: { id: n.id, label: n.id, type: n.type } })),
          ...data.edges.map((e: any) => ({ data: { id: `${e.source}-${e.target}`, source: e.source, target: e.target, label: e.type } }))
        ];

        cy = cytoscape({
          container: containerRef.current,
          elements: elements,
          style: [
            {
              selector: 'node',
              style: {
                'background-color': '#3b82f6',
                'label': 'data(label)',
                'color': '#e2e8f0',
                'text-valign': 'center',
                'text-halign': 'center',
                'font-size': '10px'
              }
            },
            {
              selector: 'edge',
              style: {
                'width': 1.5,
                'line-color': '#475569',
                'target-arrow-color': '#475569',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'label': 'data(label)',
                'font-size': '8px',
                'color': '#94a3b8',
                'text-background-opacity': 1,
                'text-background-color': '#0b0f19'
              }
            }
          ],
          layout: {
            name: 'cose',
            padding: 30
          }
        });

      } catch (e) {
        console.error("Failed to load graph", e);
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();

    return () => {
      if (cy) cy.destroy();
    };
  }, [graphMode]);

  return (
    <div className="flex flex-col h-full w-full">
      <div className="flex gap-2 mb-2 items-center">
        <select 
          value={graphMode} 
          onChange={e => setGraphMode(e.target.value as any)}
          className="text-sm bg-black bg-opacity-20 border-none px-2 py-1"
        >
          <option value="knowledge">Knowledge Graph</option>
          <option value="reasoning">Reasoning Graph</option>
          <option value="execution">Execution Graph</option>
        </select>
        {loading && <span className="text-xs text-accent-blue ml-2">Loading topology...</span>}
        <span className="text-sm text-muted flex items-center ml-auto">
          Cytoscape.js Powered
        </span>
      </div>
      <div 
        ref={containerRef} 
        style={{ flex: 1, background: 'rgba(0,0,0,0.3)', borderRadius: '4px' }} 
      />
    </div>
  );
}
