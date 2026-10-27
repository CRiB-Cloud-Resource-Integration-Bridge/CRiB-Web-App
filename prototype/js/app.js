const app = document.querySelector('#app');

const routes = {
  landing: renderLanding,
  signin: () => renderAuth('signin'),
  signup: () => renderAuth('signup'),
  empty: renderEmptyDashboard,
  providers: renderProviderSelection,
  authorize: renderAuthorize,
  dashboard: renderDashboard,
  files: renderFiles,
  folder: renderFolder,
  search: renderSearchResults,
  details: renderFileDetails,
  manage: renderProviderManagement,
  error: renderConnectionError,
  loading: renderLoading,
  noresults: renderNoResults,
};

function navigate(route) {
  window.location.hash = route;
}

function currentRoute() {
  return window.location.hash.replace('#', '') || 'landing';
}

function render() {
  const route = currentRoute();
  const renderer = routes[route] || renderLanding;
  app.innerHTML = renderer();
  bindActions();
}

function bindActions() {
  document.querySelectorAll('[data-route]').forEach((element) => {
    element.addEventListener('click', (event) => {
      event.preventDefault();
      navigate(element.dataset.route);
    });
  });

  document.querySelectorAll('[data-search-input]').forEach((searchInput) => {
    searchInput.addEventListener('keydown', (event) => {
      if (event.key !== 'Enter') return;
      navigate(searchInput.value.trim() ? 'search' : 'noresults');
    });
  });
}

function button(label, route, type = 'primary') {
  return `<a class="btn btn-${type}" href="#${route}" data-route="${route}">${label}</a>`;
}

function tag(label, style = '') {
  return `<span class="tag ${style}">${label}</span>`;
}

function brand() {
  return `
    <a class="brand" href="#landing" data-route="landing">
      <span class="brand-mark">C</span>
      <span>CRiB</span>
    </a>
  `;
}

function appShell(active, title, subtitle, body, actions = '', searchValue = 'Search files and folders') {
  const nav = [
    ['Dashboard', 'dashboard'],
    ['Browse files', 'files'],
    ['Connected providers', 'manage'],
  ];

  return `
    <div class="screen app-shell">
      <aside class="sidebar">
        ${brand()}

        <nav class="sidebar-nav" aria-label="Main navigation">
          ${nav.map(([label, route]) => `
            <a class="nav-item ${label === active ? 'active' : ''}" href="#${route}" data-route="${route}">
              ${label}
            </a>
          `).join('')}
        </nav>

        <div class="profile" aria-label="Prototype user">
          <div class="profile-avatar">U</div>
          <div class="profile-copy">
            <strong>User</strong>
            <span>user@example.com</span>
          </div>
        </div>
      </aside>

      <main class="app-main">
        <header class="topbar">
          <input
            class="search-box topbar-search"
            data-search-input
            type="search"
            aria-label="Search files and folders"
            placeholder="${searchValue}"
          >
          <div class="topbar-spacer"></div>
          ${tag('Interactive prototype', 'success')}
        </header>

        <section class="content">
          <div class="page-head">
            <div>
              <div class="eyebrow">${active}</div>
              <h1>${title}</h1>
              <p>${subtitle}</p>
            </div>
            <div>${actions}</div>
          </div>
          ${body}
        </section>
      </main>
    </div>
  `;
}

function renderLanding() {
  return `
    <div class="screen landing-screen">
      <header class="landing-nav">
        ${brand()}
        <div class="landing-status">${tag('Interactive Assessment 1 prototype', 'violet')}</div>
        <div class="landing-actions">
          ${button('Sign in', 'signin', 'light')}
          ${button('Create account', 'signup')}
        </div>
      </header>

      <section class="landing-main landing-main-v2">
        <div class="hero-copy">
          ${tag('Cloud Resource Integration Bridge', 'violet')}
          <h1>Your cloud files.<br><span class="accent-word">One interface.</span></h1>

          <p class="hero-lead">
            CRiB is designed to connect supported cloud-storage accounts and present their permitted files
            through one consistent browser, so users do not have to keep switching between separate provider interfaces.
          </p>

          <p class="hero-support">
            This interactive prototype demonstrates the journey with a simulated Google Drive connection first.
            OneDrive and Dropbox are shown as planned providers for later development.
          </p>

          <div class="hero-actions">
            ${button('Try the prototype', 'signin')}
            ${button('View provider flow', 'providers', 'light')}
          </div>

          <div class="prototype-scope">
            <strong>Current prototype scope</strong>
            <span>Connect a provider, browse permitted resources, search, inspect file details and simulate download.</span>
          </div>

          <div class="future-note">
            Future product direction may include additional providers, storage-to-storage transfers and local/NAS connections.
            Those capabilities are intentionally outside this prototype version.
          </div>
        </div>

        <div class="purpose-panel">
          <div class="purpose-panel-head">
            <div>
              <div class="eyebrow">What CRiB demonstrates</div>
              <h2>One workspace for supported cloud storage</h2>
            </div>
            ${tag('Google Drive first', 'success')}
          </div>

          <div class="purpose-grid">
            <article class="card purpose-card">
              <span class="purpose-number">01</span>
              <h3>Connect accounts</h3>
              <p>Authorize supported providers from one application instead of managing each service separately.</p>
            </article>

            <article class="card purpose-card">
              <span class="purpose-number">02</span>
              <h3>Browse consistently</h3>
              <p>Use one normalized file-browser layout for permitted folders and files from connected providers.</p>
            </article>

            <article class="card purpose-card">
              <span class="purpose-number">03</span>
              <h3>Access files</h3>
              <p>Inspect file information and simulate opening or downloading an eligible resource.</p>
            </article>
          </div>

          <div class="unified-preview">
            <div class="unified-preview-top">
              <strong>Unified file browser</strong>
              ${tag('Prototype data', 'violet')}
            </div>

            <div class="unified-provider-row">
              <span class="provider-icon small-provider-icon">GD</span>
              <div><strong>Google Drive</strong><span>Connected in this prototype</span></div>
            </div>

            <div class="unified-provider-row planned">
              <span class="provider-icon small-provider-icon">OD</span>
              <div><strong>OneDrive</strong><span>Planned provider</span></div>
            </div>

            <div class="unified-provider-row planned">
              <span class="provider-icon small-provider-icon">DB</span>
              <div><strong>Dropbox</strong><span>Planned provider</span></div>
            </div>
          </div>
        </div>
      </section>
    </div>
  `;
}

function renderAuth(mode) {
  const signup = mode === 'signup';

  return `
    <div class="screen auth-layout">
      <section class="auth-left">
        ${brand()}
        <form class="auth-form" onsubmit="return false;">
          <div class="eyebrow">${signup ? 'Create your workspace' : 'Welcome back'}</div>
          <h1>${signup ? 'Create a CRiB account' : 'Sign in to CRiB'}</h1>
          <p>${signup ? 'Create a prototype account to keep cloud connections associated with one user.' : 'Continue to your unified cloud workspace.'}</p>

          ${signup ? `
            <div class="field">
              <label>Username</label>
              <input type="text" value="user" aria-label="Username">
            </div>
          ` : ''}

          <div class="field">
            <label>Email</label>
            <input type="email" value="user@example.com" aria-label="Email">
          </div>

          <div class="field">
            <label>Password</label>
            <input type="password" value="prototype123" aria-label="Password">
          </div>

          ${signup ? `<p class="field-hint">The username is used as a display name in this prototype.</p>` : `
            <div class="form-meta">
              <span>Remember me</span>
              <span class="linkish">Forgot password?</span>
            </div>
          `}

          <a class="btn btn-primary form-submit" href="#empty" data-route="empty">${signup ? 'Create account' : 'Sign in'}</a>

          <div class="form-footer">
            ${signup
              ? `Already registered? <a class="linkish" href="#signin" data-route="signin">Sign in</a>`
              : `New to CRiB? <a class="linkish" href="#signup" data-route="signup">Create account</a>`}
          </div>
        </form>
      </section>

      <aside class="auth-right">
        <div class="auth-orb violet"></div>
        <div class="auth-orb lime"></div>
        <div class="auth-content">
          ${tag('CRiB')}
          <h2>${signup ? 'Set up one<br>cloud workspace.' : 'Less switching.<br>More finding.'}</h2>
          <p>CRiB brings supported cloud-storage connections into one interface so files can be browsed through the same workflow.</p>
          <div class="feature-list">
            <div class="feature-row"><span>Connect</span><strong>Supported providers</strong></div>
            <div class="feature-row"><span>Browse</span><strong>Unified resource view</strong></div>
            <div class="feature-row"><span>Manage</span><strong>Connections in one place</strong></div>
          </div>
        </div>
      </aside>
    </div>
  `;
}

function renderEmptyDashboard() {
  const body = `
    <div class="card empty-state">
      <div class="empty-mark">+</div>
      <h2>No cloud storage connected yet.</h2>
      <p>Connect a supported provider to start building your unified CRiB workspace. This version uses simulated provider data.</p>
      ${button('Connect cloud storage', 'providers')}
    </div>

    <div class="prototype-context">
      <strong>What happens next?</strong>
      <span>After a provider is connected, CRiB shows its permitted files through the same browser used for other supported providers.</span>
    </div>
  `;

  return appShell('Dashboard', 'Welcome, User.', 'Connect your first cloud provider to start browsing files through CRiB.', body);
}

function renderProviderSelection() {
  const providerCard = (code, name, description, status, route = null) => `
    <article class="card provider-card">
      <div class="provider-card-top">
        <div class="provider-icon">${code}</div>
        ${tag(status, route ? 'violet' : '')}
      </div>
      <h3>${name}</h3>
      <p>${description}</p>
      ${route ? button('Connect provider', route) : `<span class="btn btn-light btn-disabled" aria-disabled="true">Planned</span>`}
    </article>
  `;

  const body = `
    <div class="prototype-context context-first">
      <strong>Add another cloud connection</strong>
      <span>Connected providers are managed from one place. Google Drive is the only simulated connection in this prototype version.</span>
    </div>

    <div class="provider-grid">
      ${providerCard('GD', 'Google Drive', 'Simulate connecting a Google Drive account, then browse the permitted folders and files through CRiB.', 'Prototype provider', 'authorize')}
      ${providerCard('OD', 'OneDrive', 'Planned provider for a later implementation stage. It would use the same CRiB browsing interface.', 'Planned')}
      ${providerCard('DB', 'Dropbox', 'Planned provider for a later implementation stage. It would use the same CRiB browsing interface.', 'Planned')}
    </div>

    <div class="notice">Assessment 1 prototype: provider authorization and cloud data are simulated. No real provider account is connected.</div>
  `;

  return appShell('Connected providers', 'Add a cloud provider', 'Choose a supported storage provider to connect to the CRiB workspace.', body, button('Back to connections', 'manage', 'light'));
}

function renderAuthorize() {
  return `
    <div class="screen authz-wrap">
      <div class="card authz-card">
        <div class="authz-head">
          <div class="authz-title">
            <div class="provider-icon" style="width:58px;height:58px;border-radius:18px;">GD</div>
            <div>
              <div class="eyebrow">Simulated authorization</div>
              <h2 style="margin:0;">Connect Google Drive</h2>
            </div>
          </div>
          ${tag('Prototype', 'violet')}
        </div>

        <p style="margin-top:24px;">In a real implementation, CRiB would redirect the user to Google to approve access. This prototype only simulates that authorization step.</p>

        <div class="permission-list">
          <div class="card permission">
            <div class="check">✓</div>
            <div>
              <h4>Identify the connected Google account</h4>
              <p>Lets CRiB show which provider account is connected to this workspace.</p>
            </div>
          </div>

          <div class="card permission">
            <div class="check">✓</div>
            <div>
              <h4>Browse files and folders you allow</h4>
              <p>Lets CRiB display the permitted resources in the unified file browser.</p>
            </div>
          </div>
        </div>

        <div class="notice">Prototype only — no real Google OAuth request is sent and no real cloud data is accessed.</div>

        <div class="authz-actions">
          ${button('Cancel', 'providers', 'light')}
          ${button('Continue', 'dashboard')}
        </div>
      </div>
    </div>
  `;
}

function renderDashboard() {
  const body = `
    <div class="prototype-context context-first">
      <strong>CRiB workspace concept</strong>
      <span>Google Drive is connected in this prototype. As more supported providers are added later, their permitted resources would be presented through the same CRiB browsing experience.</span>
    </div>

    <div class="stats-grid">
      <div class="card stat-card">
        <div class="stat-label">Connected providers</div>
        <div class="stat-value">1</div>
        <div class="stat-foot">${tag('Google Drive', 'success')}</div>
      </div>
      <div class="card stat-card">
        <div class="stat-label">Visible resources</div>
        <div class="stat-value">28</div>
        <div class="stat-foot">Simulated prototype data</div>
      </div>
      <div class="card stat-card">
        <div class="stat-label">Workspace view</div>
        <div class="stat-value" style="font-size:22px;">Unified</div>
        <div class="stat-foot">One browser pattern</div>
      </div>
    </div>

    <div class="provider-hero">
      <div class="provider-hero-content">
        <div class="eyebrow" style="color:#bfc0ff;">Connected storage</div>
        <h2>Google Drive is ready.</h2>
        <p>Browse the simulated files below using the same CRiB interface intended for other supported cloud providers.</p>
      </div>
    </div>

    <div class="section-head">
      <h3>Recent files</h3>
      <a class="linkish" href="#files" data-route="files">Browse all files</a>
    </div>

    ${fileTable([
      ['COMP-2002 Brief.pdf', 'PDF', 'Google Drive', 'Today, 14:12', 'PDF', false, 'details'],
      ['University', 'Folder', 'Google Drive', 'Yesterday', 'DIR', true, 'folder'],
      ['Project Notes.docx', 'Document', 'Google Drive', '21 Oct', 'DOC', false, 'details'],
    ])}
  `;

  return appShell('Dashboard', 'Your CRiB workspace', 'Connected cloud resources are presented through one consistent interface.', body, button('Browse files', 'files'));
}

function fileTable(rows) {
  return `
    <div class="table">
      <div class="table-row table-head">
        <div>NAME</div><div>TYPE</div><div>PROVIDER</div><div>MODIFIED</div><div></div>
      </div>
      ${rows.map(([name, type, provider, modified, badge, folder, route]) => `
        <a class="table-row" href="#${route}" data-route="${route}">
          <div class="file-cell"><span class="file-badge ${folder ? 'folder' : ''}">${badge}</span><span>${name}</span></div>
          <div class="muted">${type}</div>
          <div class="muted">${provider}</div>
          <div class="muted">${modified}</div>
          <div class="row-action muted">•••</div>
        </a>
      `).join('')}
    </div>
  `;
}

function renderFiles() {
  const body = `
    <div class="prototype-context context-first">
      <strong>Unified browser</strong>
      <span>This prototype currently shows Google Drive data only. Additional supported providers would use this same normalized browsing layout.</span>
    </div>

    <div class="toolbar">
      ${tag('All types')}
      ${tag('Modified date')}
      ${tag('Provider: Google Drive')}
      <div class="toolbar-spacer"></div>
      <input class="search-box" style="width:230px;" data-search-input value="assessment" aria-label="Search files">
    </div>

    ${fileTable([
      ['University', 'Folder', 'Google Drive', 'Today', 'DIR', true, 'folder'],
      ['Documents', 'Folder', 'Google Drive', '20 Oct', 'DIR', true, 'folder'],
      ['Photos', 'Folder', 'Google Drive', '19 Oct', 'DIR', true, 'folder'],
      ['COMP-2002 Brief.pdf', 'PDF', 'Google Drive', 'Today', 'PDF', false, 'details'],
      ['Project Notes.docx', 'Document', 'Google Drive', '21 Oct', 'DOC', false, 'details'],
    ])}
  `;

  return appShell('Browse files', 'Browse files', 'View permitted files and folders through the CRiB interface.', body, button('Connected providers', 'manage', 'light'), 'Search files and folders');
}

function renderFolder() {
  const body = `
    <div class="toolbar">
      ${tag('All types')}
      ${tag('Modified date')}
      ${tag('Google Drive')}
      <div class="toolbar-spacer"></div>
      ${tag('Inside University', 'violet')}
    </div>

    ${fileTable([
      ['COMP-2002', 'Folder', 'Google Drive', 'Today', 'DIR', true, 'folder'],
      ['Programming', 'Folder', 'Google Drive', '22 Oct', 'DIR', true, 'folder'],
      ['Assessment 1.pdf', 'PDF', 'Google Drive', 'Today', 'PDF', false, 'details'],
      ['Web Development Notes.docx', 'Document', 'Google Drive', '23 Oct', 'DOC', false, 'details'],
      ['CRiB Pitch.pptx', 'Presentation', 'Google Drive', '22 Oct', 'PPT', false, 'details'],
    ])}
  `;

  return appShell('Browse files', 'University', 'Google Drive · 5 prototype items', body, button('Back to files', 'files', 'light'), 'Search University');
}

function renderSearchResults() {
  const body = `
    <div class="toolbar">
      ${tag('Query: assessment', 'violet')}
      ${tag('Type: All')}
      ${tag('Provider: Google Drive')}
    </div>

    ${fileTable([
      ['Assessment 1.pdf', 'PDF', 'Google Drive', 'Today', 'PDF', false, 'details'],
      ['Assessment Notes.docx', 'Document', 'Google Drive', '23 Oct', 'DOC', false, 'details'],
      ['Assessment Criteria.pdf', 'PDF', 'Google Drive', '20 Oct', 'PDF', false, 'details'],
      ['Assessment Demo.pptx', 'Presentation', 'Google Drive', '18 Oct', 'PPT', false, 'details'],
    ])}
  `;

  return appShell('Browse files', 'Search results', '4 simulated results for “assessment”.', body, button('Clear search', 'files', 'light'), 'assessment');
}

function renderFileDetails() {
  const detailRows = [
    ['Provider', 'Google Drive'],
    ['Type', 'PDF'],
    ['Modified', 'Today, 14:12'],
    ['Size', '2.4 MB'],
    ['Location', 'University'],
  ];

  const body = `
    <div class="detail-layout">
      <div class="card preview-card">
        <div class="preview-file-icon">PDF</div>
        <h2>Assessment 1.pdf</h2>
        <p>File content preview is outside this prototype scope. This screen demonstrates file information and available actions.</p>
      </div>

      <aside class="card detail-panel">
        <div class="detail-head"><h3>File details</h3>${tag('Available', 'success')}</div>
        <div class="detail-list">
          ${detailRows.map(([key, value]) => `<div class="detail-row"><span>${key}</span><strong>${value}</strong></div>`).join('')}
        </div>
        <div class="detail-actions">
          ${button('Open file', 'details')}
          ${button('Simulate download', 'details', 'light')}
          ${button('Back to folder', 'folder', 'light')}
        </div>
      </aside>
    </div>
  `;

  return appShell('Browse files', 'File details', 'Review the selected resource and its provider before taking an action.', body);
}

function renderProviderManagement() {
  const body = `
    <div class="prototype-context context-first">
      <strong>Manage cloud connections</strong>
      <span>Add, review or disconnect supported cloud providers here. User profile information is separate from provider connections.</span>
    </div>

    <div class="section-head">
      <h3>Connected providers</h3>
      ${button('Add provider', 'providers', 'light')}
    </div>

    <div class="card provider-row">
      <div class="provider-icon">GD</div>
      <div class="provider-row-copy">
        <h3>Google Drive</h3>
        <p>user@example.com · Simulated connection</p>
      </div>
      ${tag('Connected', 'success')}
      ${button('Simulate connection error', 'error', 'light')}
    </div>

    <div class="section-head"><h3>Connection actions</h3></div>

    <div class="card provider-row" style="border-color:#e9d1d4;">
      <div class="provider-row-copy">
        <h3>Disconnect Google Drive?</h3>
        <p>This removes the simulated CRiB connection state. It does not delete anything from Google Drive.</p>
      </div>
      ${button('Disconnect Google Drive', 'empty', 'danger')}
    </div>

    <div class="notice">Future versions may support multiple active providers at the same time. This Assessment 1 prototype demonstrates one simulated provider end-to-end.</div>
  `;

  return appShell('Connected providers', 'Connected providers', 'Add, review and disconnect cloud-storage connections from one place.', body);
}

function renderConnectionError() {
  const body = `
    <div class="card error-card">
      <div class="error-mark">!</div>
      <div>
        ${tag('Connection expired', 'danger')}
        <h2 style="margin:14px 0 0;">Google Drive connection needs to be restored</h2>
        <p class="muted" style="line-height:1.6;">CRiB cannot access your Google Drive right now. Your files are still in Google Drive. Reconnect your account to restore access in CRiB.</p>
        <div class="hero-actions" style="margin-top:20px;">
          ${button('Reconnect Google Drive', 'authorize')}
          ${button('Back to connected providers', 'manage', 'light')}
        </div>
      </div>
    </div>
  `;

  return appShell('Connected providers', 'Google Drive needs attention', 'This prototype demonstrates how CRiB handles an expired provider connection.', body);
}

function renderLoading() {
  const skeleton = Array.from({ length: 6 }, () => `
    <div class="loading-row">
      <div class="loading-line"></div><div class="loading-line"></div><div class="loading-line"></div><div class="loading-line"></div>
    </div>
  `).join('');

  const body = `
    <div class="prototype-context context-first">
      <strong>Loading provider resources</strong>
      <span>CRiB is simulating the step where permitted provider data would be normalized for the file browser.</span>
    </div>

    <div class="table">
      <div class="table-row table-head"><div>NAME</div><div>TYPE</div><div>PROVIDER</div><div>MODIFIED</div><div></div></div>
      ${skeleton}
    </div>
  `;

  return appShell('Browse files', 'Loading resources', 'Fetching the latest permitted files from the connected provider…', body);
}

function renderNoResults() {
  const body = `
    <div class="card empty-state" style="min-height:400px;">
      <div class="empty-mark neutral-empty">0</div>
      <h2>No matching resources.</h2>
      <p>Try another search term or remove the active filters.</p>
      ${button('Clear search', 'files', 'light')}
    </div>
  `;

  return appShell('Browse files', 'No results', 'Nothing matched “network-diagram-final-final”.', body, '', 'network-diagram-final-final');
}

window.addEventListener('hashchange', render);
window.addEventListener('DOMContentLoaded', render);
