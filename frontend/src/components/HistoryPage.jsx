function formatRelativeTime(timestamp) {
  if (!timestamp) return 'Recent'
  const diffMs = Date.now() - timestamp
  const diffSec = Math.floor(diffMs / 1000)
  if (diffSec < 60) return 'Just now'
  const diffMin = Math.floor(diffSec / 60)
  if (diffMin < 60) return `${diffMin} min ago`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr} hr ago`
  const diffDay = Math.floor(diffHr / 24)
  if (diffDay === 1) return 'Yesterday'
  if (diffDay < 7) return `${diffDay} days ago`
  return new Date(timestamp).toLocaleDateString()
}

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

function HistoryPage({ history = [], onClearHistory, onSelectQuery }) {
  const hasUserHistory = Array.isArray(history) && history.length > 0
  const items = hasUserHistory ? history : defaultHistoryItems

  return (
    <main className="history-page">
      <div className="history-heading">
        <div>
          <h1>Query History</h1>
          <p>Your recent questions and their answers.</p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {hasUserHistory && onClearHistory && (
            <button
              className="clear-history-button"
              onClick={onClearHistory}
              style={{
                padding: '7px 11px',
                border: '1px solid #292c36',
                borderRadius: '5px',
                background: '#15171e',
                color: '#8f93a1',
                fontSize: '10px',
                cursor: 'pointer',
                fontFamily: 'inherit',
              }}
              title="Clear all saved query history"
            >
              Clear History
            </button>
          )}
          <span className="query-count">{items.length} queries</span>
        </div>
      </div>

      <section className="history-section">
        <div className="history-section-label">
          {hasUserHistory ? 'SAVED HISTORY' : 'RECENT'}
        </div>

        <div className="history-list">
          {items.map((item, index) => {
            const isInsufficient =
              item.status === 'insufficient' || item.status === 'insufficient_documentation'
            const isError = item.status === 'error'
            const displayTime = item.timestamp
              ? formatRelativeTime(item.timestamp)
              : item.time || 'Recent'

            return (
              <article
                className="history-card"
                key={item.id || `${item.product}-${item.version}-${index}`}
                onClick={() => onSelectQuery && onSelectQuery(item)}
                style={onSelectQuery ? { cursor: 'pointer' } : undefined}
                title={onSelectQuery ? 'Click to reload this question' : undefined}
              >
                <span
                  className={`history-status ${
                    isInsufficient ? 'insufficient' : isError ? 'insufficient' : 'success'
                  }`}
                  aria-hidden="true"
                />

                <div className="history-card-content">
                  <div className="history-meta">
                    <span className="history-product">{item.product}</span>
                    <span className="history-version">{item.version}</span>
                    {isInsufficient ? (
                      <span className="history-insufficient">Insufficient docs</span>
                    ) : isError ? (
                      <span
                        className="history-insufficient"
                        style={{
                          borderColor: '#5b2d2d',
                          background: '#321b1d',
                          color: '#e87878',
                        }}
                      >
                        Failed
                      </span>
                    ) : null}
                    <span className="history-time">{displayTime}</span>
                  </div>

                  <p>{item.question}</p>
                </div>
              </article>
            )
          })}
        </div>
      </section>
    </main>
  )
}

export default HistoryPage
