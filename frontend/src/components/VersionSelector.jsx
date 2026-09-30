function VersionSelector({ product, products, version, onVersionChange }) {
  const selectedProduct = products.find((item) => item.id === product)
  const versions = selectedProduct?.versions || []

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
          <option key={item.version} value={item.version}>
            {item.version}
          </option>
        ))}
      </select>
    </div>
  )
}

export default VersionSelector
