/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BulkDeleteRequest } from '../models/BulkDeleteRequest';
import type { BulkDeleteResponse } from '../models/BulkDeleteResponse';
import type { BulkStatusUpdateRequest } from '../models/BulkStatusUpdateRequest';
import type { BulkStatusUpdateResponse } from '../models/BulkStatusUpdateResponse';
import type { ForecastStatus } from '../models/ForecastStatus';
import type { InventoryForecast } from '../models/InventoryForecast';
import type { InventoryForecastUpdate } from '../models/InventoryForecastUpdate';
import type { InventoryTransaction } from '../models/InventoryTransaction';
import type { InventoryTransactionCreate } from '../models/InventoryTransactionCreate';
import type { InventoryTransactionUpdate } from '../models/InventoryTransactionUpdate';
import type { InventoryTurnoverMetrics } from '../models/InventoryTurnoverMetrics';
import type { Order } from '../models/Order';
import type { OrderCreate } from '../models/OrderCreate';
import type { OrderStatus } from '../models/OrderStatus';
import type { OrderUpdate } from '../models/OrderUpdate';
import type { OTPRMetrics } from '../models/OTPRMetrics';
import type { PaginatedResponse_InventoryForecastResponse_ } from '../models/PaginatedResponse_InventoryForecastResponse_';
import type { PaginatedResponse_Product_ } from '../models/PaginatedResponse_Product_';
import type { PaginatedResponse_TransactionResponse_ } from '../models/PaginatedResponse_TransactionResponse_';
import type { PaginatedResponse_Warehouse_ } from '../models/PaginatedResponse_Warehouse_';
import type { Product } from '../models/Product';
import type { ProductCreate } from '../models/ProductCreate';
import type { ProductUpdate } from '../models/ProductUpdate';
import type { StockManagementAlertKPI } from '../models/StockManagementAlertKPI';
import type { TransactionManagementKPI } from '../models/TransactionManagementKPI';
import type { TransactionStatus } from '../models/TransactionStatus';
import type { TransactionType } from '../models/TransactionType';
import type { UserInfo } from '../models/UserInfo';
import type { UserWorkspaceInfo } from '../models/UserWorkspaceInfo';
import type { Warehouse } from '../models/Warehouse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ApiService {
    /**
     * Get Current User
     * Get current user information from Databricks.
     * @returns UserInfo Successful Response
     * @throws ApiError
     */
    public static getCurrentUserApiUserMeGet(): CancelablePromise<UserInfo> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/user/me',
        });
    }
    /**
     * Get User Workspace Info
     * Get user information along with workspace details.
     * @returns UserWorkspaceInfo Successful Response
     * @throws ApiError
     */
    public static getUserWorkspaceInfoApiUserMeWorkspaceGet(): CancelablePromise<UserWorkspaceInfo> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/user/me/workspace',
        });
    }
    /**
     * Get Transactions
     * Get list of inventory transactions with optional filters and pagination metadata.
     * @param status Filter by transaction status (multiple values allowed)
     * @param warehouseId Filter by warehouse ID (multiple values allowed)
     * @param productId Filter by product ID (multiple values allowed)
     * @param transactionType Filter by transaction type (multiple values allowed)
     * @param dateFrom Filter transactions from this date
     * @param dateTo Filter transactions until this date
     * @param sortBy Field to sort by (product, warehouse, transaction_timestamp)
     * @param sortOrder Sort order (asc or desc)
     * @param limit Maximum number of transactions to return
     * @param offset Number of transactions to skip
     * @returns PaginatedResponse_TransactionResponse_ Successful Response
     * @throws ApiError
     */
    public static getTransactionsApiTransactionsGet(
        status?: (Array<TransactionStatus> | null),
        warehouseId?: (Array<number> | null),
        productId?: (Array<number> | null),
        transactionType?: (Array<TransactionType> | null),
        dateFrom?: (string | null),
        dateTo?: (string | null),
        sortBy?: (string | null),
        sortOrder?: (string | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<PaginatedResponse_TransactionResponse_> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/transactions/',
            query: {
                'status': status,
                'warehouse_id': warehouseId,
                'product_id': productId,
                'transaction_type': transactionType,
                'date_from': dateFrom,
                'date_to': dateTo,
                'sort_by': sortBy,
                'sort_order': sortOrder,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Transaction
     * Create a new inventory transaction.
     * @param requestBody
     * @returns InventoryTransaction Successful Response
     * @throws ApiError
     */
    public static createTransactionApiTransactionsPost(
        requestBody: InventoryTransactionCreate,
    ): CancelablePromise<InventoryTransaction> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/transactions/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Transaction Kpi
     * Get KPI metrics for transaction management.
     * @returns TransactionManagementKPI Successful Response
     * @throws ApiError
     */
    public static getTransactionKpiApiTransactionsKpiGet(): CancelablePromise<TransactionManagementKPI> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/transactions/kpi',
        });
    }
    /**
     * Get Transaction
     * Get a specific transaction by ID.
     * @param transactionId
     * @returns InventoryTransaction Successful Response
     * @throws ApiError
     */
    public static getTransactionApiTransactionsTransactionIdGet(
        transactionId: number,
    ): CancelablePromise<InventoryTransaction> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/transactions/{transaction_id}',
            path: {
                'transaction_id': transactionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Transaction
     * Update an existing transaction.
     * @param transactionId
     * @param requestBody
     * @returns InventoryTransaction Successful Response
     * @throws ApiError
     */
    public static updateTransactionApiTransactionsTransactionIdPut(
        transactionId: number,
        requestBody: InventoryTransactionUpdate,
    ): CancelablePromise<InventoryTransaction> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/transactions/{transaction_id}',
            path: {
                'transaction_id': transactionId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Transaction
     * Cancel a transaction.
     * @param transactionId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteTransactionApiTransactionsTransactionIdDelete(
        transactionId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/transactions/{transaction_id}',
            path: {
                'transaction_id': transactionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Bulk Update Status
     * Update status for multiple transactions at once.
     * @param requestBody
     * @returns BulkStatusUpdateResponse Successful Response
     * @throws ApiError
     */
    public static bulkUpdateStatusApiTransactionsBulkStatusPut(
        requestBody: BulkStatusUpdateRequest,
    ): CancelablePromise<BulkStatusUpdateResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/transactions/bulk-status',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Bulk Delete Transactions
     * Delete multiple transactions at once.
     * @param requestBody
     * @returns BulkDeleteResponse Successful Response
     * @throws ApiError
     */
    public static bulkDeleteTransactionsApiTransactionsBulkDeleteDelete(
        requestBody: BulkDeleteRequest,
    ): CancelablePromise<BulkDeleteResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/transactions/bulk-delete',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Inventory Forecast
     * Get inventory forecast with optional filters and pagination metadata.
     * @param warehouseId Filter by warehouse ID
     * @param status Filter by forecast status
     * @param limit Maximum number of items to return
     * @param offset Number of items to skip
     * @param sortBy Sort key
     * @param sortOrder Sort order: asc or desc
     * @returns PaginatedResponse_InventoryForecastResponse_ Successful Response
     * @throws ApiError
     */
    public static getInventoryForecastApiInventoryForecastGet(
        warehouseId?: (number | null),
        status?: (ForecastStatus | null),
        limit: number = 100,
        offset?: number,
        sortBy: string = 'severity',
        sortOrder: string = 'asc',
    ): CancelablePromise<PaginatedResponse_InventoryForecastResponse_> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/inventory/forecast',
            query: {
                'warehouse_id': warehouseId,
                'status': status,
                'limit': limit,
                'offset': offset,
                'sort_by': sortBy,
                'sort_order': sortOrder,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Inventory History
     * Get historical inventory levels for a specific product and warehouse.
     * @param itemId Product SKU to get history for
     * @param warehouseId Warehouse ID to get history for
     * @param days Number of days of history to return
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getInventoryHistoryApiInventoryHistoryGet(
        itemId: string,
        warehouseId: number,
        days: number = 30,
    ): CancelablePromise<Array<Record<string, any>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/inventory/history',
            query: {
                'item_id': itemId,
                'warehouse_id': warehouseId,
                'days': days,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Stock Alerts Kpi
     * Get KPI metrics for stock management alerts.
     * @returns StockManagementAlertKPI Successful Response
     * @throws ApiError
     */
    public static getStockAlertsKpiApiInventoryAlertsKpiGet(): CancelablePromise<StockManagementAlertKPI> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/inventory/alerts/kpi',
        });
    }
    /**
     * Update Inventory Forecast
     * Update inventory forecast for a specific item.
     * @param forecastId
     * @param requestBody
     * @returns InventoryForecast Successful Response
     * @throws ApiError
     */
    public static updateInventoryForecastApiInventoryForecastForecastIdPut(
        forecastId: number,
        requestBody: InventoryForecastUpdate,
    ): CancelablePromise<InventoryForecast> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/inventory/forecast/{forecast_id}',
            path: {
                'forecast_id': forecastId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Products
     * Get all products with optional filters and pagination metadata.
     * @param category Filter by product category
     * @param search Search in product name or SKU
     * @param limit Maximum number of products to return
     * @param offset Number of products to skip
     * @returns PaginatedResponse_Product_ Successful Response
     * @throws ApiError
     */
    public static getProductsApiProductsGet(
        category?: (string | null),
        search?: (string | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<PaginatedResponse_Product_> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/products/',
            query: {
                'category': category,
                'search': search,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Product
     * Create a new product.
     * @param requestBody
     * @returns Product Successful Response
     * @throws ApiError
     */
    public static createProductApiProductsPost(
        requestBody: ProductCreate,
    ): CancelablePromise<Product> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/products/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Product
     * Get a specific product by ID.
     * @param productId
     * @returns Product Successful Response
     * @throws ApiError
     */
    public static getProductApiProductsProductIdGet(
        productId: number,
    ): CancelablePromise<Product> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/products/{product_id}',
            path: {
                'product_id': productId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Product
     * Update a product.
     * @param productId
     * @param requestBody
     * @returns Product Successful Response
     * @throws ApiError
     */
    public static updateProductApiProductsProductIdPut(
        productId: number,
        requestBody: ProductUpdate,
    ): CancelablePromise<Product> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/products/{product_id}',
            path: {
                'product_id': productId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Product
     * Delete a product.
     * @param productId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteProductApiProductsProductIdDelete(
        productId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/products/{product_id}',
            path: {
                'product_id': productId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Orders
     * Get list of orders with optional filters.
     * @param status Filter by order status
     * @param requestedBy Filter by requestor
     * @param limit Maximum number of orders to return
     * @param offset Number of orders to skip
     * @returns Order Successful Response
     * @throws ApiError
     */
    public static getOrdersApiOrdersGet(
        status?: (OrderStatus | null),
        requestedBy?: (string | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<Order>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/orders/',
            query: {
                'status': status,
                'requested_by': requestedBy,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Order
     * Create a new order.
     * @param requestBody
     * @returns Order Successful Response
     * @throws ApiError
     */
    public static createOrderApiOrdersPost(
        requestBody: OrderCreate,
    ): CancelablePromise<Order> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/orders/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Order
     * Get a specific order by ID.
     * @param orderId
     * @returns Order Successful Response
     * @throws ApiError
     */
    public static getOrderApiOrdersOrderIdGet(
        orderId: number,
    ): CancelablePromise<Order> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/orders/{order_id}',
            path: {
                'order_id': orderId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Order
     * Update an existing order.
     * @param orderId
     * @param requestBody
     * @returns Order Successful Response
     * @throws ApiError
     */
    public static updateOrderApiOrdersOrderIdPut(
        orderId: number,
        requestBody: OrderUpdate,
    ): CancelablePromise<Order> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/orders/{order_id}',
            path: {
                'order_id': orderId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Cancel Order
     * Cancel an order.
     * @param orderId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static cancelOrderApiOrdersOrderIdDelete(
        orderId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/orders/{order_id}',
            path: {
                'order_id': orderId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Otpr Metrics
     * Get On-Time Production Rate metrics from the otpr view.
     *
     * Returns the current and previous 30-day OTPR percentages,
     * the percentage point change, and trend indicator.
     *
     * This endpoint reads real-time metrics from the database view,
     * so it will reflect any updates immediately.
     * @returns OTPRMetrics Successful Response
     * @throws ApiError
     */
    public static getOtprMetricsApiOtprGet(): CancelablePromise<OTPRMetrics> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/otpr/',
        });
    }
    /**
     * Get Inventory Turnover Metrics
     * Get Inventory Turnover metrics from the inventory_turnover view.
     *
     * Returns the overall inventory turnover rate and related metrics.
     * This endpoint reads real-time metrics from the database view.
     * @returns InventoryTurnoverMetrics Successful Response
     * @throws ApiError
     */
    public static getInventoryTurnoverMetricsApiInventoryTurnoverGet(): CancelablePromise<InventoryTurnoverMetrics> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/inventory-turnover/',
        });
    }
    /**
     * Get Warehouses
     * Get all warehouses with pagination metadata.
     * @param limit Maximum number of warehouses to return
     * @param offset Number of warehouses to skip
     * @returns PaginatedResponse_Warehouse_ Successful Response
     * @throws ApiError
     */
    public static getWarehousesApiWarehousesGet(
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<PaginatedResponse_Warehouse_> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/warehouses/',
            query: {
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Warehouse
     * Get a specific warehouse by ID.
     * @param warehouseId
     * @returns Warehouse Successful Response
     * @throws ApiError
     */
    public static getWarehouseApiWarehousesWarehouseIdGet(
        warehouseId: number,
    ): CancelablePromise<Warehouse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/warehouses/{warehouse_id}',
            path: {
                'warehouse_id': warehouseId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
