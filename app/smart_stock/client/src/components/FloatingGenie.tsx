import React, { useState, useEffect } from 'react';
import { MessageCircle, X, Minimize2, Maximize2, Sparkles } from 'lucide-react';
import GenieChat from './GenieChat';

export default function FloatingGenie() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [hasUnread, setHasUnread] = useState(false);

  // Show a subtle pulse animation on first load to draw attention
  const [showPulse, setShowPulse] = useState(true);

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
          className={`fixed bottom-6 right-6 z-[9999] p-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-full shadow-lg hover:shadow-xl transform transition-all hover:scale-110 ${
            showPulse ? 'animate-pulse' : ''
          }`}
          aria-label="Open AI Assistant"
        >
          <div className="relative">
            <MessageCircle className="h-6 w-6" />
            {hasUnread && (
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full animate-ping" />
            )}
          </div>
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <>
          {/* Backdrop for mobile */}
          <div
            className="md:hidden fixed inset-0 bg-black/30 z-[9998]"
            onClick={() => setIsOpen(false)}
          />

          {/* Chat Container */}
          <div
            className={`fixed z-[9999] bg-white rounded-lg shadow-2xl transition-all transform ${
              isMinimized
                ? 'bottom-6 right-6 w-80 h-14'
                : 'bottom-6 right-6 w-full h-[90vh] md:w-[800px] md:h-[600px] max-w-[calc(100vw-3rem)] max-h-[calc(100vh-3rem)]'
            }`}
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

            {/* Full Chat */}
            {!isMinimized && (
              <div className="h-full flex flex-col">
                {/* Header Controls */}
                <div className="absolute top-4 right-4 z-[10000] flex items-center gap-2">
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
                <GenieChat onClose={() => setIsOpen(false)} />
              </div>
            )}
          </div>
        </>
      )}
    </>
  );
}