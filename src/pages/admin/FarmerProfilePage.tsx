import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import {
  ArrowLeft,
  MapPin,
  Phone,
  Mail,
  Send,
  MessageSquare,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { adminService } from '../../services/adminService';
import { AdminFarmerProfileResponse } from '../../types/api';
import { FarmMap } from '../../components/maps/FarmMap';

export const FarmerProfilePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const farmerIdNum = parseInt(id || '1', 10);

  const [profile, setProfile] = useState<AdminFarmerProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await adminService.getFarmerProfile(farmerIdNum);
      setProfile(res);
    } catch (err: any) {
      console.error('Failed to load farmer admin profile:', err);
      setError(err?.message || 'Failed to fetch farmer profile');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, [farmerIdNum]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-white border border-emerald-200 shadow-xs text-emerald-900 font-semibold text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
          <span>Loading Farmer Profile & Multi-Farm Telemetry...</span>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="bg-white p-6 rounded-3xl border border-red-200 shadow-xs text-center space-y-3 max-w-md">
          <AlertCircle className="w-8 h-8 text-red-600 mx-auto" />
          <h3 className="font-bold text-gray-900 text-base">Farmer Profile Error</h3>
          <p className="text-xs text-red-700">{error || 'Profile not found'}</p>
          <button
            onClick={fetchProfile}
            className="px-4 py-2 bg-[#0F3D2E] text-white text-xs font-bold rounded-xl"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const details = profile.farmer_details || {};
  const farmsList = profile.farms || [];
  const sensorsList = profile.nodes || [];
  const healthTrendData = profile.history_summaries || [
    { date: '20 Jul', farm1: 68, farm2: 52, farm3: 74 },
    { date: '27 Jul', farm1: 71, farm2: 55, farm3: 75 },
    { date: '03 Aug', farm1: 72, farm2: 51, farm3: 77 },
    { date: '10 Aug', farm1: 75, farm2: 56, farm3: 79 },
    { date: '17 Aug', farm1: 76, farm2: 54, farm3: 81 },
  ];
  const advisory = profile.advisories?.[0] || {
    title: 'Monitor for Blast Disease',
    date: '18 Aug 2025',
    description: 'Weather conditions are favorable for blast disease in rice. Keep monitoring leaf symptoms and gas resistance signatures.',
  };

  const primaryFarm = farmsList[0] || {};
  const mapCenter = {
    lat: primaryFarm.latitude || 19.3919,
    lng: primaryFarm.longitude || 74.6528,
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Back to Farmers Directory Link */}
      <div className="flex items-center justify-between">
        <Link
          to="/admin/farmers"
          className="flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-emerald-800 bg-white border border-gray-200 px-3.5 py-2 rounded-xl shadow-xs transition"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Farmers Directory</span>
        </Link>
        <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">
          Verified Farmer Profile
        </span>
      </div>

      {/* Main Farmer Profile Header Card */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-gray-200 shadow-xs">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5">
            {details.profile_image_url ? (
              <img
                src={details.profile_image_url}
                alt={details.full_name || 'Farmer'}
                className="w-20 h-20 rounded-2xl object-cover border-2 border-emerald-500 shadow-md"
              />
            ) : (
              <div className="w-20 h-20 rounded-2xl bg-emerald-100 text-emerald-900 border-2 border-emerald-500 flex items-center justify-center font-bold text-2xl shadow-md">
                {(details.full_name || details.username || 'F').charAt(0).toUpperCase()}
              </div>
            )}
            <div className="space-y-1.5">
              <div className="flex items-center gap-3">
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 font-serif-display">
                  {details.full_name || details.username || 'Farmer'}
                </h1>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">
                  FRM00{details.farmer_id || farmerIdNum}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-4 text-xs text-gray-600">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-emerald-600" />
                  <span>{details.address || `${details.district || ''}, ${details.state || ''}`.replace(/^,\s*/, '') || 'Location Not Set'}</span>
                </span>
                <span className="flex items-center gap-1">
                  <Phone className="w-3.5 h-3.5 text-blue-600" />
                  <span>{details.phone || 'No Phone Registered'}</span>
                </span>
                <span className="flex items-center gap-1">
                  <Mail className="w-3.5 h-3.5 text-gray-400" />
                  <span>{details.email || '-'}</span>
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <button
              onClick={() => alert(`Dialing farmer ${details.full_name}: ${details.phone}`)}
              className="flex-1 md:flex-none px-4 py-2.5 bg-white hover:bg-gray-50 border border-gray-200 rounded-xl text-xs font-bold text-gray-700 shadow-xs transition"
            >
              Call Farmer
            </button>
            <button
              onClick={() => alert(`Dispatched SMS notification to ${details.phone}`)}
              className="flex-1 md:flex-none px-4 py-2.5 bg-[#0F3D2E] hover:bg-[#14523E] text-white rounded-xl text-xs font-bold shadow-xs transition flex items-center justify-center gap-2"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Send SMS Advisory</span>
            </button>
          </div>
        </div>

        {/* Profile Attributes Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-100 text-xs">
          <div>
            <span className="text-gray-400 block text-[11px]">Experience</span>
            <strong className="text-gray-900 text-sm font-semibold">18 Years</strong>
          </div>
          <div>
            <span className="text-gray-400 block text-[11px]">State / District</span>
            <strong className="text-gray-900 text-sm font-semibold">{details.state}, {details.district}</strong>
          </div>
          <div>
            <span className="text-gray-400 block text-[11px]">Total Landholding</span>
            <strong className="text-gray-900 text-sm font-semibold">{profile.farm_areas || 4.6} Acres ({farmsList.length} Plots)</strong>
          </div>
          <div>
            <span className="text-gray-400 block text-[11px]">Overall Health</span>
            <strong className="text-emerald-800 text-sm font-semibold capitalize">{profile.health || 'Healthy'}</strong>
          </div>
        </div>
      </div>

      {/* Farms Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {farmsList.map((f: any, idx: number) => (
          <div
            key={f.farm_id || idx}
            className="bg-white p-5 rounded-3xl border border-gray-200 shadow-xs space-y-3"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-gray-500">{f.farm_name || `Farm ${idx + 1}`}</span>
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                f.status === 'active' || f.health === 'healthy'
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'bg-amber-100 text-amber-800'
              }`}>
                {f.status === 'active' ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="text-lg font-bold text-gray-900 font-serif-display">
              {f.crop} ({f.area || 4.6} ac)
            </div>
            <p className="text-xs text-gray-500">
              Coordinates: {f.latitude?.toFixed(4)}° N, {f.longitude?.toFixed(4)}° E
            </p>
          </div>
        ))}
      </div>

      {/* Center Layout: Interactive Map + 5-Week Health Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Map */}
        <div className="lg:col-span-6 bg-white p-6 rounded-3xl border border-gray-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-gray-100 pb-3">
            <div>
              <h3 className="text-base font-bold text-gray-900">Farm Plots ({details.district || 'Ahmednagar'}, {details.state || 'MH'})</h3>
              <p className="text-xs text-gray-500">Satellite view of registered land parcels.</p>
            </div>
          </div>

          <FarmMap
            center={mapCenter}
            zoom={15.5}
            height="320px"
            locationLabel={`${details.district || 'Ahmednagar'}, ${details.state || 'Maharashtra'}`}
            showLayersMenu={false}
          />
        </div>

        {/* Right: Health Trend Line Chart */}
        <div className="lg:col-span-6 bg-white p-6 rounded-3xl border border-gray-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-gray-100 pb-3">
            <div>
              <h3 className="text-base font-bold text-gray-900">Crop Health Index (%)</h3>
              <p className="text-xs text-gray-500">Historical trend across {details.full_name}'s plots.</p>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={healthTrendData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F0F4F1" />
                <XAxis dataKey="date" stroke="#88998D" fontSize={11} tickLine={false} />
                <YAxis stroke="#88998D" fontSize={11} domain={[40, 100]} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0C2B1D', border: 'none', borderRadius: '12px', color: '#fff', fontSize: '11px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line type="monotone" dataKey="farm1" stroke="#16A34A" strokeWidth={2} name="Farm 1 (Rice)" />
                <Line type="monotone" dataKey="farm2" stroke="#D97706" strokeWidth={2} name="Farm 2 (At Risk)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Row: Active Sensors Table & Latest Advisory */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Active Sensors */}
        <div className="lg:col-span-7 bg-white rounded-3xl border border-gray-200 shadow-xs overflow-hidden">
          <div className="p-6 border-b border-gray-100">
            <h3 className="text-base font-bold text-gray-900">Active Sensors on {details.full_name}'s Farms</h3>
            <p className="text-xs text-gray-500">Live readings from {sensorsList.length} connected nodes.</p>
          </div>

          <table className="w-full text-left text-xs text-gray-700">
            <thead className="bg-gray-50 text-gray-500 uppercase tracking-wider text-[10px] font-bold">
              <tr>
                <th className="px-6 py-3">Node & Farm</th>
                <th className="px-6 py-3">Battery</th>
                <th className="px-6 py-3">Signal</th>
                <th className="px-6 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {sensorsList.map((sensor: any, idx: number) => (
                <tr key={sensor.node_id || idx} className="hover:bg-gray-50">
                  <td className="px-6 py-3.5 font-bold text-gray-900">{sensor.node_name || sensor.node_id}</td>
                  <td className="px-6 py-3.5">{sensor.battery_percentage || 90}%</td>
                  <td className="px-6 py-3.5">{sensor.signal_strength || -72} dBm</td>
                  <td className="px-6 py-3.5">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                      {sensor.status || 'Online'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Active Advisory Card */}
        <div className="lg:col-span-5 bg-gradient-to-br from-amber-50/90 to-white rounded-3xl border border-amber-200/90 p-6 shadow-xs flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-extrabold uppercase tracking-widest text-amber-800 bg-amber-100 px-2.5 py-0.5 rounded-md">
                Active Agronomic Advisory
              </span>
              <span className="text-xs text-gray-500">{advisory.date || 'Today'}</span>
            </div>
            <h4 className="text-lg font-bold text-gray-900 font-serif-display">
              {advisory.title || advisory.disease_name || 'Monitor Field Conditions'}
            </h4>
            <p className="text-xs text-gray-700 leading-relaxed">
              {advisory.details || advisory.description || 'Foliar spray of Tricyclazole 75% WP @ 0.6 g/L water recommended.'}
            </p>
          </div>

          <div className="pt-4 border-t border-amber-200/60">
            <button
              onClick={() => alert(`Advisory dispatched to ${details.full_name} via SMS.`)}
              className="w-full py-2.5 px-4 bg-[#0F3D2E] hover:bg-[#14523E] text-white text-xs font-bold rounded-xl transition flex items-center justify-center gap-2"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Resend Advisory Notification</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
