/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InventoryForecast } from '../models/InventoryForecast';
import type { InventoryForecastResponse } from '../models/InventoryForecastResponse';
import type { InventoryForecastUpdate } from '../models/InventoryForecastUpdate';
import type { InventoryHistory } from '../models/InventoryHistory';
import type { InventoryStatus } from '../models/InventoryStatus';
import type { Order } from '../models/Order';
import type { OrderCreate } from '../models/OrderCreate';
import type { OrderManagementKPI } from '../models/OrderManagementKPI';
import type { OrderResponse } from '../models/OrderResponse';
import type { OrderStatus } from '../models/OrderStatus';
import type { OrderUpdate } from '../models/OrderUpdate';
import type { StockManagementAlertKPI } from '../models/StockManagementAlertKPI';
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
     * Get Orders
     * Get list of orders with optional filters.
     * @param status Filter by order status
     * @param storeId Filter by store ID
     * @param limit Maximum number of orders to return
     * @param offset Number of orders to skip
     * @returns OrderResponse Successful Response
     * @throws ApiError
     */
    public static getOrdersApiOrdersGet(
        status?: (OrderStatus | null),
        storeId?: (string | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<OrderResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/orders/',
            query: {
                'status': status,
                'store_id': storeId,
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
     * Get Order Kpi
     * Get KPI metrics for order management.
     * @returns OrderManagementKPI Successful Response
     * @throws ApiError
     */
    public static getOrderKpiApiOrdersKpiGet(): CancelablePromise<OrderManagementKPI> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/orders/kpi',
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
     * Delete Order
     * Delete an order (soft delete by setting status to cancelled).
     * @param orderId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteOrderApiOrdersOrderIdDelete(
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
     * Get Inventory Forecast
     * Get inventory forecast with optional filters.
     * @param storeId Filter by store ID
     * @param status Filter by inventory status
     * @param limit Maximum number of items to return
     * @param offset Number of items to skip
     * @returns InventoryForecastResponse Successful Response
     * @throws ApiError
     */
    public static getInventoryForecastApiInventoryForecastGet(
        storeId?: (string | null),
        status?: (InventoryStatus | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<InventoryForecastResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/inventory/forecast',
            query: {
                'store_id': storeId,
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
     * Get Inventory History
     * Get inventory transaction history.
     * @param productId Filter by product ID
     * @param storeId Filter by store ID
     * @param transactionType Filter by transaction type
     * @param limit Maximum number of records to return
     * @param offset Number of records to skip
     * @returns InventoryHistory Successful Response
     * @throws ApiError
     */
    public static getInventoryHistoryApiInventoryHistoryGet(
        productId?: (number | null),
        storeId?: (string | null),
        transactionType?: (string | null),
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<InventoryHistory>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/inventory/history',
            query: {
                'product_id': productId,
                'store_id': storeId,
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
     * Create Inventory Transaction
     * Record a new inventory transaction.
     * @param requestBody
     * @returns InventoryHistory Successful Response
     * @throws ApiError
     */
    public static createInventoryTransactionApiInventoryHistoryPost(
        requestBody: InventoryHistory,
    ): CancelablePromise<InventoryHistory> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/inventory/history',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
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
}
