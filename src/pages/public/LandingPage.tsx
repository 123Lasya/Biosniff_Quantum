import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  ShieldCheck,
  Zap,
  Activity,
  Cpu,
  Wifi,
  CloudSun,
  CheckCircle2,
  Play,
  TrendingUp,
  Clock,
  Compass,
} from 'lucide-react';
import { PublicHeader } from '../../components/common/PublicHeader';
import { PublicFooter } from '../../components/common/PublicFooter';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#F6F9F6] text-[#1A281E] flex flex-col font-sans">
      <PublicHeader />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28 border-b border-emerald-900/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Column: Heading & CTAs */}
            <div className="lg:col-span-7 space-y-8">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-100/80 border border-emerald-300/60 text-emerald-900 text-xs font-semibold tracking-wide">
                <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
                <span>Next-Gen AgTech Electronic Nose</span>
              </div>

              <h1 className="font-serif-display text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-[#0F2D1F] leading-[1.05]">
                Detect Crop Diseases Before They Spread.
              </h1>

              <p className="text-lg sm:text-xl text-[#3A5344] leading-relaxed max-w-2xl">
                Using cutting-edge electronic nose technology, BIO-SNIFF captures plant volatile organic compounds (VOCs) in real-time, detecting fungal and bacterial infections days before visible symptoms appear.
              </p>

              <div className="flex flex-wrap items-center gap-4 pt-2">
                <Link
                  to="/signup"
                  className="flex items-center gap-2.5 px-7 py-3.5 rounded-xl bg-[#0F3D2E] hover:bg-[#14523E] text-white font-semibold shadow-md hover:shadow-lg transition-all text-base"
                >
                  <span>Get Started</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  to="/farmer/overview"
                  className="flex items-center gap-2 px-6 py-3.5 rounded-xl border border-gray-300 bg-white hover:bg-gray-50 text-[#0F3D2E] font-semibold transition text-base shadow-xs"
                >
                  <Play className="w-4 h-4 text-emerald-700 fill-emerald-700" />
                  <span>Explore Live Farm Demo</span>
                </Link>
              </div>

              {/* Key Proof Metrics */}
              <div className="pt-8 border-t border-emerald-900/10 grid grid-cols-3 gap-6">
                <div>
                  <div className="text-3xl lg:text-4xl font-extrabold text-[#0F2D1F] font-serif-display">94.8%</div>
                  <div className="text-xs sm:text-sm text-[#4E6857] mt-1 font-medium">Early detection accuracy</div>
                </div>
                <div>
                  <div className="text-3xl lg:text-4xl font-extrabold text-[#0F2D1F] font-serif-display">48-72h</div>
                  <div className="text-xs sm:text-sm text-[#4E6857] mt-1 font-medium">Before visible lesions</div>
                </div>
                <div>
                  <div className="text-3xl lg:text-4xl font-extrabold text-[#0F2D1F] font-serif-display">35%</div>
                  <div className="text-xs sm:text-sm text-[#4E6857] mt-1 font-medium">Crop loss prevented</div>
                </div>
              </div>
            </div>

            {/* Right Column: Hero Visual Graphic */}
            <div className="lg:col-span-5 relative">
              <div className="relative rounded-3xl overflow-hidden shadow-2xl border border-emerald-900/15 aspect-4/3 lg:aspect-square">
                <img
                  src="https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&w=1000&q=80"
                  alt="Lush Paddy Fields"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto space-y-4">
            <span className="text-xs font-bold uppercase tracking-widest text-emerald-800">The Bio-Sniff Advantage</span>
            <h2 className="font-serif-display text-4xl sm:text-5xl font-bold text-[#0F2D1F]">
              How Plant Odor Reveals Invisible Diseases
            </h2>
            <p className="text-base text-[#476353] leading-relaxed">
              Plants emit a distinct cocktail of volatile organic compounds when attacked by pathogens. Our patented sensor topology sniffs these chemical plumes long before leaves turn yellow or spotty.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
            {/* Step 1 */}
            <div className="rounded-2xl border border-emerald-900/10 bg-[#F8FAF8] p-7 space-y-4 hover:shadow-md transition">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-800">
                <Activity className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-[#0F2D1F]">1. VOC Plume Capture</h3>
              <p className="text-sm text-[#4E6857] leading-relaxed">
                Solar-powered field nodes sniff air continuously using multi-channel metal oxide gas sensors that respond to minute ppb-level changes in chemical volatiles.
              </p>
            </div>

            {/* Step 2 */}
            <div className="rounded-2xl border border-emerald-900/10 bg-[#F8FAF8] p-7 space-y-4 hover:shadow-md transition">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-800">
                <Zap className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-[#0F2D1F]">2. Machine Learning Diagnosis</h3>
              <p className="text-sm text-[#4E6857] leading-relaxed">
                Pre-trained botanical ML models analyze the 10-channel resistance profile, matching patterns to specific threats such as Blast, Blight, or Stem Rot.
              </p>
            </div>

            {/* Step 3 */}
            <div className="rounded-2xl border border-emerald-900/10 bg-[#F8FAF8] p-7 space-y-4 hover:shadow-md transition">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-800">
                <Compass className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-[#0F2D1F]">3. Pinpoint Field Localization</h3>
              <p className="text-sm text-[#4E6857] leading-relaxed">
                By combining gas gradient measurements with real-time wind speed and direction, BIO-SNIFF calculates the precise GPS coordinate of the infection source.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Hardware & Sensor Deep Dive */}
      <section className="py-20 bg-[#F1F6F2] border-y border-emerald-900/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <span className="text-xs font-bold uppercase tracking-widest text-emerald-800">Hardware Engineering</span>
              <h2 className="font-serif-display text-4xl sm:text-5xl font-bold text-[#0F2D1F] mt-2 mb-6">
                Built for the Rigors of the Modern Farm
              </h2>
              <p className="text-base text-[#476353] leading-relaxed mb-8">
                Engineered from the ground up for Indian agricultural conditions, BIO-SNIFF field nodes withstand monsoon rains, intense heatwaves, and dust storms while maintaining laboratory-grade precision.
              </p>

              <div className="space-y-4">
                <div className="flex items-start gap-3.5">
                  <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-sm text-gray-900 block">Solar-Powered with 7-Day Battery Backup</strong>
                    <span className="text-xs text-gray-600">Operates continuously even through heavy monsoons or extended cloud cover.</span>
                  </div>
                </div>

                <div className="flex items-start gap-3.5">
                  <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-sm text-gray-900 block">Bosch BME688 + Custom 10-Channel Array</strong>
                    <span className="text-xs text-gray-600">Simultaneous readings of temperature, relative humidity, barometric pressure, and VOC gas resistance.</span>
                  </div>
                </div>

                <div className="flex items-start gap-3.5">
                  <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-sm text-gray-900 block">5G Ultra-Low Latency & Mesh Resilience</strong>
                    <span className="text-xs text-gray-600">Transmits continuous telemetry over commercial 5G networks with automated packet queueing in low-signal zones.</span>
                  </div>
                </div>
              </div>

              <div className="mt-8">
                <Link
                  to="/farmer/nodes"
                  className="inline-flex items-center gap-2 text-sm font-semibold text-emerald-900 hover:text-emerald-700"
                >
                  <span>Inspect Hardware Node Telemetry</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>

            <div className="rounded-3xl overflow-hidden shadow-xl border border-gray-200 bg-white p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                <div>
                  <h4 className="font-bold text-gray-900">Node BSN-01 Telemetry</h4>
                  <p className="text-xs text-gray-500">Ahmednagar Field • Sector A</p>
                </div>
                <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold">100% Operational</span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <span className="text-[11px] text-gray-500 block">Battery</span>
                  <strong className="text-lg text-emerald-700 font-bold">94%</strong>
                </div>
                <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <span className="text-[11px] text-gray-500 block">Temperature</span>
                  <strong className="text-lg text-gray-900 font-bold">28.4°C</strong>
                </div>
                <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <span className="text-[11px] text-gray-500 block">Humidity</span>
                  <strong className="text-lg text-gray-900 font-bold">74%</strong>
                </div>
                <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <span className="text-[11px] text-gray-500 block">Signal (5G)</span>
                  <strong className="text-lg text-emerald-700 font-bold">-76 dBm</strong>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-emerald-900 text-white flex items-center justify-between">
                <div>
                  <div className="text-xs text-emerald-300">Gas Resistance Baseline</div>
                  <div className="text-sm font-semibold">124.6 kΩ (Stable Normal)</div>
                </div>
                <Link
                  to="/farmer/system"
                  className="px-3.5 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-xs font-semibold text-white transition"
                >
                  View Details
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Farmer Testimonial */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 text-center space-y-6">
          <div className="w-16 h-16 mx-auto rounded-full overflow-hidden border-2 border-emerald-500 shadow-md">
            <img
              src="https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=150&q=80"
              alt="Farmer Ramesh Patil"
              className="w-full h-full object-cover"
            />
          </div>
          <p className="font-serif-display text-2xl sm:text-3xl text-[#0F2D1F] italic leading-relaxed">
            “BIO-SNIFF alerted us to Blast disease 3 days before any lesions appeared on the leaves. We sprayed only 1 acre instead of the whole 12 acres, saving ₹18,000 on chemicals and protecting our paddy harvest.”
          </p>
          <div>
            <strong className="block text-gray-900 font-bold text-base">Ramesh Patil</strong>
            <span className="text-xs text-emerald-700 font-medium">Progressive Farmer • Shirur, Pune District, Maharashtra</span>
          </div>
        </div>
      </section>

      {/* CTA Bottom Banner */}
      <section className="py-16 bg-[#0F3D2E] text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          <h2 className="font-serif-display text-4xl sm:text-5xl font-bold">
            Protect Your Crops Before Visible Damage Occurs
          </h2>
          <p className="text-emerald-200 text-base max-w-2xl mx-auto leading-relaxed">
            Experience the future of farm health monitoring today. Get started as a farmer or preview the administrator network.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link
              to="/signup"
              className="px-8 py-3.5 rounded-xl bg-white text-[#0F3D2E] hover:bg-gray-100 font-bold transition shadow-lg"
            >
              Start Free Registration
            </Link>
            <Link
              to="/farmer/overview"
              className="px-8 py-3.5 rounded-xl bg-emerald-800 hover:bg-emerald-700 text-white font-semibold transition border border-emerald-600"
            >
              Explore Live Farmer View
            </Link>
          </div>
        </div>
      </section>

      <PublicFooter />
    </div>
  );
};
