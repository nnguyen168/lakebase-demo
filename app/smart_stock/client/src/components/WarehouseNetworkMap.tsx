import React, { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Card } from '@/components/ui/card';
import {
  Factory, Package, Truck, Activity, AlertTriangle,
  MapPin, Users, Clock, TrendingUp
} from 'lucide-react';
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

interface WarehouseNetworkMapProps {
  warehouses: Warehouse[];
  supplyRoutes: SupplyRoute[];
}

const WarehouseNetworkMap: React.FC<WarehouseNetworkMapProps> = ({ warehouses, supplyRoutes }) => {
  const [selectedWarehouse, setSelectedWarehouse] = useState<string | null>(null);
  const [hoveredWarehouse, setHoveredWarehouse] = useState<string | null>(null);

  // Convert real coordinates to SVG coordinates
  const coordToSVG = (lat: number, lon: number): [number, number] => {
    // Map bounds (approximate Europe)
    const minLon = -5;
    const maxLon = 20;
    const minLat = 40;
    const maxLat = 60;

    const x = ((lon - minLon) / (maxLon - minLon)) * 800 + 100;
    const y = ((maxLat - lat) / (maxLat - minLat)) * 400 + 50;

    return [x, y];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return '#10b981';
      case 'maintenance': return '#f59e0b';
      default: return '#ef4444';
    }
  };

  const activeWarehouse = selectedWarehouse
    ? warehouses.find(w => w.id === selectedWarehouse)
    : hoveredWarehouse
    ? warehouses.find(w => w.id === hoveredWarehouse)
    : null;

  return (
    <div className="relative">
      <div className="flex gap-4">
        {/* Map Section */}
        <div className="flex-1">
          <svg
            width="100%"
            viewBox="0 0 1000 500"
            className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow-inner"
            style={{ minHeight: '500px' }}
          >
            {/* Background Pattern */}
            <defs>
              <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
                <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#e0e7ff" strokeWidth="0.5" opacity="0.3"/>
              </pattern>

              {/* Gradient for routes */}
              <linearGradient id="routeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.6" />
                <stop offset="50%" stopColor="#60a5fa" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.6" />
              </linearGradient>

              {/* Shadow filter */}
              <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                <feOffset dx="0" dy="2" result="offsetblur"/>
                <feComponentTransfer>
                  <feFuncA type="linear" slope="0.3"/>
                </feComponentTransfer>
                <feMerge>
                  <feMergeNode/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>

            <rect width="1000" height="500" fill="url(#grid)" />

            {/* Europe Outline (simplified) */}
            <path
              d="M 200 300 Q 250 280, 350 290 T 450 270 Q 500 260, 550 270 T 650 280 Q 700 285, 750 300 L 750 400 Q 700 410, 650 405 T 550 410 Q 450 415, 350 410 T 250 400 L 200 380 Z"
              fill="#f0f9ff"
              stroke="#cbd5e1"
              strokeWidth="1"
              opacity="0.5"
            />

            {/* Supply Routes */}
            {supplyRoutes.map((route) => {
              const [x1, y1] = coordToSVG(...route.from);
              const [x2, y2] = coordToSVG(...route.to);

              return (
                <g key={route.id}>
                  {/* Route shadow */}
                  <line
                    x1={x1}
                    y1={y1}
                    x2={x2}
                    y2={y2}
                    stroke="black"
                    strokeWidth={route.active ? 6 : 4}
                    strokeOpacity="0.1"
                    strokeDasharray={route.active ? undefined : "10,5"}
                    transform="translate(2, 2)"
                  />
                  {/* Route line */}
                  <line
                    x1={x1}
                    y1={y1}
                    x2={x2}
                    y2={y2}
                    stroke={route.color}
                    strokeWidth={route.active ? 3 : 2}
                    strokeOpacity={route.active ? 0.8 : 0.4}
                    strokeDasharray={route.active ? undefined : "10,5"}
                  />
                  {route.active && (
                    <circle r="3" fill={route.color}>
                      <animateMotion
                        dur="3s"
                        repeatCount="indefinite"
                        path={`M ${x1} ${y1} L ${x2} ${y2}`}
                      />
                    </circle>
                  )}
                </g>
              );
            })}

            {/* Warehouse Markers */}
            {warehouses.map((warehouse) => {
              const [x, y] = coordToSVG(...warehouse.coordinates);
              const isActive = selectedWarehouse === warehouse.id || hoveredWarehouse === warehouse.id;
              const statusColor = getStatusColor(warehouse.status);

              return (
                <g
                  key={warehouse.id}
                  transform={`translate(${x}, ${y})`}
                  className="cursor-pointer"
                  onClick={() => setSelectedWarehouse(
                    selectedWarehouse === warehouse.id ? null : warehouse.id
                  )}
                  onMouseEnter={() => setHoveredWarehouse(warehouse.id)}
                  onMouseLeave={() => setHoveredWarehouse(null)}
                >
                  {/* Pulse animation for operational warehouses */}
                  {warehouse.status === 'operational' && (
                    <circle
                      r="20"
                      fill={statusColor}
                      opacity="0.3"
                    >
                      <animate
                        attributeName="r"
                        values="20;30;20"
                        dur="2s"
                        repeatCount="indefinite"
                      />
                      <animate
                        attributeName="opacity"
                        values="0.3;0.1;0.3"
                        dur="2s"
                        repeatCount="indefinite"
                      />
                    </circle>
                  )}

                  {/* Warehouse circle */}
                  <circle
                    r={isActive ? 22 : 18}
                    fill={statusColor}
                    stroke="white"
                    strokeWidth="3"
                    filter="url(#shadow)"
                    className="transition-all duration-200"
                  />

                  {/* Warehouse icon */}
                  <g transform="translate(-10, -10) scale(0.8)">
                    <Factory color="white" size={24} />
                  </g>

                  {/* Status indicator */}
                  {warehouse.status === 'maintenance' && (
                    <g transform="translate(10, -10)">
                      <circle r="8" fill="#fbbf24" stroke="white" strokeWidth="2" />
                      <text
                        x="0"
                        y="3"
                        textAnchor="middle"
                        fill="white"
                        fontSize="10"
                        fontWeight="bold"
                      >
                        !
                      </text>
                    </g>
                  )}

                  {/* Label */}
                  <text
                    x="0"
                    y="35"
                    textAnchor="middle"
                    className="fill-gray-700 font-semibold text-sm"
                    style={{ pointerEvents: 'none' }}
                  >
                    {warehouse.location.split(',')[0]}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Map Legend */}
          <div className="mt-4 flex justify-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-500 rounded-full"></div>
              <span>Operational</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
              <span>Maintenance</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-1 bg-blue-500"></div>
              <span>Active Route</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-1 bg-gray-400 border-t-2 border-dashed"></div>
              <span>Inactive Route</span>
            </div>
          </div>
        </div>

        {/* Details Panel */}
        {activeWarehouse && (
          <Card className="w-80 p-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-lg">{activeWarehouse.name}</h3>
                <Badge className={cn(
                  "text-xs",
                  activeWarehouse.status === 'operational' ? 'bg-green-100 text-green-800' :
                  activeWarehouse.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                )}>
                  {activeWarehouse.status}
                </Badge>
              </div>

              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-gray-500" />
                  <span>{activeWarehouse.location}</span>
                </div>

                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-gray-500" />
                  <span>{activeWarehouse.manager}</span>
                </div>

                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-gray-500" />
                  <span>Active {activeWarehouse.lastActivity}</span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Capacity Used</span>
                  <span className="font-medium">
                    {((activeWarehouse.currentStock / activeWarehouse.capacity) * 100).toFixed(1)}%
                  </span>
                </div>
                <Progress
                  value={(activeWarehouse.currentStock / activeWarehouse.capacity) * 100}
                  className="h-2"
                />
              </div>

              <div className="grid grid-cols-2 gap-4 pt-3 border-t">
                <div className="text-center">
                  <Package className="h-8 w-8 mx-auto mb-1 text-blue-600" />
                  <div className="text-xs text-gray-600">Stock Units</div>
                  <div className="font-semibold">{activeWarehouse.currentStock.toLocaleString()}</div>
                </div>
                <div className="text-center">
                  <TrendingUp className="h-8 w-8 mx-auto mb-1 text-green-600" />
                  <div className="text-xs text-gray-600">Efficiency</div>
                  <div className="font-semibold">{activeWarehouse.efficiency}%</div>
                </div>
              </div>

              {activeWarehouse.status === 'maintenance' && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <span className="text-sm text-yellow-800">
                      Scheduled maintenance until Friday
                    </span>
                  </div>
                </div>
              )}
            </div>
          </Card>
        )}
      </div>

      {/* Summary Stats */}
      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-3 border">
          <div className="flex items-center gap-2">
            <Factory className="h-5 w-5 text-blue-600" />
            <div>
              <div className="text-sm text-gray-600">Total Warehouses</div>
              <div className="text-xl font-bold">3 Locations</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg p-3 border">
          <div className="flex items-center gap-2">
            <Package className="h-5 w-5 text-green-600" />
            <div>
              <div className="text-sm text-gray-600">Total Stock</div>
              <div className="text-xl font-bold">
                {warehouses.reduce((acc, w) => acc + w.currentStock, 0).toLocaleString()} Units
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg p-3 border">
          <div className="flex items-center gap-2">
            <Truck className="h-5 w-5 text-orange-600" />
            <div>
              <div className="text-sm text-gray-600">Active Routes</div>
              <div className="text-xl font-bold">2 of 3 Routes</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WarehouseNetworkMap;