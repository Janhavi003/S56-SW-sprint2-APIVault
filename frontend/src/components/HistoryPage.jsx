const historyItems = [
  {
    product: 'FastAPI',
    version: 'v0.115.0',
    time: '2 min ago',
    question: 'How do I create a POST endpoint with request body validation?',
    status: 'success',
  },
  {
    product: 'Next.js',
    version: 'v15.1.0',
    time: '1 hr ago',
    question: 'What breaking changes were introduced in the App Router in v15?',
    status: 'success',
  },
  {
    product: 'PostgreSQL',
    version: 'v16.3',
    time: '3 hr ago',
    question: 'How do I configure logical replication for change data capture?',
    status: 'insufficient',
  },
  {
    product: 'Redis',
    version: 'v7.4.0',
    time: 'Yesterday',
    question: 'What is the difference between EXPIRE and EXPIREAT?',
    status: 'success',
  },
  {
    product: 'Kubernetes',
    version: 'v1.31.0',
    time: '2 days ago',
    question: 'How do I configure a HorizontalPodAutoscaler with custom metrics?',
    status: 'success',
  },
  {
    product: 'Stripe API',
    version: 'v2024-11',
    time: '3 days ago',
    question: 'How do I handle webhook signature verification?',
    status: 'success',
  },
]

function HistoryPage() {
  return (
    <main className="history-page">
      <div className="history-heading">
        <div>
          <h1>Query History</h1>
          <p>Your recent questions and their answers.</p>
        </div>

        <span className="query-count">6 queries</span>
      </div>

      <section className="history-section">
        <div className="history-section-label">RECENT</div>

        <div className="history-list">
          {historyItems.map((item) => (
            <article className="history-card" key={`${item.product}-${item.question}`}>
              <span className={`history-status ${item.status}`} aria-hidden="true" />

              <div className="history-card-content">
                <div className="history-meta">
                  <span className="history-product">{item.product}</span>
                  <span className="history-version">{item.version}</span>
                  {item.status === 'insufficient' ? (
                    <span className="history-insufficient">Insufficient docs</span>
                  ) : (
                    <span className="history-time">{item.time}</span>
                  )}
                </div>

                <p>{item.question}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <div className="history-state-strip" aria-label="Demo states">
        <span className="state-label">demo</span>
        <a href="#ask">Ask</a>
        <span>Loading</span>
        <span>Answer</span>
        <span>Source</span>
        <span>No Docs</span>
        <span>Error</span>
      </div>
    </main>
  )
}

export default HistoryPage
