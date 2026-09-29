function ErrorPage({ product, version, question, errorMessage }) {
  const selectedProduct = product || 'FastAPI'
  const selectedVersion = version || 'v0.110.0'
  const selectedQuestion = question || 'Ask a documentation question.'

  const handleRetry = () => {
    window.location.hash = '#ask'
  }

  return (
    <main className="error-page">
      <div className="error-context">
        <span>{selectedProduct}</span>
        <span>{selectedVersion}</span>
      </div>

      <section className="error-card" role="alert">
        <div className="error-icon">!</div>
        <div className="error-content">
          <div className="error-label">REQUEST ERROR</div>
          <h1>Something went wrong</h1>
          <p>
            {errorMessage || 'The documentation service could not complete the request. Check that the backend is running and try again.'}
          </p>

          <div className="error-question">
            <span>Query</span>
            <strong>{selectedQuestion}</strong>
          </div>

          <div className="error-actions">
            <button className="error-retry-button" type="button" onClick={handleRetry}>
              Try Again
            </button>
            <a className="error-report-button" href="mailto:support@apivault.dev?subject=APIVault%20request%20error">
              Report Issue
            </a>
          </div>
        </div>
      </section>
    </main>
  )
}

export default ErrorPage
