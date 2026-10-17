// Source: Google Maps Platform Code Assist
import React, { useState, useCallback, useMemo } from 'react';
import {
  APIProvider,
  Map,
  AdvancedMarker,
  InfoWindow,
  Polygon,
  Circle,
  useMap,
  useApiLoadingStatus,
  APILoadingStatus,
} from '@vis.gl/react-google-maps';
import { FarmCoordinate, SensorNode } from '../../types';
import { Layers, Maximize2, Navigation, Plus, Minus, AlertTriangle, Radio, Activity, CheckCircle2, RefreshCw } from 'lucide-react';
import { checkTriangularArrangement } from '../../utils/geometry';

interface FarmMapProps {
  center: FarmCoordinate;
  zoom?: number;
  boundary?: FarmCoordinate[];
  nodes?: SensorNode[];
  diseaseSource?: {
    coordinates: FarmCoordinate;
    name: string;
    confidence: number;
  } | null;
  height?: string;
  className?: string;
  locationLabel?: string;
  showLayersMenu?: boolean;
}

// Default Google Maps API Key provided for Bio-Sniff
const GOOGLE_MAPS_API_KEY =
  (import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string) ||
  'AIzaSyBT1Q-Bb_D0AEzFLoeeLvhsrpNH90sfseI';

// Internal controller component inside Map context
interface MapControlsProps {
  center: FarmCoordinate;
  zoom: number;
  mapType: string;
  setMapType: (type: 'hybrid' | 'satellite' | 'roadmap' | 'terrain') => void;
  showLayersMenu: boolean;
}

const MapControls: React.FC<MapControlsProps> = ({
  center,
  zoom,
  mapType,
  setMapType,
  showLayersMenu,
}) => {
  const map = useMap();
  const [isLayerMenuOpen, setIsLayerMenuOpen] = useState(false);

  const handleZoomIn = useCallback(() => {
    if (!map) return;
    const currentZoom = map.getZoom() ?? zoom;
    map.setZoom(currentZoom + 1);
  }, [map, zoom]);

  const handleZoomOut = useCallback(() => {
    if (!map) return;
    const currentZoom = map.getZoom() ?? zoom;
    map.setZoom(currentZoom - 1);
  }, [map, zoom]);

  const handleRecenter = useCallback(() => {
    if (!map) return;
    map.panTo({ lat: center.lat, lng: center.lng });
    map.setZoom(zoom);
  }, [map, center, zoom]);

  return (
    <>
      {/* Top Left: Map Layer Dropdown */}
      {showLayersMenu && (
        <div className="absolute top-4 left-4 z-10">
          <div className="relative">
            <button
              type="button"
              onClick={() => setIsLayerMenuOpen(!isLayerMenuOpen)}
              className="flex items-center gap-2 rounded-xl bg-black/70 px-3 py-1.5 text-xs font-semibold text-white shadow-lg backdrop-blur-md transition-all hover:bg-black/85 border border-white/10"
            >
              <Layers className="h-3.5 w-3.5 text-emerald-400" />
              <span className="capitalize">{mapType} Aerial</span>
              <span className="text-[10px] opacity-70">▾</span>
            </button>

            {isLayerMenuOpen && (
              <div className="absolute top-9 left-0 w-40 rounded-xl border border-white/15 bg-black/90 p-1.5 shadow-2xl backdrop-blur-md z-20 space-y-1">
                <button
                  type="button"
                  onClick={() => {
                    setMapType('hybrid');
                    map?.setMapTypeId('hybrid');
                    setIsLayerMenuOpen(false);
                  }}
                  className={`flex w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-xs font-medium text-left transition ${
                    mapType === 'hybrid' ? 'bg-emerald-600 text-white' : 'text-gray-200 hover:bg-white/10'
                  }`}
                >
                  <span className="h-2 w-2 rounded-full bg-emerald-400" />
                  Hybrid Satellite
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMapType('satellite');
                    map?.setMapTypeId('satellite');
                    setIsLayerMenuOpen(false);
                  }}
                  className={`flex w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-xs font-medium text-left transition ${
                    mapType === 'satellite' ? 'bg-emerald-600 text-white' : 'text-gray-200 hover:bg-white/10'
                  }`}
                >
                  <span className="h-2 w-2 rounded-full bg-blue-400" />
                  Pure Satellite
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMapType('terrain');
                    map?.setMapTypeId('terrain');
                    setIsLayerMenuOpen(false);
                  }}
                  className={`flex w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-xs font-medium text-left transition ${
                    mapType === 'terrain' ? 'bg-emerald-600 text-white' : 'text-gray-200 hover:bg-white/10'
                  }`}
                >
                  <span className="h-2 w-2 rounded-full bg-amber-400" />
                  Terrain Topo
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMapType('roadmap');
                    map?.setMapTypeId('roadmap');
                    setIsLayerMenuOpen(false);
                  }}
                  className={`flex w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-xs font-medium text-left transition ${
                    mapType === 'roadmap' ? 'bg-emerald-600 text-white' : 'text-gray-200 hover:bg-white/10'
                  }`}
                >
                  <span className="h-2 w-2 rounded-full bg-gray-400" />
                  Standard Road
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Map Control Buttons: Zoom & Recenter */}
      <div className="absolute top-16 left-4 z-10 flex flex-col gap-1 rounded-xl bg-white/95 p-1 shadow-lg backdrop-blur-xs border border-gray-200">
        <button
          type="button"
          onClick={handleZoomIn}
          className="flex h-7 w-7 items-center justify-center rounded-lg text-gray-700 transition hover:bg-gray-100 active:bg-gray-200"
          title="Zoom In"
        >
          <Plus className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={handleZoomOut}
          className="flex h-7 w-7 items-center justify-center rounded-lg text-gray-700 transition hover:bg-gray-100 active:bg-gray-200 border-t border-gray-100"
          title="Zoom Out"
        >
          <Minus className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={handleRecenter}
          className="flex h-7 w-7 items-center justify-center rounded-lg text-gray-700 transition hover:bg-gray-100 active:bg-gray-200 border-t border-gray-100"
          title="Recenter Farm"
        >
          <Navigation className="h-3.5 w-3.5 text-emerald-700 rotate-45" />
        </button>
      </div>
    </>
  );
};

// Map status fallback
const ApiLoadingNotice = () => {
  const status = useApiLoadingStatus();

  if (status === APILoadingStatus.FAILED) {
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-gray-900/90 text-white p-6 z-20">
        <div className="text-center max-w-md space-y-3 bg-gray-800 p-6 rounded-2xl border border-red-500/30">
          <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
          <h4 className="font-bold text-base text-gray-100">Google Maps Initialization</h4>
          <p className="text-xs text-gray-300">
            Please verify that your Google Maps API Key has the <strong>Maps JavaScript API</strong> enabled and domain restrictions permitted.
          </p>
          <span className="inline-block text-[11px] font-mono text-gray-400 bg-gray-900 px-3 py-1 rounded">
            Key: {GOOGLE_MAPS_API_KEY.slice(0, 10)}...{GOOGLE_MAPS_API_KEY.slice(-4)}
          </span>
        </div>
      </div>
    );
  }

  if (status === APILoadingStatus.LOADING) {
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-emerald-950/60 backdrop-blur-xs text-white z-10">
        <div className="flex items-center gap-2 text-xs font-semibold bg-black/60 px-4 py-2 rounded-full border border-white/20">
          <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-400" />
          <span>Connecting to Google Maps Satellite...</span>
        </div>
      </div>
    );
  }

  return null;
};

export const FarmMap: React.FC<FarmMapProps> = ({
  center,
  zoom = 16.2,
  boundary,
  nodes = [],
  diseaseSource = null,
  height = '100%',
  className = '',
  locationLabel = '19.8321° N, 74.6521° E\nAhmednagar, Maharashtra',
  showLayersMenu = true,
}) => {
  const [mapType, setMapType] = useState<'hybrid' | 'satellite' | 'roadmap' | 'terrain'>('hybrid');
  const [selectedNode, setSelectedNode] = useState<SensorNode | null>(null);
  const [selectedDisease, setSelectedDisease] = useState<boolean>(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Boundary coordinates formatted for Google Maps
  const boundaryPaths = useMemo(() => {
    if (!boundary || boundary.length < 3) return [];
    return boundary.map(pt => ({ lat: pt.lat, lng: pt.lng }));
  }, [boundary]);

  // Triangular Arrangement Check
  const triangleCheck = useMemo(() => {
    return checkTriangularArrangement(nodes);
  }, [nodes]);

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border border-gray-200/80 shadow-xs transition-all ${
        isFullscreen ? 'fixed inset-4 z-50 rounded-2xl shadow-2xl border-emerald-500' : ''
      } ${className}`}
      style={{ height: isFullscreen ? 'calc(100vh - 2rem)' : height }}
    >
      {/* 3-Node Spatial Triangle Configuration Warning Banner */}
      {triangleCheck.warningMessage && (
        <div className="absolute top-3 left-1/2 -translate-x-1/2 z-30 max-w-lg w-[90%] bg-amber-900/90 text-amber-100 backdrop-blur-md px-3.5 py-2 rounded-xl border border-amber-500/50 shadow-lg text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 animate-bounce" />
          <span>{triangleCheck.warningMessage}</span>
        </div>
      )}

      <APIProvider apiKey={GOOGLE_MAPS_API_KEY}>
        <div className="h-full w-full relative bg-[#15231a]">
          <ApiLoadingNotice />

          <Map
            mapId="DEMO_MAP_ID"
            defaultCenter={{ lat: center.lat, lng: center.lng }}
            defaultZoom={zoom}
            mapTypeId={mapType}
            gestureHandling="greedy"
            disableDefaultUI={true}
            internalUsageAttributionIds={['gmp_mcp_codeassist_v1_aistudio']}
            className="w-full h-full"
            style={{ width: '100%', height: '100%' }}
          >
            {/* Interactive map controls */}
            <MapControls
              center={center}
              zoom={zoom}
              mapType={mapType}
              setMapType={setMapType}
              showLayersMenu={showLayersMenu}
            />

            {/* Farm Perimeter Polygon */}
            {boundaryPaths.length > 2 && (
              <Polygon
                paths={boundaryPaths}
                strokeColor="#22C55E"
                strokeOpacity={0.95}
                strokeWeight={2.5}
                fillColor="#22C55E"
                fillOpacity={0.14}
              />
            )}

            {/* Pathogen Anomaly Dispersion Zone */}
            {diseaseSource && (
              <Circle
                center={{
                  lat: diseaseSource.coordinates.lat,
                  lng: diseaseSource.coordinates.lng,
                }}
                radius={50}
                strokeColor="#DC2626"
                strokeOpacity={0.85}
                strokeWeight={2}
                fillColor="#EF4444"
                fillOpacity={0.25}
              />
            )}

            {/* Sensor Nodes Markers */}
            {nodes.map(node => (
              <AdvancedMarker
                key={node.id}
                position={{ lat: node.coordinates.lat, lng: node.coordinates.lng }}
                title={`${node.name} (${node.nodeId})`}
                onClick={() => {
                  setSelectedNode(node);
                  setSelectedDisease(false);
                }}
              >
                <div className="relative flex items-center group cursor-pointer">
                  <div className="relative flex items-center justify-center">
                    <span className="absolute inline-flex h-8 w-8 animate-ping rounded-full bg-emerald-400 opacity-60 pointer-events-none" />
                    <div className="relative flex h-5 w-5 items-center justify-center rounded-full border-2 border-white bg-emerald-500 shadow-md">
                      <div className="h-1.5 w-1.5 rounded-full bg-white" />
                    </div>
                  </div>
                  <div className="ml-1.5 flex items-center gap-1 rounded-full bg-emerald-950/90 px-2.5 py-0.5 text-xs font-semibold text-white shadow-lg backdrop-blur-xs border border-emerald-500/50">
                    <Radio className="w-2.5 h-2.5 text-emerald-400 animate-pulse" />
                    <span>{node.name}</span>
                  </div>
                </div>
              </AdvancedMarker>
            ))}

            {/* Node InfoWindow */}
            {selectedNode && (
              <InfoWindow
                position={{
                  lat: selectedNode.coordinates.lat,
                  lng: selectedNode.coordinates.lng,
                }}
                onCloseClick={() => setSelectedNode(null)}
                maxWidth={280}
              >
                <div className="p-1 font-sans text-gray-900">
                  <div className="flex items-center justify-between gap-3 border-b border-gray-100 pb-1.5 mb-2">
                    <strong className="text-xs font-bold text-gray-900">
                      {selectedNode.name} ({selectedNode.nodeId})
                    </strong>
                    <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800">
                      <CheckCircle2 className="w-2.5 h-2.5" /> Online
                    </span>
                  </div>
                  <div className="text-[11px] text-gray-600 space-y-1">
                    <div className="flex justify-between">
                      <span>Battery Life:</span>
                      <strong className="text-gray-900">{selectedNode.battery}%</strong>
                    </div>
                    <div className="flex justify-between">
                      <span>Mesh Signal:</span>
                      <strong className="text-gray-900">{selectedNode.signal}</strong>
                    </div>
                    <div className="flex justify-between">
                      <span>VOC Sensor:</span>
                      <strong className="text-emerald-700 font-bold">{selectedNode.readings.totalVoc} kΩ</strong>
                    </div>
                    <div className="flex justify-between">
                      <span>Temperature:</span>
                      <strong className="text-gray-900">{selectedNode.readings.temperature}°C</strong>
                    </div>
                    <div className="flex justify-between">
                      <span>Humidity:</span>
                      <strong className="text-gray-900">{selectedNode.readings.humidity}%</strong>
                    </div>
                  </div>
                </div>
              </InfoWindow>
            )}

            {/* Disease Source Marker */}
            {diseaseSource && (
              <AdvancedMarker
                position={{
                  lat: diseaseSource.coordinates.lat,
                  lng: diseaseSource.coordinates.lng,
                }}
                title={diseaseSource.name}
                onClick={() => {
                  setSelectedDisease(true);
                  setSelectedNode(null);
                }}
              >
                <div className="relative flex items-center cursor-pointer group">
                  <div className="relative flex items-center justify-center">
                    <span className="absolute inline-flex h-10 w-10 animate-ping rounded-full bg-red-500 opacity-75 pointer-events-none" />
                    <div className="relative flex h-7 w-7 items-center justify-center rounded-full border-2 border-white bg-red-600 shadow-xl">
                      <AlertTriangle className="w-3.5 h-3.5 text-white" />
                    </div>
                  </div>
                  <div className="ml-1.5 flex flex-col rounded-lg bg-red-950/95 px-2.5 py-1 text-[11px] font-bold text-white shadow-xl backdrop-blur-xs border border-red-500">
                    <span className="text-red-300 text-[9px] uppercase tracking-wider font-semibold">Triangulated Source</span>
                    <span>{diseaseSource.name} ({diseaseSource.confidence}%)</span>
                  </div>
                </div>
              </AdvancedMarker>
            )}

            {/* Disease InfoWindow */}
            {selectedDisease && diseaseSource && (
              <InfoWindow
                position={{
                  lat: diseaseSource.coordinates.lat,
                  lng: diseaseSource.coordinates.lng,
                }}
                onCloseClick={() => setSelectedDisease(false)}
                maxWidth={280}
              >
                <div className="p-1 font-sans text-gray-900">
                  <div className="flex items-center gap-1.5 text-red-600 font-bold text-xs uppercase tracking-wide">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Pathogen Anomaly</span>
                  </div>
                  <div className="font-bold text-sm text-gray-900 mt-1">{diseaseSource.name}</div>
                  <div className="text-xs text-gray-600 mt-1">
                    Localization Confidence: <strong className="text-red-700">{diseaseSource.confidence}%</strong>
                  </div>
                  <p className="text-[11px] text-gray-500 mt-1 border-t border-gray-100 pt-1">
                    Triangulated via 10-channel VOC sensor array and wind dispersion trajectory.
                  </p>
                </div>
              </InfoWindow>
            )}
          </Map>

          {/* Bottom Left: Location Coordinates Pill */}
          <div className="absolute bottom-4 left-4 z-10 pointer-events-auto">
            <div className="flex items-center gap-2.5 rounded-xl border border-white/20 bg-white/95 px-3.5 py-2 shadow-xl backdrop-blur-md">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200">
                <Navigation className="h-4 w-4 rotate-45" />
              </div>
              <div className="text-left">
                <div className="text-[10px] font-semibold uppercase tracking-wider text-emerald-800 leading-tight">
                  Google Maps Satellite
                </div>
                <div className="text-xs font-semibold text-gray-900 whitespace-pre-line leading-tight">
                  {locationLabel}
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Right: Fullscreen / Expand Control */}
          <div className="absolute bottom-4 right-4 z-10 pointer-events-auto flex items-center gap-2">
            <button
              type="button"
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="flex items-center gap-1.5 rounded-xl bg-black/70 px-3 py-1.5 text-xs font-medium text-white shadow-lg backdrop-blur-md transition-all hover:bg-black/85 border border-white/10"
            >
              <Maximize2 className="h-3.5 w-3.5 text-emerald-400" />
              <span>{isFullscreen ? 'Exit Fullscreen' : 'Expand Field View'}</span>
            </button>
          </div>
        </div>
      </APIProvider>
    </div>
  );
};
