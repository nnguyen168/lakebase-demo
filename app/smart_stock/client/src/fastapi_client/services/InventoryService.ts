/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ForecastStatus } from '../models/ForecastStatus';
import type { InventoryForecast } from '../models/InventoryForecast';
import type { InventoryForecastResponse } from '../models/InventoryForecastResponse';
import type { InventoryForecastUpdate } from '../models/InventoryForecastUpdate';
import type { StockManagementAlertKPI } from '../models/StockManagementAlertKPI';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class InventoryService {
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
}
