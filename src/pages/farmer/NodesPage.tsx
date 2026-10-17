import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Cpu,
  BatteryCharging,
  ArrowRight,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { farmService } from '../../services/farmService';
import { NodeOut } from '../../types/api';

export const NodesPage: React.FC = () => {
  const navigate = useNavigate();
  const { primaryFarmId } = useAuth();
  const farmId = primaryFarmId || 1;

  const [nodes, setNodes] = useState<NodeOut[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNodes = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await farmService.getFarmNodes(farmId);
      setNodes(data);
    } catch (err: any) {
      console.error('Failed to load farm nodes:', err);
      setError(err?.message || 'Failed to fetch nodes from backend');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNodes();
  }, [farmId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-white border border-emerald-200 shadow-xs text-emerald-900 font-semibold text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
          <span>Loading Deployed Sensor Nodes...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="bg-white p-6 rounded-3xl border border-red-200 shadow-xs text-center space-y-3 max-w-md">
          <AlertCircle className="w-8 h-8 text-red-600 mx-auto" />
          <h3 className="font-bold text-gray-900 text-base">Nodes Data Error</h3>
          <p className="text-xs text-red-700">{error}</p>
          <button
            onClick={fetchNodes}
            className="px-4 py-2 bg-[#0F3D2E] text-white text-xs font-bold rounded-xl"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const onlineCount = nodes.filter((n) => n.status === 'online').length;
  const avgBattery =
    nodes.length > 0
      ? Math.round(
          nodes.reduce((acc, n) => acc + (n.battery_percentage || 0), 0) / nodes.length
        )
      : 90;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#0F2D1F] font-serif-display">
            Field Sensor Nodes
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Hardware status and live sensor arrays for monitored plot.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-100/80 text-emerald-900 text-xs font-bold border border-emerald-300/60">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
            <span>{onlineCount} of {nodes.length} Nodes Online</span>
          </span>
        </div>
      </div>

      {/* Summary Stat Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-2xl border border-gray-200 shadow-xs">
          <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider block">Total Deployed</span>
          <strong className="text-2xl font-bold text-gray-900 mt-1 block">{nodes.length} Nodes</strong>
          <span className="text-[11px] text-gray-500">100% Mesh Field Coverage</span>
        </div>
        <div className="bg-white p-4 rounded-2xl border border-gray-200 shadow-xs">
          <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider block">Operational Status</span>
          <strong className="text-2xl font-bold text-emerald-700 mt-1 block">{onlineCount} Online</strong>
          <span className="text-[11px] text-emerald-600">{nodes.length - onlineCount} Offline</span>
        </div>
        <div className="bg-white p-4 rounded-2xl border border-gray-200 shadow-xs">
          <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider block">Avg Battery</span>
          <strong className="text-2xl font-bold text-emerald-700 mt-1 block">{avgBattery}%</strong>
          <span className="text-[11px] text-gray-500">Solar Recharged</span>
        </div>
      </div>

      {/* Node Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {nodes.map((node) => (
          <div
            key={node.node_id}
            className="bg-white rounded-3xl border border-gray-200 shadow-xs hover:shadow-md transition flex flex-col justify-between overflow-hidden"
          >
            {/* Top Card Head */}
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-800">
                    <Cpu className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-base text-gray-900">{node.node_name}</h3>
                    <p className="text-xs text-gray-500">{node.node_id}</p>
                  </div>
                </div>
                <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold ${
                  node.status === 'online' ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-600'
                }`}>
                  {node.status === 'online' ? 'Online' : 'Offline'}
                </span>
              </div>

              {/* Hardware Spec Badges */}
              <div className="p-3 bg-gray-50 rounded-xl space-y-1.5 text-xs text-gray-600">
                <div className="flex justify-between">
                  <span>Hardware:</span>
                  <strong className="text-gray-900">{node.is_master ? 'Master ESP32 + BME688' : 'Node ESP32 + BME688'}</strong>
                </div>
                <div className="flex justify-between">
                  <span>Power Source:</span>
                  <strong className="text-gray-900">Solar (with Battery)</strong>
                </div>
                <div className="flex justify-between">
                  <span>Firmware:</span>
                  <strong className="text-gray-900">{node.firmware_version || 'v2.3.1'}</strong>
                </div>
                <div className="flex justify-between">
                  <span>GPS Coordinates:</span>
                  <strong className="text-gray-900">{node.latitude.toFixed(4)}, {node.longitude.toFixed(4)}</strong>
                </div>
              </div>

              {/* Battery */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600 flex items-center gap-1">
                    <BatteryCharging className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Battery Level</span>
                  </span>
                  <strong className="text-gray-900">{node.battery_percentage}%</strong>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className="bg-emerald-600 h-2 rounded-full transition-all"
                    style={{ width: `${node.battery_percentage}%` }}
                  />
                </div>
              </div>

              {/* Live Sensor Readings */}
              <div className="grid grid-cols-3 gap-2 pt-2 text-center text-xs">
                <div className="p-2 bg-emerald-50/70 rounded-xl border border-emerald-100">
                  <span className="text-[10px] text-gray-500 block">Gas Resist</span>
                  <strong className="text-emerald-800 text-sm font-bold">
                    {node.readings?.total_voc != null ? node.readings.total_voc : 'N/A'}
                  </strong>
                  <span className="text-[9px] text-gray-400 block">kΩ</span>
                </div>
                <div className="p-2 bg-amber-50/70 rounded-xl border border-amber-100">
                  <span className="text-[10px] text-gray-500 block">Temp</span>
                  <strong className="text-gray-900 text-sm font-bold">
                    {node.readings?.temperature != null ? `${node.readings.temperature}°` : 'N/A'}
                  </strong>
                  <span className="text-[9px] text-gray-400 block">Celsius</span>
                </div>
                <div className="p-2 bg-blue-50/70 rounded-xl border border-blue-100">
                  <span className="text-[10px] text-gray-500 block">Humidity</span>
                  <strong className="text-gray-900 text-sm font-bold">
                    {node.readings?.humidity != null ? `${node.readings.humidity}%` : 'N/A'}
                  </strong>
                  <span className="text-[9px] text-gray-400 block">RH</span>
                </div>
              </div>
            </div>

            {/* Bottom Card Action */}
            <div className="p-4 bg-gray-50 border-t border-gray-100">
              <button
                onClick={() => navigate(`/farmer/node/${node.node_id}`)}
                className="w-full py-2.5 px-4 bg-[#0F3D2E] hover:bg-[#14523E] text-white text-xs font-bold rounded-xl transition flex items-center justify-center gap-2"
              >
                <span>Inspect Node Details</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
