import { useState } from 'react';
import { Box, Button, Typography, Paper, Alert } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import axios from 'axios';

const UploadPage = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            if (!selectedFile.name.match(/\.(csv|xlsx|xls)$/)) {
                setError('Please upload a valid .csv or .xlsx file');
                setFile(null);
                return;
            }
            setFile(selectedFile);
            setError(null);
            setResult(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:8000/api/data/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred during upload');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
            <Typography variant="h4" mb={4} fontWeight="bold">Upload Sales Data</Typography>

            <Paper
                elevation={0}
                sx={{
                    p: 4,
                    textAlign: 'center',
                    border: '2px dashed #ccc',
                    borderRadius: 2,
                    bgcolor: '#fafafa',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    '&:hover': { bgcolor: '#f0f0f0', borderColor: '#999' }
                }}
                component="label"
            >
                <input
                    type="file"
                    hidden
                    accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                    onChange={handleFileChange}
                />
                <CloudUpload sx={{ fontSize: 60, color: '#9e9e9e', mb: 2, display: 'block' }} />
                <Typography variant="h6">
                    {file ? file.name : 'Click or drag file to this area to upload'}
                </Typography>
                <Typography variant="body2" color="textSecondary" mt={1}>
                    Supports .csv and .xlsx
                </Typography>
            </Paper>

            {error && (
                <Alert severity="error" sx={{ mt: 3 }}>
                    {error}
                </Alert>
            )}

            {result && (
                <Alert severity="success" sx={{ mt: 3 }}>
                    Upload successful! Processed: {result.rows_processed} rows, Inserted: {result.rows_inserted} rows.
                    {result.errors?.length > 0 && (
                        <Box mt={1}>
                            <strong>Errors encountered:</strong>
                            <ul>
                                {result.errors.map((err, i) => <li key={i}>{err}</li>)}
                            </ul>
                        </Box>
                    )}
                </Alert>
            )}

            <Button
                variant="contained"
                fullWidth
                sx={{ mt: 4, py: 1.5, bgcolor: '#F0005C', '&:hover': { bgcolor: '#D0004C' } }}
                disabled={!file || loading}
                onClick={handleUpload}
            >
                {loading ? 'Uploading...' : 'Upload Data To Backend'}
            </Button>
        </Box>
    );
};

export default UploadPage;
