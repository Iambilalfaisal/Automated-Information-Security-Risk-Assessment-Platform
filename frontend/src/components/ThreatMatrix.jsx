/**
 * ThreatMatrix.jsx — Add threats per asset with NIST-aligned inputs.
 */
import { useEffect, useState } from 'react';
import { api } from '../lib/api';

const CATEGORIES = [
  'Adversarial',
  'Natural',
  'Structural',
  'Environmental',
  'Accidental',
  'Technical Failure',
];

export default function ThreatMatrix({ assets = [], onSaved }) {
  const [threats, setThreats] = useState([]);
  const [form, setForm] = useState({
    asset_id: '',
    name: '',
    category: 'Adversarial',
    probability: 0.5,
    vulnerability_score: 3,
    mitigation_effectiveness: 0.3,
    aro: 1.0,
    exposure_factor: 0.3,
    uncertainty: 0.1,
    threat_level: 3,
  });
  const [error, setError] = useState('');

  const load = async () => {
    const data = await api.getThreats();
    setThreats(data);
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    if (assets.length && !form.asset_id) {
      setForm((f) => ({ ...f, asset_id: String(assets[0].id) }));
    }
  }, [assets]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.createThreat({
        ...form,
        asset_id: parseInt(form.asset_id, 10),
        probability: parseFloat(form.probability),
        vulnerability_score: parseInt(form.vulnerability_score, 10),
        mitigation_effectiveness: parseFloat(form.mitigation_effectiveness),
        aro: parseFloat(form.aro),
        exposure_factor: parseFloat(form.exposure_factor) / (form.exposure_factor > 1 ? 100 : 1),
        uncertainty: parseFloat(form.uncertainty),
        threat_level: parseInt(form.threat_level, 10),
      });
      setForm((f) => ({ ...f, name: '' }));
      await load();
      onSaved?.();
    } catch (err) {
      setError(err.message);
    }
  };

  const Slider = ({ label, min, max, step, value, onChange, display }) => (
    <div>
      <label className="text-sm font-medium">
        {label}: {display ?? value}
      </label>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full"
      />
    </div>
  );

  return (
    <section className="bg-white rounded-xl shadow p-6">
      <h2 className="text-xl font-bold text-brand-900 mb-4">2. Threat Profile</h2>
      {assets.length === 0 ? (
        <p className="text-slate-500 text-sm">Add at least one asset first.</p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Asset *</label>
              <select
                required
                className="w-full border rounded px-3 py-2 mt-1"
                value={form.asset_id}
                onChange={(e) => setForm({ ...form, asset_id: e.target.value })}
              >
                {assets.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">Threat Name *</label>
              <input
                required
                className="w-full border rounded px-3 py-2 mt-1"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm font-medium">NIST Category</label>
              <select
                className="w-full border rounded px-3 py-2 mt-1"
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
              >
                {CATEGORIES.map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">Exposure Factor (%)</label>
              <input
                type="number"
                min="0"
                max="100"
                className="w-full border rounded px-3 py-2 mt-1"
                value={Math.round(form.exposure_factor * 100)}
                onChange={(e) =>
                  setForm({ ...form, exposure_factor: parseFloat(e.target.value) / 100 })
                }
              />
            </div>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <Slider
              label="Probability (P)"
              min={0}
              max={1}
              step={0.05}
              value={form.probability}
              onChange={(v) => setForm({ ...form, probability: v })}
            />
            <Slider
              label="Vulnerability (V)"
              min={1}
              max={5}
              step={1}
              value={form.vulnerability_score}
              onChange={(v) => setForm({ ...form, vulnerability_score: v })}
            />
            <Slider
              label="Mitigation (M)"
              min={0}
              max={1}
              step={0.05}
              value={form.mitigation_effectiveness}
              onChange={(v) => setForm({ ...form, mitigation_effectiveness: v })}
            />
            <Slider
              label="ARO (incidents/year)"
              min={0}
              max={5}
              step={0.1}
              value={form.aro}
              onChange={(v) => setForm({ ...form, aro: v })}
            />
          </div>
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button type="submit" className="bg-brand-600 text-white px-4 py-2 rounded-lg">
            Add Threat
          </button>
        </form>
      )}
      {threats.length > 0 && (
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left">
                <th className="py-2">Threat</th>
                <th>Asset ID</th>
                <th>P</th>
                <th>V</th>
                <th>EF</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {threats.map((t) => (
                <tr key={t.id} className="border-b">
                  <td className="py-2">{t.name}</td>
                  <td>{t.asset_id}</td>
                  <td>{t.probability}</td>
                  <td>{t.vulnerability_score}</td>
                  <td>{(t.exposure_factor * 100).toFixed(0)}%</td>
                  <td>
                    <button
                      type="button"
                      className="text-red-600 text-xs"
                      onClick={async () => {
                        await api.deleteThreat(t.id);
                        load();
                      }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
