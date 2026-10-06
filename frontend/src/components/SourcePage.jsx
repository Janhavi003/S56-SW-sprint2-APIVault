import { useState } from 'react'

function SourcePage({ product, version, question, answerData }) {
  const [copyStatus, setCopyStatus] = useState('idle')
  const selectedProduct = product || answerData?.product_id || 'FastAPI'
  const selectedVersion = version || answerData?.version || 'v0.110.0'
  const selectedQuestion = question || answerData?.question || 'Ask a documentation question.'
  const source = answerData?.sources?.[0]

  const handleCopySource = async () => {
    let md = `## Source Document: ${source?.document_title || selectedProduct}\n`
    md += `- **Product & Version**: ${source?.product_id || selectedProduct} (${source?.version || selectedVersion})\n`
    if (source?.section_title) md += `- **Section**: ${source?.section_title}\n`
    if (source?.source_path) md += `- **Path**: \`${source?.source_path}\`\n\n`
    md += `### Source Content Excerpt\n`
    md += `> ${source?.excerpt?.split('\n').join('\n> ') || 'No excerpt available.'}\n\n`
    md += `---\n*Indexed in APIVault*`

    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(md)
        setCopyStatus('copied')
      } else {
        const textArea = document.createElement('textarea')
        textArea.value = md
        textArea.style.position = 'fixed'
        textArea.style.opacity = '0'
        document.body.appendChild(textArea)
        textArea.focus()
        textArea.select()
        const successful = document.execCommand('copy')
        document.body.removeChild(textArea)
        if (successful) {
          setCopyStatus('copied')
        } else {
          throw new Error('execCommand failed')
        }
      }
    } catch (err) {
      console.warn('Clipboard copy failed:', err)
      setCopyStatus('error')
    }

    setTimeout(() => {
      setCopyStatus('idle')
    }, 2500)
  }

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

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              className={`copy-answer-button ${copyStatus}`}
              onClick={handleCopySource}
              title="Copy source details and excerpt as Markdown"
            >
              {copyStatus === 'copied' ? '✓ Copied' : copyStatus === 'error' ? '✕ Copy Failed' : '⎘ Copy Source'}
            </button>

            <a className="open-docs-button" href="#answer">
              View Answer ↗
            </a>
          </div>
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
