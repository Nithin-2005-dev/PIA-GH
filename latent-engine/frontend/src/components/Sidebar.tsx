import {
  GitBranch, Play, Box, Gauge, FileSearch, Network, BrainCircuit,
  FlaskConical, Scale, BarChart3, ShieldCheck, RotateCcw, Cpu, BookOpen,
  FolderKanban, Activity, Settings, ChevronLeft, ChevronRight
} from 'lucide-react';

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const NAV_SECTIONS: NavSection[] = [
  {
    title: 'Data',
    items: [
      { id: 'repositories', label: 'Repositories', icon: <GitBranch size={16} /> },
      { id: 'executions', label: 'Executions', icon: <Play size={16} /> },
      { id: 'objects', label: 'Objects', icon: <Box size={16} /> },
      { id: 'measurements', label: 'Measurements', icon: <Gauge size={16} /> },
      { id: 'evidence', label: 'Evidence', icon: <FileSearch size={16} /> },
    ],
  },
  {
    title: 'Intelligence',
    items: [
      { id: 'knowledge-graph', label: 'Knowledge Graph', icon: <Network size={16} /> },
      { id: 'reasoning-graph', label: 'Reasoning Graph', icon: <BrainCircuit size={16} /> },
      { id: 'simulation', label: 'Simulation', icon: <FlaskConical size={16} /> },
      { id: 'decisions', label: 'Decisions', icon: <Scale size={16} /> },
    ],
  },
  {
    title: 'Validation',
    items: [
      { id: 'benchmarks', label: 'Benchmarks', icon: <BarChart3 size={16} /> },
      { id: 'validation', label: 'Validation', icon: <ShieldCheck size={16} /> },
      { id: 'replay', label: 'Replay', icon: <RotateCcw size={16} /> },
    ],
  },
  {
    title: 'System',
    items: [
      { id: 'algorithms', label: 'Algorithms', icon: <Cpu size={16} /> },
      { id: 'rules', label: 'Rules', icon: <BookOpen size={16} />, badge: '14' },
      { id: 'datasets', label: 'Datasets', icon: <FolderKanban size={16} /> },
      { id: 'runtime', label: 'Runtime', icon: <Activity size={16} /> },
      { id: 'settings', label: 'Settings', icon: <Settings size={16} /> },
    ],
  },
];

interface SidebarProps {
  activePage: string;
  onNavigate: (pageId: string) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export default function Sidebar({ activePage, onNavigate, collapsed, onToggleCollapse }: SidebarProps) {
  return (
    <nav className="ide-sidebar">
      <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden' }}>
        {NAV_SECTIONS.map((section) => (
          <div key={section.title} className="sidebar-section">
            {!collapsed && (
              <div className="sidebar-section__title">{section.title}</div>
            )}
            {section.items.map((item) => (
              <div
                key={item.id}
                className={`sidebar-item ${activePage === item.id ? 'active' : ''}`}
                onClick={() => onNavigate(item.id)}
                title={collapsed ? item.label : undefined}
              >
                {item.icon}
                {!collapsed && (
                  <>
                    <span className="truncate">{item.label}</span>
                    {item.badge && (
                      <span className="sidebar-item__badge">{item.badge}</span>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Collapse toggle */}
      <div
        style={{
          padding: '8px 16px',
          borderTop: '1px solid var(--panel-border)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-end',
          color: 'var(--text-tertiary)',
          transition: 'color 150ms',
        }}
        onClick={onToggleCollapse}
        title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </div>
    </nav>
  );
}

export { NAV_SECTIONS };
export type { NavItem, NavSection };
