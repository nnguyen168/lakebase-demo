/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ForecastStatus } from './ForecastStatus';
/**
 * Model for updating inventory forecast.
 */
export type InventoryForecastUpdate = {
    current_stock?: (number | null);
    forecast_30_days?: (number | null);
    reorder_point?: (number | null);
    reorder_quantity?: (number | null);
    confidence_score?: (number | string | null);
    status?: (ForecastStatus | null);
};

