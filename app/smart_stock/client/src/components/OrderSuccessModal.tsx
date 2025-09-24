import React from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, Package, Calendar, User, FileText } from 'lucide-react';

interface OrderData {
  order_id: number;
  order_number: string;
  product_id: number;
  quantity: number;
  requested_by: string;
  status: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  product_name?: string;
  product_sku?: string;
  unit_price?: string;
}

interface OrderSuccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRefreshData?: () => void;
  orderData: OrderData | null;
}

const OrderSuccessModal: React.FC<OrderSuccessModalProps> = ({ 
  isOpen, 
  onClose, 
  onRefreshData,
  orderData 
}) => {
  if (!orderData) return null;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const totalAmount = orderData.unit_price 
    ? (parseFloat(orderData.unit_price) * orderData.quantity).toFixed(2)
    : 'N/A';

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            Order Created Successfully!
          </DialogTitle>
          <DialogDescription>
            Your order has been submitted and is now being processed.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Success Alert */}
          <Alert className="border-green-200 bg-green-50 text-green-800">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription>
              Order {orderData.order_number} has been created successfully with status: {orderData.status}
            </AlertDescription>
          </Alert>

          {/* Order Details */}
          <div className="bg-gray-50 p-4 rounded-lg space-y-3">
            <h3 className="font-semibold text-lg mb-3">Order Details</h3>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <Package className="h-4 w-4 text-gray-500" />
                <div>
                  <p className="text-gray-600">Order Number</p>
                  <p className="font-medium">{orderData.order_number}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-gray-500" />
                <div>
                  <p className="text-gray-600">Created</p>
                  <p className="font-medium">{formatDate(orderData.created_at)}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-gray-500" />
                <div>
                  <p className="text-gray-600">Requested By</p>
                  <p className="font-medium">{orderData.requested_by}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Package className="h-4 w-4 text-gray-500" />
                <div>
                  <p className="text-gray-600">Status</p>
                  <p className="font-medium capitalize">{orderData.status}</p>
                </div>
              </div>
            </div>

            {/* Product Information */}
            <div className="pt-3 border-t border-gray-200">
              <h4 className="font-medium mb-2">Product Information</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Product:</span>
                  <span className="font-medium">{orderData.product_name || `Product ID: ${orderData.product_id}`}</span>
                </div>
                {orderData.product_sku && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">SKU:</span>
                    <span className="font-mono text-sm">{orderData.product_sku}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-600">Quantity:</span>
                  <span className="font-medium">{orderData.quantity}</span>
                </div>
                {orderData.unit_price && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Unit Price:</span>
                      <span className="font-medium">${orderData.unit_price}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total Amount:</span>
                      <span className="font-bold">${totalAmount}</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Notes */}
            {orderData.notes && (
              <div className="pt-3 border-t border-gray-200">
                <div className="flex items-start gap-2">
                  <FileText className="h-4 w-4 text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-gray-600 text-sm">Notes</p>
                    <p className="text-sm mt-1">{orderData.notes}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <DialogFooter>
          <div className="flex gap-2 w-full">
            <Button 
              type="button" 
              variant="outline" 
              onClick={onClose}
              className="flex-1"
            >
              Close
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default OrderSuccessModal;
