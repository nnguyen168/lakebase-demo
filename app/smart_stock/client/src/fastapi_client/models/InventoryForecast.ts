/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ForecastStatus } from './ForecastStatus';
/**
 * Inventory forecast model with metadata.
 */
export type InventoryForecast = {
    product_id: number;
    warehouse_id: number;
    current_stock?: (number | null);
    forecast_30_days?: (number | null);
    reorder_point?: (number | null);
    reorder_quantity?: (number | null);
    confidence_score?: (string | null);
    status?: ForecastStatus;
    forecast_id: number;
    last_updated: string;
    product_name?: (string | null);
    product_sku?: (string | null);
    warehouse_name?: (string | null);
};

