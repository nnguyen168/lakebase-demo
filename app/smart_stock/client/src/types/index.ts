// Elena's KPIs
export interface ElenaKPIs {
  onTimeProductionRate: number;
  onTimeProductionRatePrev: number;
  onTimeProductionChange: number;
  onTimeProductionTrend: string;
  inventoryTurnoverRatio: number;
  inventoryTurnoverPrev: number;
  inventoryTurnoverChange: number;
  inventoryTurnoverTrend: string;
  expeditedShipmentsCost: number;
  daysOfStockOnHand: number;
}

export interface WarehouseData {
  name: string;
  location: string;
  transactionCount: number;
  inboundUnits: number;
  salesUnits: number;
  capacityUsed: number;
  lastAudit: string;
  activeProducts: number;
}

export interface TrendingProduct {
  sku: string;
  name: string;
  trend: number;
  sales: number;
}

export interface SupplierMetrics {
  supplier: string;
  avgDays: number;
  onTime: number;
}

export interface WarehouseDetail {
  id: string;
  name: string;
  location: string;
  lat: number;
  lng: number;
  capacity: number;
  currentStock: number;
  status: string;
  manager: string;
  phone: string;
  recentIncidents?: string[];
  lastAudit?: string;
}

export interface HomepageData {
  dailySummary: string;
  trendingProducts: TrendingProduct[];
  supplierMetrics: SupplierMetrics[];
  warehouseDetails: WarehouseDetail[];
  criticalCount?: number;
  warningCount?: number;
}