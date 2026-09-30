const examples = [
  ['FastAPI', 'v0.100.0', 'How do I create a POST endpoint with request body validation?'],
  ['FastAPI', 'v0.110.0', 'How do I define path operation decorators?'],
  ['Stripe API', 'v2023-10-16', 'How do I work with charges?'],
  ['Stripe API', 'v2024-04-01', 'How do I create and retrieve charges?'],
]

function ExampleQuestions({ onSelect }) {
  return (
    <section className="examples">
      <div className="section-label">EXAMPLE QUESTIONS</div>
      <div className="example-list">
        {examples.map(([product, version, question]) => (
          <button
            className="example-row"
            key={question}
            onClick={() => onSelect(question, product, version)}
          >
            <span className="tag">{product}</span>
            <span className="version-tag">{version}</span>
            <span className="example-text">{question}</span>
          </button>
        ))}
      </div>
    </section>
  )
}

export default ExampleQuestions
