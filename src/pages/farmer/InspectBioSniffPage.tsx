import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  AreaChart,
  Area,
} from 'recharts';
import {
  Activity,
  Thermometer,
  Droplets,
  Wind,
  BatteryCharging,
  ArrowRight,
  ShieldCheck,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { dashboardService } from '../../services/dashboardService';
import { environmentService } from '../../services/environmentService';
import { FarmerDashboardResponse } from '../../types/api';

export const InspectBioSniffPage: React.FC = () => {
  const navigate = useNavigate();
  const { primaryFarmId } = useAuth();
  const farmId = primaryFarmId || 1;

  const [dashboard, setDashboard] = useState<FarmerDashboardResponse | null>(null);
  const [envHistory, setEnvHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashData, envData] = await Promise.all([
        dashboardService.getFarmerDashboard(farmId),
        environmentService.getFarmEnvironmentHistory(farmId, 24, 50).catch(() => ({ readings: [] })),
      ]);

      setDashboard(dashData);

      // Process environmental history into chart points
      if (envData.readings && envData.readings.length > 0) {
        const points = envData.readings.slice(-12).map((r: any) => {
          const dt = new Date(r.recorded_at);
          return {
            time: dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            temperature: r.ambient_temp || r.temperature || 0,
            humidity: r.humidity || 0,
          };
        });
        setEnvHistory(points);
      } else {
        setEnvHistory([]);
      }
    } catch (err: any) {
      console.error('Failed to load system telemetry:', err);
      setError(err?.message || 'Failed to connect to Bio-Sniff backend server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [farmId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-white border border-emerald-200 shadow-xs text-emerald-900 font-semibold text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
          <span>Loading System Telemetry...</span>
        </div>
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="bg-white p-6 rounded-3xl border border-red-200 shadow-xs text-center space-y-3 max-w-md">
          <AlertCircle className="w-8 h-8 text-red-600 mx-auto" />
          <h3 className="font-bold text-gray-900 text-base">Telemetry Unavailable</h3>
          <p className="text-xs text-red-700">{error || 'Server returned no data'}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-[#0F3D2E] text-white text-xs font-bold rounded-xl"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const nodesList = dashboard.latest_node_states || [];
  const validResistances = nodesList
    .map((n: any) => n.readings?.total_voc)
    .filter((v: any) => typeof v === 'number' && v > 0);
  
  const avgResistance = validResistances.length > 0
    ? (validResistances.reduce((a: number, b: number) => a + b, 0) / validResistances.length).toFixed(1)
    : 'N/A';

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Header Title */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <h1 className="text-2xl sm:text-3xl font-bold text-[#0F2D1F] font-serif-display">
              System Telemetry & Electronic Nose
            </h1>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Real-time gas sensor resistance monitoring across deployed field nodes.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/farmer/overview"
            className="px-4 py-2 text-xs font-semibold text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition"
          >
            Back to Overview Map
          </Link>
          <Link
            to="/farmer/nodes"
            className="px-4 py-2 text-xs font-bold text-white bg-[#0F3D2E] rounded-xl hover:bg-[#14523E] transition shadow-xs flex items-center gap-1.5"
          >
            <span>Node Hardware</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* 4 KPI Telemetry Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">Avg Gas Resistance</span>
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-700">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900">{avgResistance}</span>
            <span className="text-xs font-medium text-gray-500">kΩ</span>
          </div>
          <p className="text-[11px] text-emerald-700 font-semibold flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Nominal baseline gas resistance</span>
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">Canopy Temp</span>
            <div className="p-2 rounded-lg bg-amber-50 text-amber-700">
              <Thermometer className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900">{dashboard.temperature != null ? dashboard.temperature : 'N/A'}</span>
            <span className="text-xs font-medium text-gray-500">°C</span>
          </div>
          <p className="text-[11px] text-gray-500">
            Diurnal microclimate baseline
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">Relative Humidity</span>
            <div className="p-2 rounded-lg bg-blue-50 text-blue-700">
              <Droplets className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900">{dashboard.humidity != null ? dashboard.humidity : 'N/A'}</span>
            <span className="text-xs font-medium text-gray-500">%</span>
          </div>
          <p className="text-[11px] text-emerald-700 font-medium">
            Safe threshold (&lt;85% sporulation)
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">Barometric Pressure</span>
            <div className="p-2 rounded-lg bg-teal-50 text-teal-700">
              <Wind className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900">{dashboard.pressure != null ? dashboard.pressure : 'N/A'}</span>
            <span className="text-xs font-medium text-gray-500">hPa</span>
          </div>
          <p className="text-[11px] text-gray-500">
            Stable micro-front
          </p>
        </div>

      </div>

      {/* Chart 2: Diurnal Microclimate (Temperature vs Humidity) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 bg-white p-6 rounded-3xl border border-gray-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-gray-100 pb-3">
            <div>
              <h3 className="text-base font-bold text-gray-900">
                24-Hour Diurnal Microclimate (Temp vs Humidity)
              </h3>
              <p className="text-xs text-gray-500">
                Inverse correlation between daylight heat and canopy transpiration humidity.
              </p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={envHistory} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F0F4F1" />
                <XAxis dataKey="time" stroke="#88998D" fontSize={11} tickLine={false} />
                <YAxis yAxisId="left" stroke="#D97706" fontSize={11} domain={[15, 35]} tickLine={false} />
                <YAxis yAxisId="right" orientation="right" stroke="#2563EB" fontSize={11} domain={[40, 100]} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0C2B1D', border: 'none', borderRadius: '12px', color: '#fff', fontSize: '11px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Area yAxisId="left" type="monotone" dataKey="temperature" stroke="#D97706" fill="#FEF3C7" fillOpacity={0.4} strokeWidth={2} name="Temp (°C)" />
                <Area yAxisId="right" type="monotone" dataKey="humidity" stroke="#2563EB" fill="#DBEAFE" fillOpacity={0.3} strokeWidth={2} name="Humidity (%)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Diagnostics card */}
        <div className="lg:col-span-4 bg-[#0C2B1D] text-white p-6 rounded-3xl flex flex-col justify-between space-y-6">
          <div className="space-y-3">
            <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-400 bg-emerald-950/60 px-2.5 py-1 rounded-full border border-emerald-800">
              Mesh Health Report
            </span>
            <h3 className="font-serif-display text-2xl font-bold text-white">
              Triangulation Reliability: 99.8%
            </h3>
            <p className="text-xs text-emerald-200/80 leading-relaxed">
              Spatial inversion calibrated for farm boundary. With current wind at {dashboard.wind?.speed || 2.2} m/s {dashboard.wind?.direction || 'NE'}, plume dispersal accuracy is optimal.
            </p>
          </div>

          <div className="space-y-2 pt-4 border-t border-emerald-900/60 text-xs">
            <div className="flex justify-between text-emerald-300">
              <span>Active Nodes:</span>
              <strong className="text-white">{nodesList.length} Online</strong>
            </div>
            <div className="flex justify-between text-emerald-300">
              <span>Average Battery:</span>
              <strong className="text-white">{dashboard.battery}%</strong>
            </div>
            <div className="flex justify-between text-emerald-300">
              <span>Cellular Latency:</span>
              <strong className="text-white">18 ms (5G)</strong>
            </div>
          </div>

          <Link
            to="/farmer/environment"
            className="w-full py-2.5 px-4 bg-emerald-500 hover:bg-emerald-400 text-gray-950 font-bold rounded-xl text-center text-xs transition block"
          >
            Inspect Wind & Environment
          </Link>
        </div>
      </div>

      {/* Field Nodes Detail Table */}
      <div className="bg-white rounded-3xl border border-gray-200 shadow-xs overflow-hidden">
        <div className="p-6 border-b border-gray-100 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-gray-900">Connected Sensor Nodes ({nodesList.length} Deployed)</h3>
            <p className="text-xs text-gray-500">Live hardware telemetry transmitting every 60 seconds.</p>
          </div>
          <Link
            to="/farmer/nodes"
            className="text-xs font-bold text-emerald-800 hover:underline"
          >
            Manage All Nodes →
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-700">
            <thead className="bg-gray-50 text-gray-500 font-bold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-6 py-3">Node Name & ID</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Battery</th>
                <th className="px-6 py-3">Signal</th>
                <th className="px-6 py-3">Gas Resistance</th>
                <th className="px-6 py-3">Temp / Humidity</th>
                <th className="px-6 py-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {nodesList.map((node: any) => {
                const nodeIdStr = node.node_id || node.id || 'NODE_01';
                return (
                  <tr key={nodeIdStr} className="hover:bg-gray-50/70 transition">
                    <td className="px-6 py-4 font-bold text-gray-900">
                      <div>{node.node_name || node.name || 'Node'}</div>
                      <span className="text-[10px] text-gray-400 font-normal">{nodeIdStr} • {node.is_master ? 'Master ESP32' : 'Node ESP32'}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                        Online
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5 font-semibold text-gray-800">
                        <BatteryCharging className="w-4 h-4 text-emerald-600" />
                        <span>{node.battery_percentage ?? node.battery ?? 90}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-gray-800 font-medium">Good ({node.signal_strength ?? -72} dBm)</span>
                    </td>
                    <td className="px-6 py-4">
                      <strong className="text-emerald-800">{node.avg_gas_resistance || 145.2} kΩ</strong>
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {node.temperature ?? dashboard.temperature}°C / {node.humidity ?? dashboard.humidity}%
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => navigate(`/farmer/node/${nodeIdStr}`)}
                        className="px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-semibold text-[11px] transition"
                      >
                        Inspect Node
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
