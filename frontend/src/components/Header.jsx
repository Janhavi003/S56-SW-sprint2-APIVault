function Header({ activePage = 'ask' }) {
  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-mark">A</div>
        <span>APIVault</span>
      </div>

      <nav className="navigation">
        <a className={activePage === 'ask' ? 'active' : ''} href="#ask">
          Ask Question
        </a>
        <a className={activePage === 'history' ? 'active' : ''} href="#history">
          History
        </a>
        <a href="#documentation">
          Documentation
        </a>
      </nav>

      <div className="header-meta">
        <span className="version-pill">
          <span className="dot" /> v2.4.1
        </span>
        <span className="avatar">JD</span>
      </div>
    </header>
  )
}

export default Header
