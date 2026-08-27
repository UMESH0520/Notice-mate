/**
 * Screen 3 — Processing. Runs the analysis while showing honest progress:
 * the steps advance on a timer, but the screen only moves on when the API
 * actually returns.
 */

import api from '../api.js';
import { navigate } from '../router.js';
import { state, setState } from '../state.js';
import { t } from '../i18n.js';
import { icon } from '../icons.js';
import { alert, button, esc, errorState } from '../ui.js';
import { friendlyError, lang, requireNotice } from './shared.js';

const STEPS = ['processing.s1', 'processing.s2', 'processing.s3', 'processing.s4'];

export default async function processing({ main }) {
  if (!requireNotice()) return;

  main.innerHTML = `<section class="screen">
    <div class="processing">
      <div class="spinner" role="status"
           aria-label="${esc(t('processing.title'))}"></div>
      <h1 class="screen__title">${esc(t('processing.title'))}</h1>
      <p class="screen__subtitle">${esc(t('processing.sub'))}</p>
      <ul class="proc-steps" id="proc-steps">
        ${STEPS.map(
          (key, i) => `<li class="proc-step${i === 0 ? ' is-active' : ''}"
              data-step="${i}">
            <span class="proc-step__dot">${icon('check', 13, 2.4)}</span>
            <span>${esc(t(key))}</span>
          </li>`,
        ).join('')}
      </ul>
      <p class="small muted mt hidden" id="slow">${esc(t('processing.slow'))}</p>
    </div>
  </section>`;

  const items = [...main.querySelectorAll('.proc-step')];
  let index = 0;
  const tick = setInterval(() => {
    if (index >= items.length - 1) return;
    items[index].classList.remove('is-active');
    items[index].classList.add('is-done');
    index += 1;
    items[index].classList.add('is-active');
  }, 50);
  const slowTimer = setTimeout(
    () => main.querySelector('#slow')?.classList.remove('hidden'),
    3000,
  );

  const stop = () => {
    clearInterval(tick);
    clearTimeout(slowTimer);
  };

  try {
    const analysis = await api.analyze(state.noticeId, lang());
    stop();
    items.forEach((el) => {
      el.classList.remove('is-active');
      el.classList.add('is-done');
    });
    setState({
      notice: { ...(state.notice || {}), id: state.noticeId, analysis },
      analysis,
      plan: null,
      documents: null,
    });
    // Instant 50ms settle
    await new Promise((r) => setTimeout(r, 50));
    navigate('/explain', { replace: true });
  } catch (err) {
    stop();
    const isNotFound = err?.status === 404;
    if (isNotFound) {
      import('../state.js').then(({ resetNotice }) => resetNotice());
    }
    main.innerHTML = `<section class="screen">
      ${errorState(friendlyError(err))}
      <div class="actions" style="margin-top: 1rem">
        ${button({
          label: isNotFound ? 'Upload Notice' : t('common.startOver'),
          variant: 'primary',
          attrs: 'data-restart',
        })}
      </div>
      ${alert(esc(t('welcome.trust')), 'warn', 'shield')}
    </section>`;
    main.querySelector('[data-retry]')?.addEventListener('click', () => {
      processing({ main });
    });
    main.querySelector('[data-restart]')?.addEventListener('click', () => {
      navigate('/input');
    });
  }
}
