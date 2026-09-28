function NoDocsPage({ product, version, question }) {
  const selectedProduct = product || 'FastAPI'
  const selectedVersion = version || 'v0.115.0'
  const selectedQuestion = question || 'How do I create a POST endpoint with request body validation?'

  const handleTryAgain = () => {
    window.location.hash = '#ask'
  }

  const handleDifferentVersion = () => {
    window.location.hash = '#ask'
  }

  return (
    <main className="no-docs-page">
      <div className="no-docs-context">
        <span>{selectedProduct}</span>
        <span>{selectedVersion}</span>
      </div>

      <section className="no-docs-card" role="status">
        <div className="no-docs-icon" aria-hidden="true">?</div>
        <div className="no-docs-content">
          <div className="no-docs-label">INSUFFICIENT DOCUMENTATION</div>
          <h1>No relevant documentation found</h1>
          <p>
            APIVault could not find enough reliable documentation for this question in the selected product and version. No unsupported answer was generated.
          </p>

          <div className="no-docs-query">
            <span>Query</span>
            <strong>{selectedQuestion}</strong>
          </div>

          <div className="no-docs-actions">
            <button className="no-docs-primary" type="button" onClick={handleTryAgain}>
              Try Another Question
            </button>
            <button className="no-docs-secondary" type="button" onClick={handleDifferentVersion}>
              Different Version
            </button>
          </div>
        </div>
      </section>
    </main>
  )
}

export default NoDocsPage
