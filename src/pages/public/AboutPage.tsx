import React from 'react';
import { PublicHeader } from '../../components/common/PublicHeader';
import { PublicFooter } from '../../components/common/PublicFooter';
import { CheckCircle2, Cpu, Wind, ShieldCheck, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';

export const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#F6F9F6] text-[#1A281E] flex flex-col font-sans">
      <PublicHeader />

      {/* Hero */}
      <section className="pt-16 pb-20 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <span className="text-xs font-bold uppercase tracking-widest text-emerald-800">Our Mission</span>
            <h1 className="font-serif-display text-4xl sm:text-5xl lg:text-6xl font-bold text-[#0F2D1F] mt-3 mb-6">
              Technology That Listens to Your Fields.
            </h1>
            <p className="text-lg text-[#476353] leading-relaxed">
              BIO-SNIFF was founded on a simple scientific insight: long before a pathogen produces visible discoloration or leaf decay, infected crop cells release distinct volatile organic signatures into the canopy air.
            </p>
          </div>
        </div>
      </section>

      {/* Core Technology Pillars */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-800">
                <Cpu className="w-6 h-6" />
              </div>
              <h3 className="font-serif-display text-3xl font-bold text-[#0F2D1F]">
                10-Channel Gas Resistance Matrix
              </h3>
              <p className="text-sm text-[#4E6857] leading-relaxed">
                Conventional visual cameras can only detect disease once necrotic lesions have already destroyed plant tissue. BIO-SNIFF deploys an array of 10 micro-machined metal oxide gas sensors (MOS) operating at stepped temperature setpoints to construct a high-dimensional chemical fingerprint of the field atmosphere.
              </p>
              <ul className="space-y-2 pt-2 text-xs text-gray-700">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Ultra-sensitive detection threshold down to single-digit parts-per-billion (ppb)</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Dynamic baseline compensation adjusting for ambient humidity and temperature</span>
                </li>
              </ul>
            </div>
            <div className="rounded-2xl overflow-hidden shadow-lg border border-gray-200">
              <img
                src="https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80"
                alt="Sensor Engineering"
                className="w-full h-80 object-cover"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center md:flex-row-reverse">
            <div className="rounded-2xl overflow-hidden shadow-lg border border-gray-200 order-2 md:order-1">
              <img
                src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80"
                alt="Open agricultural field"
                className="w-full h-80 object-cover"
              />
            </div>
            <div className="space-y-4 order-1 md:order-2">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-800">
                <Wind className="w-6 h-6" />
              </div>
              <h3 className="font-serif-display text-3xl font-bold text-[#0F2D1F]">
                Atmospheric Plume Triangulation
              </h3>
              <p className="text-sm text-[#4E6857] leading-relaxed">
                A reading alone is not enough—farmers need to know where the infection began. By factoring in real-time ultrasonic wind vectors (speed and azimuth) alongside spatial node gradient differentials, BIO-SNIFF reconstructs the upwind odor trajectory to pinpoint the disease epicenter down to a 20-meter radius.
              </p>
              <ul className="space-y-2 pt-2 text-xs text-gray-700">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Eliminates the cost and environmental hazard of blanket chemical spraying</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Enables localized micro-treatment of early focus zones</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 bg-[#0C2B1D] text-white">
        <div className="max-w-4xl mx-auto px-4 text-center space-y-6">
          <p className="font-handwritten text-3xl text-emerald-200">
            “Healthy fields, brighter tomorrows.”
          </p>
          <h2 className="font-serif-display text-3xl sm:text-4xl font-bold">
            Ready to deploy electronic nose monitoring on your farm?
          </h2>
          <div className="pt-2">
            <Link
              to="/farmer/overview"
              className="inline-block px-8 py-3.5 bg-emerald-500 hover:bg-emerald-400 text-gray-950 font-bold rounded-xl shadow-lg transition"
            >
              Experience The Interactive Dashboard
            </Link>
          </div>
        </div>
      </section>

      <PublicFooter />
    </div>
  );
};
