/**
 * Minimal hash router. Hash routing keeps deep links working when the SPA is
 * served by StaticFiles (no server-side rewrite rules needed).
 */

const routes = new Map();
let notFound = null;
let current = null;

export function register(path, render) {
  routes.set(path, render);
}

export function setNotFound(render) {
  notFound = render;
}

export function parseHash(hash = location.hash) {
  const raw = (hash || '').replace(/^#/, '') || '/';
  const [pathPart, queryPart] = raw.split('?');
  const path = pathPart.startsWith('/') ? pathPart : `/${pathPart}`;
  const query = Object.fromEntries(new URLSearchParams(queryPart || ''));
  return { path: path.replace(/\/+$/, '') || '/', query };
}

export function navigate(path, { replace = false } = {}) {
  const target = path.startsWith('#') ? path : `#${path}`;
  rendering = false;
  if (location.hash === target) {
    render();
    return;
  }
  if (replace) history.replaceState(null, '', target);
  else location.hash = target;
  if (replace) render();
}

export function currentPath() {
  return parseHash().path;
}

let rendering = false;

export async function render() {
  const { path, query } = parseHash();
  const view = routes.get(path) || notFound;
  if (!view) return;
  if (rendering) return;
  rendering = true;
  const main = document.getElementById('main');
  try {
    current = path;
    await view({ main, path, query });
    if (main) {
      main.focus({ preventScroll: true });
      window.scrollTo({ top: 0, behavior: 'auto' });
      requestAnimationFrame(() => window.scrollTo({ top: 0, behavior: 'auto' }));
    }
  } catch (err) {
    console.error('[NoticeMate Router Error]', err);
    if (main) {
      main.innerHTML = `<section class="screen">
        <div class="card" style="margin-top:2rem;text-align:center;padding:2rem">
          <h2 style="font-size:1.2rem;margin-bottom:0.5rem">NoticeMate Assistant</h2>
          <p style="color:var(--text-soft);margin-bottom:1.2rem">An unexpected error occurred or the notice was reset.</p>
          <button class="btn btn--primary" onclick="location.hash='#/'" style="margin:0 auto">Return to Welcome Screen</button>
        </div>
      </section>`;
    }
  } finally {
    rendering = false;
  }
}

export function start() {
  window.addEventListener('hashchange', render);
  if (!location.hash || location.hash === '#') {
    location.hash = '#/';
  } else {
    render();
  }
}

export function activeRoute() {
  return current;
}
