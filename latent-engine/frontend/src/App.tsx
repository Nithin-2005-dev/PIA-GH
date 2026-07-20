import { useState, useEffect } from 'react';
import { useWorkspaceStore } from './store/workspaceStore';
import { Layers, Search, Database, Bot, Menu } from 'lucide-react';
import Sidebar from './components/Sidebar';
import CommandPalette from './components/CommandPalette';
import ChatAgentSidebar from './components/ChatAgentSidebar';
import { useLiveTelemetry } from './api/useLiveTelemetry';

// Pages
import RepositoriesPage from './pages/RepositoriesPage';
import ExecutionsPage from './pages/ExecutionsPage';
import ObjectsPage from './pages/ObjectsPage';
import MeasurementsPage from './pages/MeasurementsPage';
import EvidencePage from './pages/EvidencePage';
import KnowledgeGraphPage from './pages/KnowledgeGraphPage';
import ReasoningGraphPage from './pages/ReasoningGraphPage';
import SimulationPage from './pages/SimulationPage';
import DecisionsPage from './pages/DecisionsPage';
import BenchmarksPage from './pages/BenchmarksPage';
import ValidationPage from './pages/ValidationPage';
import ReplayPage from './pages/ReplayPage';
import AlgorithmsPage from './pages/AlgorithmsPage';
import RulesPage from './pages/RulesPage';
import DatasetsPage from './pages/DatasetsPage';
import RuntimePage from './pages/RuntimePage';
import SettingsPage from './pages/SettingsPage';

const PAGE_MAP: Record<string, React.ReactNode> = {
  'repositories': <RepositoriesPage />,
  'executions': <ExecutionsPage />,
  'objects': <ObjectsPage />,
  'measurements': <MeasurementsPage />,
  'evidence': <EvidencePage />,
  'knowledge-graph': <KnowledgeGraphPage />,
  'reasoning-graph': <ReasoningGraphPage />,
  'simulation': <SimulationPage />,
  'decisions': <DecisionsPage />,
  'benchmarks': <BenchmarksPage />,
  'validation': <ValidationPage />,
  'replay': <ReplayPage />,
  'algorithms': <AlgorithmsPage />,
  'rules': <RulesPage />,
  'datasets': <DatasetsPage />,
  'runtime': <RuntimePage />,
  'settings': <SettingsPage />,
};

function App() {
  useLiveTelemetry();
  const { workspace } = useWorkspaceStore();
  const [activePage, setActivePage] = useState('repositories');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [isMobileViewport, setIsMobileViewport] = useState(false);
  const [cmdPaletteOpen, setCmdPaletteOpen] = useState(false);
  
  // Chat Agent State
  const [chatOpen, setChatOpen] = useState(false);
  const [chatExpanded, setChatExpanded] = useState(false);

  // Global Ctrl+K handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCmdPaletteOpen(prev => !prev);
      }
      if (e.key === 'Escape') {
        setCmdPaletteOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    const media = window.matchMedia('(max-width: 900px)');
    const syncViewport = () => setIsMobileViewport(media.matches);
    syncViewport();
    media.addEventListener('change', syncViewport);
    return () => media.removeEventListener('change', syncViewport);
  }, []);

  const navigate = (pageId: string) => {
    setActivePage(pageId);
    setMobileSidebarOpen(false);
  };

  return (
    <>
      <div className={`ide-shell ${sidebarCollapsed ? 'sidebar-collapsed' : ''} ${mobileSidebarOpen ? 'mobile-sidebar-open' : ''}`}>
        {/* Header */}
        <header className="ide-header">
          <div className="ide-header__brand">
            <button
              type="button"
              className="mobile-nav-toggle"
              onClick={() => setMobileSidebarOpen(prev => !prev)}
              aria-label="Toggle navigation"
            >
              <Menu size={18} />
            </button>
            <Layers size={20} />
            <span>PIA</span>
          </div>

          <div className="ide-header__center">
            <div className="cmd-trigger" onClick={() => setCmdPaletteOpen(true)}>
              <Search size={14} />
              <span>Search everything...</span>
              <kbd>Ctrl K</kbd>
            </div>
          </div>

          <div className="ide-header__actions">
            <div className="workspace-badge">
              <div className="workspace-badge__dot" />
              <Database size={12} />
              <span>{workspace.repository}</span>
              <span style={{ opacity: 0.4 }}>/</span>
              <span>{workspace.branch}</span>
            </div>
            
            {/* Copilot Toggle */}
            <button 
              onClick={() => setChatOpen(!chatOpen)}
              className={`flex items-center justify-center p-2 rounded-md transition-colors ${chatOpen ? 'bg-blue-600 text-white' : 'hover:bg-slate-800 text-slate-400 hover:text-slate-200'}`}
              title="Toggle Copilot"
            >
              <Bot size={16} />
            </button>
          </div>
        </header>

        {/* Sidebar */}
          <Sidebar
            activePage={activePage}
            onNavigate={navigate}
            collapsed={isMobileViewport ? false : sidebarCollapsed}
            onToggleCollapse={() => setSidebarCollapsed(prev => !prev)}
          />
        {mobileSidebarOpen && (
          <button
            type="button"
            className="mobile-sidebar-backdrop"
            onClick={() => setMobileSidebarOpen(false)}
            aria-label="Close navigation"
          />
        )}

        {/* Main Content & Chat */}
        <div className="app-workspace flex flex-1 overflow-hidden">
          <main className="ide-main flex-1">
            {PAGE_MAP[activePage] || (
              <div className="empty-state" style={{ height: '100%' }}>
                <div className="empty-state__title">Page not found</div>
              </div>
            )}
          </main>
          
          {chatOpen && (
            <ChatAgentSidebar 
              onClose={() => setChatOpen(false)}
              isExpanded={chatExpanded}
              setIsExpanded={setChatExpanded}
            />
          )}
        </div>
      </div>

      {/* Command Palette */}
      <CommandPalette
        isOpen={cmdPaletteOpen}
        onClose={() => setCmdPaletteOpen(false)}
        onNavigate={navigate}
      />
    </>
  );
}

export default App;
