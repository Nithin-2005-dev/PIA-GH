import React, { useState } from 'react';
import { useWorkspaceStore } from './store/workspaceStore';
import { Database, Layers, Settings, Search, Network, BarChart3, Activity, Clock, Info } from 'lucide-react';
import QueryPlayground from './features/query/QueryPlayground';
import InteractiveGraph from './features/graph/InteractiveGraph';
import TraceTimeline from './features/query/TraceTimeline';
import ExplainabilityView from './features/query/ExplainabilityView';
import RuntimeInspector from './features/runtime/RuntimeInspector';
import BenchmarkCenter from './features/benchmark/BenchmarkCenter';
import ProjectionHealthConsole from './features/runtime/ProjectionHealthConsole';
import ObjectInspectorView from './features/runtime/ObjectInspectorView';

// Basic Plugin Registry Architecture
const PLUGINS = [
  { id: 'inspector', label: 'Object Inspector', icon: <Search size={16}/>, component: <ObjectInspectorView /> },
  { id: 'graph', label: 'Interactive Graph', icon: <Network size={16}/>, component: <InteractiveGraph /> },
  { id: 'benchmark', label: 'Benchmark Center', icon: <BarChart3 size={16}/>, component: <BenchmarkCenter /> }
];

function App() {
  const { workspace, updateWorkspace } = useWorkspaceStore();
  const [activeTab, setActiveTab] = useState(PLUGINS[0].id);

  const activePlugin = PLUGINS.find(p => p.id === activeTab);

  return (
    <div className="ide-container">
      {/* HEADER */}
      <header className="ide-header glass-panel">
        <div className="flex items-center gap-4">
          <Layers size={24} className="text-accent-blue" />
          <h2>PIA Developer Console</h2>
        </div>
        
        {/* Repository Workspace First-Class Object */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-muted bg-black bg-opacity-20 p-2 rounded">
            <Database size={16} />
            <select 
              value={workspace.repository} 
              onChange={e => updateWorkspace({ repository: e.target.value })}
              className="bg-transparent border-none font-bold"
            >
              <option value="facebook/react">facebook/react</option>
              <option value="expressjs/express">expressjs/express</option>
            </select>
            <span className="opacity-50">/</span>
            <select 
              value={workspace.dataset} 
              onChange={e => updateWorkspace({ dataset: e.target.value })}
              className="bg-transparent border-none"
            >
              <option value="v1">v1</option>
              <option value="v2">v2</option>
            </select>
            <span className="opacity-50">/</span>
            <span className="font-mono">{workspace.branch}</span>
            <span className="ml-2 text-xs text-accent-green border border-accent-green px-1 rounded bg-accent-green bg-opacity-10">
              Win: {workspace.commitWindow}
            </span>
          </div>
          <button className="flex items-center gap-2"><Settings size={16} /> Config</button>
        </div>
      </header>

      {/* LEFT SIDEBAR: Pipeline & Query Playground */}
      <aside className="ide-sidebar-left glass-panel p-4 flex-col">
        <h3 className="flex items-center gap-2 mb-4"><Search size={18}/> Query Playground</h3>
        <QueryPlayground />
      </aside>

      {/* MAIN CONTENT: Plugin View */}
      <main className="ide-main glass-panel p-4 flex flex-col">
        <div className="flex items-center gap-4 mb-4 border-b pb-2" style={{ borderBottomColor: 'var(--panel-border)' }}>
          {PLUGINS.map(plugin => (
            <button 
              key={plugin.id}
              style={{ 
                background: activeTab === plugin.id ? 'var(--accent-blue)' : 'transparent', 
                color: activeTab === plugin.id ? 'white' : 'var(--text-muted)' 
              }}
              onClick={() => setActiveTab(plugin.id)}
              className="flex items-center gap-2"
            >
              {plugin.icon} {plugin.label}
            </button>
          ))}
        </div>
        <div className="flex-1" style={{ position: 'relative' }}>
           {activePlugin?.component}
        </div>
      </main>

      {/* RIGHT SIDEBAR: Runtime & Health */}
      <aside className="ide-sidebar-right glass-panel p-4 flex-col overflow-y-auto">
        <h3 className="flex items-center gap-2 mb-4"><Activity size={18}/> Runtime Inspector</h3>
        <RuntimeInspector />
        
        <h3 className="flex items-center gap-2 mt-8 mb-4"><Database size={18}/> Projection Health</h3>
        <ProjectionHealthConsole />
      </aside>

      {/* FOOTER LEFT: Trace Timeline */}
      <section className="glass-panel p-4 flex-col overflow-y-auto">
        <h3 className="flex items-center gap-2 mb-4"><Clock size={18}/> Pipeline Timeline</h3>
        <TraceTimeline />
      </section>

      {/* FOOTER RIGHT: Explanation */}
      <section className="glass-panel p-4 flex-col overflow-y-auto">
        <h3 className="flex items-center gap-2 mb-4"><Info size={18}/> Explainability</h3>
        <ExplainabilityView />
      </section>
    </div>
  );
}

export default App;
