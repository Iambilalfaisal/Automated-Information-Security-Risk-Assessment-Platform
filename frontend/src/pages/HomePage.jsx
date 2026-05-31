/**
 * HomePage.jsx — Landing page with project overview and navigation.
 */
import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section className="bg-white rounded-xl shadow p-8">
        <h1 className="text-3xl font-bold text-brand-900 mb-4">
          Automated Information Security Risk Assessment
        </h1>
        <p className="text-slate-600 mb-6">
          Enter your asset inventory and threat profile. The platform calculates SLE, ALE, and
          composite risk scores, generates a prioritised risk register, cost-benefit analysis, and
          NIST SP 800-30 compliance checklist—with CVE intelligence and control recommendations.
        </p>
        <Link
          to="/assessment"
          className="inline-block bg-brand-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-brand-800"
        >
          Start Assessment
        </Link>
      </section>
      <div className="grid md:grid-cols-3 gap-4">
        {[
          { title: 'Quantitative Risk', desc: 'SLE, ALE, R = P×V−M+U per NIST SP 800-30' },
          { title: 'CVE Intelligence', desc: 'NVD integration with severity colour coding' },
          { title: 'PDF Reports', desc: 'Risk register, CBA, and compliance exports' },
        ].map((f) => (
          <div key={f.title} className="bg-white rounded-lg shadow p-5">
            <h3 className="font-semibold text-brand-800">{f.title}</h3>
            <p className="text-sm text-slate-600 mt-2">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
