const defaultHistoryItems = [
  {
    product: 'FastAPI',
    version: 'v0.100.0',
    time: '2 min ago',
    question: 'How do I create a POST endpoint with request body validation?',
    status: 'success',
  },
  {
    product: 'FastAPI',
    version: 'v0.110.0',
    time: '1 hr ago',
    question: 'What are the changes for Pydantic v2 and model_validator?',
    status: 'success',
  },
  {
    product: 'Stripe API',
    version: 'v2023-10-16',
    time: '3 hr ago',
    question: 'What parameters are required to create a charge in Stripe?',
    status: 'success',
  },
  {
    product: 'Stripe API',
    version: 'v2024-04-01',
    time: 'Yesterday',
    question: 'How do I create a payment intent with automatic payment methods?',
    status: 'success',
  },
  {
    product: 'FastAPI',
    version: 'v0.100.0',
    time: '2 days ago',
    question: 'How do I configure logical replication for change data capture?',
    status: 'insufficient',
  },
]

function HistoryPage({ history = [] }) {
  const items = history && history.length > 0 ? history : defaultHistoryItems

  return (
    <main className="history-page">
      <div className="history-heading">
        <div>
          <h1>Query History</h1>
          <p>Your recent questions and their answers.</p>
        </div>

        <span className="query-count">{items.length} queries</span>
      </div>

      <section className="history-section">
        <div className="history-section-label">RECENT</div>

        <div className="history-list">
          {items.map((item, index) => (
            <article className="history-card" key={`${item.product}-${item.version}-${index}`}>
              <span className={`history-status ${item.status}`} aria-hidden="true" />

              <div className="history-card-content">
                <div className="history-meta">
                  <span className="history-product">{item.product}</span>
                  <span className="history-version">{item.version}</span>
                  {item.status === 'insufficient' || item.status === 'insufficient_documentation' ? (
                    <span className="history-insufficient">Insufficient docs</span>
                  ) : (
                    <span className="history-time">{item.time || 'Recent'}</span>
                  )}
                </div>

                <p>{item.question}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}

export default HistoryPage
