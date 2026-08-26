/** Screen 1 — Welcome. Sets expectations, offers the two ways in. */

import { navigate } from '../router.js';
import { state, resetNotice } from '../state.js';
import { t } from '../i18n.js';
import { icon } from '../icons.js';
import { alert, badge, button, esc } from '../ui.js';

const FEATURES = [
  ['sparkles', 'welcome.f1.title', 'welcome.f1.desc'],
  ['list', 'welcome.f2.title', 'welcome.f2.desc'],
  ['docCheck', 'welcome.f3.title', 'welcome.f3.desc'],
  ['send', 'welcome.f4.title', 'welcome.f4.desc'],
];

function resumeCard() {
  if (!state.noticeId) return '';
  return `<div class="card mt">
    <p class="card__label">${esc(t('resume.title'))}</p>
    <p class="small muted">${esc(t('resume.body'))}</p>
    <div class="actions actions--row">
      ${button({
        label: t('resume.cta'),
        variant: 'secondary',
        iconName: 'arrowRight',
        iconAfter: true,
        attrs: 'data-resume',
      })}
      ${button({
        label: t('resume.discard'),
        variant: 'ghost',
        attrs: 'data-discard',
      })}
    </div>
  </div>`;
}

export default function welcome({ main }) {
  main.innerHTML = `<section class="screen">
    <div class="hero">
      <div class="hero__badge">${badge(t('welcome.badge'), 'brand', true)}</div>
      <h1 class="hero__title">
        ${esc(t('welcome.title1'))}<br />
        <span class="grad">${esc(t('welcome.title2'))}</span>
      </h1>
      <p class="hero__sub">${esc(t('welcome.sub'))}</p>
    </div>

    <div class="actions">
      ${button({
        label: t('welcome.cta'),
        iconName: 'arrowRight',
        iconAfter: true,
        size: 'lg',
        attrs: 'data-start',
      })}
      ${button({
        label: t('welcome.demoCta'),
        variant: 'secondary',
        iconName: 'eye',
        attrs: 'data-demo',
      })}
    </div>

    ${resumeCard()}

    <div class="feature-grid">
      ${FEATURES.map(
        ([ico, title, desc]) => `<div class="feature">
          <span class="feature__icon">${icon(ico, 21)}</span>
          <div>
            <p class="feature__title">${esc(t(title))}</p>
            <p class="feature__desc">${esc(t(desc))}</p>
          </div>
        </div>`,
      ).join('')}
    </div>

    <div class="mt">
      ${alert(esc(t('welcome.trust')), 'warn', 'shield')}
    </div>
  </section>`;

  main.querySelector('[data-start]')?.addEventListener('click', () => {
    resetNotice();
    navigate('/input');
  });
  main.querySelector('[data-demo]')?.addEventListener('click', () => {
    resetNotice();
    navigate('/input?tab=demo');
  });
  main.querySelector('[data-resume]')?.addEventListener('click', () => {
    navigate(state.submissionId ? '/status' : '/explain');
  });
  main.querySelector('[data-discard]')?.addEventListener('click', () => {
    resetNotice();
    navigate('/input');
  });
}
