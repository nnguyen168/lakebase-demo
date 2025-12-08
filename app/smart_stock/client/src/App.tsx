import React, { useEffect, Suspense, useRef, createContext } from "react";
import { Toaster } from "@/components/ui/toaster";
import FloatingGenie, { FloatingGenieRef } from "@/components/FloatingGenie";

// Create context for FloatingGenie ref
export const FloatingGenieContext = createContext<React.RefObject<FloatingGenieRef> | null>(null);

// Lazy load the dashboard to catch any import errors
const SmartStockDashboard = React.lazy(() =>
  import("./pages/SmartStockDashboard").catch((error) => {
    console.error("Failed to load SmartStockDashboard:", error);
    return { default: () => <div>Error loading dashboard: {error.message}</div> };
  })
);

// Error boundary component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', backgroundColor: '#fee', color: '#c00' }}>
          <h1>Application Error</h1>
          <pre>{this.state.error?.message || "Unknown error"}</pre>
          <p>Check the browser console for more details.</p>
        </div>
      );
    }

    return this.props.children;
  }
}

function App() {
  const floatingGenieRef = useRef<FloatingGenieRef>(null);

  useEffect(() => {
    console.log("App component mounted successfully!");
    console.log("React version:", React.version);
    console.log("Window location:", window.location.href);
  }, []);

  return (
    <ErrorBoundary>
      <FloatingGenieContext.Provider value={floatingGenieRef}>
        <div style={{ minHeight: '100vh', backgroundColor: '#ffffff' }}>
          <Suspense fallback={
            <div style={{ padding: '20px', textAlign: 'center' }}>
              <h1 style={{ color: '#333', fontSize: '24px' }}>Loading SmartStock...</h1>
              <p style={{ color: '#666' }}>If this message persists, check the browser console.</p>
            </div>
          }>
            <SmartStockDashboard />
          </Suspense>
          <FloatingGenie ref={floatingGenieRef} />
        </div>
        <Toaster />
      </FloatingGenieContext.Provider>
    </ErrorBoundary>
  );
}

export default App;