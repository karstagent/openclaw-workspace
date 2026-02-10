'use client';

import React, { useState } from 'react';
import { Archive, ChevronDown, ChevronRight, Download, Filter, Search, Trash } from 'lucide-react';
import { formatDate } from '@/lib/utils';

interface ArchiveItem {
  id: string;
  title: string;
  type: 'message' | 'task' | 'alert' | 'report';
  category: string;
  timestamp: string;
  size: string;
  author: string;
  tags?: string[];
}

const SAMPLE_ARCHIVES: ArchiveItem[] = [
  {
    id: 'm1',
    title: 'Weekly Status Update - Jan 2026',
    type: 'message',
    category: 'Status Updates',
    timestamp: '2026-01-31T15:30:00Z',
    size: '42 KB',
    author: 'System',
    tags: ['weekly', 'status']
  },
  {
    id: 'm2',
    title: 'User Feedback Collection - Q1 2026',
    type: 'report',
    category: 'User Research',
    timestamp: '2026-02-01T09:15:00Z',
    size: '1.2 MB',
    author: 'Research Team',
    tags: ['user feedback', 'quarterly']
  },
  {
    id: 'm3',
    title: 'Server Outage Incident Report',
    type: 'alert',
    category: 'Incidents',
    timestamp: '2026-02-02T22:45:00Z',
    size: '156 KB',
    author: 'System',
    tags: ['outage', 'incident']
  },
  {
    id: 'm4',
    title: 'API Integration Documentation',
    type: 'message',
    category: 'Documentation',
    timestamp: '2026-02-03T11:20:00Z',
    size: '230 KB',
    author: 'Development Team',
    tags: ['api', 'docs']
  },
  {
    id: 'm5',
    title: 'Message Queue Performance Metrics',
    type: 'report',
    category: 'Performance',
    timestamp: '2026-02-04T14:10:00Z',
    size: '890 KB',
    author: 'Performance Team',
    tags: ['metrics', 'performance']
  },
  {
    id: 'm6',
    title: 'User Onboarding Flow Design',
    type: 'task',
    category: 'Design',
    timestamp: '2026-02-05T08:30:00Z',
    size: '1.8 MB',
    author: 'Design Team',
    tags: ['onboarding', 'design']
  },
  {
    id: 'm7',
    title: 'Database Optimization Recommendations',
    type: 'task',
    category: 'Development',
    timestamp: '2026-02-06T16:45:00Z',
    size: '125 KB',
    author: 'Database Team',
    tags: ['database', 'optimization']
  },
  {
    id: 'm8',
    title: 'Security Vulnerability Report - Feb 2026',
    type: 'alert',
    category: 'Security',
    timestamp: '2026-02-07T10:15:00Z',
    size: '315 KB',
    author: 'Security Team',
    tags: ['security', 'vulnerability']
  },
  {
    id: 'm9',
    title: 'System Architecture Documentation',
    type: 'message',
    category: 'Documentation',
    timestamp: '2026-02-07T13:20:00Z',
    size: '1.5 MB',
    author: 'Development Team',
    tags: ['architecture', 'docs']
  },
  {
    id: 'm10',
    title: 'Annual Budget Forecast - 2026',
    type: 'report',
    category: 'Finance',
    timestamp: '2026-02-08T09:00:00Z',
    size: '450 KB',
    author: 'Finance Team',
    tags: ['budget', 'annual']
  }
];

const typeIcons = {
  message: <Archive className="h-4 w-4 text-primary" />,
  task: <Archive className="h-4 w-4 text-success" />,
  alert: <Archive className="h-4 w-4 text-warning" />,
  report: <Archive className="h-4 w-4 text-danger" />
};

const ArchiveSystem: React.FC = () => {
  const [archives, setArchives] = useState<ArchiveItem[]>(SAMPLE_ARCHIVES);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [expandedFilters, setExpandedFilters] = useState(true);

  const types = ['all', 'message', 'task', 'alert', 'report'];
  const categories = ['all', ...Array.from(new Set(SAMPLE_ARCHIVES.map(item => item.category)))];
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };
  
  const handleTypeFilter = (type: string) => {
    setSelectedType(type);
  };
  
  const handleCategoryFilter = (category: string) => {
    setSelectedCategory(category);
  };
  
  const toggleItemSelection = (id: string) => {
    setSelectedItems(prev => 
      prev.includes(id) 
        ? prev.filter(itemId => itemId !== id)
        : [...prev, id]
    );
  };
  
  const toggleSelectAll = () => {
    if (selectedItems.length === filteredArchives.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(filteredArchives.map(item => item.id));
    }
  };
  
  const handleDeleteSelected = () => {
    setArchives(archives.filter(item => !selectedItems.includes(item.id)));
    setSelectedItems([]);
  };
  
  // Apply filters
  const filteredArchives = archives.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          item.author.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (item.tags && item.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())));
    
    const matchesType = selectedType === 'all' || item.type === selectedType;
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    
    return matchesSearch && matchesType && matchesCategory;
  });
  
  // Sort by date (newest first)
  const sortedArchives = [...filteredArchives].sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return (
    <div className="glass-container p-4">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <Archive className="h-5 w-5 mr-2 text-content" />
          <h2 className="text-lg font-semibold text-content">Message Archive System</h2>
        </div>
      </div>
      
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className={`glass-card ${expandedFilters ? 'md:w-1/4' : 'md:w-auto'}`}>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm font-semibold text-content">Filters</h3>
            <button 
              onClick={() => setExpandedFilters(!expandedFilters)}
              className="glass-button p-1 rounded-full"
            >
              {expandedFilters ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </button>
          </div>
          
          {expandedFilters && (
            <div className="space-y-4">
              <div>
                <label className="text-xs text-content-muted block mb-1">Type</label>
                <div className="flex flex-wrap gap-2">
                  {types.map(type => (
                    <button 
                      key={type}
                      className={`text-xs px-3 py-1 rounded-full ${selectedType === type ? 'glass-button-primary' : 'glass-button'}`}
                      onClick={() => handleTypeFilter(type)}
                    >
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="text-xs text-content-muted block mb-1">Category</label>
                <select 
                  className="glass-select w-full text-sm"
                  value={selectedCategory}
                  onChange={(e) => handleCategoryFilter(e.target.value)}
                >
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category === 'all' ? 'All Categories' : category}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="text-xs text-content-muted block mb-1">Date Range</label>
                <div className="grid grid-cols-2 gap-2">
                  <input 
                    type="date"
                    className="glass-input text-sm py-1"
                    placeholder="From"
                  />
                  <input 
                    type="date"
                    className="glass-input text-sm py-1"
                    placeholder="To"
                  />
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="flex-1">
          <div className="mb-4 flex flex-col md:flex-row gap-2">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-content-muted" />
              </div>
              <input
                type="text"
                className="glass-input pl-10 w-full"
                placeholder="Search archives..."
                value={searchTerm}
                onChange={handleSearch}
              />
            </div>
            
            <div className="flex gap-2">
              <button className="glass-button flex items-center">
                <Filter className="h-4 w-4 mr-1" />
                <span>More Filters</span>
              </button>
              
              {selectedItems.length > 0 && (
                <button 
                  className="glass-button-danger flex items-center"
                  onClick={handleDeleteSelected}
                >
                  <Trash className="h-4 w-4 mr-1" />
                  <span>Delete ({selectedItems.length})</span>
                </button>
              )}
            </div>
          </div>
          
          <div className="glass-container overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="text-content-muted text-xs uppercase border-b border-glass">
                  <th className="px-4 py-3 text-left">
                    <input
                      type="checkbox"
                      className="glass-checkbox"
                      checked={selectedItems.length === filteredArchives.length && filteredArchives.length > 0}
                      onChange={toggleSelectAll}
                    />
                  </th>
                  <th className="px-4 py-3 text-left">Title</th>
                  <th className="px-4 py-3 text-left">Type</th>
                  <th className="px-4 py-3 text-left">Category</th>
                  <th className="px-4 py-3 text-left">Date</th>
                  <th className="px-4 py-3 text-left">Size</th>
                  <th className="px-4 py-3 text-left">Author</th>
                  <th className="px-4 py-3 text-left">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-glass">
                {sortedArchives.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-content-muted">
                      No archive items found matching your criteria.
                    </td>
                  </tr>
                ) : (
                  sortedArchives.map(item => (
                    <tr key={item.id} className="text-sm hover:bg-glass-light">
                      <td className="px-4 py-3">
                        <input
                          type="checkbox"
                          className="glass-checkbox"
                          checked={selectedItems.includes(item.id)}
                          onChange={() => toggleItemSelection(item.id)}
                        />
                      </td>
                      <td className="px-4 py-3 font-medium">{item.title}</td>
                      <td className="px-4 py-3 flex items-center">
                        {typeIcons[item.type]}
                        <span className="ml-2 capitalize">{item.type}</span>
                      </td>
                      <td className="px-4 py-3">{item.category}</td>
                      <td className="px-4 py-3">{formatDate(item.timestamp)}</td>
                      <td className="px-4 py-3">{item.size}</td>
                      <td className="px-4 py-3">{item.author}</td>
                      <td className="px-4 py-3">
                        <button className="glass-button p-1 rounded-full mr-1">
                          <Download className="h-4 w-4" />
                        </button>
                        <button className="glass-button-danger p-1 rounded-full">
                          <Trash className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArchiveSystem;