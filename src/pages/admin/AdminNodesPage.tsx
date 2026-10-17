import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Cpu,
  BatteryCharging,
  Wifi,
  RefreshCw,
  AlertCircle,
  Search,
  Filter,
} from 'lucide-react';
import { adminService } from '../../services/adminService';
import { AdminNodeListItem } from '../../types/api';

export const AdminNodesPage: React.FC = () => {
  const navigate = useNavigate();
  const [nodes, setNodes] = useState<AdminNodeListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All Status');

  const fetchNodes = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminService.getNodes();
      setNodes(data);
    } catch (err: any) {
      console.error('Failed to load admin nodes directory:', err);
      setError(err?.message || 'Failed to fetch node inventory from server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNodes();
  }, []);

  const filteredNodes = nodes.filter((n) => {
    const matchesSearch =
      n.node_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      n.node_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      n.farm_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      n.farmer_name.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === 'All Status' ||
      (statusFilter === 'Online' && n.status === 'online') ||
      (statusFilter === 'Offline' && n.status !== 'online');

    return matchesSearch && matchesStatus;
  });

  const onlineCount = nodes.filter((n) => n.status === 'online').length;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#0F2D1F] font-serif-display">
            National E-Nose Sensor Hardware Directory
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Real-time status, battery telemetry, and AI pathogen inferencing across all registered field nodes.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-100 text-emerald-900 text-xs font-bold border border-emerald-300">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
            <span>{onlineCount} of {nodes.length} System Nodes Online</span>
          </span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-gray-200 shadow-xs flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search by Node ID, Farm, or Farmer name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs focus:bg-white focus:outline-hidden focus:border-emerald-600"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs text-gray-700 font-medium focus:outline-hidden"
        >
          <option>All Status</option>
          <option>Online</option>
          <option>Offline</option>
        </select>
      </div>

      {/* Node Inventory Table */}
      <div className="bg-white rounded-3xl border border-gray-200 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-12 text-center flex items-center justify-center gap-3">
            <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
            <span className="text-xs text-gray-500 font-medium">Loading hardware node registry...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center space-y-2">
            <AlertCircle className="w-6 h-6 text-red-600 mx-auto" />
            <p className="text-xs text-red-700">{error}</p>
            <button
              onClick={fetchNodes}
              className="px-4 py-2 bg-[#0F3D2E] text-white text-xs font-bold rounded-xl"
            >
              Retry
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-700">
              <thead className="bg-gray-50 text-gray-500 uppercase tracking-wider text-[10px] font-bold border-b border-gray-100">
                <tr>
                  <th className="px-6 py-3.5">Node ID & Type</th>
                  <th className="px-6 py-3.5">Farm & Farmer</th>
                  <th className="px-6 py-3.5">GPS Location</th>
                  <th className="px-6 py-3.5">Status & Signal</th>
                  <th className="px-6 py-3.5">Power / Battery</th>
                  <th className="px-6 py-3.5">Latest Readings</th>
                  <th className="px-6 py-3.5">Latest AI Prediction</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredNodes.map((node) => (
                  <tr key={node.node_id} className="hover:bg-gray-50/70 transition">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-800 font-bold flex items-center justify-center shrink-0">
                          <Cpu className="w-5 h-5" />
                        </div>
                        <div>
                          <strong className="text-gray-900 font-bold block">{node.node_name}</strong>
                          <span className="text-[10px] text-gray-400 font-normal">
                            {node.node_id} • {node.is_master ? 'Master 5G Gateway' : 'Slave Mesh Node'}
                          </span>
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <div className="space-y-0.5">
                        <button
                          onClick={() => navigate(`/admin/farmer/${node.farmer_id}`)}
                          className="font-bold text-gray-900 hover:text-emerald-700 text-left block hover:underline"
                        >
                          {node.farmer_name}
                        </button>
                        <span className="text-[11px] text-gray-500">{node.farm_name}</span>
                      </div>
                    </td>

                    <td className="px-6 py-4 font-mono text-[11px]">
                      {node.latitude.toFixed(4)}° N, {node.longitude.toFixed(4)}° E
                    </td>

                    <td className="px-6 py-4">
                      <div className="space-y-1">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          node.status === 'online' ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-600'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${node.status === 'online' ? 'bg-emerald-600' : 'bg-gray-400'}`} />
                          <span>{node.status === 'online' ? 'Online' : 'Offline'}</span>
                        </span>
                        <div className="text-[10px] text-gray-500">
                          {node.signal_strength != null ? `${node.signal_strength} dBm` : 'No signal record'}
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5 font-semibold text-gray-800">
                        <BatteryCharging className="w-4 h-4 text-emerald-600" />
                        <span>{node.battery_percentage != null ? `${node.battery_percentage}%` : 'No data'}</span>
                      </div>
                    </td>

                    <td className="px-6 py-4 text-gray-600">
                      {node.latest_temperature != null ? (
                        <div>
                          <strong>{node.latest_temperature}°C</strong> / {node.latest_humidity}% RH
                          <span className="text-[10px] text-emerald-700 block font-semibold">VOC: {node.latest_voc || 'N/A'} kΩ</span>
                        </div>
                      ) : (
                        <span className="text-gray-400 italic">No cycles recorded</span>
                      )}
                    </td>

                    <td className="px-6 py-4">
                      {node.latest_prediction ? (
                        <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                          node.latest_prediction.toLowerCase().includes('healthy')
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {node.latest_prediction}
                        </span>
                      ) : (
                        <span className="text-gray-400 italic text-[11px]">No prediction yet</span>
                      )}
                    </td>

                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => navigate(`/admin/farmer/${node.farmer_id}`)}
                        className="px-3 py-1.5 rounded-xl bg-[#0F3D2E] hover:bg-[#14523E] text-white font-semibold text-[11px] transition shadow-xs"
                      >
                        Inspect Farm
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
