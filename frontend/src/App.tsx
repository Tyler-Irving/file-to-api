import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import DatasetList from './components/DatasetList';
import DatasetDetail from './components/DatasetDetail';
import FileUpload from './components/FileUpload';
import APIKeys from './components/APIKeys';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<DatasetList />} />
            <Route path="/upload" element={<FileUpload />} />
            <Route path="/datasets/:slug" element={<DatasetDetail />} />
            <Route path="/keys" element={<APIKeys />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
