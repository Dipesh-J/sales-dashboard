import { Box, FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import { useGlobalState } from '../../context/GlobalState';

const GlobalFilters = () => {
    const { filters, filterOptions, updateFilter } = useGlobalState();

    const handleFilterChange = (key) => (event) => {
        updateFilter(key, event.target.value);
    };

    return (
        <Box sx={{ display: 'flex', gap: 2, p: 2, bgcolor: '#f5f5f5', borderBottom: '1px solid #e0e0e0' }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Date Range</InputLabel>
                <Select value={filters.dateRange} label="Date Range" onChange={handleFilterChange('dateRange')}>
                    <MenuItem value="month">Month</MenuItem>
                    <MenuItem value="quarter">Quarter</MenuItem>
                    <MenuItem value="year">Year</MenuItem>
                </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Brand</InputLabel>
                <Select value={filters.brand} label="Brand" onChange={handleFilterChange('brand')}>
                    {filterOptions.brands.map(brand => (
                        <MenuItem key={brand} value={brand}>{brand}</MenuItem>
                    ))}
                </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Category</InputLabel>
                <Select value={filters.category} label="Category" onChange={handleFilterChange('category')}>
                    {filterOptions.categories.map(cat => (
                        <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                    ))}
                </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Region</InputLabel>
                <Select value={filters.region} label="Region" onChange={handleFilterChange('region')}>
                    {filterOptions.regions.map(reg => (
                        <MenuItem key={reg} value={reg}>{reg}</MenuItem>
                    ))}
                </Select>
            </FormControl>
        </Box>
    );
};

export default GlobalFilters;
