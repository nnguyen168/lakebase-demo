/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OTPRMetrics } from '../models/OTPRMetrics';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class OtprService {
    /**
     * Get Otpr Metrics
     * Get On-Time Production Rate metrics from the otpr view.
     *
     * Returns the current and previous 30-day OTPR percentages,
     * the percentage point change, and trend indicator.
     *
     * This endpoint reads real-time metrics from the database view,
     * so it will reflect any updates immediately.
     * @returns OTPRMetrics Successful Response
     * @throws ApiError
     */
    public static getOtprMetricsApiOtprGet(): CancelablePromise<OTPRMetrics> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/otpr/',
        });
    }
}
