/**
 * Application bootstrap: language, routes, health check, global error safety.
 *
 * DEMO PROTOTYPE — NOT AN OFFICIAL GOVERNMENT SERVICE.
 */

import api from './api.js?v=10';
import { register, setNotFound, start, render, navigate } from './router.js?v=10';
import { state, setState } from './state.js?v=10';
import { applyStaticTranslations, setLanguage, t } from './i18n.js?v=10';
import { emptyState, toast } from './ui.js?v=10';

import welcome from './screens/welcome.js?v=10';
import inputScreen from './screens/input.js?v=10';
import processing from './screens/processing.js?v=10';
import explain from './screens/explain.js?v=10';
import plan from './screens/plan.js?v=10';
import documents from './screens/documents.js?v=10';
import responseScreen from './screens/response.js?v=10';
import review from './screens/review.js?v=10';
import confirmation from './screens/confirmation.js?v=10';
import statusScreen from './screens/status.js?v=10';

/* ---- Routes -------------------------------------------------------------- */
register('/', welcome);
register('/input', inputScreen);
register('/processing', processing);
register('/explain', explain);
register('/plan', plan);
register('/documents', documents);
register('/response', responseScreen);
register('/review', review);
register('/confirmation', confirmation);
register('/status', statusScreen);

setNotFound(({ main }) => {
  main.innerHTML = `<section class="screen">${emptyState({
    iconName: 'question',
    title: t('error.title'),
    body: t('error.noNotice'),
  })}</section>`;
  setTimeout(() => navigate('/', { replace: true }), 1200);
});

/* ---- Language ------------------------------------------------------------ */
function initLanguage() {
  const select = document.getElementById('lang');
  const stored = state.language || 'en';
  setLanguage(stored);
  if (select) {
    select.value = stored;
    select.addEventListener('change', async () => {
      setState({ language: setLanguage(select.value) });
      applyStaticTranslations();
      // The backend supplies translated explanations, so re-analyse quietly to
      // pick up the chosen language before re-rendering the current screen.
      if (state.noticeId) {
        try {
          const analysis = await api.analyze(state.noticeId, state.language);
          setState({ analysis });
        } catch {
          /* keep the existing analysis; the UI chrome is already translated */
        }
      }
      await render();
    });
  }
  applyStaticTranslations();
}

/* ---- Health banner ------------------------------------------------------- */
async function initHealth() {
  try {
    const health = await api.health();
    setState({ health });
    if (!health.ai_enabled) {
      // Not an error — just be transparent about the demo fallback.
      console.info(
        '[NoticeMate] No OpenAI key configured — using the built-in demo analysis.',
      );
    }
  } catch {
    toast(t('error.offline'), 'danger');
  }
}

/* ---- Global safety nets -------------------------------------------------- */
window.addEventListener('error', (e) => {
  console.error('[NoticeMate]', e.error || e.message);
  toast(t('error.generic'), 'danger');
});
window.addEventListener('unhandledrejection', (e) => {
  if (e.reason?.name === 'AbortError') return;
  console.error('[NoticeMate]', e.reason);
  toast(t('error.generic'), 'danger');
});

/* ---- Go ------------------------------------------------------------------ */
function bootstrap() {
  initLanguage();
  initHealth();
  start();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}
