/** Screen 11 — Status tracker: timeline plus the honest activity log. */

import api from '../api.js';
import { navigate } from '../router.js';
import { state, resetNotice } from '../state.js';
import { t } from '../i18n.js';
import { icon } from '../icons.js';
import {
  alert,
  button,
  esc,
  formatDateTime,
  screenHead,
} from '../ui.js';
import { loadInto, requireNotice } from './shared.js';

function timeline(steps) {
  return `<ol class="timeline">
    ${steps
      .map(
        (s) => `<li class="timeline__item" data-done="${s.done}"
          data-system="${esc(s.system)}">
          <span class="timeline__marker">${
            s.done
              ? icon('check', 14, 2.8)
              : s.system === 'government'
                ? icon('building', 14)
                : icon('circle', 12)
          }</span>
          <p class="timeline__label">${esc(s.label)}</p>
          ${s.note ? `<p class="timeline__note">${esc(s.note)}</p>` : ''}
        </li>`,
      )
      .join('')}
  </ol>`;
}

function legend() {
  return `<div class="legend">
    <span><span class="swatch" style="background:var(--success-600)"></span>${esc(
      t('status.legendDone'),
    )}</span>
    <span><span class="swatch" style="background:var(--border-strong)"></span>${esc(
      t('status.legendPending'),
    )}</span>
    <span><span class="swatch" style="background:var(--brand-500)"></span>${esc(
      t('status.legendGov'),
    )}</span>
  </div>`;
}

function history(events) {
  if (!events?.length) return '';
  return `<div class="card">
    <p class="card__label">${esc(t('status.history'))}</p>
    <ul class="stack--sm stack">
      ${events
        .slice()
        .reverse()
        .map(
          (e) => `<li class="check-line">
            ${icon('clock', 15)}
            <span><strong>${esc(e.message)}</strong>
              <span class="small muted"> · ${esc(
                formatDateTime(e.created_at),
              )}</span></span>
          </li>`,
        )
        .join('')}
    </ul>
  </div>`;
}

export default async function status({ main }) {
  if (!requireNotice()) return;

  await loadInto(
    main,
    () => api.status(state.noticeId),
    (data) => {
      main.innerHTML = `<section class="screen">
        ${screenHead({
          eyebrow: t('status.eyebrow'),
          title: t('status.title'),
          subtitle: t('status.subtitle'),
        })}

        <div class="stack">
          <div class="card">
            ${timeline(data.steps)}
            ${legend()}
          </div>
          ${alert(esc(t('status.govNote')), 'warn', 'shield')}
          ${history(data.events)}
        </div>

        <div class="actions">
          ${button({
            label: t('status.refresh'),
            variant: 'secondary',
            iconName: 'refresh',
            attrs: 'data-refresh',
          })}
          ${button({
            label: t('status.cta'),
            variant: 'ghost',
            attrs: 'data-new',
          })}
        </div>
      </section>`;

      main
        .querySelector('[data-refresh]')
        ?.addEventListener('click', () => status({ main }));
      main.querySelector('[data-new]')?.addEventListener('click', () => {
        resetNotice();
        navigate('/input');
      });
    },
  );
}
