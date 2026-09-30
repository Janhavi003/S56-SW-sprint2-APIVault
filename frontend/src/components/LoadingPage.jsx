function LoadingPage({ product, version, question, isLoading = true }) {
  const selectedProduct = product || 'FastAPI'
  const selectedVersion = version || 'v0.115.0'
  const selectedQuestion = question || 'How do I create a POST endpoint with request body validation?'

  const steps = [
    { label: 'Searching documentation', status: 'complete' },
    { label: 'Retrieving relevant sections', status: 'active' },
    { label: 'Preparing grounded answer', status: 'pending' },
  ]

  return (
    <main className="loading-page">
      <div className="loading-context">
        <span>{selectedProduct}</span>
        <span>{selectedVersion}</span>
      </div>

      <section className="loading-card" aria-live="polite">
        <div className="loading-spinner" aria-hidden="true" />
        <div className="loading-heading">
          <div className="loading-label">PROCESSING REQUEST</div>
          <h1>Finding the right documentation</h1>
          <p>{selectedQuestion}</p>
        </div>

        <div className="loading-steps">
          {steps.map((step) => (
            <div className={`loading-step ${step.status}`} key={step.label}>
              <span className="loading-step-indicator" aria-hidden="true">
                {step.status === 'complete' ? '✓' : step.status === 'active' && isLoading ? '•' : ''}
              </span>
              <span>{step.label}</span>
            </div>
          ))}
        </div>

        <div className="loading-skeleton" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>

        <div className="loading-note">
          Answers are grounded exclusively in documentation for the selected product and version.
        </div>
      </section>
    </main>
  )
}

export default LoadingPage
