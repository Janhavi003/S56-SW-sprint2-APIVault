import { useState } from 'react'

function renderFormattedAnswer(text) {
  if (!text) return null

  // Split by code blocks first
  const parts = text.split(/(```[\s\S]*?```)/g)

  return parts.map((part, index) => {
    if (part.startsWith('```') && part.endsWith('```')) {
      const firstLineBreak = part.indexOf('\n')
      const code = firstLineBreak !== -1
        ? part.slice(firstLineBreak + 1, -3)
        : part.slice(3, -3)

      return (
        <pre className="code-block" key={index}>
          <code>{code.trim()}</code>
        </pre>
      )
    }

    const lines = part.split('\n')
    return (
      <div key={index}>
        {lines.map((line, lIndex) => {
          const trimmed = line.trim()
          if (!trimmed) return null

          if (trimmed.startsWith('### ')) {
            return (
              <h2 key={lIndex} style={{ marginTop: '14px', marginBottom: '6px' }}>
                {trimmed.replace('### ', '')}
              </h2>
            )
          }

          if (trimmed.startsWith('## ')) {
            return (
              <h2 key={lIndex} style={{ marginTop: '14px', marginBottom: '6px' }}>
                {trimmed.replace('## ', '')}
              </h2>
            )
          }

          if (trimmed.startsWith('# ')) {
            return (
              <h1 key={lIndex} style={{ fontSize: '13px', marginTop: '14px', marginBottom: '6px' }}>
                {trimmed.replace('# ', '')}
              </h1>
            )
          }

          if (trimmed.startsWith('- ')) {
            return (
              <li key={lIndex} style={{ marginLeft: '16px', color: '#9296a4', fontSize: '9px', lineHeight: '1.6' }}>
                {trimmed.replace('- ', '')}
              </li>
            )
          }

          return <p key={lIndex}>{trimmed}</p>
        })}
      </div>
    )
  })
}

export function formatAnswerMarkdown({ product, version, question, answer, sources = [] }) {
  let md = `## Question\n${question}\n\n`
  md += `## Answer (${product} ${version})\n\n${answer}\n\n`
  md += `---\n\n### Supporting Documentation Sources\n`

  if (!sources || sources.length === 0) {
    md += `- **Product**: ${product}\n- **Version**: ${version}\n- *No source citations returned.*\n`
  } else {
    sources.forEach((src, idx) => {
      md += `\n**Source #${idx + 1}: ${src.document_title || product}**\n`
      md += `- **Product & Version**: ${src.product_id || product} (${src.version || version})\n`
      if (src.section_title) {
        md += `- **Section**: ${src.section_title}\n`
      }
      if (src.source_path) {
        md += `- **Path**: \`${src.source_path}\`\n`
      }
      if (src.excerpt) {
        md += `\n> ${src.excerpt.split('\n').join('\n> ')}\n`
      }
    })
  }

  md += `\n---\n*Grounded & generated via APIVault*`
  return md
}

function AnswerSourcePage({ product, version, question, answerData }) {
  const [copyStatus, setCopyStatus] = useState('idle') // 'idle' | 'copied' | 'error'

  const selectedProduct = product || answerData?.product_id || 'FastAPI'
  const selectedVersion = version || answerData?.version || 'v0.110.0'
  const selectedQuestion = question || answerData?.question || 'Ask a documentation question.'
  const sources = answerData?.sources || []
  const answer = answerData?.answer || 'No answer data is available yet.'

  const handleCopyAnswer = async () => {
    const textToCopy = formatAnswerMarkdown({
      product: selectedProduct,
      version: selectedVersion,
      question: selectedQuestion,
      answer,
      sources,
    })

    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(textToCopy)
        setCopyStatus('copied')
      } else {
        const textArea = document.createElement('textarea')
        textArea.value = textToCopy
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

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              className={`copy-answer-button ${copyStatus}`}
              onClick={handleCopyAnswer}
              title="Copy answer and source citations to clipboard as Markdown"
            >
              {copyStatus === 'copied' ? '✓ Copied' : copyStatus === 'error' ? '✕ Copy Failed' : '⎘ Copy Answer'}
            </button>

            <a className="open-docs-button" href="#source">
              View Source ↗
            </a>
          </div>
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
          <span>{sources[0]?.source_path || 'Source path will appear here'}</span>
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
          {renderFormattedAnswer(answer)}
        </div>
      </article>

      <div className="answer-source-question">
        <span>Question</span>
        <p>{selectedQuestion}</p>
      </div>

      <section className="source-list" style={{ marginTop: '20px' }}>
        <div className="section-label" style={{ marginBottom: '10px' }}>SUPPORTING SOURCES</div>
        {sources.length === 0 ? (
          <p style={{ color: '#777b89', fontSize: '9px' }}>No supporting source was returned.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {sources.map((source) => (
              <article
                className="source-card"
                key={source.chunk_id}
                style={{
                  padding: '12px 14px',
                  border: '1px solid #272a33',
                  borderRadius: '4px',
                  background: '#111319',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                  <strong style={{ color: '#e2e5eb', fontSize: '10px' }}>{source.document_title}</strong>
                  <span className="source-version-tag" style={{ fontSize: '7px' }}>{source.version}</span>
                </div>
                <div style={{ color: '#d6a83d', fontSize: '8px', marginBottom: '6px' }}>§ {source.section_title}</div>
                <code style={{ display: 'block', color: '#555a69', fontSize: '7px', fontFamily: 'ui-monospace, monospace', marginBottom: '6px' }}>
                  {source.source_path}
                </code>
                {source.excerpt && (
                  <p style={{ margin: 0, color: '#8c909e', fontSize: '9px', lineHeight: '1.45' }}>
                    {source.excerpt}
                  </p>
                )}
              </article>
            ))}
          </div>
        )}
      </section>

      <a className="back-to-answer" href="#ask">‹ Back to Ask Question</a>
    </main>
  )
}

export default AnswerSourcePage
