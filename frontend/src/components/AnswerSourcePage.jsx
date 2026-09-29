function AnswerSourcePage({ product, version, question, answerData }) {
  const selectedProduct = product || answerData?.product_id || 'FastAPI'
  const selectedVersion = version || answerData?.version || 'v0.110.0'
  const selectedQuestion = question || answerData?.question || 'Ask a documentation question.'
  const sources = answerData?.sources || []
  const answer = answerData?.answer || 'No answer data is available yet.'

  return (
    <main className="answer-source-page">
      <div className="answer-breadcrumb">Answer / {sources.length || 0} source{sources.length === 1 ? '' : 's'}</div>

      <section className="source-summary-card">
        <div className="source-summary-top">
          <div>
            <h1>{selectedProduct} Documentation</h1>
            <div className="source-tags">
              <span className="source-product-tag">{selectedProduct}</span>
              <span className="source-version-tag">{selectedVersion}</span>
            </div>
          </div>

          <a className="open-docs-button" href="#source">
            View Source ↗
          </a>
        </div>

        <div className="source-meta-row">
          <span>Version-grounded answer</span>
          <span>{sources.length} supporting source{sources.length === 1 ? '' : 's'}</span>
          <span className="source-match">
            {answerData?.confidence != null
              ? `${Math.round(answerData.confidence * 100)}% confidence`
              : 'Grounded'}
          </span>
        </div>

        <div className="source-url-row">
          {sources[0]?.source_path || 'Source path will appear here'}
          <span>{selectedVersion}</span>
        </div>
      </section>

      <div className="source-notice">
        <span className="source-notice-icon">ⓘ</span>
        <p>
          This answer is generated only from documentation retrieved for the selected product and version.
        </p>
      </div>

      <article className="documentation-excerpt">
        <div className="excerpt-heading">
          <span>Grounded Answer</span>
          <span className="excerpt-badge">SOURCE GROUNDED</span>
        </div>

        <div className="excerpt-content">
          {answer.split('\n').map((line, index) =>
            line.trim() ? <p key={`${line}-${index}`}>{line}</p> : null
          )}
        </div>
      </article>

      <div className="answer-source-question">
        <span>Question</span>
        <p>{selectedQuestion}</p>
      </div>

      <section className="source-list">
        <div className="section-label">SUPPORTING SOURCES</div>
        {sources.length === 0 ? (
          <p>No supporting source was returned.</p>
        ) : (
          sources.map((source) => (
            <article className="source-card" key={source.chunk_id}>
              <strong>{source.document_title}</strong>
              <span>{source.section_title}</span>
              <code>{source.source_path}</code>
              {source.excerpt && <p>{source.excerpt}</p>}
            </article>
          ))
        )}
      </section>

      <a className="back-to-answer" href="#ask">‹ Back to Ask Question</a>
    </main>
  )
}

export default AnswerSourcePage
