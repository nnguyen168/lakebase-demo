/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Health
     * Health check endpoint.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static healthHealthGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health',
        });
    }
    /**
     * Debug Env
     * Debug endpoint to check environment variables.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static debugEnvDebugEnvGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/debug/env',
        });
    }
    /**
     * Test Api
     * Serve test page for API debugging.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static testApiTestApiGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/test-api',
        });
    }
    /**
     * Debug Db Test
     * Test database connection and query.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static debugDbTestDebugDbTestGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/debug/db-test',
        });
    }
}
