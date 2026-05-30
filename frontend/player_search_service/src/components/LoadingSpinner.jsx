import React from 'react';

function LoadingSpinner({ size = 'md', text = 'Загрузка...' }) {
  const sizes = {
    sm: { width: '20px', height: '20px', borderWidth: '2px' },
    md: { width: '40px', height: '40px', borderWidth: '3px' },
    lg: { width: '60px', height: '60px', borderWidth: '4px' },
  };

  return (
    <div className="empty-state">
      <div 
        className="loading-spinner" 
        style={sizes[size]}
      />
      {text && <p className="mt-4">{text}</p>}
    </div>
  );
}

export default LoadingSpinner;