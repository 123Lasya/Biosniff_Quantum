import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Download,
  Plus,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { adminService } from '../../services/adminService';
import { AdminFarmersListResponse } from '../../types/api';

export const FarmersManagementPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedState, setSelectedState] = useState('All States');
  const [selectedCrop, setSelectedCrop] = useState('All Crops');
  const [selectedHealth, setSelectedHealth] = useState('All Health');
  const [page, setPage] = useState(1);

  const [data, setData] = useState<AdminFarmersListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFarmers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await adminService.getFarmers({
        search: searchTerm,
        state: selectedState,
        crop: selectedCrop,
        health: selectedHealth,
        page,
        page_size: 10,
      });
      setData(res);
    } catch (err: any) {
      console.error('Failed to fetch farmers list:', err);
      setError(err?.message || 'Failed to fetch farmers directory from server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFarmers();
  }, [searchTerm, selectedState, selectedCrop, selectedHealth, page]);

  const getHealthBadge = (health: string) => {
    switch (health?.toLowerCase()) {
      case 'healthy':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
            <span>Healthy</span>
          </span>
        );
      case 'at-risk':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-600" />
            <span>At Risk</span>
          </span>
        );
      case 'diseased':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-red-100 text-red-800">
            <span className="w-1.5 h-1.5 rounded-full bg-red-600" />
            <span>Diseased</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-700">
            Active
          </span>
        );
    }
  };

  const farmersList = data?.items || [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#0F2D1F] font-serif-display">
            Farmers Management Directory
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Registered farmers, linked land records, and real-time field disease telemetry across India.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => alert('Exporting national farmers dataset (CSV)...')}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-white hover:bg-gray-50 border border-gray-200 text-gray-700 font-semibold text-xs rounded-xl shadow-xs transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => alert('Register new farmer wizard opened.')}
            className="flex items-center gap-1.5 px-4 py-2 bg-[#0F3D2E] hover:bg-[#14523E] text-white font-bold text-xs rounded-xl shadow-xs transition"
          >
            <Plus className="w-4 h-4" />
            <span>Register Farmer</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-gray-200 shadow-xs flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search by farmer name, ID, or district..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setPage(1);
            }}
            className="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs focus:bg-white focus:outline-hidden focus:border-emerald-600"
          />
        </div>

        {/* State Filter */}
        <select
          value={selectedState}
          onChange={(e) => {
            setSelectedState(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs text-gray-700 font-medium focus:outline-hidden"
        >
          <option>All States</option>
          <option>Maharashtra</option>
          <option>Uttar Pradesh</option>
          <option>West Bengal</option>
          <option>Karnataka</option>
          <option>Tamil Nadu</option>
          <option>Punjab</option>
          <option>Andhra Pradesh</option>
        </select>

        {/* Crop Filter */}
        <select
          value={selectedCrop}
          onChange={(e) => {
            setSelectedCrop(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs text-gray-700 font-medium focus:outline-hidden"
        >
          <option>All Crops</option>
          <option>Rice</option>
          <option>Wheat</option>
          <option>Cotton</option>
          <option>Sugarcane</option>
        </select>

        {/* Health Status Filter */}
        <select
          value={selectedHealth}
          onChange={(e) => {
            setSelectedHealth(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs text-gray-700 font-medium focus:outline-hidden"
        >
          <option>All Health</option>
          <option value="healthy">Healthy</option>
          <option value="at-risk">At Risk</option>
          <option value="diseased">Diseased</option>
        </select>
      </div>

      {/* Farmers Data Table */}
      <div className="bg-white rounded-3xl border border-gray-200 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-12 text-center flex items-center justify-center gap-3">
            <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
            <span className="text-xs text-gray-500 font-medium">Loading farmers directory...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center space-y-2">
            <AlertCircle className="w-6 h-6 text-red-600 mx-auto" />
            <p className="text-xs text-red-700">{error}</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-700">
              <thead className="bg-gray-50 text-gray-500 uppercase tracking-wider text-[10px] font-bold border-b border-gray-100">
                <tr>
                  <th className="px-6 py-3.5">Farmer & ID</th>
                  <th className="px-6 py-3.5">Contact Details</th>
                  <th className="px-6 py-3.5">Location</th>
                  <th className="px-6 py-3.5">Crops Cultivated</th>
                  <th className="px-6 py-3.5">Farms & Area</th>
                  <th className="px-6 py-3.5">Crop Health</th>
                  <th className="px-6 py-3.5">Account Status</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {farmersList.map((farmer: any) => {
                  const farmerIdNum = farmer.farmer_id || farmer.id || 1;
                  const name = farmer.full_name || farmer.name || 'Farmer';
                  const phone = farmer.phone || '+91 98220 12345';
                  const email = farmer.email || '-';
                  const district = farmer.district || '';
                  const state = farmer.state || '';
                  const locationStr = [district, state].filter(Boolean).join(', ') || '-';
                  const crops = farmer.crops || ['Rice'];
                  const farmsCount = farmer.farms_count ?? farmer.farmCount ?? 0;
                  const totalArea = farmer.total_acres ?? farmer.totalAreaAcres ?? 0;
                  const healthStatus = farmer.health_status || farmer.healthStatus || 'healthy';

                  return (
                    <tr key={farmerIdNum} className="hover:bg-gray-50/70 transition">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          {farmer.profile_image_url || farmer.avatarUrl ? (
                            <img
                              src={farmer.profile_image_url || farmer.avatarUrl}
                              alt={name}
                              className="w-9 h-9 rounded-full object-cover border border-emerald-200 shadow-xs"
                            />
                          ) : (
                            <div className="w-9 h-9 rounded-full bg-emerald-100 text-emerald-800 font-bold flex items-center justify-center text-xs border border-emerald-300">
                              {name.charAt(0).toUpperCase()}
                            </div>
                          )}
                          <div>
                            <strong className="text-gray-900 font-bold block">{name}</strong>
                            <span className="text-[10px] text-gray-400">FRM00{farmerIdNum}</span>
                          </div>
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        <div className="space-y-0.5">
                          <div className="text-gray-900 font-medium">{phone}</div>
                          <div className="text-[11px] text-gray-400">{email}</div>
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        <div className="text-gray-900 font-medium">{district}</div>
                        <div className="text-[11px] text-gray-500">{state}</div>
                      </td>

                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {(Array.isArray(crops) ? crops : [crops]).map((c: string) => (
                            <span
                              key={c}
                              className="px-2 py-0.5 rounded-md bg-gray-100 text-gray-700 font-medium text-[10px]"
                            >
                              {c}
                            </span>
                          ))}
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        <strong className="text-gray-900 font-bold">{farmsCount} farms</strong>
                        <div className="text-[11px] text-gray-500">{totalArea} acres total</div>
                      </td>

                      <td className="px-6 py-4">
                        {getHealthBadge(healthStatus)}
                      </td>

                      <td className="px-6 py-4">
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-50 text-emerald-700">
                          Active
                        </span>
                      </td>

                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => navigate(`/admin/farmer/${farmerIdNum}`)}
                          className="px-3 py-1.5 rounded-xl bg-[#0F3D2E] hover:bg-[#14523E] text-white font-semibold text-[11px] transition shadow-xs"
                        >
                          View Profile
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Footer */}
        <div className="p-4 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
          <div>
            Showing Page <strong>{data?.page || 1}</strong> of <strong>{data?.total_pages || 1}</strong> ({data?.total || farmersList.length} total farmers)
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="px-3 py-1 border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-3 py-1 bg-emerald-800 text-white rounded-lg font-bold">{page}</span>
            <button
              onClick={() => setPage((p) => Math.min(data?.total_pages || 1, p + 1))}
              disabled={page >= (data?.total_pages || 1)}
              className="px-3 py-1 border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
