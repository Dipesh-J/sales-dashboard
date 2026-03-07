import { useState } from 'react';
import { Box, IconButton, useMediaQuery } from '@mui/material';
import { Menu as MenuIcon } from '@mui/icons-material';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import FilterBar from './FilterBar';

const drawerWidth = 240;

const Layout = () => {
    const location = useLocation();
    const isDashboard = location.pathname === '/sales' || location.pathname === '/stores';
    const isMobile = useMediaQuery('(max-width: 768px)');
    const [mobileOpen, setMobileOpen] = useState(false);

    return (
        <Box sx={{ display: 'flex', height: '100vh', width: '100vw' }}>
            <Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} isMobile={isMobile} />
            <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', width: isMobile ? '100%' : `calc(100% - ${drawerWidth}px)` }}>
                {isMobile && (
                    <Box sx={{ display: 'flex', alignItems: 'center', px: 1, py: 0.5, borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-page)' }}>
                        <IconButton onClick={() => setMobileOpen(true)} sx={{ color: 'var(--color-text-dark)' }}>
                            <MenuIcon />
                        </IconButton>
                    </Box>
                )}
                {isDashboard && <FilterBar />}
                <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto', backgroundColor: 'var(--color-bg-page)' }}>
                    <Outlet />
                </Box>
            </Box>
        </Box>
    );
};

export default Layout;
