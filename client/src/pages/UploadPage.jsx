import { useState } from 'react';
import { Box, Button, Typography, Paper, Alert, Divider } from '@mui/material';
import { CloudUpload, GetApp } from '@mui/icons-material';
import api, { getSampleData } from '../services/api';

const UploadPage = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);
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
            const response = await api.post('/api/data/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred during upload');
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateSample = async () => {
        setGenerating(true);
        setError(null);
        try {
            const data = await getSampleData(10);

            // Convert to CSV
            if (data.length === 0) throw new Error("No data generated");

            const headers = Object.keys(data[0]);
            const csvRows = [
                headers.join(','), // header row
                ...data.map(row =>
                    headers.map(header => {
                        const cell = row[header] === null || row[header] === undefined ? '' : row[header];
                        return `"${String(cell).replace(/"/g, '""')}"`;
                    }).join(',')
                )
            ];
            const csvString = csvRows.join('\n');

            // Trigger download
            const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'sample_sales_data.csv');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            setResult({ summary: "Sample data generated and downloaded successfully!" });
        } catch (err) {
            setError(err.message || 'Failed to generate sample data');
        } finally {
            setGenerating(false);
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
                    {result.summary || "Upload successful!"}
                    {result.rows_processed !== undefined && ` Processed: ${result.rows_processed} rows, Inserted: ${result.rows_inserted} rows.`}
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

            <Divider sx={{ my: 4 }}>OR</Divider>

            <Button
                variant="outlined"
                fullWidth
                startIcon={<GetApp />}
                sx={{ py: 1.5, borderColor: '#F0005C', color: '#F0005C', '&:hover': { borderColor: '#D0004C', bgcolor: 'rgba(240, 0, 92, 0.04)' } }}
                disabled={generating}
                onClick={handleGenerateSample}
            >
                {generating ? 'Generating...' : 'Generate 10 rows of Sample Data'}
            </Button>
        </Box>
    );
};

export default UploadPage;
