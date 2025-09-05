/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InventoryStatus } from './InventoryStatus';
/**
 * Model for updating inventory forecast.
 */
export type InventoryForecastUpdate = {
    current_stock?: (number | null);
    forecast_30_days?: (number | null);
    reorder_point?: (number | null);
    reorder_quantity?: (number | null);
    status?: (InventoryStatus | null);
};

