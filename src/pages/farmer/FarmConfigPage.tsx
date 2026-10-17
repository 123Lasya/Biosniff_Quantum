import React, { useState, useEffect } from 'react';
import {
  Save,
  CheckCircle2,
  Sliders,
  LandPlot,
  Smartphone,
  RefreshCw,
  AlertCircle,
  MapPin,
  Compass,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { farmService } from '../../services/farmService';
import { FarmOut } from '../../types/api';

export const FarmConfigPage: React.FC = () => {
  const { primaryFarmId } = useAuth();
  const farmId = primaryFarmId || 1;

  const [farm, setFarm] = useState<FarmOut | null>(null);
  const [farmName, setFarmName] = useState('');
  const [crop, setCrop] = useState('');
  const [cropVariety, setCropVariety] = useState('');
  const [area, setArea] = useState('');
  const [address, setAddress] = useState('');
  const [latitude, setLatitude] = useState<number>(19.8321);
  const [longitude, setLongitude] = useState<number>(74.6521);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFarm = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await farmService.getFarm(farmId);
      setFarm(data);
      setFarmName(data.farm_name || '');
      setCrop(data.crop || '');
      setCropVariety(data.crop_variety || '');
      setArea(data.area ? data.area.toString() : '5.0');
      setAddress(data.address || '');
      if (data.latitude) setLatitude(data.latitude);
      if (data.longitude) setLongitude(data.longitude);
    } catch (err: any) {
      console.error('Failed to load farm configuration:', err);
      setError(err?.message || 'Failed to fetch farm settings from server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFarm();
  }, [farmId]);

  const handleDetectLocation = () => {
    if (!navigator.geolocation) {
      setError('Browser geolocation is not supported by your device.');
      return;
    }
    setIsGettingLocation(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLatitude(parseFloat(position.coords.latitude.toFixed(6)));
        setLongitude(parseFloat(position.coords.longitude.toFixed(6)));
        setIsGettingLocation(false);
      },
      (err) => {
        console.warn('Geolocation error:', err);
        setError('Could not retrieve current location. Please enter coordinates manually.');
        setIsGettingLocation(false);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const updated = await farmService.updateFarm(farmId, {
        farm_name: farmName,
        crop,
        crop_variety: cropVariety,
        area: parseFloat(area) || 5.0,
        address,
        latitude,
        longitude,
      });
      setFarm(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      console.error('Failed to update farm config:', err);
      setError(err?.message || 'Failed to save farm settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-white border border-emerald-200 shadow-xs text-emerald-900 font-semibold text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
          <span>Loading Farm Configuration...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#0F2D1F] font-serif-display">
            Farm Settings & Sensor Calibration
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Configure authoritative farm location coordinates, parcel metadata, and alert thresholds.
          </p>
        </div>

        {saved && (
          <span className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold animate-fadeIn">
            <CheckCircle2 className="w-4 h-4" />
            <span>Settings Saved</span>
          </span>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-red-50 border border-red-200 text-xs font-semibold text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Section 1: Plot Information */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-gray-200 shadow-xs space-y-5">
          <h2 className="text-base font-bold text-gray-900 border-b border-gray-100 pb-3 flex items-center gap-2">
            <LandPlot className="w-4 h-4 text-emerald-700" />
            <span>Farm Parcel Details</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1.5">
              <label className="font-semibold text-gray-700">Farm / Plot Name</label>
              <input
                type="text"
                value={farmName}
                onChange={(e) => setFarmName(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-emerald-600 font-medium"
              />
            </div>

            <div className="space-y-1.5">
              <label className="font-semibold text-gray-700">Cultivated Crop</label>
              <input
                type="text"
                value={crop}
                onChange={(e) => setCrop(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-emerald-600 font-medium"
              />
            </div>

            <div className="space-y-1.5">
              <label className="font-semibold text-gray-700">Crop Variety</label>
              <input
                type="text"
                value={cropVariety}
                onChange={(e) => setCropVariety(e.target.value)}
                placeholder="e.g. Basmati 1121"
                className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-emerald-600 font-medium"
              />
            </div>

            <div className="space-y-1.5">
              <label className="font-semibold text-gray-700">Total Acreage (Acres)</label>
              <input
                type="number"
                step="0.1"
                value={area}
                onChange={(e) => setArea(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-emerald-600 font-medium"
              />
            </div>

            <div className="sm:col-span-2 space-y-1.5">
              <label className="font-semibold text-gray-700">Street / Village Address</label>
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-emerald-600 font-medium"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Authoritative Farm Location */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-gray-200 shadow-xs space-y-5">
          <div className="flex items-center justify-between border-b border-gray-100 pb-3">
            <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-emerald-700" />
              <span>Authoritative GPS Coordinates</span>
            </h2>

            <button
              type="button"
              onClick={handleDetectLocation}
              disabled={isGettingLocation}
              className="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 disabled:bg-gray-400 text-white rounded-xl font-bold flex items-center gap-1.5 transition text-xs shrink-0"
            >
              {isGettingLocation ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Compass className="w-3.5 h-3.5" />
              )}
              <span>Detect Device GPS</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1.5">
              <label className="font-semibold text-gray-700">Latitude (North)</label>
              <input
                type="number"
                step="0.000001"
                value={latitude}
                onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-emerald-600 font-mono font-medium"
              />
            </div>

            <div className="space-y-1.5">
              <label className="font-semibold text-gray-700">Longitude (East)</label>
              <input
                type="number"
                step="0.000001"
                value={longitude}
                onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-emerald-600 font-mono font-medium"
              />
            </div>
          </div>
        </div>

        {/* Section 3: Sensor Alert Thresholds */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-gray-200 shadow-xs space-y-5">
          <h2 className="text-base font-bold text-gray-900 border-b border-gray-100 pb-3 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-emerald-700" />
            <span>Automated AI Anomaly Thresholds</span>
          </h2>

          <div className="space-y-4 text-xs">
            <div className="flex items-center justify-between p-3.5 bg-gray-50 rounded-2xl border border-gray-100">
              <div>
                <strong className="text-gray-900 block font-semibold">Gas Resistance Alarm Sensitivity</strong>
                <p className="text-gray-500 text-[11px]">Triggers SMS warning when volatile resistance profile departs from baseline.</p>
              </div>
              <select className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-xs font-semibold text-gray-800">
                <option>High Sensitivity (&gt;15% deviation)</option>
                <option>Standard (&gt;25% deviation)</option>
                <option>Conservative (&gt;35% deviation)</option>
              </select>
            </div>

            <div className="flex items-center justify-between p-3.5 bg-gray-50 rounded-2xl border border-gray-100">
              <div>
                <strong className="text-gray-900 block font-semibold">Microclimate Saturation Alarm</strong>
                <p className="text-gray-500 text-[11px]">Alerts if relative humidity exceeds threshold for more than 3 hours.</p>
              </div>
              <span className="font-bold text-gray-900 text-sm">85% RH</span>
            </div>
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
                <span>Saving...</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>Save All Configurations</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
