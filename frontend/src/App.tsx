import { BrowserRouter, Routes, Route } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import Header from './components/Header'
import ScriptList from './components/ScriptList'
import ScriptDetail from './components/ScriptDetail'
import UploadScript from './components/UploadScript'

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
          <Header />

          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={<ScriptList />} />
              <Route path="/scripts/:id" element={<ScriptDetail />} />
              <Route path="/upload" element={<UploadScript />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
