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
import { getProducts, queryDocumentation } from './api'
import './App.css'

const savedQuery = () => {
  try {
    return JSON.parse(sessionStorage.getItem('apivault-query') || 'null')
  } catch {
    return null
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
  const [product, setProduct] = useState(saved?.product || '')
  const [version, setVersion] = useState(saved?.version || '')
  const [question, setQuestion] = useState(saved?.question || '')
  const [error, setError] = useState('')
  const [errorMessage, setErrorMessage] = useState(saved?.errorMessage || '')
  const [loading, setLoading] = useState(false)
  const [answerData, setAnswerData] = useState(saved?.answerData || null)

  useEffect(() => {
    const handleHashChange = () => setPage(getPageFromHash())
    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const data = await getProducts()
        setProducts(Array.isArray(data) ? data : [])
      } catch (requestError) {
        setErrorMessage(requestError.message)
      }
    }

    loadProducts()
  }, [])

  useEffect(() => {
    sessionStorage.setItem(
      'apivault-query',
      JSON.stringify({ product, version, question, answerData, errorMessage })
    )
  }, [product, version, question, answerData, errorMessage])

  const selectedProduct = useMemo(
    () => products.find((item) => item.id === product),
    [products, product]
  )

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

      if (data.status === 'insufficient_documentation') {
        window.location.hash = '#no-docs'
      } else {
        window.location.hash = '#answer'
      }
    } catch (requestError) {
      setErrorMessage(requestError.message)
      window.location.hash = '#error'
    } finally {
      setLoading(false)
    }
  }

  const handleProductChange = (selectedProduct) => {
    setProduct(selectedProduct)
    setVersion('')
    setError('')
    resetResult()
  }

  const handleExampleSelect = (selectedQuestion, selectedProductName, selectedVersion) => {
    const selected = products.find((item) => item.name === selectedProductName)
    setQuestion(selectedQuestion)
    setProduct(selected?.id || '')
    setVersion(selectedVersion)
    setError('')
    resetResult()
  }

  const displayProductName = selectedProduct?.name || product

  const handleRetry = () => {
    window.location.hash = '#ask'
  }

  const state = page === 'answer'
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
      <Header activePage={page} />

      {page === 'history' ? (
        <HistoryPage />
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
                  disabled={loading || !products.length}
                >
                  {loading ? 'Asking...' : '⌕ Ask Question'}
                </button>
              </div>

              {error && <div className="form-error">{error}</div>}
              {!products.length && (
                <div className="form-error">
                  Unable to load products. Make sure the backend is running.
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
