import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import { GlobalStateProvider } from './context/GlobalState';
import UploadPage from './pages/UploadPage';

import SalesDashboard from './pages/SalesDashboard';

// Placeholders for dashboards
import StoresDashboard from './pages/StoresDashboard';

function App() {
  return (
    <Router>
      <GlobalStateProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<UploadPage />} />
            <Route path="sales" element={<SalesDashboard />} />
            <Route path="stores" element={<StoresDashboard />} />
          </Route>
        </Routes>
      </GlobalStateProvider>
    </Router>
  );
}

export default App;
