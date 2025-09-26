import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { 
  AlertTriangle, Package, 
  BarChart3, X, Target, ShoppingCart
} from 'lucide-react';

import type { InventoryForecastResponse } from '@/fastapi_client';

interface ForecastDataPoint {
  date: string;
  day: number;
  pastStock?: number;  // Stock level for past days
  forecastStock?: number;  // Stock level for future days
  incomingOrder?: number;  // Expected incoming order delivery on this day
}

interface ForecastModalProps {
  isOpen: boolean;
  onClose: () => void;
  item: InventoryForecastResponse | null;
  onCreateOrder?: (item: InventoryForecastResponse) => void;
}

const ForecastModal: React.FC<ForecastModalProps> = ({ 
  isOpen, 
  onClose, 
  item,
  onCreateOrder
}) => {
  const [forecastData, setForecastData] = useState<ForecastDataPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [todayDateString, setTodayDateString] = useState<string>('');

  useEffect(() => {
    if (isOpen && item) {
      generateForecastData(item);
    }
  }, [isOpen, item]);

  const generateForecastData = (item: InventoryForecastResponse) => {
    setLoading(true);
    
    // Generate 30 days past + today + 30 days future
    const data: ForecastDataPoint[] = [];
    const today = new Date();
    const todayDateString = today.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    
    // Generate past 30 days + today (historical data)
    let pastStock = Math.round(item.stock * 1.3); // Start higher in the past
    for (let day = -30; day <= 0; day++) {
      const date = new Date(today);
      date.setDate(today.getDate() + day);
      
      if (day === 0) {
        // Today - connect past to forecast
        data.push({
          date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          day: day,
          pastStock: item.stock,
          forecastStock: item.stock, // Same value to connect the lines
        });
      } else {
        // Past days - simulate gradual decline to today's stock
        const progress = (30 + day) / 30; // 0 to 1 as we approach today
        const stockLevel = Math.round(
          pastStock - ((pastStock - item.stock) * progress) + 
          (Math.random() - 0.5) * 4 // Small random variation
        );
        
        data.push({
          date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          day: day,
          pastStock: Math.max(0, stockLevel),
        });
      }
    }
    
    // Generate future 30 days (forecast)
    let futureStock = item.stock;
    const avgDailyDemand = item.forecast_30_days / 30;
    
    // Simulate expected delivery for resolved items
    let expectedDeliveryDay = null;
    let expectedDeliveryQuantity = 0;
    
    if (item.status === 'resolved') {
      // Calculate delivery timing based on urgency
      const deliveryDays = item.stock === 0 ? 3 : item.stock < 20 ? 5 : 7;
      expectedDeliveryDay = deliveryDays;
      
      // Estimate delivery quantity based on action
      if (item.action === 'Urgent Reorder') {
        expectedDeliveryQuantity = Math.max(50, item.forecast_30_days * 1.5);
      } else if (item.action === 'Reorder Now') {
        expectedDeliveryQuantity = Math.max(30, item.forecast_30_days);
      } else {
        expectedDeliveryQuantity = Math.max(20, item.forecast_30_days * 0.8);
      }
    }
    
    for (let day = 1; day <= 30; day++) {
      const date = new Date(today);
      date.setDate(today.getDate() + day);
      
      // Simple forecast decline
      const dailyDemand = avgDailyDemand + (Math.random() - 0.5) * 1;
      futureStock = Math.max(0, futureStock - dailyDemand);
      
      // Add expected delivery
      let incomingOrder = undefined;
      if (day === expectedDeliveryDay) {
        futureStock += expectedDeliveryQuantity; // Boost stock when delivery arrives
        incomingOrder = Math.round(futureStock);
      }
      
      data.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        day: day,
        forecastStock: Math.round(futureStock),
        incomingOrder: incomingOrder, // Renamed from expectedDelivery
      });
    }
    
    setForecastData(data);
    setTodayDateString(todayDateString);
    setLoading(false);
  };

  const handleReorder = () => {
    if (item && onCreateOrder) {
      onCreateOrder(item);
      onClose(); // Close the forecast modal after starting order creation
    }
  };

  const canReorder = (status: string) => {
    // Don't allow reordering for resolved items
    return status.toLowerCase() !== 'resolved';
  };

  const getInventoryStatusStyles = (status: string) => {
    switch (status.toLowerCase()) {
      case 'in_stock':
        return {
          variant: 'secondary' as const,
          className: 'bg-green-100 text-green-800 border-green-200',
          icon: Package
        };
      case 'low_stock':
        return {
          variant: 'secondary' as const,
          className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          icon: AlertTriangle
        };
      case 'out_of_stock':
        return {
          variant: 'destructive' as const,
          className: 'bg-red-100 text-red-800 border-red-200',
          icon: AlertTriangle
        };
      case 'reorder_needed':
        return {
          variant: 'secondary' as const,
          className: 'bg-orange-100 text-orange-800 border-orange-200',
          icon: Target
        };
      case 'resolved':
        return {
          variant: 'secondary' as const,
          className: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: Target
        };
      default:
        return {
          variant: 'secondary' as const,
          className: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: Package
        };
    }
  };

  if (!item) return null;

  const statusStyle = getInventoryStatusStyles(item.status);
  const StatusIcon = statusStyle.icon;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <StatusIcon className="h-5 w-5" />
{item.item_name} - Forecast
          </DialogTitle>
          <DialogDescription>
            View the past 30 days of stock history and projected 30-day forecast
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Status and Current Stock */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Badge 
                variant={statusStyle.variant}
                className={`${statusStyle.className} flex items-center gap-1`}
              >
                <StatusIcon className="h-3 w-3" />
                {item.status.replace('_', ' ')}
              </Badge>
              <div>
                <span className="text-2xl font-bold">{item.stock}</span>
                <span className="text-muted-foreground ml-1">units in stock</span>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Simple Line Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <BarChart3 className="h-5 w-5" />
                30-Day History & 30-Day Forecast
              </CardTitle>
              <div className="flex gap-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-0.5 bg-gray-500"></div>
                  <span>Past 30 days</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-0.5 border-t-2 border-dashed border-blue-500"></div>
                  <span>Next 30 days (forecast)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-0.5 h-4 bg-red-500"></div>
                  <span>Today</span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="h-80 flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={320}>
                  <LineChart data={forecastData}>
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis 
                      dataKey="date"
                      tick={{ fontSize: 12 }}
                      interval={4} // Show every 5th label to avoid crowding
                    />
                    <YAxis 
                      tick={{ fontSize: 12 }}
                      label={{ value: 'Stock Units', angle: -90, position: 'insideLeft' }}
                    />
                    <RechartsTooltip 
                      formatter={(value, name) => {
                        if (name === 'Incoming Order Delivery') {
                          return ['Incoming Order Delivery'];
                        }
                        return [
                          `${value} units`,
                          name === 'pastStock' ? 'Historical Stock' : 'Forecast Stock'
                        ];
                      }}
                      labelFormatter={(date) => date}
                    />
                    
                    {/* Past stock line (solid gray) */}
                    <Line
                      type="monotone"
                      dataKey="pastStock"
                      stroke="#6b7280"
                      strokeWidth={3}
                      dot={false}
                      connectNulls={false}
                      name="Historical Stock"
                    />
                    
                    {/* Forecast stock line (dashed blue) */}
                    <Line
                      type="monotone"
                      dataKey="forecastStock"
                      stroke="#3b82f6"
                      strokeWidth={3}
                      strokeDasharray="8 4"
                      dot={false}
                      connectNulls={false}
                      name="Forecast Stock"
                    />
                    
                    {/* Incoming order delivery points (green) */}
                    <Line
                      type="monotone"
                      dataKey="incomingOrder"
                      stroke="#10b981"
                      strokeWidth={0}
                      dot={{ 
                        fill: '#10b981', 
                        stroke: '#059669', 
                        strokeWidth: 3, 
                        r: 8,
                        fillOpacity: 0.8
                      }}
                      connectNulls={false}
                      name="Incoming Order Delivery"
                    />
                    
                    {/* Today reference line */}
                    <ReferenceLine 
                      x={todayDateString} 
                      stroke="#ef4444" 
                      strokeDasharray="2 2"
                      strokeWidth={2}
                      label={{ value: "Today", position: "top", fontSize: 12 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>

          {/* Simple Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardContent className="pt-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">30-day forecast:</span>
                    <span className="font-medium">{item.forecast_30_days} units</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Current action:</span>
                    <span className="font-medium">{item.action}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={onClose}>
                Close
              </Button>
              {onCreateOrder && canReorder(item.status) && (
                <Button onClick={handleReorder} className="flex items-center gap-2">
                  <ShoppingCart className="h-4 w-4" />
                  Create Order
                </Button>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ForecastModal;