import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  User,
  Phone,
  MapPin,
  Sprout,
  Lock,
  Mail,
  Upload,
  Compass,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  LandPlot,
  ShieldCheck,
  Camera,
} from 'lucide-react';
import { BioSniffLogo } from '../../components/common/BioSniffLogo';
import { authService } from '../../services/authService';
import { farmService } from '../../services/farmService';
import { useAuth } from '../../context/AuthContext';

export const SignUpPage: React.FC = () => {
  const navigate = useNavigate();
  const { refreshSession } = useAuth();

  // Active form section: 1 (Account), 2 (Farm Info), 3 (Location)
  const [activeStep, setActiveStep] = useState<number>(1);

  // Form State
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Profile Photo Upload State
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  // Farm Details State
  const [farmName, setFarmName] = useState('');
  const [crop, setCrop] = useState('Rice (Paddy)');
  const [cropVariety, setCropVariety] = useState('');
  const [area, setArea] = useState('5.0');
  const [address, setAddress] = useState('');
  const [state, setState] = useState('Maharashtra');
  const [district, setDistrict] = useState('Ahmednagar');

  // Location Details State
  const [latitude, setLatitude] = useState<number>(19.8321);
  const [longitude, setLongitude] = useState<number>(74.6521);
  const [boundaryGeoJson, setBoundaryGeoJson] = useState('');
  const [isGettingLocation, setIsGettingLocation] = useState(false);

  // UI State
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handle Photo Selection
  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
      if (!validTypes.includes(file.type)) {
        setError('Please select a valid image file (JPEG, PNG, WEBP, or GIF).');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setError('Profile picture file size must be less than 5MB.');
        return;
      }
      setAvatarFile(file);
      setAvatarPreview(URL.createObjectURL(file));
    }
  };

  // Browser Geolocation Retrieval
  const handleDetectLocation = () => {
    if (!navigator.geolocation) {
      setError('Browser geolocation is not supported by your device.');
      return;
    }
    setIsGettingLocation(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLatitude(parseFloat(position.coords.latitude.toFixed(6)));
        setLongitude(parseFloat(position.coords.longitude.toFixed(6)));
        setIsGettingLocation(false);
      },
      (err) => {
        console.warn('Geolocation error:', err);
        setError('Could not retrieve current location. Please enter coordinates manually.');
        setIsGettingLocation(false);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  // Form Validation Before Step Progression / Submission
  const validateCurrentStep = (): boolean => {
    setError(null);
    if (activeStep === 1) {
      if (!fullName.trim()) {
        setError('Please enter your full name.');
        return false;
      }
      if (!phone.trim()) {
        setError('Please enter your mobile phone number.');
        return false;
      }
      if (!email.trim() || !email.includes('@')) {
        setError('Please enter a valid email address.');
        return false;
      }
      if (!password || password.length < 6) {
        setError('Password must be at least 6 characters in length.');
        return false;
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match. Please confirm your password.');
        return false;
      }
    } else if (activeStep === 2) {
      if (!farmName.trim()) {
        setError('Please enter your farm or plot name.');
        return false;
      }
      const numArea = parseFloat(area);
      if (isNaN(numArea) || numArea <= 0) {
        setError('Please enter a valid positive acreage for your farm.');
        return false;
      }
      if (!district.trim()) {
        setError('Please enter your district or taluka.');
        return false;
      }
    }
    return true;
  };

  const handleNextStep = () => {
    if (validateCurrentStep()) {
      setActiveStep((prev) => Math.min(prev + 1, 3));
    }
  };

  const handlePrevStep = () => {
    setError(null);
    setActiveStep((prev) => Math.max(prev - 1, 1));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateCurrentStep()) return;

    setError(null);
    setIsSubmitting(true);

    try {
      // 1. Register User & Farmer Profile
      const username = email.trim().toLowerCase();
      await authService.register({
        username,
        email: email.trim(),
        password,
        role: 'farmer',
        full_name: fullName.trim(),
        phone: phone.trim(),
        address: address.trim() || `${district}, ${state}`,
        state: state.trim(),
        district: district.trim(),
      });

      // 2. Login to obtain JWT Token
      await authService.login({
        username_or_email: email.trim(),
        password,
      });

      // 3. Upload Profile Image if selected
      if (avatarFile) {
        try {
          await authService.uploadAvatar(avatarFile);
        } catch (uploadErr) {
          console.warn('Avatar upload warning:', uploadErr);
        }
      }

      // 4. Create Farm Record linked to the Farmer
      const createdFarm = await farmService.createFarm({
        farm_name: farmName.trim(),
        crop: crop.trim(),
        crop_variety: cropVariety.trim() || undefined,
        growth_stage: 'Vegetative',
        area: parseFloat(area) || 5.0,
        address: address.trim() || `${district}, ${state}`,
        latitude,
        longitude,
        boundary_geojson: boundaryGeoJson.trim() || undefined,
      });

      if (createdFarm?.farm_id) {
        localStorage.setItem('biosniff_farm_id', createdFarm.farm_id.toString());
      }

      // 5. Refresh context session & route to Farmer Overview
      await refreshSession();
      navigate('/farmer/overview');
    } catch (err: any) {
      console.error('Registration failed:', err);
      setError(err?.message || 'Registration failed. Please check your information and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F6F9F6] flex flex-col justify-center py-8">
      <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
        <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-emerald-950/10 grid grid-cols-1 lg:grid-cols-12 min-h-[720px]">
          {/* Left Hero Graphic Banner */}
          <div className="lg:col-span-5 bg-[#0C2B1D] text-white p-8 sm:p-12 flex flex-col justify-between relative overflow-hidden">
            <div className="absolute inset-0 bg-radial from-emerald-600/20 via-transparent to-transparent pointer-events-none" />
            <img
              src="https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=800&q=80"
              alt="Agricultural farmland"
              className="absolute inset-0 w-full h-full object-cover mix-blend-overlay opacity-30"
            />

            <div className="relative z-10">
              <Link to="/">
                <BioSniffLogo variant="light" size="lg" />
              </Link>
              <div className="mt-10 space-y-3">
                <span className="inline-block px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 text-xs font-semibold uppercase tracking-wider">
                  Join The Network
                </span>
                <h2 className="font-serif-display text-3xl sm:text-4xl font-bold text-white leading-tight">
                  Protect every acre with electronic precision.
                </h2>
                <p className="text-sm text-emerald-200/80 leading-relaxed">
                  Register your agricultural profile to connect 3-node electronic VOC telemetry sensors and receive instant early disease warnings.
                </p>
              </div>
            </div>

            {/* Stepper indicator on left panel */}
            <div className="relative z-10 pt-6 border-t border-emerald-800/60 space-y-3">
              <div className="text-xs font-semibold text-emerald-300 uppercase tracking-wider">
                Registration Progress
              </div>
              <div className="space-y-2">
                <div
                  className={`flex items-center gap-3 text-xs p-2 rounded-xl transition-all ${
                    activeStep === 1
                      ? 'bg-emerald-800/80 text-white font-bold ring-1 ring-emerald-400'
                      : activeStep > 1
                      ? 'text-emerald-300'
                      : 'text-emerald-400/60'
                  }`}
                >
                  <span
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                      activeStep > 1 ? 'bg-emerald-400 text-emerald-950' : 'bg-emerald-700 text-white'
                    }`}
                  >
                    {activeStep > 1 ? '✓' : '1'}
                  </span>
                  <span>1. Account Information</span>
                </div>

                <div
                  className={`flex items-center gap-3 text-xs p-2 rounded-xl transition-all ${
                    activeStep === 2
                      ? 'bg-emerald-800/80 text-white font-bold ring-1 ring-emerald-400'
                      : activeStep > 2
                      ? 'text-emerald-300'
                      : 'text-emerald-400/60'
                  }`}
                >
                  <span
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                      activeStep > 2 ? 'bg-emerald-400 text-emerald-950' : 'bg-emerald-700 text-white'
                    }`}
                  >
                    {activeStep > 2 ? '✓' : '2'}
                  </span>
                  <span>2. Farm Information</span>
                </div>

                <div
                  className={`flex items-center gap-3 text-xs p-2 rounded-xl transition-all ${
                    activeStep === 3
                      ? 'bg-emerald-800/80 text-white font-bold ring-1 ring-emerald-400'
                      : 'text-emerald-400/60'
                  }`}
                >
                  <span className="w-5 h-5 rounded-full bg-emerald-700 text-white flex items-center justify-center text-[10px] font-bold">
                    3
                  </span>
                  <span>3. Farm Location & GPS</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Form Card */}
          <div className="lg:col-span-7 p-6 sm:p-10 flex flex-col justify-between">
            <div className="max-w-xl mx-auto w-full space-y-5">
              <div>
                <h3 className="font-serif-display text-2xl sm:text-3xl font-bold text-[#0F2D1F]">
                  {activeStep === 1 && 'Account & Identity'}
                  {activeStep === 2 && 'Farm Parcel Profile'}
                  {activeStep === 3 && 'Farm Location & Boundary'}
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  {activeStep === 1 && 'Create your farmer account login credentials and avatar photo.'}
                  {activeStep === 2 && 'Provide agricultural metadata for tailored disease monitoring.'}
                  {activeStep === 3 && 'Specify authoritative GPS coordinates for your field.'}
                </p>
              </div>

              {/* Error Banner */}
              {error && (
                <div className="p-3.5 rounded-2xl bg-red-50 border border-red-200 text-xs font-semibold text-red-700 flex items-center gap-2 animate-shake">
                  <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* STEP 1: ACCOUNT INFORMATION */}
                {activeStep === 1 && (
                  <div className="space-y-4 animate-fadeIn">
                    {/* Profile Photo Upload */}
                    <div className="flex items-center gap-4 p-3 bg-emerald-50/60 rounded-2xl border border-emerald-100">
                      <div className="relative shrink-0">
                        {avatarPreview ? (
                          <img
                            src={avatarPreview}
                            alt="Avatar Preview"
                            className="w-16 h-16 rounded-full object-cover border-2 border-emerald-500 shadow-xs"
                          />
                        ) : (
                          <div className="w-16 h-16 rounded-full bg-emerald-800 text-white font-bold text-lg flex items-center justify-center border-2 border-emerald-600 shadow-xs">
                            {fullName ? fullName.charAt(0).toUpperCase() : 'BS'}
                          </div>
                        )}
                        <label
                          htmlFor="avatar-upload"
                          className="absolute bottom-0 right-0 p-1 bg-emerald-700 hover:bg-emerald-800 text-white rounded-full cursor-pointer shadow-md transition"
                          title="Upload Profile Photo"
                        >
                          <Camera className="w-3.5 h-3.5" />
                        </label>
                        <input
                          id="avatar-upload"
                          type="file"
                          accept="image/*"
                          onChange={handlePhotoChange}
                          className="hidden"
                        />
                      </div>
                      <div className="text-xs">
                        <strong className="text-gray-900 block font-semibold">Profile Photo</strong>
                        <p className="text-gray-500 text-[11px]">
                          Upload a photo for your farmer profile badge. Max 5MB (JPG, PNG).
                        </p>
                        {avatarFile && (
                          <span className="text-[11px] font-semibold text-emerald-700 block mt-0.5">
                            Selected: {avatarFile.name}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                          Full Name *
                        </label>
                        <div className="relative">
                          <User className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                          <input
                            type="text"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            required
                            placeholder="e.g. Ramesh Patel"
                            className="w-full pl-9 pr-3 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                          Mobile Phone *
                        </label>
                        <div className="relative">
                          <Phone className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                          <input
                            type="text"
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                            required
                            placeholder="+91 9876543210"
                            className="w-full pl-9 pr-3 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium"
                          />
                        </div>
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                        Email Address *
                      </label>
                      <div className="relative">
                        <Mail className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                        <input
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          required
                          placeholder="ramesh.patel@agri.bio-sniff.in"
                          className="w-full pl-9 pr-3 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                          Password *
                        </label>
                        <div className="relative">
                          <Lock className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                          <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="Min 6 characters"
                            className="w-full pl-9 pr-3 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                          Confirm Password *
                        </label>
                        <div className="relative">
                          <ShieldCheck className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                          <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            placeholder="Re-enter password"
                            className="w-full pl-9 pr-3 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* STEP 2: FARM INFORMATION */}
                {activeStep === 2 && (
                  <div className="space-y-4 animate-fadeIn">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                          Farm / Plot Name *
                        </label>
                        <div className="relative">
                          <LandPlot className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                          <input
                            type="text"
                            value={farmName}
                            onChange={(e) => setFarmName(e.target.value)}
                            required
                            placeholder="e.g. Green Valley Paddy Fields"
                            className="w-full pl-9 pr-3 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                          Farm Area (Acres) *
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          value={area}
                          onChange={(e) => setArea(e.target.value)}
                          required
                          placeholder="5.0"
                          className="w-full px-3.5 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                          Cultivated Crop *
                        </label>
                        <div className="relative">
                          <Sprout className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                          <select
                            value={crop}
                            onChange={(e) => setCrop(e.target.value)}
                            className="w-full pl-9 pr-3 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium"
                          >
                            <option value="Rice (Paddy)">Rice (Paddy)</option>
                            <option value="Wheat">Wheat</option>
                            <option value="Cotton">Cotton</option>
                            <option value="Sugarcane">Sugarcane</option>
                            <option value="Maize">Maize</option>
                            <option value="Soybean">Soybean</option>
                            <option value="Grapes">Grapes</option>
                          </select>
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                          Crop Variety
                        </label>
                        <input
                          type="text"
                          value={cropVariety}
                          onChange={(e) => setCropVariety(e.target.value)}
                          placeholder="e.g. Basmati PB-1121"
                          className="w-full px-3.5 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                        Street Address / Village
                      </label>
                      <input
                        type="text"
                        value={address}
                        onChange={(e) => setAddress(e.target.value)}
                        placeholder="e.g. Gat No. 142, Rahuri Sector B"
                        className="w-full px-3.5 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium"
                      />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                          State *
                        </label>
                        <div className="relative">
                          <MapPin className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                          <select
                            value={state}
                            onChange={(e) => setState(e.target.value)}
                            className="w-full pl-9 pr-3 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium"
                          >
                            <option value="Maharashtra">Maharashtra</option>
                            <option value="Gujarat">Gujarat</option>
                            <option value="Punjab">Punjab</option>
                            <option value="Uttar Pradesh">Uttar Pradesh</option>
                            <option value="Madhya Pradesh">Madhya Pradesh</option>
                            <option value="Karnataka">Karnataka</option>
                            <option value="Tamil Nadu">Tamil Nadu</option>
                          </select>
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                          District / Taluka *
                        </label>
                        <input
                          type="text"
                          value={district}
                          onChange={(e) => setDistrict(e.target.value)}
                          required
                          placeholder="e.g. Ahmednagar"
                          className="w-full px-3.5 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* STEP 3: LOCATION & COORDINATES */}
                {activeStep === 3 && (
                  <div className="space-y-4 animate-fadeIn">
                    <div className="p-3 bg-emerald-50 rounded-2xl border border-emerald-200 text-xs flex items-center justify-between">
                      <div>
                        <strong className="text-emerald-950 font-semibold block">Authoritative Farm GPS Location</strong>
                        <span className="text-emerald-800 text-[11px]">
                          Used for 3-node spatial triangulation and wind pathogen dispersion calculations.
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={handleDetectLocation}
                        disabled={isGettingLocation}
                        className="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 disabled:bg-gray-400 text-white rounded-xl font-bold flex items-center gap-1.5 transition text-[11px] shrink-0"
                      >
                        {isGettingLocation ? (
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <Compass className="w-3.5 h-3.5" />
                        )}
                        <span>Use Device GPS</span>
                      </button>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                          Latitude (Degrees North) *
                        </label>
                        <input
                          type="number"
                          step="0.000001"
                          value={latitude}
                          onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                          required
                          className="w-full px-3.5 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium font-mono"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                          Longitude (Degrees East) *
                        </label>
                        <input
                          type="number"
                          step="0.000001"
                          value={longitude}
                          onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                          required
                          className="w-full px-3.5 py-2.5 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-medium font-mono"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                        Optional Farm Boundary GeoJSON
                      </label>
                      <textarea
                        rows={2}
                        value={boundaryGeoJson}
                        onChange={(e) => setBoundaryGeoJson(e.target.value)}
                        placeholder='{"type": "Polygon", "coordinates": [[[74.652, 19.832], [74.654, 19.832], ...]]}'
                        className="w-full px-3.5 py-2 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden font-mono"
                      />
                      <p className="text-[11px] text-gray-400 mt-1">
                        If omitted, farm perimeter polygon will display "Farm boundary not configured".
                      </p>
                    </div>

                    <div className="pt-2">
                      <label className="flex items-start gap-2 cursor-pointer text-xs text-gray-600">
                        <input
                          type="checkbox"
                          defaultChecked
                          required
                          className="rounded border-gray-300 text-emerald-600 focus:ring-emerald-500 mt-0.5"
                        />
                        <span>
                          I confirm that these farm coordinates are accurate and agree to terms of service for real-time telemetry.
                        </span>
                      </label>
                    </div>
                  </div>
                )}

                {/* Step Controls */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  {activeStep > 1 ? (
                    <button
                      type="button"
                      onClick={handlePrevStep}
                      disabled={isSubmitting}
                      className="px-4 py-2.5 text-xs font-bold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-xl transition"
                    >
                      Back
                    </button>
                  ) : (
                    <div />
                  )}

                  {activeStep < 3 ? (
                    <button
                      type="button"
                      onClick={handleNextStep}
                      className="px-6 py-2.5 text-xs font-bold text-white bg-[#0F3D2E] hover:bg-[#14523E] rounded-xl shadow-md transition flex items-center gap-2"
                    >
                      <span>Continue to {activeStep === 1 ? 'Farm Profile' : 'Location Setup'}</span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  ) : (
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="px-6 py-3 bg-[#0F3D2E] hover:bg-[#14523E] disabled:bg-gray-400 text-white font-bold rounded-xl shadow-md transition flex items-center gap-2 text-xs"
                    >
                      {isSubmitting ? (
                        <>
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          <span>Creating Profile & Farm...</span>
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="w-4 h-4" />
                          <span>Complete Registration & Launch Dashboard</span>
                        </>
                      )}
                    </button>
                  )}
                </div>
              </form>

              <div className="text-center pt-2 text-xs text-gray-500">
                Already registered?{' '}
                <Link to="/signin" className="font-semibold text-emerald-700 hover:underline">
                  Sign In to Dashboard
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
