/**
 * ResultsPage.jsx — Assessment results, dashboard, compliance, and reports.
 */
import { useEffect, useState } from 'react';
import RiskDashboard from '../components/RiskDashboard';
import ComplianceChecklist from '../components/ComplianceChecklist';
import ReportDownload from '../components/ReportDownload';
import { api } from '../lib/api';

export default function ResultsPage() {
  const [results, setResults] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    api
      .getResults()
      .then(setResults)
      .catch((e) => setError(e.message));
    api
      .getNotifications()
      .then(setNotifications)
      .catch(() => {});
  }, []);

  if (error) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <p className="text-amber-800">{error}</p>
        <p className="text-sm mt-2">Complete an assessment on the Assessment page first.</p>
      </div>
    );
  }

  if (!results) {
    return <p className="text-slate-500">Loading results…</p>;
  }

  return (
    <div className="space-y-8">
      {notifications.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="font-semibold text-red-800">Alerts</h3>
          <ul className="text-sm mt-2 space-y-1">
            {notifications.slice(0, 5).map((n) => (
              <li key={n.id}>{n.message}</li>
            ))}
          </ul>
        </div>
      )}
      <RiskDashboard results={results} />
      <ReportDownload />
      <ComplianceChecklist />
    </div>
  );
}
