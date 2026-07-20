import { Scale, TrendingUp, AlertTriangle, Shield, Target } from 'lucide-react';

const DECISION_TYPES = [
  { icon: <AlertTriangle size={16} />, label: 'Risk Assessments', desc: 'Single-point-of-failure identification, bus factor warnings', count: 0, color: 'var(--accent-red)' },
  { icon: <Target size={16} />, label: 'Recommendations', desc: 'Ownership rotation, review diversity, documentation priorities', count: 0, color: 'var(--accent-blue)' },
  { icon: <Shield size={16} />, label: 'Interventions', desc: 'Proposed policy changes and their predicted impact', count: 0, color: 'var(--accent-green)' },
  { icon: <TrendingUp size={16} />, label: 'Forecasts', desc: 'Trend predictions for velocity, coverage, and knowledge distribution', count: 0, color: 'var(--accent-yellow)' },
];

export default function DecisionsPage() {
  return (
    <div className="page">
      <div className="page-header">
        <div className="page-header__title">
          <Scale size={24} />
          <div>
            <h1>Decisions</h1>
            <div className="page-header__subtitle">Executive recommendations, risk assessments, and intervention plans</div>
          </div>
        </div>
      </div>

      <div className="stat-row">
        {DECISION_TYPES.map(d => (
          <div key={d.label} className="stat-card">
            <div className="stat-card__label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ color: d.color }}>{d.icon}</span> {d.label}
            </div>
            <div className="stat-card__value" style={{ color: d.color }}>{d.count}</div>
          </div>
        ))}
      </div>

      <div className="card-grid">
        {DECISION_TYPES.map(d => (
          <div key={d.label} className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <div style={{ color: d.color }}>{d.icon}</div>
              <h3 style={{ fontSize: 14, fontWeight: 600 }}>{d.label}</h3>
            </div>
            <p style={{ fontSize: 12, color: 'var(--text-tertiary)', lineHeight: 1.6 }}>{d.desc}</p>
          </div>
        ))}
      </div>

      <div className="empty-state" style={{ marginTop: 24 }}>
        <Scale size={48} />
        <div className="empty-state__title">No decisions generated yet</div>
        <div className="empty-state__desc">Decisions are produced by the executive intelligence layer after pipeline execution on a synced repository.</div>
      </div>
    </div>
  );
}
