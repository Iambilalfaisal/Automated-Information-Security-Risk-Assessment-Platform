/**
 * RiskDashboard.jsx — Summary cards, charts, heat map, and risk register table.
 */
import { useMemo, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { criticalityColor } from '../lib/api';

export default function RiskDashboard({ results }) {
  const register = results?.risk_register || [];
  const summary = results?.summary || {};
  const [filter, setFilter] = useState('');
  const [sortKey, setSortKey] = useState('risk_impact_rating');

  const chartData = useMemo(
    () =>
      register.reduce((acc, r) => {
        const existing = acc.find((x) => x.name === r.asset_name);
        if (existing) {
          existing.impact = Math.max(existing.impact, r.risk_impact_rating);
        } else {
          acc.push({ name: r.asset_name?.slice(0, 12), impact: r.risk_impact_rating });
        }
        return acc;
      }, []),
    [register]
  );

  const filtered = useMemo(() => {
    let rows = [...register];
    if (filter) {
      rows = rows.filter(
        (r) =>
          r.asset_name?.toLowerCase().includes(filter.toLowerCase()) ||
          r.threat_name?.toLowerCase().includes(filter.toLowerCase())
      );
    }
    rows.sort((a, b) => (b[sortKey] ?? 0) - (a[sortKey] ?? 0));
    return rows;
  }, [register, filter, sortKey]);

  const heatLevels = [1, 2, 3, 4, 5];
  const heatMap = useMemo(() => {
    const grid = {};
    register.forEach((r) => {
      const l = Math.min(5, Math.max(1, Math.ceil(r.probability * 5)));
      const i = Math.min(5, Math.max(1, Math.ceil(r.risk_impact_rating / 50)));
      const key = `${l}-${i}`;
      grid[key] = (grid[key] || 0) + 1;
    });
    return grid;
  }, [register]);

  const heatColor = (count) => {
    if (!count) return 'bg-slate-100';
    if (count >= 3) return 'bg-red-500 text-white';
    if (count >= 2) return 'bg-orange-400 text-white';
    return 'bg-yellow-300';
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-brand-900">Risk Dashboard</h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Assets', value: summary.total_assets ?? 0 },
          { label: 'Total Threats', value: summary.total_threats ?? 0 },
          {
            label: 'Highest Risk',
            value: summary.highest_risk?.threat_name?.slice(0, 20) || '—',
          },
          { label: 'Total ALE', value: `$${(summary.total_ale ?? 0).toLocaleString()}` },
        ].map((c) => (
          <div key={c.label} className="bg-white rounded-lg shadow p-4">
            <p className="text-xs text-slate-500 uppercase">{c.label}</p>
            <p className="text-xl font-bold mt-1">{c.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow p-4 h-72">
        <h3 className="font-semibold mb-2">Risk Impact Rating by Asset</h3>
        <ResponsiveContainer width="100%" height="90%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="impact" fill="#2563eb" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-xl shadow p-4">
        <h3 className="font-semibold mb-3">Likelihood vs Impact Heat Map</h3>
        <div className="overflow-x-auto">
          <table className="text-xs mx-auto">
            <thead>
              <tr>
                <th className="p-1"></th>
                {heatLevels.map((i) => (
                  <th key={i} className="p-2">
                    Impact {i}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {heatLevels.map((l) => (
                <tr key={l}>
                  <td className="p-2 font-medium">Likelihood {l}</td>
                  {heatLevels.map((i) => {
                    const count = heatMap[`${l}-${i}`] || 0;
                    return (
                      <td key={i} className={`p-4 text-center border ${heatColor(count)}`}>
                        {count || ''}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow p-4 overflow-x-auto">
        <div className="flex flex-wrap gap-2 mb-3">
          <input
            placeholder="Filter…"
            className="border rounded px-2 py-1 text-sm"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <select
            className="border rounded px-2 py-1 text-sm"
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value)}
          >
            <option value="risk_impact_rating">Impact Rating</option>
            <option value="ale">ALE</option>
            <option value="risk_score">Risk Score</option>
          </select>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left bg-slate-50">
              <th className="p-2">Asset</th>
              <th>Threat</th>
              <th>SLE</th>
              <th>ALE</th>
              <th>R</th>
              <th>Criticality</th>
              <th>CBA</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r, idx) => (
              <tr key={idx} className="border-b hover:bg-slate-50">
                <td className="p-2">{r.asset_name}</td>
                <td>{r.threat_name}</td>
                <td>${r.sle?.toLocaleString()}</td>
                <td>${r.ale?.toLocaleString()}</td>
                <td>{r.risk_score}</td>
                <td>
                  <span className={`px-2 py-0.5 rounded text-xs ${criticalityColor(r.risk_criticality)}`}>
                    {r.risk_criticality}
                  </span>
                </td>
                <td>{r.control_recommended ? '✓ Rec.' : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {results?.llm_recommendations?.recommendations?.length > 0 && (
        <div className="bg-white rounded-xl shadow p-4">
          <h3 className="font-semibold mb-2">
            Control Recommendations ({results.llm_recommendations.source})
          </h3>
          <ul className="space-y-3 text-sm">
            {results.llm_recommendations.recommendations.map((rec, i) => (
              <li key={i} className="border-l-4 border-brand-600 pl-3">
                <strong>
                  {rec.control_id} — {rec.control_name}
                </strong>
                <p className="text-slate-600 mt-1">{rec.plain_english_explanation}</p>
                <p className="text-xs text-slate-400 mt-1">
                  Priority {rec.implementation_priority} · {rec.estimated_cost_range}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
