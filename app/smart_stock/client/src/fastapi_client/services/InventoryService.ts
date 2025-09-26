/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ForecastStatus } from '../models/ForecastStatus';
import type { InventoryForecast } from '../models/InventoryForecast';
import type { InventoryForecastUpdate } from '../models/InventoryForecastUpdate';
import type { PaginatedResponse_InventoryForecastResponse_ } from '../models/PaginatedResponse_InventoryForecastResponse_';
import type { StockManagementAlertKPI } from '../models/StockManagementAlertKPI';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class InventoryService {
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
    ): CancelablePromise<Array<{date: string; stock_level: number}>> {
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
}
