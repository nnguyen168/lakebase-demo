/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InventoryStatus } from './InventoryStatus';
/**
 * Response model for inventory forecast display.
 */
export type InventoryForecastResponse = {
    forecast_id: number;
    item_id: string;
    item_name: string;
    stock: number;
    forecast_30_days: number;
    status: InventoryStatus;
    action: string;
};

