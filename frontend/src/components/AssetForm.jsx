/**
 * AssetForm.jsx — Multi-step asset entry form with CVE display after submit.
 */
import { useState } from 'react';
import { api, severityColor } from '../lib/api';

const ASSET_TYPES = ['Hardware', 'Software', 'Data', 'People', 'Process'];

export default function AssetForm({ onSaved }) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    name: '',
    asset_type: 'Software',
    value_usd: '',
    description: '',
    software: '',
  });
  const [cves, setCves] = useState([]);
  const [assets, setAssets] = useState([]);
  const [error, setError] = useState('');

  const loadAssets = async () => {
    const data = await api.getAssets();
    setAssets(data);
    onSaved?.();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const created = await api.createAsset({
        ...form,
        value_usd: parseFloat(form.value_usd),
      });
      const cveList = await api.getAssetCves(created.id);
      setCves(cveList);
      setStep(2);
      await loadAssets();
      setForm({ name: '', asset_type: 'Software', value_usd: '', description: '', software: '' });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <section className="bg-white rounded-xl shadow p-6">
      <h2 className="text-xl font-bold text-brand-900 mb-4">1. Asset Inventory</h2>
      <div className="flex gap-2 mb-4 text-sm">
        <span className={step === 1 ? 'font-bold text-brand-600' : 'text-slate-400'}>Step 1: Details</span>
        <span>→</span>
        <span className={step === 2 ? 'font-bold text-brand-600' : 'text-slate-400'}>Step 2: CVE Review</span>
      </div>
      {step === 1 && (
        <form onSubmit={handleSubmit} className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium">Asset Name *</label>
            <input
              required
              className="w-full border rounded px-3 py-2 mt-1"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm font-medium">Type *</label>
            <select
              className="w-full border rounded px-3 py-2 mt-1"
              value={form.asset_type}
              onChange={(e) => setForm({ ...form, asset_type: e.target.value })}
            >
              {ASSET_TYPES.map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">Value (USD) *</label>
            <input
              required
              type="number"
              min="0"
              className="w-full border rounded px-3 py-2 mt-1"
              value={form.value_usd}
              onChange={(e) => setForm({ ...form, value_usd: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm font-medium">Software / OS (for CVE lookup)</label>
            <input
              className="w-full border rounded px-3 py-2 mt-1"
              placeholder="e.g. Windows Server, Apache, Linux"
              value={form.software}
              onChange={(e) => setForm({ ...form, software: e.target.value })}
            />
          </div>
          <div className="md:col-span-2">
            <label className="text-sm font-medium">Description</label>
            <textarea
              className="w-full border rounded px-3 py-2 mt-1"
              rows={2}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
          {error && <p className="text-red-600 text-sm md:col-span-2">{error}</p>}
          <button type="submit" className="bg-brand-600 text-white px-4 py-2 rounded-lg md:col-span-2 w-fit">
            Add Asset &amp; Fetch CVEs
          </button>
        </form>
      )}
      {step === 2 && (
        <div>
          <h3 className="font-semibold mb-3">CVEs for last added asset</h3>
          {cves.length === 0 ? (
            <p className="text-slate-500 text-sm">No CVEs returned.</p>
          ) : (
            <ul className="space-y-2">
              {cves.map((c) => (
                <li key={c.cve_id} className="border rounded p-3 flex justify-between gap-2">
                  <div>
                    <a href={c.link} target="_blank" rel="noreferrer" className="font-mono text-brand-600">
                      {c.cve_id}
                    </a>
                    <p className="text-sm text-slate-600 mt-1">{c.description?.slice(0, 120)}…</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs h-fit ${severityColor(c.severity)}`}>
                    {c.severity} ({c.cvss_score})
                  </span>
                </li>
              ))}
            </ul>
          )}
          <button type="button" onClick={() => setStep(1)} className="mt-4 text-brand-600 text-sm underline">
            Add another asset
          </button>
        </div>
      )}
      {assets.length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold text-sm mb-2">Registered Assets ({assets.length})</h3>
          <ul className="text-sm space-y-1">
            {assets.map((a) => (
              <li key={a.id} className="flex justify-between border-b py-1">
                <span>
                  {a.name} — {a.asset_type} (${Number(a.value_usd).toLocaleString()})
                </span>
                <button
                  type="button"
                  className="text-red-600 text-xs"
                  onClick={async () => {
                    await api.deleteAsset(a.id);
                    loadAssets();
                  }}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
