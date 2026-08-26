/** Screen 10 — Confirmation of the simulated submission. */

import api from '../api.js';
import { navigate } from '../router.js';
import { state, setState, resetNotice } from '../state.js';
import { t } from '../i18n.js';
import { icon } from '../icons.js';
import {
  alert,
  badge,
  button,
  copyText,
  esc,
  formatDateTime,
  screenHead,
} from '../ui.js';
import { loadInto } from './shared.js';

export default async function confirmation({ main }) {
  if (!state.submissionId) {
    navigate(state.noticeId ? '/review' : '/input', { replace: true });
    return;
  }

  await loadInto(
    main,
    () => api.submission(state.submissionId),
    (sub) => {
      setState({ submission: sub });

      main.innerHTML = `<section class="screen">
        <div class="center">
          <div class="state__icon" style="background:var(--success-50);
            color:var(--success-600);width:68px;height:68px">
            ${icon('checkCircle', 34)}
          </div>
        </div>
        ${screenHead({ title: t('confirm.title'), subtitle: t('confirm.sub') })}

        <div class="stack">
          <div class="card">
            <div class="summary-row">
              <span class="summary-row__label">${esc(
                t('confirm.reference'),
              )}</span>
              <span class="summary-row__value">
                <strong style="font-family:ui-monospace,SFMono-Regular,Menlo,monospace">${esc(
                  sub.reference,
                )}</strong>
                <button class="btn btn--ghost" data-copy
                  style="min-height:34px;padding:.1rem .5rem;margin-left:.4rem">
                  ${icon('copy', 16)}
                </button>
              </span>
            </div>
            <div class="summary-row">
              <span class="summary-row__label">${esc(t('confirm.status'))}</span>
              <span class="summary-row__value">${badge(
                sub.status,
                'success',
                true,
              )} <span class="small muted">${esc(
                formatDateTime(sub.submitted_at),
              )}</span></span>
            </div>
            <div class="summary-row">
              <span class="summary-row__label">${esc(
                t('confirm.whatNext'),
              )}</span>
              <span class="summary-row__value">${esc(sub.next_steps)}</span>
            </div>
          </div>

          ${alert(`<strong>${esc(t('confirm.simulated'))}</strong>`, 'warn', 'shield')}
        </div>

        <div class="actions">
          ${button({
            label: t('confirm.cta'),
            iconName: 'clipboard',
            size: 'lg',
            attrs: 'data-track',
          })}
          ${button({
            label: t('confirm.newNotice'),
            variant: 'ghost',
            attrs: 'data-new',
          })}
        </div>
      </section>`;

      main
        .querySelector('[data-copy]')
        ?.addEventListener('click', () => copyText(sub.reference));
      main
        .querySelector('[data-track]')
        ?.addEventListener('click', () => navigate('/status'));
      main.querySelector('[data-new]')?.addEventListener('click', () => {
        resetNotice();
        navigate('/input');
      });
    },
  );
}
