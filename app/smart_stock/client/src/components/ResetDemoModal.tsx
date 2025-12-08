import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  RotateCcw, 
  ExternalLink, 
  CheckCircle, 
  XCircle, 
  Loader2,
  AlertTriangle,
  Play
} from 'lucide-react';

interface JobRunStatus {
  run_id: number;
  job_id: number;
  state: string;
  life_cycle_state: string;
  result_state?: string;
  state_message?: string;
  run_page_url?: string;
}

interface ResetDemoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ResetDemoModal({ isOpen, onClose }: ResetDemoModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  const [currentRun, setCurrentRun] = useState<JobRunStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Check for active runs when modal opens
  useEffect(() => {
    if (isOpen) {
      checkActiveRun();
    }
  }, [isOpen]);

  // Poll for status updates when a run is active
  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;

    if (isPolling && currentRun?.run_id) {
      intervalId = setInterval(() => {
        fetchRunStatus(currentRun.run_id);
      }, 3000); // Poll every 3 seconds
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isPolling, currentRun?.run_id]);

  const checkActiveRun = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch('/api/jobs/demo-reset/active-run');
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || 'Failed to check active runs');
      }
      
      const data = await response.json();
      
      if (data) {
        setCurrentRun(data);
        // Start polling if the run is still active
        if (isRunActive(data.life_cycle_state)) {
          setIsPolling(true);
        }
      } else {
        setCurrentRun(null);
        setIsPolling(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check job status');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRunStatus = async (runId: number) => {
    try {
      const response = await fetch(`/api/jobs/demo-reset/run/${runId}`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || 'Failed to fetch run status');
      }
      
      const data = await response.json();
      setCurrentRun(data);
      
      // Stop polling if the run is complete
      if (!isRunActive(data.life_cycle_state)) {
        setIsPolling(false);
      }
    } catch (err) {
      console.error('Error fetching run status:', err);
      // Don't set error here to avoid interrupting the UI during polling
    }
  };

  const triggerReset = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch('/api/jobs/demo-reset/trigger', {
        method: 'POST',
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || 'Failed to trigger demo reset');
      }
      
      const data = await response.json();
      
      // Fetch the full run status
      await fetchRunStatus(data.run_id);
      setIsPolling(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger demo reset');
    } finally {
      setIsLoading(false);
    }
  };

  const isRunActive = (state: string): boolean => {
    return ['PENDING', 'RUNNING', 'QUEUED', 'BLOCKED'].includes(state);
  };

  const getStateIcon = () => {
    if (!currentRun) return null;
    
    const state = currentRun.life_cycle_state;
    const resultState = currentRun.result_state;
    
    if (isRunActive(state)) {
      return <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />;
    }
    
    if (state === 'TERMINATED') {
      if (resultState === 'SUCCESS') {
        return <CheckCircle className="h-8 w-8 text-green-500" />;
      } else if (resultState === 'FAILED' || resultState === 'TIMEDOUT') {
        return <XCircle className="h-8 w-8 text-red-500" />;
      } else if (resultState === 'CANCELED') {
        return <AlertTriangle className="h-8 w-8 text-yellow-500" />;
      }
    }
    
    return <AlertTriangle className="h-8 w-8 text-gray-500" />;
  };

  const getStateText = () => {
    if (!currentRun) return '';
    
    const state = currentRun.life_cycle_state;
    const resultState = currentRun.result_state;
    
    if (state === 'PENDING') return 'Preparing...';
    if (state === 'QUEUED') return 'Queued...';
    if (state === 'RUNNING') return 'Running...';
    if (state === 'BLOCKED') return 'Waiting for resources...';
    
    if (state === 'TERMINATED') {
      if (resultState === 'SUCCESS') return 'Completed successfully!';
      if (resultState === 'FAILED') return 'Failed';
      if (resultState === 'TIMEDOUT') return 'Timed out';
      if (resultState === 'CANCELED') return 'Canceled';
    }
    
    return state;
  };

  const getProgressValue = () => {
    if (!currentRun) return 0;
    
    const state = currentRun.life_cycle_state;
    const resultState = currentRun.result_state;
    
    if (state === 'PENDING' || state === 'QUEUED') return 10;
    if (state === 'BLOCKED') return 20;
    if (state === 'RUNNING') return 50;
    if (state === 'TERMINATED') {
      if (resultState === 'SUCCESS') return 100;
      return 100; // Show full bar for any terminal state
    }
    
    return 0;
  };

  const canTriggerNewRun = !currentRun || !isRunActive(currentRun.life_cycle_state);

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <RotateCcw className="h-5 w-5 text-blue-600" />
            Reset Demo Data
          </DialogTitle>
          <DialogDescription>
            This will regenerate all demo data including products, warehouses, transactions, and forecasts.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {isLoading && !currentRun && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
            </div>
          )}

          {currentRun && (
            <div className="space-y-4">
              {/* Status Display */}
              <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                {getStateIcon()}
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{getStateText()}</p>
                  {currentRun.state_message && (
                    <p className="text-sm text-gray-600 mt-1">{currentRun.state_message}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">Run ID: {currentRun.run_id}</p>
                </div>
              </div>

              {/* Progress Bar */}
              {isRunActive(currentRun.life_cycle_state) && (
                <div className="space-y-2">
                  <Progress value={getProgressValue()} className="h-2" />
                  <p className="text-xs text-gray-500 text-center">
                    This may take a few minutes...
                  </p>
                </div>
              )}

              {/* Link to Databricks */}
              {currentRun.run_page_url && (
                <a
                  href={currentRun.run_page_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 p-3 bg-blue-50 hover:bg-blue-100 rounded-lg text-blue-700 transition-colors"
                >
                  <ExternalLink className="h-4 w-4" />
                  <span className="text-sm font-medium">View in Databricks</span>
                </a>
              )}

              {/* Success message */}
              {currentRun.life_cycle_state === 'TERMINATED' && currentRun.result_state === 'SUCCESS' && (
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
                  Demo data has been reset successfully! Refresh the page to see the new data.
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-2">
            {canTriggerNewRun && (
              <Button
                onClick={triggerReset}
                disabled={isLoading}
                className="flex-1 bg-blue-600 hover:bg-blue-700"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Play className="h-4 w-4 mr-2" />
                )}
                {currentRun ? 'Run Again' : 'Start Reset'}
              </Button>
            )}
            
            <Button
              variant="outline"
              onClick={onClose}
              className="flex-1"
            >
              {isRunActive(currentRun?.life_cycle_state || '') ? 'Close' : 'Done'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

