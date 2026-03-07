import { Dialog, DialogTitle, DialogContent, IconButton, Table, TableHead, TableBody, TableRow, TableCell, CircularProgress, Box } from '@mui/material';
import { Close } from '@mui/icons-material';

const DrillDownModal = ({ open, onClose, title, data, isLoading, columns }) => {
    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', bgcolor: 'var(--color-bg-card)', color: 'var(--color-text-dark)' }}>
                {title}
                <IconButton onClick={onClose} size="small" sx={{ color: 'var(--color-text-gray)' }}>
                    <Close />
                </IconButton>
            </DialogTitle>
            <DialogContent sx={{ bgcolor: 'var(--color-bg-card)', p: 0 }}>
                {isLoading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                        <CircularProgress />
                    </Box>
                ) : data && data.length > 0 ? (
                    <Table size="small">
                        <TableHead>
                            <TableRow>
                                {columns.map(col => (
                                    <TableCell key={col.key} sx={{ fontWeight: 600, color: 'var(--color-text-dark)', borderColor: 'var(--color-border)' }}>
                                        {col.label}
                                    </TableCell>
                                ))}
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {data.map((row, i) => (
                                <TableRow key={i}>
                                    {columns.map(col => (
                                        <TableCell key={col.key} sx={{ color: 'var(--color-text-dark)', borderColor: 'var(--color-border)' }}>
                                            {col.format ? col.format(row[col.key]) : row[col.key]}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                ) : (
                    <Box sx={{ p: 3, textAlign: 'center', color: 'var(--color-text-gray)' }}>
                        No data available
                    </Box>
                )}
            </DialogContent>
        </Dialog>
    );
};

export default DrillDownModal;
