function VersionSelector({ product, version, onVersionChange }) {
  const versionsByProduct = {
    FastAPI: ['v0.115'],
    'Next.js': ['v15.1'],
    PostgreSQL: ['v16.3'],
    Redis: ['v7.4'],
    Kubernetes: ['v1.31'],
    'Stripe API': ['2024-11'],
  }

  const versions = versionsByProduct[product] || []

  return (
    <div className="field">
      <label htmlFor="version">Version</label>

      <select
        id="version"
        value={version}
        onChange={(event) => onVersionChange(event.target.value)}
        disabled={!product}
      >
        <option value="">
          {product ? 'Select version' : 'Select product first'}
        </option>

        {versions.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>
    </div>
  )
}

export default VersionSelector