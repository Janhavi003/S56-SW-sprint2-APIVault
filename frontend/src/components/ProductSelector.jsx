function ProductSelector({ product, products, onProductChange }) {
  return (
    <div className="field">
      <label htmlFor="product">Product</label>
      <select
        id="product"
        value={product}
        onChange={(event) => onProductChange(event.target.value)}
      >
        <option value="">Select product</option>
        {products.map((item) => (
          <option key={item.id} value={item.id}>
            {item.name}
          </option>
        ))}
      </select>
    </div>
  )
}

export default ProductSelector
