/**
 * App.jsx — Root layout and routing for Risk Assessment Platform.
 */
import { Link, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AssessmentPage from './pages/AssessmentPage';
import ResultsPage from './pages/ResultsPage';

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-brand-900 text-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="text-xl font-bold">
            InfoSec Risk Platform
          </Link>
          <nav className="flex gap-4 text-sm">
            <Link to="/" className="hover:underline">
              Home
            </Link>
            <Link to="/assessment" className="hover:underline">
              Assessment
            </Link>
            <Link to="/results" className="hover:underline">
              Results
            </Link>
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/assessment" element={<AssessmentPage />} />
          <Route path="/results" element={<ResultsPage />} />
        </Routes>
      </main>
      <footer className="text-center text-xs text-slate-500 py-4 border-t">
        UMT InfoSec Spring 2026 — NIST SP 800-30 &amp; AssessITS (Rahman et al., 2024)
      </footer>
    </div>
  );
}
