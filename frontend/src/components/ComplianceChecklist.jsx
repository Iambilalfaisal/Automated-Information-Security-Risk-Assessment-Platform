/**
 * ComplianceChecklist.jsx — NIST SP 800-30 checklist with score and gap analysis.
 */
import { useEffect, useState } from 'react';
import { api } from '../lib/api';

const STATUSES = ['implemented', 'partial', 'not_implemented'];

export default function ComplianceChecklist() {
  const [data, setData] = useState({ controls: [], score_percent: 0, gaps: [] });
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const d = await api.getCompliance();
      setData(d);
    } catch {
      setData({ controls: [], score_percent: 0, gaps: [] });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const updateStatus = async (control, status) => {
    await api.updateCompliance({
      control_id: control.control_id,
      control_name: control.control_name,
      status,
      notes: control.notes || '',
    });
    load();
  };

  if (loading) return <p className="text-slate-500">Loading compliance…</p>;

  return (
    <section className="bg-white rounded-xl shadow p-6">
      <h2 className="text-xl font-bold text-brand-900 mb-2">NIST SP 800-30 Compliance</h2>
      <div className="flex items-center gap-4 mb-4">
        <div className="text-3xl font-bold text-brand-600">{data.score_percent}%</div>
        <div className="flex-1 h-3 bg-slate-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-brand-600 transition-all"
            style={{ width: `${data.score_percent}%` }}
          />
        </div>
      </div>
      <p className="text-sm text-slate-600 mb-4">
        Gap analysis: {data.gaps?.length ?? 0} control(s) not fully implemented.
      </p>
      <ul className="space-y-2 max-h-96 overflow-y-auto">
        {data.controls.map((c) => (
          <li key={c.control_id} className="flex flex-wrap items-center gap-2 border-b py-2 text-sm">
            <span className="font-mono w-16">{c.control_id}</span>
            <span className="flex-1 min-w-[200px]">{c.control_name}</span>
            <select
              className="border rounded px-2 py-1 text-xs"
              value={c.status || 'not_implemented'}
              onChange={(e) => updateStatus(c, e.target.value)}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s.replace('_', ' ')}
                </option>
              ))}
            </select>
          </li>
        ))}
      </ul>
    </section>
  );
}
