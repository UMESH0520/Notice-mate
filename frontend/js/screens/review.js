/** Screen 9 — Review everything, confirm, then submit (simulated). */

import api from '../api.js';
import { navigate } from '../router.js';
import { state, setState } from '../state.js';
import { t } from '../i18n.js';
import { icon } from '../icons.js';
import {
  alert,
  button,
  esc,
  orUnknown,
  progress,
  screenHead,
  setBusy,
  backLink,
  toast,
} from '../ui.js';
import { lang, loadInto, requireNotice, showError } from './shared.js';

function row(label, value) {
  return `<div class="summary-row">
    <span class="summary-row__label">${esc(label)}</span>
    <span class="summary-row__value">${esc(value)}</span>
  </div>`;
}

export default async function review({ main }) {
  if (!requireNotice()) return;

  await loadInto(
    main,
    () => api.getNotice(state.noticeId, lang()),
    (notice) => {
      const a = notice.analysis || {};
      const docs = notice.documents || [];
      const added = docs.filter((d) => d.status === 'uploaded').length;
      const draft = notice.response;

      if (!draft) {
        navigate('/response', { replace: true });
        return;
      }

      main.innerHTML = `<section class="screen">
        ${progress(6)}
        ${backLink('#/response')}
        ${screenHead({
          eyebrow: t('review.eyebrow'),
          title: t('review.title'),
          subtitle: t('review.subtitle'),
        })}

        <div class="stack">
          <div class="card">
            ${row(t('review.notice'), orUnknown(a.subject || a.notice_type))}
            ${row(t('explain.reference'), orUnknown(a.reference_number))}
            ${row(t('explain.authority'), orUnknown(a.authority))}
            ${row(t('review.deadline'), orUnknown(a.deadline))}
            ${row(
              t('review.documents'),
              t('review.docsCount', { done: added, total: docs.length }),
            )}
          </div>

          <div class="card">
            <div class="row-between">
              <p class="card__label" style="margin:0">${esc(
                t('review.response'),
              )}</p>
              <a class="back-link" href="#/response" style="margin:0">
                ${icon('edit', 16)}${esc(t('review.edit'))}
              </a>
            </div>
            <p class="summary-row__value" style="margin-top:.5rem">${esc(
              draft.content,
            )}</p>
          </div>

          ${alert(
            `<strong>${esc(t('confirm.simulated'))}</strong>`,
            'warn',
            'shield',
          )}

          <label class="check">
            <input type="checkbox" id="confirm" />
            <span class="check__text">${esc(t('review.confirmLabel'))}</span>
          </label>
        </div>

        <div class="actions">
          ${button({
            label: t('review.cta'),
            iconName: 'send',
            size: 'lg',
            attrs: 'data-submit',
            disabled: true,
          })}
        </div>
      </section>`;

      const checkbox = main.querySelector('#confirm');
      const submitBtn = main.querySelector('[data-submit]');
      checkbox.addEventListener('change', () => {
        submitBtn.disabled = !checkbox.checked;
      });

      submitBtn.addEventListener('click', async () => {
        if (!checkbox.checked) {
          toast(t('review.needConfirm'), 'danger');
          checkbox.focus();
          return;
        }
        setBusy(submitBtn, true);
        try {
          const submission = await api.submit(state.noticeId, true);
          setState({ submissionId: submission.id, submission });
          navigate('/confirmation');
        } catch (err) {
          setBusy(submitBtn, false);
          showError(err);
        }
      });
    },
  );
}
