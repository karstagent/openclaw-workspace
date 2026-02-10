'use client';

import React, { useEffect, useState } from 'react';
import { Activity, ArrowDown, ArrowUp, ArrowRight } from 'lucide-react';

interface MetricProps {
  title: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  change: number;
  className?: string;
  isLoading?: boolean;
}

const MetricWidget: React.FC<MetricProps> = ({
  title,
  value,
  unit,
  trend,
  change,
  className = '',
  isLoading = false,
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <ArrowUp className="h-4 w-4 text-success" />;
      case 'down':
        return <ArrowDown className="h-4 w-4 text-danger" />;
      case 'stable':
        return <ArrowRight className="h-4 w-4 text-content-muted" />;
    }
  };

  const getTrendClass = () => {
    switch (trend) {
      case 'up':
        return 'text-success';
      case 'down':
        return 'text-danger';
      case 'stable':
        return 'text-content-muted';
    }
  };

  return (
    <div className={`glass-card glass-card-hover ${className}`}>
      <h3 className="text-sm font-medium text-content-muted mb-1">{title}</h3>
      {isLoading ? (
        <div className="animate-pulse h-8 bg-glass-light rounded-md my-1"></div>
      ) : (
        <div className="flex items-baseline">
          <span className="text-2xl font-bold text-content">{value}</span>
          <span className="text-xs ml-1 text-content-subtle">{unit}</span>
        </div>
      )}
      {isLoading ? (
        <div className="animate-pulse h-4 bg-glass-light rounded-md mt-2 w-20"></div>
      ) : (
        <div className={`flex items-center mt-2 text-xs ${getTrendClass()}`}>
          {getTrendIcon()}
          <span className="ml-1">
            {change > 0 ? '+' : ''}
            {change}% from last period
          </span>
        </div>
      )}
    </div>
  );
};

interface LineChartProps {
  data: number[];
  height?: number;
  lineColor?: string;
  fillColor?: string;
  isLoading?: boolean;
}

const MiniLineChart: React.FC<LineChartProps> = ({
  data,
  height = 40,
  lineColor = 'rgba(14, 165, 233, 0.8)',
  fillColor = 'rgba(14, 165, 233, 0.2)',
  isLoading = false,
}) => {
  // If loading or no data, show placeholder
  if (isLoading || !data.length) {
    return (
      <div 
        style={{ height: `${height}px` }}
        className="w-full animate-pulse bg-glass-light rounded-md"
      ></div>
    );
  }

  // Calculate min and max for scaling
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1; // Avoid division by zero

  // Create SVG path
  const width = 100; // Percentage width
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  const linePath = `M ${points}`;
  
  // Create a path for the area under the line
  const areaPath = `
    M 0,${height} 
    L ${points} 
    L ${width},${height} 
    Z
  `;

  return (
    <svg
      className="w-full overflow-visible"
      style={{ height: `${height}px` }}
      preserveAspectRatio="none"
      viewBox={`0 0 ${width} ${height}`}
    >
      <path
        d={areaPath}
        fill={fillColor}
        fillOpacity="0.3"
      />
      <path
        d={linePath}
        fill="none"
        stroke={lineColor}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export interface MetricData {
  id: string;
  title: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  change: number;
  history: number[];
}

interface MetricsWidgetProps {
  title?: string;
  metrics?: MetricData[];
  isLoading?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

// Real system metrics - these should be fetched from an API in production
const defaultMetrics: MetricData[] = [
  {
    id: 'cpu',
    title: 'CPU Usage',
    value: 32,
    unit: '%',
    trend: 'stable',
    change: 0,
    history: [30, 31, 33, 32, 35, 36, 32, 31, 32, 32]
  },
  {
    id: 'memory',
    title: 'Memory Usage',
    value: 45,
    unit: '%',
    trend: 'up',
    change: 2,
    history: [40, 42, 41, 43, 42, 44, 45, 45, 45, 45]
  },
  {
    id: 'disk',
    title: 'Disk I/O',
    value: 3,
    unit: 'MB/s',
    trend: 'down',
    change: -1,
    history: [5, 4, 6, 5, 4, 4, 3, 3, 3, 3]
  },
  {
    id: 'network',
    title: 'Network Traffic',
    value: 128,
    unit: 'KB/s',
    trend: 'up',
    change: 5,
    history: [100, 105, 110, 115, 120, 125, 122, 124, 127, 128]
  },
  {
    id: 'latency',
    title: 'API Latency',
    value: 85,
    unit: 'ms',
    trend: 'down',
    change: -2,
    history: [92, 90, 91, 89, 88, 87, 86, 86, 85, 85]
  },
  {
    id: 'errors',
    title: 'Error Rate',
    value: 0,
    unit: '%',
    trend: 'stable',
    change: 0,
    history: [1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
  },
];

const MetricsWidget: React.FC<MetricsWidgetProps> = ({
  title = 'System Metrics',
  metrics: initialMetrics,
  isLoading = false,
  autoRefresh = false, // Disabled auto-refresh of synthetic data
  refreshInterval = 30000, // 30 seconds
}) => {
  const [metrics, setMetrics] = useState<MetricData[]>(initialMetrics || defaultMetrics);
  const [refreshing, setRefreshing] = useState(false);

  // This function would be replaced with a real API call in production
  const fetchRealMetrics = async () => {
    try {
      // In a real implementation, this would fetch metrics from an API
      // For now, we'll just return the static metrics
      return defaultMetrics;
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      return metrics; // Return current metrics on error
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    const updatedMetrics = await fetchRealMetrics();
    setMetrics(updatedMetrics);
    setRefreshing(false);
  };

  return (
    <div className="glass-container p-4">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center">
          <Activity className="h-5 w-5 mr-2 text-content" />
          <h2 className="text-lg font-semibold text-content">{title}</h2>
        </div>
        <button
          className={`glass-button px-3 py-1 text-xs ${refreshing ? 'opacity-50' : ''}`}
          onClick={handleRefresh}
          disabled={refreshing}
        >
          {refreshing ? 'Refreshing...' : 'Refresh Now'}
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {metrics.map((metric) => (
          <div key={metric.id} className="glass-card">
            <MetricWidget
              title={metric.title}
              value={metric.value}
              unit={metric.unit}
              trend={metric.trend}
              change={metric.change}
              isLoading={isLoading}
            />
            <div className="mt-2">
              <MiniLineChart
                data={metric.history}
                isLoading={isLoading}
                lineColor={
                  metric.trend === 'up'
                    ? 'rgba(16, 185, 129, 0.8)'
                    : metric.trend === 'down'
                    ? 'rgba(239, 68, 68, 0.8)'
                    : 'rgba(14, 165, 233, 0.8)'
                }
                fillColor={
                  metric.trend === 'up'
                    ? 'rgba(16, 185, 129, 0.2)'
                    : metric.trend === 'down'
                    ? 'rgba(239, 68, 68, 0.2)'
                    : 'rgba(14, 165, 233, 0.2)'
                }
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MetricsWidget;