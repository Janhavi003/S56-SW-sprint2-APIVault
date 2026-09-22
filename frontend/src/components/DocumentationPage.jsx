const documentationData = [
  {
    name: 'FastAPI',
    icon: '⚡',
    description: 'Modern Python web framework with automatic OpenAPI',
    versions: ['v0.115.0', 'v0.118.0', 'v0.104.1', 'v0.100.0', 'v0.95.2'],
    latest: 'v0.115.0',
  },
  {
    name: 'Next.js',
    icon: '▲',
    description: 'React framework for production web applications',
    versions: ['v15.1.0', 'v14.2.5', 'v13.5.6', 'v12.3.4'],
    latest: 'v15.1.0',
  },
  {
    name: 'PostgreSQL',
    icon: '◈',
    description: 'Advanced open-source relational database',
    versions: ['v16.3', 'v15.7', 'v14.12', 'v13.15'],
    latest: 'v16.3',
  },
  {
    name: 'Redis',
    icon: '◯',
    description: 'In-memory data structure store and cache',
    versions: ['v7.4.0', 'v7.2.4', 'v7.0.15', 'v6.2.14'],
    latest: 'v7.4.0',
  },
  {
    name: 'Kubernetes',
    icon: '◉',
    description: 'Container orchestration and workload management',
    versions: ['v1.31.0', 'v1.30.3', 'v1.29.7', 'v1.28.12'],
    latest: 'v1.31.0',
  },
  {
    name: 'Stripe API',
    icon: '$',
    description: 'Payment processing and subscription management',
    versions: ['v2024-11', 'v2024-06', 'v2023-10', 'v2023-08'],
    latest: 'v2024-11',
  },
]

function DocumentationPage() {
  return (
    <main className="documentation-page">
      <div className="documentation-header">
        <div>
          <h1>Documentation</h1>
          <p>Indexed products and available version coverage.</p>
        </div>
      </div>

      <section className="documentation-section">
        <div className="documentation-section-label">
          INDEXED PRODUCTS
        </div>

        <div className="documentation-grid">
          {documentationData.map((product) => (
            <article
              className="documentation-card"
              key={product.name}
            >
              <div className="documentation-card-header">
                <div className="documentation-icon">
                  {product.icon}
                </div>

                <div className="documentation-product-info">
                  <h2>{product.name}</h2>
                  <p>{product.description}</p>
                </div>
              </div>

              <div className="documentation-versions">
                {product.versions.map((version) => (
                  <span
                    className={
                      version === product.latest
                        ? 'documentation-version latest'
                        : 'documentation-version'
                    }
                    key={version}
                  >
                    {version}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>

      <div className="documentation-note">
        <span className="documentation-note-icon">ⓘ</span>

        <p>
          All indexed documentation is scraped from official sources and
          re-indexed per version. Answers are never generated from
          cross-version or cross-product data.{' '}
          <strong>Highlighted versions</strong> are the latest indexed
          release for each product.
        </p>
      </div>
    </main>
  )
}

export default DocumentationPage