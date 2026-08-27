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

function documentsGuideExplanationCard(docs) {
  return `<div class="card card--flat" style="border:1px solid var(--border);background:var(--bg-surface);padding:1.25rem;border-radius:14px;margin-bottom:1rem">
    <div class="row-between" style="margin-bottom:0.75rem">
      <strong style="font-size:1.05rem;color:var(--brand);display:flex;align-items:center;gap:0.4rem">
        ${icon('sparkles', 20)} Required Documents Guidance
      </strong>
      ${badge(`${docs.length} DOCUMENT${docs.length === 1 ? '' : 'S'} LISTED`, 'brand', true)}
    </div>

    <p style="font-size:0.93rem;line-height:1.55;color:var(--text);margin-bottom:0.8rem">
      NoticeMate extracted these specific required documents directly from your notice provisions. Having these ready ensures your application or response is complete and avoids delays or rejections:
    </p>

    <div class="stack stack--sm">
      <div style="background:var(--bg-subtle);padding:0.75rem 0.9rem;border-radius:10px">
        <strong style="font-size:0.88rem;color:var(--text)">📄 Why These Documents Matter</strong>
        <p class="small muted" style="margin-top:0.2rem;line-height:1.45">Each document serves as proof for specific claims mentioned in the notice (e.g., tax deductions, identity validation, utility bill history, or deposit receipts).</p>
      </div>
      <div style="background:var(--bg-subtle);padding:0.75rem 0.9rem;border-radius:10px">
        <strong style="font-size:0.88rem;color:var(--text)">🔍 Honest Document Checking</strong>
        <p class="small muted" style="margin-top:0.2rem;line-height:1.45">Upload your document to run basic structure and date checks. NoticeMate never stores sensitive files off-device or sends them to any external system.</p>
      </div>
    </div>
  </div>`;
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

        ${documentsGuideExplanationCard(docs)}

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
