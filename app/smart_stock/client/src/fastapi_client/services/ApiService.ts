/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ForecastStatus } from '../models/ForecastStatus';
import type { InventoryForecast } from '../models/InventoryForecast';
import type { InventoryForecastResponse } from '../models/InventoryForecastResponse';
import type { InventoryForecastUpdate } from '../models/InventoryForecastUpdate';
import type { InventoryTransaction } from '../models/InventoryTransaction';
import type { InventoryTransactionCreate } from '../models/InventoryTransactionCreate';
import type { InventoryTransactionUpdate } from '../models/InventoryTransactionUpdate';
import type { Order } from '../models/Order';
import type { OrderCreate } from '../models/OrderCreate';
import type { OrderStatus } from '../models/OrderStatus';
import type { OrderUpdate } from '../models/OrderUpdate';
import type { Product } from '../models/Product';
import type { ProductCreate } from '../models/ProductCreate';
import type { ProductUpdate } from '../models/ProductUpdate';
import type { StockManagementAlertKPI } from '../models/StockManagementAlertKPI';
import type { TransactionManagementKPI } from '../models/TransactionManagementKPI';
import type { TransactionResponse } from '../models/TransactionResponse';
import type { TransactionStatus } from '../models/TransactionStatus';
import type { TransactionType } from '../models/TransactionType';
import type { UserInfo } from '../models/UserInfo';
import type { UserWorkspaceInfo } from '../models/UserWorkspaceInfo';
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
     * Get list of inventory transactions with optional filters.
     * @param status Filter by transaction status
     * @param warehouseId Filter by warehouse ID
     * @param transactionType Filter by transaction type
     * @param limit Maximum number of transactions to return
     * @param offset Number of transactions to skip
     * @returns TransactionResponse Successful Response
     * @throws ApiError
     */
    public static getTransactionsApiTransactionsGet(
        status?: (TransactionStatus | null),
        warehouseId?: (number | null),
        transactionType?: (TransactionType | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<TransactionResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/transactions/',
            query: {
                'status': status,
                'warehouse_id': warehouseId,
                'transaction_type': transactionType,
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
     * Get Inventory Forecast
     * Get inventory forecast with optional filters.
     * @param warehouseId Filter by warehouse ID
     * @param status Filter by forecast status
     * @param limit Maximum number of items to return
     * @param offset Number of items to skip
     * @returns InventoryForecastResponse Successful Response
     * @throws ApiError
     */
    public static getInventoryForecastApiInventoryForecastGet(
        warehouseId?: (number | null),
        status?: (ForecastStatus | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<InventoryForecastResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/inventory/forecast',
            query: {
                'warehouse_id': warehouseId,
                'status': status,
                'limit': limit,
                'offset': offset,
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
     * Get all products with optional filters.
     * @param category Filter by product category
     * @param search Search in product name or SKU
     * @param limit Maximum number of products to return
     * @param offset Number of products to skip
     * @returns Product Successful Response
     * @throws ApiError
     */
    public static getProductsApiProductsGet(
        category?: (string | null),
        search?: (string | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<Product>> {
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
}
