import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Tooltip as LeafletTooltip } from 'react-leaflet';
import L from 'leaflet';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { AlertTriangle, Factory, Package, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';
import 'leaflet/dist/leaflet.css';

// Fix for default markers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

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

interface WarehouseMapProps {
  warehouses: Warehouse[];
  supplyRoutes: SupplyRoute[];
}

const WarehouseMap: React.FC<WarehouseMapProps> = ({ warehouses, supplyRoutes }) => {
  // Create custom icons for different warehouse statuses
  const createWarehouseIcon = (status: string) => {
    const colorMap: Record<string, string> = {
      operational: '#10b981',
      maintenance: '#f59e0b',
      alert: '#ef4444'
    };

    const svgIcon = `
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
        <circle cx="20" cy="20" r="18" fill="${colorMap[status]}" stroke="white" stroke-width="3"/>
        <path d="M20 10 L10 15 L10 25 L20 30 L30 25 L30 15 Z" fill="white" opacity="0.9"/>
        <path d="M20 10 L30 15 M20 10 L10 15 M10 15 L10 25 L20 30 L30 25 L30 15"
              stroke="${colorMap[status]}" stroke-width="1.5" fill="none"/>
      </svg>
    `;

    return L.divIcon({
      className: 'custom-warehouse-icon',
      html: svgIcon,
      iconSize: [40, 40],
      iconAnchor: [20, 20],
      popupAnchor: [0, -20]
    });
  };

  useEffect(() => {
    // Add custom styles for the map
    const style = document.createElement('style');
    style.innerHTML = `
      .custom-warehouse-icon {
        background: transparent;
        border: none;
      }
      .leaflet-container {
        font-family: inherit;
      }
      .leaflet-popup-content-wrapper {
        border-radius: 8px;
      }
      .leaflet-tooltip {
        background-color: rgba(0, 0, 0, 0.8);
        border: none;
        color: white;
        border-radius: 4px;
        padding: 4px 8px;
      }
    `;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, []);

  return (
    <div className="relative">
      <MapContainer
        center={[49.0, 7.0]}
        zoom={5}
        style={{ height: '500px', width: '100%', borderRadius: '0.5rem' }}
        className="z-0"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Supply Routes */}
        {supplyRoutes.map((route) => (
          <Polyline
            key={route.id}
            positions={[route.from, route.to]}
            pathOptions={{
              color: route.color,
              weight: route.active ? 3 : 2,
              opacity: route.active ? 0.8 : 0.3,
              dashArray: route.active ? undefined : '10, 10'
            }}
          />
        ))}

        {/* Warehouse Markers */}
        {warehouses.map((warehouse) => (
          <Marker
            key={warehouse.id}
            position={warehouse.coordinates}
            icon={createWarehouseIcon(warehouse.status)}
          >
            <LeafletTooltip direction="top" offset={[0, -10]} opacity={0.9}>
              <div className="font-semibold">{warehouse.name}</div>
            </LeafletTooltip>
            <Popup>
              <div className="p-2 min-w-[200px]">
                <h3 className="font-bold text-lg mb-2">{warehouse.name}</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Status:</span>
                    <Badge className={cn(
                      "text-xs",
                      warehouse.status === 'operational' ? 'bg-green-100 text-green-800' :
                      warehouse.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    )}>
                      {warehouse.status}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Manager:</span>
                    <span className="font-medium">{warehouse.manager}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Capacity:</span>
                    <span className="font-medium">{warehouse.capacity.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Current Stock:</span>
                    <span className="font-medium">{warehouse.currentStock.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Utilization:</span>
                    <span className="font-medium">
                      {((warehouse.currentStock / warehouse.capacity) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Efficiency:</span>
                    <span className="font-medium">{warehouse.efficiency}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Last Activity:</span>
                    <span className="font-medium">{warehouse.lastActivity}</span>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t">
                  <Progress value={(warehouse.currentStock / warehouse.capacity) * 100} className="h-2" />
                </div>
                {warehouse.status === 'maintenance' && (
                  <Alert className="mt-3 p-2">
                    <AlertTriangle className="h-3 w-3" />
                    <AlertDescription className="text-xs ml-1">
                      Scheduled maintenance until Friday
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Map Legend */}
      <div className="absolute bottom-4 right-4 bg-white p-3 rounded-lg shadow-lg z-[1000]">
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
            <div className="w-3 h-3 bg-blue-500 opacity-80" style={{ height: '2px' }}></div>
            <span className="text-xs">Active Route</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 opacity-30" style={{ height: '2px', borderTop: '2px dashed' }}></div>
            <span className="text-xs">Inactive Route</span>
          </div>
        </div>
      </div>

      {/* Map Stats Overlay */}
      <div className="absolute top-4 left-4 bg-white p-3 rounded-lg shadow-lg z-[1000]">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Factory className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium">3 Warehouses</span>
          </div>
          <div className="flex items-center gap-2">
            <Package className="h-4 w-4 text-green-600" />
            <span className="text-sm font-medium">
              {warehouses.reduce((acc, w) => acc + w.currentStock, 0).toLocaleString()} Total Units
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-orange-600" />
            <span className="text-sm font-medium">2 Active Routes</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WarehouseMap;