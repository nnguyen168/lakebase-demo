import React, { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';

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

interface ClientOnlyMapProps {
  warehouses: Warehouse[];
  supplyRoutes: SupplyRoute[];
}

const ClientOnlyMap: React.FC<ClientOnlyMapProps> = ({ warehouses, supplyRoutes }) => {
  const [Map, setMap] = useState<React.ComponentType<any> | null>(null);

  useEffect(() => {
    // Only import on client side
    if (typeof window !== 'undefined') {
      import('./WarehouseMap').then((module) => {
        setMap(() => module.default);
      }).catch((error) => {
        console.error('Failed to load map component:', error);
      });
    }
  }, []);

  if (!Map) {
    return (
      <div className="flex items-center justify-center h-[500px]">
        <div className="flex items-center gap-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading warehouse map...</span>
        </div>
      </div>
    );
  }

  return <Map warehouses={warehouses} supplyRoutes={supplyRoutes} />;
};

export default ClientOnlyMap;