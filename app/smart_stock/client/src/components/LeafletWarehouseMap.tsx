import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Badge } from '@/components/ui/badge';
import { Factory, Package, Truck, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Warehouse {
  id: string;
  name: string;
  location: string;
  coordinates: [number, number];
  capacity: number;
  currentStock: number;
  status: string;
  manager: string;
  lastActivity: string;
  efficiency: number;
}

interface SupplyRoute {
  id: string;
  from: [number, number];
  to: [number, number];
  color: string;
  active: boolean;
}

interface LeafletWarehouseMapProps {
  warehouses: Warehouse[];
  supplyRoutes: SupplyRoute[];
}

const LeafletWarehouseMap: React.FC<LeafletWarehouseMapProps> = ({ warehouses, supplyRoutes }) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    // Initialize map
    const map = L.map(mapRef.current, {
      center: [49.0, 7.0],
      zoom: 5,
      scrollWheelZoom: true,
      zoomControl: true
    });

    mapInstanceRef.current = map;

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(map);

    // Removed supply routes - they looked terrible as straight lines

    // Create custom icons for warehouses
    const createIcon = (status: string) => {
      const colorMap: Record<string, string> = {
        operational: '#10b981',
        maintenance: '#f59e0b',
        alert: '#ef4444'
      };

      const color = colorMap[status] || '#6b7280';

      return L.divIcon({
        className: 'custom-div-icon',
        html: `
          <div style="
            background-color: ${color};
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 3px 10px rgba(0,0,0,0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
          ">
            <svg width="20" height="20" fill="white" viewBox="0 0 24 24">
              <path d="M18 8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2h12zm0 2H6v10h12V10zM12 2l5 5H7l5-5z"/>
            </svg>
            ${status === 'maintenance' ? `
              <div style="
                position: absolute;
                top: -5px;
                right: -5px;
                background-color: #fbbf24;
                border: 2px solid white;
                border-radius: 50%;
                width: 16px;
                height: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
              ">
                <span style="color: white; font-size: 10px; font-weight: bold;">!</span>
              </div>
            ` : ''}
          </div>
        `,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
        popupAnchor: [0, -18]
      });
    };

    // Add warehouse markers
    warehouses.forEach((warehouse) => {
      const marker = L.marker(warehouse.coordinates, {
        icon: createIcon(warehouse.status),
        title: warehouse.name
      }).addTo(map);

      // Create popup content
      const popupContent = `
        <div style="min-width: 250px; font-family: system-ui, -apple-system, sans-serif;">
          <h3 style="font-size: 16px; font-weight: bold; margin: 0 0 8px 0;">${warehouse.name}</h3>
          <div style="font-size: 14px; color: #6b7280; margin-bottom: 12px;">${warehouse.location}</div>

          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #6b7280;">Status:</span>
            <span style="
              background-color: ${warehouse.status === 'operational' ? '#dcfce7' : '#fef3c7'};
              color: ${warehouse.status === 'operational' ? '#166534' : '#92400e'};
              padding: 2px 8px;
              border-radius: 4px;
              font-size: 12px;
              font-weight: 500;
            ">${warehouse.status}</span>
          </div>

          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #6b7280;">Manager:</span>
            <span style="font-weight: 500;">${warehouse.manager}</span>
          </div>

          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #6b7280;">Capacity:</span>
            <span style="font-weight: 500;">${warehouse.capacity.toLocaleString()}</span>
          </div>

          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #6b7280;">Current Stock:</span>
            <span style="font-weight: 500;">${warehouse.currentStock.toLocaleString()}</span>
          </div>

          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #6b7280;">Utilization:</span>
            <span style="font-weight: 500;">${((warehouse.currentStock / warehouse.capacity) * 100).toFixed(1)}%</span>
          </div>

          <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
              <span style="color: #6b7280; font-size: 12px;">Efficiency</span>
              <span style="font-size: 12px; font-weight: 500;">${warehouse.efficiency}%</span>
            </div>
            <div style="background-color: #e5e7eb; height: 6px; border-radius: 3px; overflow: hidden;">
              <div style="
                background-color: ${warehouse.efficiency > 80 ? '#10b981' : '#f59e0b'};
                width: ${warehouse.efficiency}%;
                height: 100%;
              "></div>
            </div>
          </div>

          ${warehouse.status === 'maintenance' ? `
            <div style="
              margin-top: 12px;
              padding: 8px;
              background-color: #fef3c7;
              border: 1px solid #fde68a;
              border-radius: 4px;
            ">
              <div style="display: flex; align-items: center; gap: 4px;">
                <svg width="14" height="14" fill="#d97706" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                <span style="color: #92400e; font-size: 12px;">Scheduled maintenance until Friday</span>
              </div>
            </div>
          ` : ''}
        </div>
      `;

      marker.bindPopup(popupContent);
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <div className="relative">
      <div ref={mapRef} style={{ height: '500px', width: '100%', borderRadius: '0.5rem' }} />

      {/* Map Legend */}
      <div className="absolute bottom-4 right-4 bg-white p-3 rounded-lg shadow-lg z-[400]">
        <h4 className="font-semibold text-sm mb-2">Legend</h4>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-xs">Operational</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-xs">Maintenance</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span className="text-xs">Alert</span>
          </div>
        </div>
      </div>

      {/* Map Stats - moved to bottom left to not block zoom controls */}
      <div className="absolute bottom-4 left-4 bg-white p-3 rounded-lg shadow-lg z-[400]">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Factory className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium">3 Warehouses</span>
          </div>
          <div className="flex items-center gap-2">
            <Package className="h-4 w-4 text-green-600" />
            <span className="text-sm font-medium">
              {warehouses.reduce((acc, w) => acc + w.currentStock, 0).toLocaleString()} Units
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-orange-600" />
            <span className="text-sm font-medium">
              {warehouses.filter(w => w.status === 'operational').length} Operational
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeafletWarehouseMap;