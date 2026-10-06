import { useEffect, useMemo, useState } from 'react'
import Header from './components/Header'
import ProductSelector from './components/ProductSelector'
import VersionSelector from './components/VersionSelector'
import QuestionInput from './components/QuestionInput'
import ExampleQuestions from './components/ExampleQuestions'
import Sidebar from './components/Sidebar'
import HistoryPage from './components/HistoryPage'
import DocumentationPage from './components/DocumentationPage'
import AnswerSourcePage from './components/AnswerSourcePage'
import SourcePage from './components/SourcePage'
import ErrorPage from './components/ErrorPage'
import LoadingPage from './components/LoadingPage'
import NoDocsPage from './components/NoDocsPage'
import StateNavigator from './components/StateNavigator'
import { checkHealth, getProducts, queryDocumentation } from './api'
import './App.css'

const savedQuery = () => {
  try {
    return JSON.parse(sessionStorage.getItem('apivault-query') || 'null')
  } catch {
    return null
  }
}

const loadSavedHistory = () => {
  try {
    const raw = localStorage.getItem('apivault-history')
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed.filter(
      (item) => item && typeof item === 'object' && typeof item.question === 'string'
    )
  } catch (error) {
    console.warn('Failed to load history from localStorage:', error)
    return []
  }
}

const getPageFromHash = () => {
  if (window.location.hash === '#history') return 'history'
  if (window.location.hash === '#documentation') return 'documentation'
  if (window.location.hash === '#answer') return 'answer'
  if (window.location.hash === '#source') return 'source'
  if (window.location.hash === '#error') return 'error'
  if (window.location.hash === '#loading') return 'loading'
  if (window.location.hash === '#no-docs') return 'no-docs'
  return 'ask'
}

function App() {
  const saved = savedQuery()

  const [page, setPage] = useState(getPageFromHash())
  const [products, setProducts] = useState([])
  const [apiStatus, setApiStatus] = useState('checking')
  const [product, setProduct] = useState(saved?.product || '')
  const [version, setVersion] = useState(saved?.version || '')
  const [question, setQuestion] = useState(saved?.question || '')
  const [error, setError] = useState('')
  const [errorMessage, setErrorMessage] = useState(saved?.errorMessage || '')
  const [loading, setLoading] = useState(false)
  const [answerData, setAnswerData] = useState(saved?.answerData || null)
  const [history, setHistory] = useState(loadSavedHistory)

  useEffect(() => {
    const handleHashChange = () => setPage(getPageFromHash())
    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  useEffect(() => {
    const loadBackendData = async () => {
      setApiStatus('checking')
      try {
        const [, data] = await Promise.all([checkHealth(), getProducts()])
        setProducts(Array.isArray(data) ? data : [])
        setApiStatus('connected')
        setErrorMessage('')
      } catch (requestError) {
        setApiStatus('disconnected')
        setProducts([])
        setErrorMessage(requestError.message)
      }
    }

    loadBackendData()
  }, [])

  useEffect(() => {
    sessionStorage.setItem(
      'apivault-query',
      JSON.stringify({ product, version, question, answerData, errorMessage })
    )
  }, [product, version, question, answerData, errorMessage])

  useEffect(() => {
    try {
      localStorage.setItem('apivault-history', JSON.stringify(history))
    } catch (e) {
      console.warn('Failed to persist history to localStorage', e)
    }
  }, [history])

  const selectedProduct = useMemo(
    () => products.find((item) => item.id === product),
    [products, product]
  )

  const displayProductName = selectedProduct?.name || product

  const resetResult = () => {
    setAnswerData(null)
    setErrorMessage('')
  }

  const handleAskQuestion = async () => {
    if (!product || !version || !question.trim()) {
      setError('Select a product, version, and enter a question.')
      return
    }

    const versionExists = selectedProduct?.versions?.some((item) => item.version === version)
    if (!versionExists) {
      setError('Select a valid version for the selected product.')
      return
    }

    setError('')
    setErrorMessage('')
    setLoading(true)
    resetResult()
    window.location.hash = '#loading'

    try {
      const data = await queryDocumentation({
        productId: product,
        version,
        question: question.trim(),
        topK: 3,
      })

      setAnswerData(data)

      // Add to persistent history
      const historyItem = {
        id: `hist-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        product: displayProductName,
        productId: product,
        version: version,
        question: question.trim(),
        status: data.status,
        timestamp: Date.now(),
        time: 'Just now',
      }
      setHistory((prev) => [historyItem, ...(Array.isArray(prev) ? prev : [])])

      if (data.status === 'insufficient_documentation') {
        window.location.hash = '#no-docs'
      } else {
        window.location.hash = '#answer'
      }
    } catch (requestError) {
      setErrorMessage(requestError.message)

      // Record failed query in persistent history
      const failedItem = {
        id: `hist-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        product: displayProductName,
        productId: product,
        version: version,
        question: question.trim(),
        status: 'error',
        timestamp: Date.now(),
        time: 'Just now',
        errorMessage: requestError.message,
      }
      setHistory((prev) => [failedItem, ...(Array.isArray(prev) ? prev : [])])

      window.location.hash = '#error'
    } finally {
      setLoading(false)
    }
  }

  const handleProductChange = (selectedProductId) => {
    setProduct(selectedProductId)
    setVersion('')
    setError('')
    resetResult()
  }

  const handleExampleSelect = (selectedQuestion, selectedProductName, selectedVersion) => {
    const selected = products.find(
      (item) =>
        item.name.toLowerCase() === selectedProductName.toLowerCase() ||
        item.id.toLowerCase() === selectedProductName.toLowerCase()
    )
    const selectedId =
      selected?.id || (selectedProductName.toLowerCase().includes('stripe') ? 'stripe-api' : 'fastapi')
    setQuestion(selectedQuestion)
    setProduct(selectedId)
    setVersion(selectedVersion)
    setError('')
    resetResult()
  }

  const handleClearHistory = () => {
    setHistory([])
    try {
      localStorage.removeItem('apivault-history')
    } catch (e) {
      console.warn('Failed to clear history from localStorage', e)
    }
  }

  const handleSelectHistoryQuery = (item) => {
    if (!item) return
    if (item.productId) {
      setProduct(item.productId)
    } else if (item.product) {
      const matched = products.find(
        (p) => p.name.toLowerCase() === item.product.toLowerCase() || p.id === item.product
      )
      if (matched) setProduct(matched.id)
    }
    if (item.version) setVersion(item.version)
    if (item.question) setQuestion(item.question)
    setError('')
    resetResult()
    window.location.hash = '#ask'
  }

  const handleRetry = () => {
    window.location.hash = '#ask'
  }

  const state =
    page === 'answer'
      ? 'Answer'
      : page === 'source'
        ? 'Source'
        : page === 'error'
          ? 'Error'
          : page === 'loading'
            ? 'Loading'
            : page === 'no-docs'
              ? 'No Docs'
              : page === 'ask'
                ? 'Ask'
                : 'demo'

  return (
    <div className="app-shell">
      <Header activePage={page} apiStatus={apiStatus} />

      {page === 'history' ? (
        <HistoryPage
          history={history}
          onClearHistory={handleClearHistory}
          onSelectQuery={handleSelectHistoryQuery}
        />
      ) : page === 'documentation' ? (
        <DocumentationPage />
      ) : page === 'answer' ? (
        <AnswerSourcePage
          product={displayProductName}
          version={version}
          question={question}
          answerData={answerData}
        />
      ) : page === 'source' ? (
        <SourcePage
          product={displayProductName}
          version={version}
          question={question}
          answerData={answerData}
        />
      ) : page === 'error' ? (
        <ErrorPage
          product={displayProductName}
          version={version}
          question={question}
          errorMessage={errorMessage}
          onRetry={handleRetry}
        />
      ) : page === 'loading' ? (
        <LoadingPage
          product={displayProductName}
          version={version}
          question={question}
          isLoading={loading}
        />
      ) : page === 'no-docs' ? (
        <NoDocsPage
          product={displayProductName}
          version={version}
          question={question}
        />
      ) : (
        <div className="page-layout">
          <main className="main-content">
            <div className="hero">
              <div className="badge-row">
                <span><span className="dot" /> Version-aware</span>
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
                  products={products}
                  onProductChange={handleProductChange}
                />

                <VersionSelector
                  product={product}
                  products={products}
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
                  disabled={loading || !products.length || apiStatus !== 'connected'}
                >
                  {loading ? 'Asking...' : '⌕ Ask Question'}
                </button>
              </div>

              {error && <div className="form-error">{error}</div>}
              {apiStatus === 'checking' && (
                <div className="api-status-message">Connecting to APIVault backend...</div>
              )}
              {apiStatus === 'disconnected' && (
                <div className="form-error">
                  Backend unavailable. Start the API on port 8000 and refresh the page.
                </div>
              )}
            </section>

            <ExampleQuestions onSelect={handleExampleSelect} />
          </main>

          <Sidebar />
        </div>
      )}

      <StateNavigator activeState={state} />
    </div>
  )
}

export default App
