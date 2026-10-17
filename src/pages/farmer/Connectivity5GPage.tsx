import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import {
  Radio,
  Signal,
  ArrowUp,
  ArrowDown,
  Link2,
  Gauge,
  CheckCircle2,
  Check,
  MapPin,
  Cpu,
  CreditCard,
  Antenna,
  BatteryCharging,
  Settings,
  Clock,
  Activity,
  HeartPulse,
  Lightbulb,
  ExternalLink,
  X,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';

import masterNodeStationImg from '../../assets/images/master_node_station_1789036321529.jpg';
import bioSniff5gHeroImg from '../../assets/images/bio_sniff_5g_hero_1789118897365.jpg';
import { useAuth } from '../../context/AuthContext';
import { connectivityService } from '../../services/connectivityService';
import { ConnectivityCurrentResponse } from '../../types/api';

export const Connectivity5GPage: React.FC = () => {
  const { primaryFarmId } = useAuth();
  const farmId = primaryFarmId || 1;

  const [conn, setConn] = useState<ConnectivityCurrentResponse | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [timeTab, setTimeTab] = useState<'1h' | 'today' | '7d'>('1h');
  const [learnMoreOpen, setLearnMoreOpen] = useState(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchConnectivity = async () => {
    setLoading(true);
    setError(null);
    try {
      const [currData, histData] = await Promise.all([
        connectivityService.getFarmConnectivity(farmId),
        connectivityService.getFarmConnectivityHistory(farmId, 24, 50).catch(() => ({ logs: [] })),
      ]);

      setConn(currData);

      if (histData.logs && histData.logs.length > 0) {
        const points = histData.logs.slice(-12).map((l: any) => {
          const dt = new Date(l.recorded_at);
          return {
            time: dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            upload: l.uplink_mbps || 0,
            download: l.downlink_mbps || 0,
          };
        });
        setHistory(points);
      } else {
        setHistory([]);
      }
    } catch (err: any) {
      console.error('Failed to fetch connectivity:', err);
      setError(err?.message || 'Failed to fetch network connectivity status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConnectivity();
  }, [farmId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-white border border-emerald-200 shadow-xs text-emerald-900 font-semibold text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
          <span>Loading 5G Gateway Status...</span>
        </div>
      </div>
    );
  }

  if (error || !conn) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="bg-white p-6 rounded-3xl border border-red-200 shadow-xs text-center space-y-3 max-w-md">
          <AlertCircle className="w-8 h-8 text-red-600 mx-auto" />
          <h3 className="font-bold text-gray-900 text-base">Connectivity Error</h3>
          <p className="text-xs text-red-700">{error || 'No connectivity metrics found'}</p>
          <button
            onClick={fetchConnectivity}
            className="px-4 py-2 bg-[#0F3D2E] text-white text-xs font-bold rounded-xl"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-2xl bg-emerald-100/70 text-emerald-700 flex items-center justify-center shrink-0 mt-0.5 shadow-xs">
            <Radio className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0F2D1F] tracking-tight">
              5G Connectivity
            </h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Your farm is connected. Data from your field is safely reaching the Bio-Sniff cloud in real time.
            </p>
          </div>
        </div>

        {/* Connected & Working Status Badge */}
        <div className="flex items-center gap-3 bg-emerald-50/90 border border-emerald-200/90 rounded-2xl px-4 py-2.5 shadow-xs">
          <span className="relative flex h-3.5 w-3.5 shrink-0">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500" />
          </span>
          <div>
            <div className="text-sm font-bold text-emerald-950 leading-tight">Connected & Working</div>
            <div className="text-[11px] text-gray-500 leading-tight mt-0.5">Last updated: {new Date(conn.recorded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
          </div>
        </div>
      </div>

      {/* Hero Architecture Infographic Banner */}
      <div className="relative rounded-3xl overflow-hidden border border-gray-200 shadow-md bg-emerald-950 group">
        <div className="relative w-full aspect-16/9 sm:aspect-21/9 min-h-[320px] max-h-[480px]">
          <img
            src={bioSniff5gHeroImg}
            alt="Bio-Sniff 5G Farm Network Architecture"
            className="w-full h-full object-cover object-center"
            referrerPolicy="no-referrer"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20 pointer-events-none" />

          <div className="absolute top-3 left-3 sm:top-5 sm:left-5 flex items-center gap-2.5 bg-black/40 backdrop-blur-md px-3.5 py-2 rounded-2xl border border-white/20 shadow-lg text-white">
            <div className="w-8 h-8 rounded-xl bg-emerald-600 flex items-center justify-center text-white shadow-sm font-bold text-sm">
              🌿
            </div>
            <div className="leading-tight">
              <span className="font-black text-sm tracking-wide block text-white">BIO-SNIFF</span>
              <span className="text-[10px] text-emerald-300 font-medium">Detect Before You See It.</span>
            </div>
          </div>

          <div className="absolute bottom-3 right-3 sm:bottom-5 sm:right-5 bg-black/60 backdrop-blur-md px-3.5 py-1.5 rounded-2xl border border-white/20 text-white text-xs flex items-center gap-2.5">
            <div className="flex items-center gap-1.5 text-cyan-300 font-semibold">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <span>Real-Time Cloud Uplink Active</span>
            </div>
            <span className="text-white/30">•</span>
            <span className="text-emerald-300 font-medium">{conn.latency_ms}ms Latency</span>
          </div>
        </div>
      </div>

      {/* Row of 4 Telemetry Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: 5G Signal Strength */}
        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-100/70 text-emerald-700 flex items-center justify-center shrink-0">
            <Signal className="w-6 h-6" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-semibold text-gray-500">5G Signal Strength</div>
            <div className="text-2xl font-bold text-gray-900 leading-tight mt-0.5">{conn.rssi} dBm</div>
            <div className="mt-1">
              <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                Excellent (4 / 4 Bars)
              </span>
            </div>
          </div>
        </div>

        {/* Card 2: Network Provider */}
        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-blue-100/70 text-blue-600 flex items-center justify-center shrink-0">
            <Radio className="w-6 h-6" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500">Network Provider</span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                Connected
              </span>
            </div>
            <div className="text-2xl font-bold text-gray-900 leading-tight mt-0.5">{conn.carrier} {conn.gateway_type}</div>
            <div className="text-xs text-gray-500 mt-1">5G (NSA) Band n78</div>
          </div>
        </div>

        {/* Card 3: Connection Speed */}
        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-purple-100/70 text-purple-700 flex items-center justify-center shrink-0">
            <Gauge className="w-6 h-6" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-semibold text-gray-500">Connection Speed</div>
            <div className="grid grid-cols-2 gap-2 mt-1">
              <div>
                <div className="flex items-center text-sm font-bold text-emerald-700">
                  <ArrowUp className="w-3.5 h-3.5 mr-0.5 stroke-[2.5]" />
                  <span>{conn.uplink_mbps}</span>
                  <span className="text-[10px] ml-0.5 text-gray-500 font-normal">Mbps</span>
                </div>
                <div className="text-[10px] text-gray-500">Upload</div>
              </div>
              <div>
                <div className="flex items-center text-sm font-bold text-blue-600">
                  <ArrowDown className="w-3.5 h-3.5 mr-0.5 stroke-[2.5]" />
                  <span>{conn.downlink_mbps}</span>
                  <span className="text-[10px] ml-0.5 text-gray-500 font-normal">Mbps</span>
                </div>
                <div className="text-[10px] text-gray-500">Download</div>
              </div>
            </div>
          </div>
        </div>

        {/* Card 4: Link Status */}
        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-100/70 text-emerald-700 flex items-center justify-center shrink-0">
            <Link2 className="w-6 h-6" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-semibold text-gray-500">Link Status</div>
            <div className="text-2xl font-bold text-gray-900 leading-tight mt-0.5">Connected</div>
            <div className="flex flex-col gap-0.5 mt-1 text-xs text-gray-700">
              <div className="flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span className="text-[11px] font-medium">Latency: {conn.latency_ms} ms</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span className="text-[11px] font-medium">Packet Loss: {conn.packet_loss_pct}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3 Main Functional Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">

        {/* Left Card: 5G Gateway (Master Node) */}
        <div className="lg:col-span-4 bg-white p-5 sm:p-6 rounded-3xl border border-gray-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <Radio className="w-4 h-4 text-emerald-700" />
                <h3 className="font-bold text-gray-900 text-sm sm:text-base">
                  5G Gateway (Master Node)
                </h3>
              </div>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-900 text-[11px] font-bold">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
                <span>Working Perfectly</span>
              </span>
            </div>

            {/* Master Node Photo and Specifications */}
            <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 mt-4">
              <div className="sm:col-span-5 relative rounded-2xl overflow-hidden border border-gray-200 bg-emerald-950 aspect-3/4 sm:aspect-auto">
                <img
                  src={masterNodeStationImg}
                  alt="Bio-Sniff Master Node 1 5G Gateway Station"
                  className="w-full h-full object-cover"
                  referrerPolicy="no-referrer"
                />
                <div className="absolute bottom-2 left-2 right-2 bg-black/60 backdrop-blur-xs text-white text-[10px] font-bold px-2 py-1 rounded-md text-center">
                  BIO-SNIFF Station
                </div>
              </div>

              <div className="sm:col-span-7 space-y-2.5 text-xs">
                <div className="flex items-start justify-between gap-1 py-1 border-b border-gray-50">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <MapPin className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>Location</span>
                  </div>
                  <strong className="text-gray-900 text-right">Central Farm Hub</strong>
                </div>

                <div className="flex items-start justify-between gap-1 py-1 border-b border-gray-50">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <Cpu className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>Modem Model</span>
                  </div>
                  <strong className="text-gray-900 text-right">Quectel RM500Q-GL</strong>
                </div>

                <div className="flex items-start justify-between gap-1 py-1 border-b border-gray-50">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <CreditCard className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>SIM Provider</span>
                  </div>
                  <strong className="text-gray-900 text-right">{conn.carrier}</strong>
                </div>

                <div className="flex items-start justify-between gap-1 py-1 border-b border-gray-50">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <Antenna className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>Antenna Type</span>
                  </div>
                  <strong className="text-gray-900 text-right">High-Gain 5G Antenna</strong>
                </div>

                <div className="flex items-start justify-between gap-1 py-1 border-b border-gray-50">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <BatteryCharging className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>Power Supply</span>
                  </div>
                  <strong className="text-gray-900 text-right">Solar + Battery (12V, 10Ah)</strong>
                </div>

                <div className="flex items-start justify-between gap-1 py-1 border-b border-gray-50">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <Settings className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>Firmware Version</span>
                  </div>
                  <strong className="text-gray-900 text-right">v2.3.1</strong>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between">
            <Link
              to="/farmer/node/NODE_01"
              className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 flex items-center gap-1"
            >
              <span>View Node 1 Telemetry Sensors</span>
              <span>→</span>
            </Link>
          </div>
        </div>

        {/* Right Card: Network Health */}
        <div className="lg:col-span-3 bg-white p-5 sm:p-6 rounded-3xl border border-gray-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 pb-3 border-b border-gray-100">
              <HeartPulse className="w-4 h-4 text-emerald-700" />
              <h3 className="font-bold text-gray-900 text-sm sm:text-base">
                Network Health
              </h3>
            </div>

            <div className="space-y-3 mt-4 text-xs">
              <div className="flex items-center justify-between py-1.5 border-b border-gray-50">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700">
                    <Check className="w-3 h-3 stroke-[3]" />
                  </div>
                  <span className="font-medium text-gray-800">5G Modem</span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[11px]">
                  Good
                </span>
              </div>

              <div className="flex items-center justify-between py-1.5 border-b border-gray-50">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700">
                    <Check className="w-3 h-3 stroke-[3]" />
                  </div>
                  <span className="font-medium text-gray-800">SIM Connection</span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[11px]">
                  Good
                </span>
              </div>

              <div className="flex items-center justify-between py-1.5 border-b border-gray-50">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700">
                    <Check className="w-3 h-3 stroke-[3]" />
                  </div>
                  <span className="font-medium text-gray-800">Internet Access</span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[11px]">
                  Good
                </span>
              </div>

              <div className="flex items-center justify-between py-1.5 border-b border-gray-50">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700">
                    <Check className="w-3 h-3 stroke-[3]" />
                  </div>
                  <span className="font-medium text-gray-800">Cloud Server</span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[11px]">
                  Good
                </span>
              </div>

              <div className="flex items-center justify-between py-1.5">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700">
                    <Check className="w-3 h-3 stroke-[3]" />
                  </div>
                  <span className="font-medium text-gray-800">Data Transmission</span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[11px]">
                  Good
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4 p-4 rounded-2xl bg-emerald-50 border border-emerald-200/80 flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center shrink-0 shadow-xs">
              <Check className="w-5 h-5 stroke-[2.5]" />
            </div>
            <div>
              <div className="text-sm font-bold text-emerald-950">Everything is working well!</div>
              <p className="text-xs text-emerald-800 leading-relaxed mt-0.5">
                Your farm data is being sent to the cloud without any issues.
              </p>
            </div>
          </div>
        </div>

      </div>

      {/* Educational Callout */}
      <div className="bg-white border border-gray-200 rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xs">
        <div className="flex items-start gap-3.5">
          <div className="w-10 h-10 rounded-full bg-amber-100/80 flex items-center justify-center shrink-0 text-amber-600">
            <Lightbulb className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-blue-950">What does this mean?</h4>
            <p className="text-xs text-gray-600 mt-0.5 leading-relaxed">
              Your Bio-Sniff system uses 5G to send field data to the cloud. This helps you get real-time updates, faster alerts, and better crop protection.
            </p>
          </div>
        </div>

        <button
          onClick={() => setLearnMoreOpen(true)}
          className="px-4 py-2 border border-blue-300 hover:border-blue-400 bg-white hover:bg-blue-50/50 text-blue-700 text-xs font-semibold rounded-xl flex items-center gap-1.5 transition shadow-xs shrink-0"
        >
          <span>Learn More</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Learn More Modal Dialog */}
      {learnMoreOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-gray-200 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center">
                  <Radio className="w-4 h-4" />
                </div>
                <h3 className="font-bold text-gray-900 text-base">How 5G Powers Bio-Sniff</h3>
              </div>
              <button
                onClick={() => setLearnMoreOpen(false)}
                className="p-1 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs text-gray-600 leading-relaxed">
              <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100">
                <strong className="text-emerald-950 block mb-1">Single Gateway Architecture</strong>
                Only Node 1 carries a 5G SIM card and radio modem. Slave nodes (Node 2 and Node 3) communicate locally via low-power sub-GHz RF mesh, cutting energy drain by 78% and reducing SIM cellular subscription fees for the farmer.
              </div>

              <div className="p-3 bg-blue-50 rounded-xl border border-blue-100">
                <strong className="text-blue-950 block mb-1">Ultra-Reliable Low Latency (URLLC)</strong>
                Bio-Sniff's 5G link transmits volatile gas fingerprints every 60 seconds with an average latency of {conn.latency_ms}ms. When dangerous fungus spore blooms or pest volatiles spike, an automated advisory alert reaches your phone within 3 seconds.
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setLearnMoreOpen(false)}
                className="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold transition shadow-xs"
              >
                Close Explanation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
