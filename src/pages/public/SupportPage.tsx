import React, { useState } from 'react';
import { PublicHeader } from '../../components/common/PublicHeader';
import { PublicFooter } from '../../components/common/PublicFooter';
import { HelpCircle, Phone, Mail, FileQuestion, CheckCircle2, Send } from 'lucide-react';

export const SupportPage: React.FC = () => {
  const [submitted, setSubmitted] = useState(false);

  return (
    <div className="min-h-screen bg-[#F6F9F6] text-[#1A281E] flex flex-col font-sans">
      <PublicHeader />

      <section className="pt-16 pb-20 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <span className="text-xs font-bold uppercase tracking-widest text-emerald-800">Support & Guides</span>
            <h1 className="font-serif-display text-4xl sm:text-5xl lg:text-6xl font-bold text-[#0F2D1F] mt-3 mb-6">
              How Can We Help Your Farm?
            </h1>
            <p className="text-lg text-[#476353] leading-relaxed">
              Find quick answers about node installation, reading interpretation, SIM connectivity, and agricultural advisories.
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* FAQ Column */}
          <div className="lg:col-span-2 space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 font-serif-display">Frequently Asked Questions</h2>
            
            <div className="space-y-4">
              <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs">
                <h3 className="font-bold text-base text-gray-900 mb-2">How high should the BIO-SNIFF nodes be mounted?</h3>
                <p className="text-xs text-gray-600 leading-relaxed">
                  Nodes should be mounted 30 to 50 cm above the crop canopy level. For paddy at the tillering stage, 1.2 meters above ground level ensures optimal sampling of rising volatile plumes.
                </p>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs">
                <h3 className="font-bold text-base text-gray-900 mb-2">What happens if 5G cellular coverage is weak?</h3>
                <p className="text-xs text-gray-600 leading-relaxed">
                  BIO-SNIFF nodes feature localized flash buffer storage capable of holding 14 days of high-frequency sensor readings. If cellular connection drops, readings queue and automatically synchronize once 5G/4G connectivity is restored.
                </p>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs">
                <h3 className="font-bold text-base text-gray-900 mb-2">How accurate is the disease localization?</h3>
                <p className="text-xs text-gray-600 leading-relaxed">
                  With a standard 3-node triangular layout on a 4-to-5 acre plot, the plume inversion algorithm locates the infection epicenter within a radius of 15–20 meters.
                </p>
              </div>
            </div>
          </div>

          {/* Contact Form Column */}
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs space-y-5 h-fit">
            <h3 className="text-xl font-bold text-gray-900 font-serif-display">Field Support Hotline</h3>
            <p className="text-xs text-gray-600">
              Need technical assistance or on-site node diagnostics? Submit your inquiry below:
            </p>

            {submitted ? (
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs space-y-2">
                <div className="flex items-center gap-2 font-bold">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Request Received</span>
                </div>
                <p>An agronomist will contact you within 2 hours at your registered mobile number.</p>
              </div>
            ) : (
              <form onSubmit={(e) => { e.preventDefault(); setSubmitted(true); }} className="space-y-3 text-xs">
                <div>
                  <label className="block text-gray-700 font-semibold mb-1">Farmer Name</label>
                  <input required placeholder="Ravi Kumar" className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-hidden" />
                </div>
                <div>
                  <label className="block text-gray-700 font-semibold mb-1">Mobile Number</label>
                  <input required placeholder="98765 43210" className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-hidden" />
                </div>
                <div>
                  <label className="block text-gray-700 font-semibold mb-1">Node ID (Optional)</label>
                  <input placeholder="BSN-01" className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-hidden" />
                </div>
                <div>
                  <label className="block text-gray-700 font-semibold mb-1">Issue Description</label>
                  <textarea required rows={3} placeholder="Describe the issue or reading question..." className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-hidden" />
                </div>
                <button type="submit" className="w-full py-2.5 bg-[#0F3D2E] text-white font-bold rounded-lg hover:bg-[#14523E] transition flex items-center justify-center gap-2">
                  <Send className="w-3.5 h-3.5" />
                  <span>Submit Ticket</span>
                </button>
              </form>
            )}

            <div className="pt-4 border-t border-gray-100 text-xs text-gray-500 space-y-1">
              <div>Toll-free Kisan Helpline: <strong>1800-BIO-SNIFF</strong></div>
              <div>Operating hours: <strong>6:00 AM – 8:00 PM IST</strong></div>
            </div>
          </div>
        </div>
      </section>

      <PublicFooter />
    </div>
  );
};
