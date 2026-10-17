import React, { useEffect, useRef } from 'react';
import * as maplibregl from 'maplibre-gl';
import { Plus, Minus } from 'lucide-react';
import { AdminFarmMapItem } from '../../types/api';

interface AdminIndiaMapProps {
  height?: string;
  farmsData?: AdminFarmMapItem[];
}

export const AdminIndiaMap: React.FC<AdminIndiaMapProps> = ({
  height = '380px',
  farmsData = [],
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    try {
      const map = new maplibregl.Map({
        container: containerRef.current,
        style: {
          version: 8,
          sources: {
            'light-tiles': {
              type: 'raster',
              tiles: [
                'https://basemaps.cartocdn.com/rastertiles/light_nolabels/{z}/{x}/{y}{r}.png',
              ],
              tileSize: 256,
              attribution: '© OpenStreetMap contributors © CARTO',
            },
          },
          layers: [
            {
              id: 'base-tiles',
              type: 'raster',
              source: 'light-tiles',
              minzoom: 0,
              maxzoom: 18,
            },
          ],
        },
        center: [78.9629, 21.5937],
        zoom: 3.8,
        attributionControl: false,
      });

      mapRef.current = map;

      // Add markers from real API farms data if available
      const pointsToDisplay = farmsData.length > 0 ? farmsData : [];

      pointsToDisplay.forEach((farm) => {
        const el = document.createElement('div');
        const statusKey = farm.health_status || farm.status || 'healthy';
        const color =
          statusKey === 'healthy'
            ? 'bg-emerald-500'
            : statusKey === 'at-risk'
            ? 'bg-amber-500'
            : statusKey === 'diseased'
            ? 'bg-red-500'
            : 'bg-gray-400';

        el.className = 'cursor-pointer group';
        el.innerHTML = `
          <div class="relative flex items-center justify-center">
            <span class="absolute inline-flex h-4 w-4 rounded-full ${color} opacity-40 group-hover:animate-ping"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 ${color} border border-white shadow-xs"></span>
          </div>
        `;

        const popup = new maplibregl.Popup({ offset: 10 }).setHTML(`
          <div class="p-1.5 text-xs font-sans">
            <strong class="text-gray-900 block">${farm.farm_name}</strong>
            <span class="text-gray-500 text-[10px]">${farm.farmer} • ${farm.state || ''}</span>
            <div class="mt-1 font-semibold capitalize text-[10px] ${
              statusKey === 'healthy' ? 'text-emerald-700' : statusKey === 'diseased' ? 'text-red-600' : 'text-amber-600'
            }">Status: ${statusKey} (${farm.crop})</div>
          </div>
        `);

        new maplibregl.Marker({ element: el })
          .setLngLat([farm.longitude, farm.latitude])
          .setPopup(popup)
          .addTo(map);
      });

      return () => {
        map.remove();
        mapRef.current = null;
      };
    } catch (err) {
      console.warn('MapLibre error', err);
    }
  }, [farmsData]);

  return (
    <div className="relative overflow-hidden rounded-2xl border border-gray-200/80 bg-[#EBF3EC]" style={{ height }}>
      <div ref={containerRef} className="h-full w-full" />

      {/* Map Legend */}
      <div className="absolute top-3 right-3 z-10 flex flex-col gap-1 rounded-xl bg-white/95 px-3 py-2 text-[11px] shadow-sm backdrop-blur-xs border border-gray-200">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          <span className="text-gray-700 font-medium">Healthy</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-amber-500" />
          <span className="text-gray-700 font-medium">At Risk</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-red-500" />
          <span className="text-gray-700 font-medium">Diseased</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-gray-400" />
          <span className="text-gray-700 font-medium">Inactive</span>
        </div>
      </div>

      {/* Zoom buttons */}
      <div className="absolute bottom-3 left-3 z-10 flex flex-col gap-1 rounded-lg bg-white/90 p-1 shadow-xs border border-gray-200">
        <button
          onClick={() => mapRef.current?.zoomIn()}
          className="flex h-6 w-6 items-center justify-center rounded text-gray-700 hover:bg-gray-100"
        >
          <Plus className="h-3.5 w-3.5" />
        </button>
        <button
          onClick={() => mapRef.current?.zoomOut()}
          className="flex h-6 w-6 items-center justify-center rounded text-gray-700 hover:bg-gray-100 border-t border-gray-100"
        >
          <Minus className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Geographical labels overlay */}
      <div className="pointer-events-none absolute bottom-4 left-12 text-[10px] font-medium text-gray-400 tracking-wider">
        Arabian Sea
      </div>
      <div className="pointer-events-none absolute bottom-4 right-8 text-[10px] font-medium text-gray-400 tracking-wider">
        Bay of Bengal
      </div>
      <div className="pointer-events-none absolute bottom-1 left-24 text-[9px] font-medium text-gray-400 tracking-wider">
        Indian Ocean
      </div>
    </div>
  );
};
