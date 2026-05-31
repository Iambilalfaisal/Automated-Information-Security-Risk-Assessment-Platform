/**
 * ReportDownload.jsx — Buttons to download Risk Register, CBA, and Compliance PDFs.
 */
import { api } from '../lib/api';

export default function ReportDownload() {
  const buttons = [
    { label: 'Risk Register PDF', type: 'risk-register' },
    { label: 'CBA Report PDF', type: 'cba' },
    { label: 'Compliance Report PDF', type: 'compliance' },
  ];

  return (
    <section className="bg-white rounded-xl shadow p-6">
      <h2 className="text-xl font-bold text-brand-900 mb-4">Download Reports</h2>
      <div className="flex flex-wrap gap-3">
        {buttons.map((b) => (
          <button
            key={b.type}
            type="button"
            onClick={() => api.downloadReport(b.type)}
            className="bg-brand-900 text-white px-4 py-2 rounded-lg text-sm hover:bg-brand-800"
          >
            {b.label}
          </button>
        ))}
      </div>
      <p className="text-xs text-slate-500 mt-3">
        Reports include executive summary, colour-coded risk tables, and IEEE-style references.
      </p>
    </section>
  );
}
