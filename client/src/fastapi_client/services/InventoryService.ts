/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InventoryForecast } from '../models/InventoryForecast';
import type { InventoryForecastResponse } from '../models/InventoryForecastResponse';
import type { InventoryForecastUpdate } from '../models/InventoryForecastUpdate';
import type { InventoryHistory } from '../models/InventoryHistory';
import type { InventoryStatus } from '../models/InventoryStatus';
import type { StockManagementAlertKPI } from '../models/StockManagementAlertKPI';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class InventoryService {
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
