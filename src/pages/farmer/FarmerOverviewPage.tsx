import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Radio,
  CheckCircle2,
  AlertCircle,
  Eye,
  RefreshCw,
} from 'lucide-react';
import { FarmerTopHeader } from '../../components/common/FarmerTopHeader';
import { FarmMap } from '../../components/maps/FarmMap';
import { useAuth } from '../../context/AuthContext';
import { dashboardService } from '../../services/dashboardService';
import { FarmerDashboardResponse } from '../../types/api';
import { SensorNode, FarmCoordinate } from '../../types';
import healthyFoliageImg from '../../assets/images/healthy_foliage_reference.png';
import diseasedSymptomImg from '../../assets/images/diseased_foliar_symptom_reference.png';

export const FarmerOverviewPage: React.FC = () => {
  const navigate = useNavigate();
  const { primaryFarmId } = useAuth();
  const farmId = primaryFarmId || 1;

  const [dashboardData, setDashboardData] = useState<FarmerDashboardResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await dashboardService.getFarmerDashboard(farmId);
      setDashboardData(data);
    } catch (err: any) {
      console.error('Failed to load farmer dashboard:', err);
      setError(err?.message || 'Failed to connect to Bio-Sniff backend server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [farmId]);

  const handleInspectBioSniff = () => {
    navigate('/farmer/system');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F6F9F6] text-[#1A281E] flex flex-col font-sans">
        <FarmerTopHeader />
        <main className="flex-1 flex items-center justify-center p-8">
          <div className="bg-white p-8 rounded-3xl border border-gray-200 shadow-md flex flex-col items-center gap-4 text-center max-w-sm">
            <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin" />
            <div>
              <h3 className="font-bold text-gray-900 text-base">Loading Telemetry</h3>
              <p className="text-xs text-gray-500 mt-1">Connecting to Bio-Sniff field nodes & backend...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <div className="min-h-screen bg-[#F6F9F6] text-[#1A281E] flex flex-col font-sans">
        <FarmerTopHeader />
        <main className="flex-1 flex items-center justify-center p-8">
          <div className="bg-white p-8 rounded-3xl border border-red-200 shadow-md flex flex-col items-center gap-4 text-center max-w-md">
            <AlertCircle className="w-10 h-10 text-red-600" />
            <div>
              <h3 className="font-bold text-gray-900 text-lg">API Connection Issue</h3>
              <p className="text-xs text-red-700 mt-1">{error || 'No farm data returned from server.'}</p>
            </div>
            <button
              onClick={fetchDashboard}
              className="px-5 py-2.5 bg-[#0F3D2E] hover:bg-[#14523E] text-white text-xs font-bold rounded-xl shadow-sm transition"
            >
              Retry Connection
            </button>
          </div>
        </main>
      </div>
    );
  }

  // Derive status
  const isDiseaseDetected =
    dashboardData.health_status === 'diseased' ||
    dashboardData.health_status === 'at-risk' ||
    (dashboardData.detected_diseases && dashboardData.detected_diseases.length > 0) ||
    dashboardData.latest_prediction?.disease_detected === true;

  const farmName = dashboardData.farm?.farm_name || dashboardData.farm?.name || 'Bio-Sniff Farm';
  const farmerName = dashboardData.farmer?.full_name || 'Farmer';
  const cropVariety = dashboardData.crop_variety || dashboardData.crop || 'Paddy / Crop';
  const areaAcres = dashboardData.farm?.area || dashboardData.farm?.area_acres || 0;
  const lastUpdate = dashboardData.last_update || 'No cycles recorded yet';

  // Format farm coordinates & boundary
  const farmCenter: FarmCoordinate = {
    lat: dashboardData.farm_coordinates?.lat || dashboardData.farm?.coordinates?.lat || 19.8321,
    lng: dashboardData.farm_coordinates?.lng || dashboardData.farm?.coordinates?.lng || 74.6521,
  };

  const farmBoundary: FarmCoordinate[] = (dashboardData.farm_boundary || []).map((b) => ({
    lat: b.lat,
    lng: b.lng,
  }));

  // Format nodes for FarmMap
  const mappedNodes: SensorNode[] = (dashboardData.latest_node_states || []).map((n: any) => ({
    id: n.node_id || n.id,
    nodeId: n.node_id || n.id,
    name: n.node_name || n.name || n.node_id,
    status: n.status === 'online' ? 'online' : 'offline',
    battery: n.battery_percentage ?? n.battery ?? 100,
    signal: n.signal_strength && n.signal_strength > -75 ? 'Excellent' : 'Good',
    signalDbm: n.signal_strength ?? -75,
    coordinates: {
      lat: n.latitude ?? n.coordinates?.lat ?? farmCenter.lat,
      lng: n.longitude ?? n.coordinates?.lng ?? farmCenter.lng,
    },
    lastTransmission: n.last_seen ? new Date(n.last_seen).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'No transmission yet',
    firmwareVersion: n.firmware_version || 'v2.3.1',
    deploymentDate: 'Active',
    hardware: n.is_master ? 'Master ESP32 + BME688' : 'Node ESP32 + BME688',
    powerSource: 'Solar (with Battery)',
    readings: {
      temperature: n.readings?.temperature ?? n.temperature ?? 0,
      humidity: n.readings?.humidity ?? n.humidity ?? 0,
      pressure: n.readings?.pressure ?? n.pressure ?? 0,
      totalVoc: n.readings?.total_voc ?? n.avg_gas_resistance ?? 0,
      gasResistance10: n.readings?.gas_resistance_10 || n.gas_readings || [],
    },
  }));

  // Disease source formatting
  const locLat = dashboardData.localized_source?.lat || dashboardData.localization?.estimated_latitude;
  const locLng = dashboardData.localized_source?.lng || dashboardData.localization?.estimated_longitude;

  const diseaseSource = (isDiseaseDetected && locLat && locLng)
    ? {
        coordinates: {
          lat: locLat,
          lng: locLng,
        },
        name: dashboardData.detected_diseases?.[0] || dashboardData.latest_prediction?.predicted_class || 'Pathogen Anomaly',
        confidence: Math.round((dashboardData.latest_prediction?.confidence || dashboardData.confidence || 0.9) * (dashboardData.latest_prediction?.confidence <= 1 ? 100 : 1)),
      }
    : null;

  const diseaseName = dashboardData.detected_diseases?.[0] || dashboardData.latest_prediction?.predicted_class || 'Pathogen Anomaly';
  const confidenceScore = diseaseSource
    ? diseaseSource.confidence
    : (dashboardData.latest_prediction?.confidence ? Math.round(dashboardData.latest_prediction.confidence * (dashboardData.latest_prediction.confidence <= 1 ? 100 : 1)) : 0);
  const affectedZone = dashboardData.affected_zone?.name || dashboardData.localization?.affected_zone?.name || 'Estimated micro-zone';
  const recommendedAction = dashboardData.recommended_action_summary || dashboardData.latest_recommendation?.details || 'Maintain routine field scouting and monitor hourly node cycles.';

  return (
    <div className="min-h-screen bg-[#F6F9F6] text-[#1A281E] flex flex-col font-sans">
      {/* Top Header WITHOUT Sidebar */}
      <FarmerTopHeader
        farmerName={farmerName}
        farmName={farmName}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        
        {/* Notice Bar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-white border border-gray-200/90 shadow-xs">
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-xl ${isDiseaseDetected ? 'bg-red-50 text-red-600 border border-red-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'}`}>
              {isDiseaseDetected ? (
                <AlertTriangle className="w-5 h-5 animate-bounce" />
              ) : (
                <ShieldCheck className="w-5 h-5" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold text-gray-900">
                  {farmName} — Field Overview
                </h1>
                <span className="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-gray-100 text-gray-700">
                  {areaAcres} Acres • {cropVariety}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-0.5">
                Last synchronized telemetry: <strong>{lastUpdate}</strong>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className={`px-3 py-1.5 rounded-xl text-xs font-bold ${
              isDiseaseDetected ? 'bg-red-100 text-red-800 border border-red-200' : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
            }`}>
              {isDiseaseDetected ? 'Pathogen Anomaly Active' : 'Crop System Nominal'}
            </span>
          </div>
        </div>

        {/* Core Layout: Left Map + Right Health Intelligence Card */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Column: Interactive Map (7 Cols) */}
          <div className="lg:col-span-7 space-y-4">
            <div className="bg-white rounded-3xl p-4 sm:p-5 border border-gray-200 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Radio className="w-4 h-4 text-emerald-700 animate-pulse" />
                  <h2 className="text-sm font-bold text-gray-900">
                    Satellite Farm Boundary & Mesh Nodes
                  </h2>
                </div>
                <span className="text-[11px] font-medium text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                  Google Maps Satellite
                </span>
              </div>

              {/* Real Google Maps Platform */}
              <div className="relative">
                <FarmMap
                  center={farmCenter}
                  zoom={16.2}
                  boundary={farmBoundary}
                  nodes={mappedNodes}
                  diseaseSource={diseaseSource}
                  height="440px"
                  locationLabel={`${farmCenter.lat.toFixed(4)}° N, ${farmCenter.lng.toFixed(4)}° E\n${dashboardData.farm?.address || 'Ahmednagar, Maharashtra'}`}
                />
              </div>

              {/* Farm Metadata Bar */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-xs">
                <div className="p-2.5 rounded-xl bg-gray-50 border border-gray-100">
                  <span className="text-gray-500 block text-[11px]">Location</span>
                  <strong className="text-gray-900">{dashboardData.farmer?.district || 'Ahmednagar'}, MH</strong>
                </div>
                <div className="p-2.5 rounded-xl bg-gray-50 border border-gray-100">
                  <span className="text-gray-500 block text-[11px]">Cultivated Area</span>
                  <strong className="text-gray-900">{areaAcres} Acres</strong>
                </div>
                <div className="p-2.5 rounded-xl bg-gray-50 border border-gray-100">
                  <span className="text-gray-500 block text-[11px]">Crop Variety</span>
                  <strong className="text-gray-900">{cropVariety}</strong>
                </div>
                <div className="p-2.5 rounded-xl bg-gray-50 border border-gray-100">
                  <span className="text-gray-500 block text-[11px]">Growth Stage</span>
                  <strong className="text-gray-900">{dashboardData.farm?.growth_stage || 'Tillering'}</strong>
                </div>
              </div>
            </div>

            {/* PRIMARY USER ACTION: INSPECT BIO-SNIFF BUTTON */}
            <button
              id="inspect-bio-sniff-btn"
              onClick={handleInspectBioSniff}
              className="w-full py-4 px-6 rounded-2xl bg-[#0F3D2E] hover:bg-[#14523E] text-white font-bold shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-3 text-base group cursor-pointer border border-emerald-800"
            >
              <Eye className="w-5 h-5 text-emerald-400 group-hover:scale-110 transition-transform" />
              <span>Inspect Bio-Sniff</span>
              <ArrowRight className="w-5 h-5 text-emerald-400 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

          {/* Right Column: Health Status (5 Cols) */}
          <div className="lg:col-span-5 space-y-4">
            
            {/* Health Status Box */}
            <div className={`rounded-3xl p-6 border shadow-xs transition-all ${
              isDiseaseDetected
                ? 'bg-gradient-to-b from-red-50/90 to-white border-red-200'
                : 'bg-gradient-to-b from-emerald-50/80 to-white border-emerald-200'
            }`}>
              
              {/* Header badge */}
              <div className="flex items-center justify-between pb-3 border-b border-gray-100">
                <span className="text-xs font-bold uppercase tracking-wider text-gray-500">
                  AI Plant Pathology Analysis
                </span>
                <span className={`px-3 py-1 rounded-full text-xs font-extrabold flex items-center gap-1.5 ${
                  isDiseaseDetected
                    ? 'bg-red-600 text-white'
                    : 'bg-emerald-600 text-white'
                }`}>
                  {isDiseaseDetected ? (
                    <>
                      <AlertCircle className="w-3.5 h-3.5" />
                      <span>DISEASE DETECTED</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>CROP HEALTHY</span>
                    </>
                  )}
                </span>
              </div>

              {/* Status Details */}
              <div className="mt-4 space-y-4">
                {isDiseaseDetected ? (
                  <>
                    <div>
                      <div className="text-xs text-red-600 font-semibold uppercase tracking-wide">
                        Target Pathogen Identified
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 mt-0.5">
                        {diseaseName}
                      </h3>
                      <div className="flex items-center gap-3 mt-1.5 text-xs text-gray-600">
                        <span>Confidence: <strong className="text-red-700">{confidenceScore}%</strong></span>
                        <span>•</span>
                        <span>Detected: <strong>{lastUpdate}</strong></span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-2.5 rounded-2xl bg-red-100/70 border border-red-200 shadow-xs hover:border-red-300 transition-colors">
                      <img
                        src={diseasedSymptomImg}
                        alt="Diseased Crop Foliar Lesion Symptom Reference"
                        className="w-20 h-16 sm:w-24 sm:h-16 rounded-xl object-cover border border-red-200 shrink-0 shadow-xs"
                      />
                      <div className="text-xs space-y-0.5">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-red-800">
                          Symptom Reference
                        </span>
                        <h4 className="font-bold text-red-950 text-xs">
                          Foliar Lesions
                        </h4>
                        <p className="text-[11px] text-red-900/90 leading-tight">
                          Elliptical volatile signatures & foliar spots.
                        </p>
                      </div>
                    </div>

                    <div className="p-3.5 rounded-xl bg-red-100/60 border border-red-200/80 text-xs space-y-1.5 text-red-950">
                      <div className="font-bold flex items-center justify-between">
                        <span>Affected Zone: {affectedZone}</span>
                        <span className="text-[10px] px-2 py-0.5 bg-red-700 text-white rounded-md font-semibold">Localization Active</span>
                      </div>
                      <p className="text-red-900/90 leading-relaxed">
                        Source triangulated at <strong>{diseaseSource?.coordinates.lat.toFixed(4)}° N, {diseaseSource?.coordinates.lng.toFixed(4)}° E</strong> using multi-node gas dispersion inversion.
                      </p>
                    </div>

                    <div className="space-y-1.5 text-xs">
                      <strong className="text-gray-900 block font-bold">Recommended Immediate Action:</strong>
                      <p className="text-gray-700 bg-gray-50 p-3 rounded-xl border border-gray-200 leading-relaxed">
                        {recommendedAction}
                      </p>
                    </div>
                  </>
                ) : (
                  <>
                    <div>
                      <div className="text-xs text-emerald-700 font-semibold uppercase tracking-wide">
                        Atmospheric Volatile Scan
                      </div>
                      <h3 className="text-2xl font-bold text-gray-900 mt-0.5">
                        No Pathogen Volatiles Detected
                      </h3>
                      <p className="text-xs text-gray-600 mt-1 leading-relaxed">
                        All field nodes report nominal baseline gas resistance signatures (120–160 kΩ). Plant physiological transpiration and respiration are operating under healthy parameters.
                      </p>
                    </div>

                    <div className="flex items-center gap-3 p-2.5 rounded-2xl bg-white border border-emerald-200 shadow-xs hover:border-emerald-300 transition-colors">
                      <img
                        src={healthyFoliageImg}
                        alt="Healthy Crop Foliage Visual Reference"
                        className="w-20 h-16 sm:w-24 sm:h-16 rounded-xl object-cover border border-emerald-100 shrink-0 shadow-xs"
                      />
                      <div className="text-xs space-y-0.5">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700">
                          Visual Reference
                        </span>
                        <h4 className="font-bold text-emerald-950 text-xs">
                          Healthy Foliage
                        </h4>
                        <p className="text-[11px] text-gray-600 leading-tight">
                          Lush canopy with zero foliar lesions or stress.
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3 pt-2">
                      <div className="p-3 rounded-xl bg-emerald-50/70 border border-emerald-100 text-xs">
                        <span className="text-gray-500 block text-[11px]">Pathogen Risk Index</span>
                        <strong className="text-emerald-800 text-base font-bold">Low (&lt;5%)</strong>
                      </div>
                      <div className="p-3 rounded-xl bg-emerald-50/70 border border-emerald-100 text-xs">
                        <span className="text-gray-500 block text-[11px]">Model Confidence</span>
                        <strong className="text-emerald-800 text-base font-bold">{confidenceScore}%</strong>
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-white border border-gray-200 text-xs text-gray-600 space-y-1">
                      <div className="font-semibold text-gray-900 flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span>Field Microclimate Optimal</span>
                      </div>
                      <p>
                        Current leaf temperature ({dashboardData.temperature}°C) and canopy humidity ({dashboardData.humidity}%) are within safe vegetative thresholds.
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>

          </div>

        </div>

      </main>
    </div>
  );
};
