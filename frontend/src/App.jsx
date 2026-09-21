import { useEffect, useState } from 'react'
import Header from './components/Header'
import ProductSelector from './components/ProductSelector'
import VersionSelector from './components/VersionSelector'
import QuestionInput from './components/QuestionInput'
import ExampleQuestions from './components/ExampleQuestions'
import Sidebar from './components/Sidebar'
import HistoryPage from './components/HistoryPage'
import './App.css'

function App() {
  const [page, setPage] = useState(window.location.hash === '#history' ? 'history' : 'ask')
  const [product, setProduct] = useState('')
  const [version, setVersion] = useState('')
  const [question, setQuestion] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const handleHashChange = () => {
      setPage(window.location.hash === '#history' ? 'history' : 'ask')
    }

    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  const handleAskQuestion = () => {
    if (!product || !version || !question.trim()) {
      setError('Select a product, version, and enter a question.')
      return
    }

    setError('')
    setLoading(true)

    console.log({
      product,
      version,
      question,
    })

    setTimeout(() => {
      setLoading(false)
    }, 1000)
  }

  const handleProductChange = (selectedProduct) => {
    setProduct(selectedProduct)
    setVersion('')
    setError('')
  }

  const handleExampleSelect = (
    selectedQuestion,
    selectedProduct,
    selectedVersion
  ) => {
    setQuestion(selectedQuestion)
    setProduct(selectedProduct)
    setVersion(selectedVersion)
    setError('')
  }

  return (
    <div className="app-shell">
      <Header activePage={page} />

      {page === 'history' ? (
        <HistoryPage />
      ) : (
        <div className="page-layout">
          <main className="main-content">
            <div className="hero">
              <div className="badge-row">
                <span>
                  <span className="dot" /> Version-aware
                </span>
                <span>Source-grounded</span>
                <span>Developer-first</span>
              </div>

              <h1>
                Version-Aware Technical
                <br />
                Documentation Assistant
              </h1>

              <p>
                Select a product and version. Ask a technical question. Get a
                grounded answer with the exact documentation source — every time.
              </p>
            </div>

            <section className="question-card">
              <div className="selectors">
                <ProductSelector
                  product={product}
                  onProductChange={handleProductChange}
                />

                <VersionSelector
                  product={product}
                  version={version}
                  onVersionChange={setVersion}
                />
              </div>

              <QuestionInput
                question={question}
                onQuestionChange={setQuestion}
              />

              <div className="submit-row">
                <button
                  className="ask-button"
                  onClick={handleAskQuestion}
                  disabled={loading}
                >
                  {loading ? 'Asking...' : '⌕ Ask Question'}
                </button>
              </div>

              {error && (
                <div className="form-error">
                  {error}
                </div>
              )}
            </section>

            <ExampleQuestions onSelect={handleExampleSelect} />
          </main>

          <Sidebar />
        </div>
      )}
    </div>
  )
}

export default App
