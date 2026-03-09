import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const GlobalStateContext = createContext();

export const GlobalStateProvider = ({ children }) => {
  const [filters, setFilters] = useState({
    dateRange: 'year', // month, quarter, year
    brand: 'All',
    category: 'All',
    region: 'All',
  });

  const [filterOptions, setFilterOptions] = useState({
    brands: ['All'],
    categories: ['All'],
    regions: ['All'],
    dateRanges: [],
  });

  // Dark mode state with localStorage persistence
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });

  // Dashboard data for CSV export
  const [dashboardData, setDashboardData] = useState(null);

  // Apply dark mode class to body
  useEffect(() => {
    document.body.classList.toggle('dark-mode', darkMode);
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode(prev => !prev);

  // Fetch initial filter options from backend
  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const [brandsRes, categoriesRes, regionsRes, datesRes] = await Promise.all([
          api.get('/api/filters/brands').catch(() => ({ data: [] })),
          api.get('/api/filters/categories').catch(() => ({ data: [] })),
          api.get('/api/filters/regions').catch(() => ({ data: [] })),
          api.get('/api/filters/date-range').catch(() => ({ data: [] }))
        ]);

        setFilterOptions({
          brands: ['All', ...brandsRes.data.map(i => i.name || i)],
          categories: ['All', ...categoriesRes.data.map(i => i.name || i)],
          regions: ['All', ...regionsRes.data.map(i => i.name || i)],
          dateRanges: datesRes.data.length ? datesRes.data : ['year', 'quarter', 'month']
        });
      } catch (error) {
        console.error("Failed to fetch filters", error);
      }
    };
    fetchFilters();
  }, []);

  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  return (
    <GlobalStateContext.Provider value={{
      filters, filterOptions, updateFilter,
      darkMode, toggleDarkMode,
      dashboardData, setDashboardData
    }}>
      {children}
    </GlobalStateContext.Provider>
  );
};

export const useGlobalState = () => useContext(GlobalStateContext);
