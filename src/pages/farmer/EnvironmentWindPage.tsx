import React, { useState, useEffect } from 'react';
import {
  Wind,
  Compass,
  Thermometer,
  Droplets,
  CloudSun,
  ShieldCheck,
  CheckCircle2,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { environmentService } from '../../services/environmentService';
import { EnvironmentCurrentResponse } from '../../types/api';

export const EnvironmentWindPage: React.FC = () => {
  const { primaryFarmId } = useAuth();
  const farmId = primaryFarmId || 1;

  const [env, setEnv] = useState<EnvironmentCurrentResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEnv = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await environmentService.getFarmEnvironment(farmId);
      setEnv(data);
    } catch (err: any) {
      console.error('Failed to load environment telemetry:', err);
      setError(err?.message || 'Failed to connect to microclimate sensor service');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEnv();
  }, [farmId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-white border border-emerald-200 shadow-xs text-emerald-900 font-semibold text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
          <span>Loading Environment & Wind Telemetry...</span>
        </div>
      </div>
    );
  }

  if (error || !env) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="bg-white p-6 rounded-3xl border border-red-200 shadow-xs text-center space-y-3 max-w-md">
          <AlertCircle className="w-8 h-8 text-red-600 mx-auto" />
          <h3 className="font-bold text-gray-900 text-base">Environmental Sensor Error</h3>
          <p className="text-xs text-red-700">{error || 'No environment telemetry returned'}</p>
          <button
            onClick={fetchEnv}
            className="px-4 py-2 bg-[#0F3D2E] text-white text-xs font-bold rounded-xl"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const windAngle = env.wind_angle || 48;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#0F2D1F] font-serif-display">
            Environment & Wind Telemetry
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Ultrasonic anemometer dynamics, canopy microclimate, and spatial odor dispersion modeling.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-100 text-emerald-900 text-xs font-bold border border-emerald-300">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
            <span>Anemometer Active • {env.wind_direction}</span>
          </span>
        </div>
      </div>

      {/* Field Environmental Microclimate KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-[11px] font-bold uppercase tracking-wider">Canopy Temp</span>
            <Thermometer className="w-4 h-4 text-emerald-600" />
          </div>
          <strong className="text-2xl font-bold text-gray-900 block">{env.temperature} °C</strong>
          <span className="text-xs text-emerald-700 font-medium">Optimal vegetative range</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-[11px] font-bold uppercase tracking-wider">Relative Humidity</span>
            <Droplets className="w-4 h-4 text-blue-600" />
          </div>
          <strong className="text-2xl font-bold text-gray-900 block">{env.humidity} %</strong>
          <span className="text-xs text-blue-700 font-medium">Moist sub-tropical condition</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-[11px] font-bold uppercase tracking-wider">Barometric Pressure</span>
            <CloudSun className="w-4 h-4 text-amber-600" />
          </div>
          <strong className="text-2xl font-bold text-gray-900 block">{env.pressure} hPa</strong>
          <span className="text-xs text-gray-500">Stable atmospheric front</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-[11px] font-bold uppercase tracking-wider">Wind Velocity</span>
            <Wind className="w-4 h-4 text-teal-600" />
          </div>
          <strong className="text-2xl font-bold text-teal-900 block">{env.wind_speed} m/s</strong>
          <span className="text-xs text-teal-700 font-medium">{env.wind_direction}</span>
        </div>
      </div>

      {/* Wind Compass & Dispersion Dynamics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Compass Rose & Vector */}
        <div className="lg:col-span-6 bg-white p-6 rounded-3xl border border-gray-200 shadow-xs flex flex-col justify-between items-center text-center space-y-6">
          <div className="w-full text-left">
            <h3 className="text-base font-bold text-gray-900">Atmospheric Wind Compass</h3>
            <p className="text-xs text-gray-500">Real-time ultrasonic azimuth vector.</p>
          </div>

          {/* Compass Circle */}
          <div className="relative w-56 h-56 rounded-full border-4 border-emerald-100 bg-[#F8FAF8] flex items-center justify-center shadow-inner">
            {/* Cardinal marks */}
            <span className="absolute top-2 font-bold text-xs text-emerald-900">N</span>
            <span className="absolute right-3 font-bold text-xs text-gray-500">E</span>
            <span className="absolute bottom-2 font-bold text-xs text-gray-500">S</span>
            <span className="absolute left-3 font-bold text-xs text-gray-500">W</span>
            
            <span className="absolute top-8 right-8 font-semibold text-[10px] text-emerald-700">NE (45°)</span>
            <span className="absolute bottom-8 right-8 font-semibold text-[10px] text-gray-400">SE</span>
            <span className="absolute bottom-8 left-8 font-semibold text-[10px] text-gray-400">SW</span>
            <span className="absolute top-8 left-8 font-semibold text-[10px] text-gray-400">NW</span>

            {/* Rotating Arrow needle */}
            <div
              className="relative w-full h-full flex items-center justify-center transition-transform duration-700"
              style={{ transform: `rotate(${windAngle}deg)` }}
            >
              <div className="w-1.5 h-24 bg-gradient-to-t from-transparent via-emerald-600 to-red-500 rounded-full relative">
                {/* Arrowhead */}
                <div className="absolute -top-2 -left-1.5 w-0 h-0 border-x-5 border-x-transparent border-b-8 border-b-red-600" />
              </div>
              <div className="absolute w-4 h-4 rounded-full bg-gray-900 border-2 border-white shadow-md" />
            </div>
          </div>

          {/* Live readings block */}
          <div className="w-full grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-emerald-50/80 rounded-xl border border-emerald-100 text-left">
              <span className="text-gray-500 text-[11px] block">Wind Velocity</span>
              <strong className="text-xl font-bold text-emerald-900">{env.wind_speed} m/s</strong>
              <span className="text-[10px] text-emerald-700 block mt-0.5">Light breeze ({(env.wind_speed * 3.6).toFixed(1)} km/h)</span>
            </div>
            <div className="p-3 bg-gray-50 rounded-xl border border-gray-100 text-left">
              <span className="text-gray-500 text-[11px] block">Direction Azimuth</span>
              <strong className="text-xl font-bold text-gray-900">{env.wind_direction}</strong>
              <span className="text-[10px] text-gray-500 block mt-0.5">Stable prevailing vector</span>
            </div>
          </div>
        </div>

        {/* Canopy Aerodynamics & Sensor Specs */}
        <div className="lg:col-span-6 bg-white p-6 rounded-3xl border border-gray-200 shadow-xs flex flex-col justify-between space-y-6">
          <div className="space-y-4">
            <div className="border-b border-gray-100 pb-3">
              <h3 className="text-base font-bold text-gray-900">Canopy Aerodynamics & Sensor Specs</h3>
              <p className="text-xs text-gray-500">Ultrasonic anemometer and spatial transpiration modeling.</p>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between py-2 border-b border-gray-50">
                <span className="text-gray-500">Sensor Model</span>
                <strong className="text-gray-900">Ultrasonic 2D Anemometer (Solid-State)</strong>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-gray-50">
                <span className="text-gray-500">Sampling Rate</span>
                <strong className="text-gray-900">Continuous 1 Hz • 60s Telemetry Aggregation</strong>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-gray-50">
                <span className="text-gray-500">Measurement Accuracy</span>
                <strong className="text-emerald-700">± 0.1 m/s (Speed) • ± 1.5° (Direction)</strong>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-gray-50">
                <span className="text-gray-500">Anemometer Mounting Elevation</span>
                <strong className="text-gray-900">2.2 m Above Crop Canopy (Mast Mounted)</strong>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-gray-50">
                <span className="text-gray-500">Soil Moisture Level</span>
                <strong className="text-gray-900">{env.soil_moisture}% Moisture</strong>
              </div>

              <div className="flex items-center justify-between py-2">
                <span className="text-gray-500">Sensor Operational Health</span>
                <span className="inline-flex items-center gap-1 text-emerald-700 font-bold">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Calibrated & Active</span>
                </span>
              </div>
            </div>
          </div>

          {/* Microclimatic implication note */}
          <div className="p-4 bg-emerald-50/70 rounded-2xl border border-emerald-100 text-xs text-emerald-950 flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <strong className="block text-emerald-900 font-bold">Plume Dispersion & Triangulation Coverage</strong>
              <p className="leading-relaxed text-emerald-900/80">
                Wind blowing from {env.wind_direction} at {env.wind_speed} m/s carries plant transpiration plumes across field nodes, allowing optimal spatial triangulation coverage.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
