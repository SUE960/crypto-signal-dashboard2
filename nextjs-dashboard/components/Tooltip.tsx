'use client';

import React, { useState, useRef, useEffect } from 'react';

interface TooltipProps {
  content: string;
  children: React.ReactNode;
}

const Tooltip: React.FC<TooltipProps> = ({ content, children }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isVisible && triggerRef.current && tooltipRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      
      // 툴팁 위치 계산 (트리거 요소 위에 표시)
      let top = triggerRect.top - tooltipRect.height - 12;
      let left = triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2);
      
      // 화면 밖으로 나가지 않도록 조정
      if (left < 10) left = 10;
      if (left + tooltipRect.width > window.innerWidth - 10) {
        left = window.innerWidth - tooltipRect.width - 10;
      }
      
      // 위쪽 공간이 부족하면 아래에 표시
      if (top < 10) {
        top = triggerRect.bottom + 12;
      }
      
      setPosition({ top, left });
    }
  }, [isVisible]);

  const handleMouseEnter = () => {
    setIsVisible(true);
  };

  const handleMouseLeave = () => {
    setIsVisible(false);
  };

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className="inline-block cursor-help"
      >
        {children}
      </div>
      
      {isVisible && (
        <div
          ref={tooltipRef}
          className="fixed z-[9999] animate-fadeIn"
          style={{
            top: `${position.top}px`,
            left: `${position.left}px`,
          }}
        >
          {/* 말풍선 본체 */}
          <div className="relative bg-white text-gray-900 rounded-xl shadow-2xl border border-gray-200 p-4 max-w-md">
            {/* 내용 */}
            <div className="text-sm leading-relaxed whitespace-pre-line">
              {content}
            </div>
            
            {/* 화살표 (아래쪽) */}
            <div className="absolute left-1/2 transform -translate-x-1/2 -bottom-2">
              <div className="w-4 h-4 bg-white border-b border-r border-gray-200 transform rotate-45"></div>
            </div>
          </div>
        </div>
      )}
      
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-4px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.2s ease-out;
        }
      `}</style>
    </>
  );
};

export default Tooltip;

