import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import { GlobalStateProvider } from './context/GlobalState';
import UploadPage from './pages/UploadPage';

const SalesDashboard = lazy(() => import('./pages/SalesDashboard'));
const StoresDashboard = lazy(() => import('./pages/StoresDashboard'));

function App() {
  return (
    <Router>
      <GlobalStateProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<UploadPage />} />
            <Route path="sales" element={
              <Suspense fallback={<div style={{ padding: '2rem', textAlign: 'center' }}>Loading dashboard…</div>}>
                <SalesDashboard />
              </Suspense>
            } />
            <Route path="stores" element={
              <Suspense fallback={<div style={{ padding: '2rem', textAlign: 'center' }}>Loading dashboard…</div>}>
                <StoresDashboard />
              </Suspense>
            } />
          </Route>
        </Routes>
      </GlobalStateProvider>
    </Router>
  );
}

export default App;
