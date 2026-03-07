import { Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Typography, IconButton } from '@mui/material';
import { Dashboard, Storefront, FileUpload, DarkMode, LightMode } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useGlobalState } from '../../context/GlobalState';

const drawerWidth = 240;

const Sidebar = ({ mobileOpen, onClose, isMobile }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const { darkMode, toggleDarkMode } = useGlobalState();

    const menuItems = [
        { text: 'Upload Data', icon: <FileUpload />, path: '/' },
        { text: 'Sales Overview', icon: <Dashboard />, path: '/sales' },
        { text: 'Active Stores', icon: <Storefront />, path: '/stores' },
    ];

    const handleNav = (path) => {
        navigate(path);
        if (isMobile) onClose();
    };

    const drawerContent = (
        <>
            <Box sx={{ p: 2, borderBottom: '1px solid rgba(255, 255, 255, 0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" fontWeight="bold">Analytics Dashboard</Typography>
                <IconButton onClick={toggleDarkMode} sx={{ color: 'white' }} size="small">
                    {darkMode ? <LightMode /> : <DarkMode />}
                </IconButton>
            </Box>
            <List>
                {menuItems.map((item) => (
                    <ListItem key={item.text} disablePadding>
                        <ListItemButton
                            selected={location.pathname === item.path}
                            onClick={() => handleNav(item.path)}
                            sx={{
                                '&.Mui-selected': { backgroundColor: 'var(--color-magenta)' },
                                '&:hover': { backgroundColor: 'var(--color-sales-header)' },
                                '&.Mui-selected:hover': { backgroundColor: 'var(--color-magenta)' },
                            }}
                        >
                            <ListItemIcon sx={{ color: 'white' }}>{item.icon}</ListItemIcon>
                            <ListItemText primary={item.text} />
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
        </>
    );

    return (
        <Drawer
            variant={isMobile ? 'temporary' : 'permanent'}
            open={isMobile ? mobileOpen : true}
            onClose={onClose}
            ModalProps={{ keepMounted: true }}
            sx={{
                width: isMobile ? 0 : drawerWidth,
                flexShrink: 0,
                '& .MuiDrawer-paper': {
                    width: drawerWidth,
                    boxSizing: 'border-box',
                    backgroundColor: 'var(--color-sidebar-bg)',
                    color: 'white',
                    borderRight: '1px solid var(--color-border)',
                },
            }}
        >
            {drawerContent}
        </Drawer>
    );
};

export default Sidebar;
