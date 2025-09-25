/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Model for creating a new order.
 */
export type OrderCreate = {
    product_id: number;
    quantity: number;
    warehouse_id: number;
    requested_by: string;
    notes?: (string | null);
    forecast_id?: (number | null);
};

