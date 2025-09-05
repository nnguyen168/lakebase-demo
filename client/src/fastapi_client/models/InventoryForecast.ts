/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InventoryStatus } from './InventoryStatus';
/**
 * Inventory forecast model with metadata.
 */
export type InventoryForecast = {
    product_id: number;
    store_id: string;
    current_stock: number;
    forecast_30_days: number;
    reorder_point: number;
    reorder_quantity: number;
    status: InventoryStatus;
    forecast_id: number;
    last_updated: string;
    product_name?: (string | null);
    product_sku?: (string | null);
};

