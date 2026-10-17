import React from 'react';

interface BioSniffLogoProps {
  variant?: 'light' | 'dark' | 'header';
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const BioSniffLogo: React.FC<BioSniffLogoProps> = ({
  variant = 'dark',
  className = '',
  size = 'md',
}) => {
  const isLight = variant === 'light';

  const iconSizes = {
    sm: 'w-7 h-7',
    md: 'w-9 h-9',
    lg: 'w-11 h-11',
  };

  const titleSizes = {
    sm: 'text-base font-extrabold tracking-tight',
    md: 'text-xl font-black tracking-tight',
    lg: 'text-2xl font-black tracking-tight',
  };

  const subSizes = {
    sm: 'text-[10px] tracking-wide',
    md: 'text-xs tracking-wide',
    lg: 'text-sm tracking-wide',
  };

  return (
    <div className={`flex items-center gap-2.5 select-none ${className}`}>
      {/* Bio-Sniff Sprout Icon */}
      <div className={`relative flex items-center justify-center rounded-xl transition-transform hover:scale-105 ${iconSizes[size]}`}>
        <svg
          viewBox="0 0 40 40"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full drop-shadow-xs"
        >
          {/* Main Leaf */}
          <path
            d="M20 4C20 4 10 12 10 24C10 29.5228 14.4772 34 20 34C25.5228 34 30 29.5228 30 24C30 12 20 4 20 4Z"
            fill="#22C55E"
          />
          {/* Accent Leaf Cut / Vein */}
          <path
            d="M20 4C20 4 16 14 16 23C16 26.5 17.8 30.5 20 33.5C22.2 30.5 24 26.5 24 23C24 14 20 4 20 4Z"
            fill="#16A34A"
          />
          {/* Sprout Stem */}
          <path
            d="M20 34V38"
            stroke="#15803D"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <path
            d="M13 18C8 16 6 22 10 25C14 28 17 25 17 25"
            fill="#4ADE80"
            fillOpacity="0.85"
          />
          <path
            d="M27 18C32 16 34 22 30 25C26 28 23 25 23 25"
            fill="#15803D"
            fillOpacity="0.85"
          />
        </svg>
      </div>

      <div className="flex flex-col leading-none">
        <span
          className={`${titleSizes[size]} ${
            isLight ? 'text-white' : 'text-[#0F2D1F]'
          }`}
        >
          BIO-SNIFF
        </span>
        <span
          className={`${subSizes[size]} font-medium ${
            isLight ? 'text-emerald-300/80' : 'text-[#476353]'
          }`}
        >
          Detect Before You See It.
        </span>
      </div>
    </div>
  );
};
