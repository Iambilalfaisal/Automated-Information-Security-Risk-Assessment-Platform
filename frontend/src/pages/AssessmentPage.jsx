/**
 * AssessmentPage.jsx — Asset and threat data entry workflow.
 */
import { useEffect, useState } from 'react';
import AssetForm from '../components/AssetForm';
import ThreatMatrix from '../components/ThreatMatrix';
import { api } from '../lib/api';

export default function AssessmentPage() {
  const [assets, setAssets] = useState([]);
  const [orgName, setOrgName] = useState('UMT Organisation');
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState('');

  const refreshAssets = async () => {
    const data = await api.getAssets();
    setAssets(data);
  };

  useEffect(() => {
    refreshAssets().catch(() => {});
  }, []);

  const handleRun = async () => {
    setRunning(true);
    setMessage('');
    try {
      await api.runAssessment(orgName);
      setMessage('Assessment completed successfully. View results.');
    } catch (e) {
      setMessage(e.message);
    } finally {
      setRunning(false);
    }
  };

  const handleSeed = async () => {
    setMessage('');
    try {
      const res = await api.seedDemo();
      await refreshAssets();
      setMessage(`Loaded demo data: ${res.assets} assets and ${res.threats} threats.`);
    } catch (e) {
      setMessage(e.message);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-sm font-medium mb-1">Organisation Name</label>
          <input
            className="border rounded px-3 py-2"
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
          />
        </div>
        <button
          type="button"
          onClick={handleRun}
          disabled={running}
          className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          {running ? 'Running…' : 'Run Assessment'}
        </button>
        <button
          type="button"
          onClick={handleSeed}
          className="bg-slate-200 text-slate-800 px-4 py-2 rounded-lg hover:bg-slate-300"
        >
          Load Demo Data
        </button>
      </div>
      {message && (
        <p
          className={`text-sm ${
            message.includes('success') || message.includes('Loaded')
              ? 'text-green-700'
              : 'text-red-600'
          }`}
        >
          {message}
        </p>
      )}
      <AssetForm onSaved={refreshAssets} />
      <ThreatMatrix assets={assets} onSaved={refreshAssets} />
    </div>
  );
}
