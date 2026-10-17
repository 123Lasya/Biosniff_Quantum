import React from 'react';
import { PublicHeader } from '../../components/common/PublicHeader';
import { PublicFooter } from '../../components/common/PublicFooter';
import { TrendingUp, ShieldCheck, Sprout, Users, CheckCircle2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const ImpactPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#F6F9F6] text-[#1A281E] flex flex-col font-sans">
      <PublicHeader />

      {/* Hero */}
      <section className="pt-16 pb-20 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <span className="text-xs font-bold uppercase tracking-widest text-emerald-800">Field Impact</span>
            <h1 className="font-serif-display text-4xl sm:text-5xl lg:text-6xl font-bold text-[#0F2D1F] mt-3 mb-6">
              Measurable Outcomes for Indian Agriculture.
            </h1>
            <p className="text-lg text-[#476353] leading-relaxed">
              Early warning is the single highest leverage point in crop disease management. Here is how BIO-SNIFF is transforming economic stability and environmental health for farmers across the nation.
            </p>
          </div>
        </div>
      </section>

      {/* Big Impact Numbers */}
      <section className="py-16 bg-[#0F3D2E] text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
            <div className="space-y-2">
              <div className="font-serif-display text-4xl sm:text-5xl font-extrabold text-emerald-300">₹42 Cr+</div>
              <div className="text-xs sm:text-sm text-emerald-100/80 font-medium">Estimated Crop Loss Prevented</div>
            </div>
            <div className="space-y-2">
              <div className="font-serif-display text-4xl sm:text-5xl font-extrabold text-emerald-300">65%</div>
              <div className="text-xs sm:text-sm text-emerald-100/80 font-medium">Fungicide Application Reduction</div>
            </div>
            <div className="space-y-2">
              <div className="font-serif-display text-4xl sm:text-5xl font-extrabold text-emerald-300">18,256</div>
              <div className="text-xs sm:text-sm text-emerald-100/80 font-medium">Farms Continuously Protected</div>
            </div>
            <div className="space-y-2">
              <div className="font-serif-display text-4xl sm:text-5xl font-extrabold text-emerald-300">24,921</div>
              <div className="text-xs sm:text-sm text-emerald-100/80 font-medium">Solar 5G Nodes in Field</div>
            </div>
          </div>
        </div>
      </section>

      {/* Case Studies */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
            <span className="text-xs font-bold uppercase tracking-widest text-emerald-800">Field Studies</span>
            <h2 className="font-serif-display text-3xl sm:text-4xl font-bold text-[#0F2D1F]">
              Real Stories from the Ground
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-xs space-y-4">
              <span className="text-xs font-bold text-emerald-800 bg-emerald-50 px-3 py-1 rounded-full">Paddy Blast Prevention</span>
              <h3 className="font-bold text-lg text-gray-900">Ahmednagar, Maharashtra</h3>
              <p className="text-xs text-gray-600 leading-relaxed">
                Detected elevated terpene and alcohol esters 70 hours ahead of visible leaf blast lesions in tillering stage rice, allowing selective spot spraying on only 0.8 acres.
              </p>
              <div className="pt-2 border-t border-gray-100 text-xs font-semibold text-emerald-800 flex justify-between">
                <span>Yield preserved: 96%</span>
                <span>Chemical savings: ₹18,000</span>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-xs space-y-4">
              <span className="text-xs font-bold text-amber-800 bg-amber-50 px-3 py-1 rounded-full">Wheat Rust Warning</span>
              <h3 className="font-bold text-lg text-gray-900">Ludhiana, Punjab</h3>
              <p className="text-xs text-gray-600 leading-relaxed">
                Identified microclimate humidity traps and early fungal VOC plume in high-density wheat fields. The farmer avoided 2 full blanket rounds of generic fungicide.
              </p>
              <div className="pt-2 border-t border-gray-100 text-xs font-semibold text-emerald-800 flex justify-between">
                <span>Yield preserved: 98%</span>
                <span>Chemical savings: ₹26,500</span>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-xs space-y-4">
              <span className="text-xs font-bold text-blue-800 bg-blue-50 px-3 py-1 rounded-full">Sugarcane Red Rot Alert</span>
              <h3 className="font-bold text-lg text-gray-900">Mandya, Karnataka</h3>
              <p className="text-xs text-gray-600 leading-relaxed">
                Localized a persistent VOC fermentation signature indicating early internal cane rotting before the stalks became brittle, safeguarding 16 acres of prime harvest.
              </p>
              <div className="pt-2 border-t border-gray-100 text-xs font-semibold text-emerald-800 flex justify-between">
                <span>Yield preserved: 94%</span>
                <span>Chemical savings: ₹41,000</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <PublicFooter />
    </div>
  );
};
