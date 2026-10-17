import React, { useState } from 'react';
import {
  Sliders,
  ShieldCheck,
  Save,
  CheckCircle2,
  Database,
  Radio,
  Bell,
  Cpu,
  RefreshCw,
} from 'lucide-react';

export const AdminSettingsPage: React.FC = () => {
  const [syncInterval, setSyncInterval] = useState('60');
  const [anomalySensitivity, setAnomalySensitivity] = useState('Standard (25% variance)');
  const [lstmConfidenceThreshold, setLstmConfidenceThreshold] = useState('80%');
  const [alertSmsEnabled, setAlertSmsEnabled] = useState(true);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    }, 500);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#0F2D1F] font-serif-display">
            National System & AI Model Configurations
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Configure platform-wide e-nose ingestion parameters, LSTM inference confidence limits, and alert gateways.
          </p>
        </div>

        {saved && (
          <span className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold animate-fadeIn">
            <CheckCircle2 className="w-4 h-4" />
            <span>Settings Saved</span>
          </span>
        )}
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Section 1: Ingestion & Telemetry Parameters */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-gray-200 shadow-xs space-y-5">
          <h2 className="text-base font-bold text-gray-900 border-b border-gray-100 pb-3 flex items-center gap-2">
            <Radio className="w-4 h-4 text-emerald-700" />
            <span>Ingestion & Gateway Parameters</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1.5">
              <label className="font-semibold text-gray-700">Node Sync Interval (Seconds)</label>
              <input
                type="number"
                value={syncInterval}
                onChange={(e) => setSyncInterval(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-emerald-600 font-medium"
              />
            </div>

            <div className="space-y-1.5">
              <label className="font-semibold text-gray-700">Gas Resistance Anomaly Threshold</label>
              <select
                value={anomalySensitivity}
                onChange={(e) => setAnomalySensitivity(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-emerald-600 font-medium"
              >
                <option>High Sensitivity (&gt;15% variance)</option>
                <option>Standard (25% variance)</option>
                <option>Conservative (&gt;35% variance)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Section 2: Machine Learning Inference Configuration */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-gray-200 shadow-xs space-y-5">
          <h2 className="text-base font-bold text-gray-900 border-b border-gray-100 pb-3 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-emerald-700" />
            <span>LSTM Model & Pathogen Classification</span>
          </h2>

          <div className="space-y-4 text-xs">
            <div className="flex items-center justify-between p-3.5 bg-gray-50 rounded-2xl border border-gray-100">
              <div>
                <strong className="text-gray-900 block font-semibold">Active Botanical Model Version</strong>
                <p className="text-gray-500 text-[11px]">PyTorch LSTM v2.4 (best_biosniff_lstm.pkl)</p>
              </div>
              <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 font-bold text-xs">
                Active & Calibrated
              </span>
            </div>

            <div className="flex items-center justify-between p-3.5 bg-gray-50 rounded-2xl border border-gray-100">
              <div>
                <strong className="text-gray-900 block font-semibold">Minimum Confidence Cutoff for Advisory</strong>
                <p className="text-gray-500 text-[11px]">Classifications below this threshold trigger manual verification alerts.</p>
              </div>
              <select
                value={lstmConfidenceThreshold}
                onChange={(e) => setLstmConfidenceThreshold(e.target.value)}
                className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-xs font-semibold text-gray-800"
              >
                <option>75%</option>
                <option>80%</option>
                <option>85%</option>
                <option>90%</option>
              </select>
            </div>
          </div>
        </div>

        {/* Section 3: National Alert Gateways */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-gray-200 shadow-xs space-y-5">
          <h2 className="text-base font-bold text-gray-900 border-b border-gray-100 pb-3 flex items-center gap-2">
            <Bell className="w-4 h-4 text-emerald-700" />
            <span>SMS & Advisory Dispatch Settings</span>
          </h2>

          <div className="flex items-center justify-between p-3.5 bg-gray-50 rounded-2xl border border-gray-100 text-xs">
            <div>
              <strong className="text-gray-900 block font-semibold">Automated Farmer SMS Advisories</strong>
              <p className="text-gray-500 text-[11px]">Dispatches immediate targeted SMS spray guidelines upon disease detection.</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={alertSmsEnabled}
                onChange={(e) => setAlertSmsEnabled(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-hidden rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600" />
            </label>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-3 pt-2">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-3 bg-[#0F3D2E] hover:bg-[#14523E] disabled:bg-gray-400 text-white text-xs font-bold rounded-xl shadow-md transition flex items-center gap-2"
          >
            {saving ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Saving System Settings...</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>Save All System Configurations</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
