import React, { useState, useEffect, useImperativeHandle, forwardRef } from 'react';
import { Bot, X, Minimize2, Maximize2, Sparkles, RotateCcw } from 'lucide-react';
import AgentChat from './AgentChat';

export interface FloatingGenieRef {
  openWithMessage: (message: string) => void;
}

const FloatingGenie = forwardRef<FloatingGenieRef>((props, ref) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [hasUnread, setHasUnread] = useState(false);
  const [initialMessage, setInitialMessage] = useState<string | undefined>(undefined);
  const [chatKey, setChatKey] = useState(0);

  // Show a subtle pulse animation on first load to draw attention
  const [showPulse, setShowPulse] = useState(true);

  const handleNewChat = () => {
    setChatKey(prev => prev + 1);
    setInitialMessage(undefined);
  };

  // Expose methods to parent component
  useImperativeHandle(ref, () => ({
    openWithMessage: (message: string) => {
      setInitialMessage(message);
      setIsOpen(true);
      setIsMinimized(false);
      setShowPulse(false);
      setHasUnread(false);
    }
  }));

  useEffect(() => {
    // Stop pulse after user interacts
    if (isOpen) {
      setShowPulse(false);
      setHasUnread(false);
    }
  }, [isOpen]);

  const toggleChat = () => {
    if (isOpen && !isMinimized) {
      setIsOpen(false);
    } else {
      setIsOpen(true);
      setIsMinimized(false);
    }
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <button
          onClick={toggleChat}
          className="fixed bottom-6 right-6 z-[9999] p-4 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transform transition-all duration-300 hover:scale-110 group"
          aria-label="Open AI Assistant"
        >
          <div className="relative">
            <Bot className="h-7 w-7 transition-transform group-hover:scale-110" />
            {hasUnread && (
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full animate-ping" />
            )}
          </div>
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <>
          {/* Backdrop for mobile and desktop - only show when not minimized */}
          {!isMinimized && (
            <div
              className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[9998] transition-opacity duration-300 ease-out"
              onClick={() => setIsOpen(false)}
              style={{ animation: 'fadeIn 0.3s ease-out' }}
            />
          )}

          {/* Chat Container */}
          <div
            className={`fixed z-[9999] bg-white rounded-2xl shadow-2xl transition-all duration-500 ease-out transform ${
              isMinimized
                ? 'bottom-6 right-6 w-80 h-14 scale-95 opacity-90'
                : 'bottom-4 right-4 w-[95vw] h-[90vh] sm:w-[90vw] sm:h-[85vh] md:w-[80vw] md:h-[80vh] lg:w-[70vw] lg:h-[75vh] xl:w-[60vw] xl:h-[80vh] 2xl:w-[50vw] 2xl:h-[80vh] max-w-[1200px] max-h-[900px] scale-100 opacity-100'
            }`}
            style={{ 
              animation: isMinimized ? 'none' : 'slideInScale 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)'
            }}
          >
            {/* Minimized Header */}
            {isMinimized && (
              <div
                className="flex items-center justify-between p-4 cursor-pointer bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg"
                onClick={toggleMinimize}
              >
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-white" />
                  <span className="text-white font-medium">AI Assistant</span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleMinimize();
                    }}
                    className="text-white hover:bg-white/20 p-1 rounded"
                  >
                    <Maximize2 className="h-4 w-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setIsOpen(false);
                    }}
                    className="text-white hover:bg-white/20 p-1 rounded"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )}

            {/* Full Chat - always mounted to preserve state, just hidden when minimized */}
            <div className={`h-full flex flex-col ${isMinimized ? 'hidden' : ''}`}>
              {/* Header Controls */}
              <div className="absolute top-4 right-4 z-[10000] flex items-center gap-2">
                <button
                  onClick={handleNewChat}
                  className="px-3 py-2 bg-white/80 backdrop-blur rounded-lg shadow hover:bg-white transition-colors flex items-center gap-1.5"
                  aria-label="Start new chat"
                  title="Start new chat"
                >
                  <RotateCcw className="h-4 w-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-600">New Chat</span>
                </button>
                <button
                  onClick={toggleMinimize}
                  className="p-2 bg-white/80 backdrop-blur rounded-lg shadow hover:bg-white transition-colors"
                  aria-label="Minimize chat"
                >
                  <Minimize2 className="h-4 w-4 text-gray-600" />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 bg-white/80 backdrop-blur rounded-lg shadow hover:bg-white transition-colors"
                  aria-label="Close chat"
                >
                  <X className="h-4 w-4 text-gray-600" />
                </button>
              </div>

              {/* Chat Component */}
              <AgentChat 
                key={chatKey}
                onClose={() => setIsOpen(false)} 
                initialMessage={initialMessage}
                onMessageSent={() => setInitialMessage(undefined)}
                showNewChatButton={false}
              />
            </div>
          </div>
        </>
      )}
      
      {/* Custom Animations */}
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes slideInScale {
          from {
            opacity: 0;
            transform: scale(0.8) translateY(20px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
      `}</style>
    </>
  );
});

FloatingGenie.displayName = 'FloatingGenie';

export default FloatingGenie;