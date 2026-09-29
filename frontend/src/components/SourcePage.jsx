function SourcePage({ product, version, question, answerData }) {
  const selectedProduct = product || answerData?.product_id || 'FastAPI'
  const selectedVersion = version || answerData?.version || 'v0.110.0'
  const selectedQuestion = question || answerData?.question || 'Ask a documentation question.'
  const source = answerData?.sources?.[0]

  return (
    <main className="answer-source-page">
      <div className="answer-breadcrumb">‹ Answer / Source #1</div>

      <section className="source-summary-card">
        <div className="source-summary-top">
          <div>
            <h1>{source?.document_title || `${selectedProduct} Documentation`}</h1>
            <div className="source-tags">
              <span className="source-product-tag">{selectedProduct}</span>
              <span className="source-version-tag">{selectedVersion}</span>
            </div>
          </div>

          <a className="open-docs-button" href="#source">
            Indexed Source ↗
          </a>
        </div>

        <div className="source-meta-row">
          <span>Original indexed documentation</span>
          <span>§ {source?.section_title || 'Source section'}</span>
          <span className="source-match">Version exact</span>
        </div>

        <div className="source-url-row">
          {source?.source_path || 'No source path returned'}
          <span>{selectedVersion}</span>
        </div>
      </section>

      <div className="source-notice">
        <span className="source-notice-icon">ⓘ</span>
        <p>
          The content below is the documentation excerpt returned by the backend retrieval service. It is shown as source evidence, not generated answer text.
        </p>
      </div>

      <article className="documentation-excerpt">
        <div className="excerpt-heading">
          <span>{source?.section_title || 'Original Documentation'}</span>
          <span className="excerpt-badge">SOURCE</span>
        </div>

        <div className="excerpt-content">
          <p>{source?.excerpt || 'No source excerpt was returned for this answer.'}</p>
        </div>
      </article>

      <div className="answer-source-question">
        <span>Question</span>
        <p>{selectedQuestion}</p>
      </div>

      <a className="back-to-answer" href="#answer">‹ Back to Answer</a>
    </main>
  )
}

export default SourcePage
