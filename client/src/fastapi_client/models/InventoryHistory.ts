/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Inventory history model with ID.
 */
export type InventoryHistory = {
    product_id: number;
    store_id: string;
    quantity_change: number;
    transaction_type: string;
    reference_id?: (string | null);
    notes?: (string | null);
    history_id: number;
    transaction_date: string;
    balance_after: number;
    created_by: string;
};

