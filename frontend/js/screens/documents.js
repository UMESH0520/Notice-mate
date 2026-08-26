/** Screen 7 — Document checklist with upload and honest validation feedback. */

import api from '../api.js';
import { navigate } from '../router.js';
import { state, setState } from '../state.js';
import { t } from '../i18n.js';
import { icon } from '../icons.js';
import {
  alert,
  badge,
  button,
  emptyState,
  esc,
  progress,
  screenHead,
  backLink,
} from '../ui.js';
import { loadInto, requireNotice, showError } from './shared.js';

const STATUS_VARIANT = {
  uploaded: 'success',
  unavailable: 'warn',
  needed: 'muted',
};

function validationBlock(doc) {
  const v = doc.validation;
  if (!v || !v.checks?.length) return '';
  return `<div class="doc__validation">
    <p class="card__label">${esc(t('docs.checkTitle'))}</p>
    ${v.checks
      .map(
        (c) => `<p class="check-line ${c.ok ? 'check-line--ok' : 'check-line--no'}">
          ${icon(c.ok ? 'checkCircle' : 'alert', 16)}
          <span>${esc(c.label)}${c.detail ? ` — ${esc(c.detail)}` : ''}</span>
        </p>`,
      )
      .join('')}
    <p class="small muted mt-sm">${esc(v.message || '')}</p>
  </div>`;
}

function docRow(doc) {
  return `<li class="doc" data-doc="${esc(doc.id)}">
    <div class="doc__top">
      <div>
        <p class="doc__name">${icon('doc', 17)} ${esc(doc.name)}</p>
        ${doc.reason ? `<p class="doc__why">${esc(doc.reason)}</p>` : ''}
        ${
          doc.original_filename
            ? `<p class="small muted mt-sm">${esc(doc.original_filename)}</p>`
            : ''
        }
      </div>
      <div class="chips" style="flex-direction:column;align-items:flex-end">
        ${badge(
          t(`docs.status.${doc.status}`),
          STATUS_VARIANT[doc.status] || 'muted',
          true,
        )}
        ${badge(doc.required ? t('docs.required') : t('docs.helpful'), 'muted')}
      </div>
    </div>

    ${validationBlock(doc)}

    <div class="doc__actions">
      <label class="btn btn--secondary" for="up-${esc(doc.id)}">
        ${icon('upload', 17)} ${esc(t('docs.upload'))}
      </label>
      <input id="up-${esc(doc.id)}" class="hidden" type="file"
        accept=".pdf,.png,.jpg,.jpeg,.txt,.webp" data-upload="${esc(doc.id)}" />
      ${
        doc.status === 'needed'
          ? `<button class="btn btn--ghost" data-status="${esc(doc.id)}"
               data-value="unavailable">${icon('x', 17)} ${esc(
              t('docs.markUnavailable'),
            )}</button>`
          : `<button class="btn btn--ghost" data-status="${esc(doc.id)}"
               data-value="needed">${icon('refresh', 17)} ${esc(
              t('docs.markNeeded'),
            )}</button>`
      }
    </div>
  </li>`;
}

export default async function documents({ main }) {
  if (!requireNotice()) return;

  await loadInto(
    main,
    () => api.documents(state.noticeId),
    (docs) => {
      setState({ documents: docs });
      const added = docs.filter((d) => d.status !== 'needed').length;

      main.innerHTML = `<section class="screen">
        ${progress(4)}
        ${backLink('#/plan')}
        ${screenHead({
          eyebrow: t('docs.eyebrow'),
          title: t('docs.title'),
          subtitle: t('docs.subtitle'),
        })}

        ${
          docs.length
            ? `<div class="stack">
                <p class="small muted">${esc(
                  t('review.docsCount', { done: added, total: docs.length }),
                )}</p>
                <ul>${docs.map(docRow).join('')}</ul>
                ${alert(esc(t('docs.noteVerify')), 'info', 'shield')}
              </div>`
            : emptyState({
                iconName: 'docCheck',
                title: t('docs.emptyTitle'),
                body: t('docs.emptyBody'),
              })
        }

        <div class="actions">
          ${button({
            label: t('docs.cta'),
            iconName: 'arrowRight',
            iconAfter: true,
            size: 'lg',
            attrs: 'data-next',
          })}
        </div>
      </section>`;

      main.querySelectorAll('[data-upload]').forEach((inputEl) => {
        inputEl.addEventListener('change', async () => {
          const file = inputEl.files?.[0];
          if (!file) return;
          const row = main.querySelector(`[data-doc="${inputEl.dataset.upload}"]`);
          row?.setAttribute('aria-busy', 'true');
          try {
            await api.uploadDocument(state.noticeId, inputEl.dataset.upload, file);
            await documents({ main });
          } catch (err) {
            row?.removeAttribute('aria-busy');
            showError(err);
          }
        });
      });

      main.querySelectorAll('[data-status]').forEach((btn) => {
        btn.addEventListener('click', async () => {
          btn.disabled = true;
          try {
            await api.setDocumentStatus(
              state.noticeId,
              btn.dataset.status,
              btn.dataset.value,
            );
            await documents({ main });
          } catch (err) {
            btn.disabled = false;
            showError(err);
          }
        });
      });

      main
        .querySelector('[data-next]')
        ?.addEventListener('click', () => navigate('/response'));
    },
  );
}
