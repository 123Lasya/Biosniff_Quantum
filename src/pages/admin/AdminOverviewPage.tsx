import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Users,
  LandPlot,
  HeartPulse,
  Cpu,
  ArrowUpRight,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { AdminIndiaMap } from '../../components/maps/AdminIndiaMap';
import { adminService } from '../../services/adminService';
import { AdminDashboardResponse, AdminFarmMapItem } from '../../types/api';

export const AdminOverviewPage: React.FC = () => {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState<AdminDashboardResponse | null>(null);
  const [farmsMap, setFarmsMap] = useState<AdminFarmMapItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAdminData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashData, mapData] = await Promise.all([
        adminService.getDashboard(),
        adminService.getFarmsMap().catch(() => []),
      ]);
      setDashboard(dashData);
      setFarmsMap(mapData);
    } catch (err: any) {
      console.error('Failed to load admin overview:', err);
      setError(err?.message || 'Failed to connect to national telemetry backend');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-white border border-emerald-200 shadow-xs text-emerald-900 font-semibold text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
          <span>Loading National Agricultural Telemetry...</span>
        </div>
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="bg-white p-6 rounded-3xl border border-red-200 shadow-xs text-center space-y-3 max-w-md">
          <AlertCircle className="w-8 h-8 text-red-600 mx-auto" />
          <h3 className="font-bold text-gray-900 text-base">Admin Telemetry Connection Error</h3>
          <p className="text-xs text-red-700">{error || 'Server returned no admin data'}</p>
          <button
            onClick={fetchAdminData}
            className="px-4 py-2 bg-[#0F3D2E] text-white text-xs font-bold rounded-xl"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const topStates = dashboard.regional_summaries || [];
  const cropsMonitored = dashboard.crops_monitored || [];
  const recentAlerts = dashboard.recent_alerts || [];
  const networkHealth = dashboard.network_health || {};

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#0F2D1F] font-serif-display">
            National Agricultural Telemetry Overview
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Aggregated electronic nose health monitoring across {dashboard.total_farms} registered farms in India.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/admin/farmers"
            className="px-4 py-2 text-xs font-bold text-white bg-[#0F3D2E] rounded-xl hover:bg-[#14523E] transition shadow-xs flex items-center gap-1.5"
          >
            <Users className="w-3.5 h-3.5" />
            <span>Manage All Farmers</span>
          </Link>
        </div>
      </div>

      {/* 4 Top KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Card 1: Total Farmers */}
        <div className="bg-white p-6 rounded-3xl border border-gray-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">Total Farmers</span>
            <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-800">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-bold text-gray-900 font-serif-display">{dashboard.total_farmers}</div>
          <p className="text-xs text-emerald-700 font-semibold flex items-center gap-1">
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>Verified accounts active</span>
          </p>
        </div>

        {/* Card 2: Total Farms */}
        <div className="bg-white p-6 rounded-3xl border border-gray-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">Total Farms</span>
            <div className="p-2.5 rounded-xl bg-blue-50 text-blue-800">
              <LandPlot className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-bold text-gray-900 font-serif-display">{dashboard.total_farms}</div>
          <p className="text-xs text-gray-500">
            <strong className="text-gray-900 font-bold">{dashboard.active_farms}</strong> Active • <strong className="text-gray-500">{dashboard.inactive_farms}</strong> Inactive
          </p>
        </div>

        {/* Card 3: Crop Health */}
        <div className="bg-white p-6 rounded-3xl border border-gray-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">Crop Health</span>
            <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-800">
              <HeartPulse className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-bold text-gray-900 font-serif-display">{dashboard.healthy_farms} Healthy</div>
          <p className="text-xs text-gray-500">
            <strong className="text-emerald-700">{dashboard.healthy_farms} Healthy</strong> • <strong className="text-red-600">{dashboard.diseased_farms + dashboard.at_risk_farms} At Risk/Diseased</strong>
          </p>
        </div>

        {/* Card 4: Active Sensors */}
        <div className="bg-white p-6 rounded-3xl border border-gray-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">Active Nodes</span>
            <div className="p-2.5 rounded-xl bg-amber-50 text-amber-800">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-bold text-gray-900 font-serif-display">{dashboard.active_nodes + dashboard.offline_nodes}</div>
          <p className="text-xs text-gray-500">
            <strong className="text-emerald-700">{dashboard.active_nodes}</strong> Online • <strong className="text-amber-600">{dashboard.offline_nodes}</strong> Offline
          </p>
        </div>
      </div>

      {/* Middle Row: Farms Across India Map + Top States Table */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Map Column (8 cols) */}
        <div className="lg:col-span-8 bg-white p-6 rounded-3xl border border-gray-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-gray-100 pb-3">
            <div>
              <h3 className="text-base font-bold text-gray-900">Farms Across India</h3>
              <p className="text-xs text-gray-500">Spatial distribution of monitored agricultural plots.</p>
            </div>
            <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 text-xs font-bold border border-emerald-200">
              Live API Coordinates
            </span>
          </div>

          {/* India Network Map Component */}
          <AdminIndiaMap height="390px" farmsData={farmsMap} />
        </div>

        {/* Top States List (4 cols) */}
        <div className="lg:col-span-4 bg-white p-6 rounded-3xl border border-gray-200 shadow-xs space-y-4 flex flex-col justify-between">
          <div className="border-b border-gray-100 pb-3">
            <h3 className="text-base font-bold text-gray-900">Regional Farm Distribution</h3>
            <p className="text-xs text-gray-500">Highest density of Bio-Sniff sensor coverage.</p>
          </div>

          <div className="space-y-2 overflow-y-auto max-h-[350px] pr-1">
            {topStates.map((item: any, idx: number) => (
              <div
                key={item.state || idx}
                className="flex items-center justify-between p-2 rounded-xl hover:bg-gray-50 transition text-xs"
              >
                <div className="flex items-center gap-2.5">
                  <span className="w-5 h-5 rounded-md bg-gray-100 flex items-center justify-center font-bold text-gray-600 text-[10px]">
                    {idx + 1}
                  </span>
                  <span className="font-semibold text-gray-900">{item.state}</span>
                </div>
                <strong className="text-gray-800">{item.farms || item.count || 0} farms</strong>
              </div>
            ))}
          </div>

          <button
            onClick={() => navigate('/admin/farmers')}
            className="w-full py-2.5 bg-gray-50 hover:bg-gray-100 text-xs font-bold text-gray-700 rounded-xl border border-gray-200 transition"
          >
            View Farmers Directory
          </button>
        </div>
      </div>

      {/* Bottom Row: Crops Monitored + Sensor Network Health + Recent Alerts */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Crops Monitored */}
        <div className="bg-white p-6 rounded-3xl border border-gray-200 shadow-xs space-y-4">
          <div className="border-b border-gray-100 pb-3">
            <h3 className="text-base font-bold text-gray-900">Crops Monitored</h3>
            <p className="text-xs text-gray-500">Commodity distribution across active acreage.</p>
          </div>

          <div className="space-y-3">
            {cropsMonitored.map((crop: any) => (
              <div key={crop.crop || crop.name} className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="font-semibold text-gray-800">{crop.crop || crop.name}</span>
                  <span className="text-gray-500">{crop.farms || crop.count} farms</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-emerald-600 transition-all"
                    style={{ width: `${Math.min(100, ((crop.farms || crop.count || 1) / Math.max(dashboard.total_farms, 1)) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sensor Network Health */}
        <div className="bg-white p-6 rounded-3xl border border-gray-200 shadow-xs space-y-4 flex flex-col justify-between">
          <div>
            <div className="border-b border-gray-100 pb-3">
              <h3 className="text-base font-bold text-gray-900">Sensor Network Health</h3>
              <p className="text-xs text-gray-500">Grid reliability and IoT transmission status.</p>
            </div>

            <div className="mt-4 flex items-center justify-center p-4">
              <div className="relative w-36 h-36 rounded-full border-8 border-emerald-500 flex flex-col items-center justify-center text-center">
                <span className="text-3xl font-bold text-gray-900 font-serif-display">
                  {networkHealth.online_percentage || 98}%
                </span>
                <span className="text-[10px] text-emerald-700 font-bold uppercase tracking-wider">Health Score</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center text-xs border-t border-gray-100 pt-3">
            <div className="p-2 bg-emerald-50 rounded-xl">
              <strong className="text-emerald-800 block font-bold text-sm">{dashboard.active_nodes}</strong>
              <span className="text-[10px] text-emerald-700">Online</span>
            </div>
            <div className="p-2 bg-red-50 rounded-xl">
              <strong className="text-red-700 block font-bold text-sm">{dashboard.offline_nodes}</strong>
              <span className="text-[10px] text-red-600">Offline</span>
            </div>
            <div className="p-2 bg-amber-50 rounded-xl">
              <strong className="text-amber-800 block font-bold text-sm">{dashboard.active_alerts}</strong>
              <span className="text-[10px] text-amber-700">Alerts</span>
            </div>
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-white p-6 rounded-3xl border border-gray-200 shadow-xs space-y-4 flex flex-col justify-between">
          <div className="border-b border-gray-100 pb-3 flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-gray-900">Recent Critical Alerts</h3>
              <p className="text-xs text-gray-500">Anomalies requiring agronomic review.</p>
            </div>
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
              {recentAlerts.length}
            </span>
          </div>

          <div className="space-y-2.5 overflow-y-auto max-h-[260px]">
            {recentAlerts.map((alert: any, i: number) => (
              <div
                key={alert.id || alert.alert_id || i}
                className="p-2.5 rounded-xl bg-gray-50 border border-gray-100 hover:bg-red-50/40 transition text-xs space-y-1"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-gray-900">{alert.title || alert.farm || 'Farm Alert'}</span>
                  <span className={`px-2 py-0.5 rounded-md text-[9px] font-extrabold uppercase tracking-wider ${
                    alert.severity === 'critical'
                      ? 'bg-red-600 text-white'
                      : alert.severity === 'high'
                      ? 'bg-amber-600 text-white'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {alert.severity || 'info'}
                  </span>
                </div>
                <div className="flex items-center justify-between text-gray-500 text-[11px]">
                  <span className="text-gray-700 font-medium">{alert.message || alert.issue || 'Telemetry update'}</span>
                  <span>{alert.created_at ? new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : (alert.time || 'Today')}</span>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={() => navigate('/admin/farmers')}
            className="w-full py-2 bg-[#0F3D2E] hover:bg-[#14523E] text-white text-xs font-bold rounded-xl transition"
          >
            View National Directory
          </button>
        </div>
      </div>
    </div>
  );
};
