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
  return `<div class="card card--flat" style="border:1px solid var(--border);background:var(--bg-surface);padding:1.25rem;border-radius:14px;margin-bottom:1.25rem">
    <div class="row-between" style="margin-bottom:0.75rem;flex-wrap:wrap;gap:0.5rem">
      <strong style="font-size:1.05rem;color:var(--brand);display:flex;align-items:center;gap:0.4rem">
        ${icon('sparkles', 20)} Required Documents & Official Resolution
      </strong>
      ${badge('AUTOMATIC OFFICIAL PORTAL LOOKUP', 'brand', true)}
    </div>

    <p style="font-size:0.94rem;line-height:1.6;color:var(--text);margin-bottom:0.85rem">
      If a notice image or letter does not explicitly list required documents, NoticeMate automatically queries the official department regulations (e.g., Karnataka Electrical Inspectorate, Income Tax Dept, EPF, Municipal Corporation) to extract the mandatory document checklist for you.
    </p>

    <div class="stack stack--sm">
      <div style="background:var(--bg-subtle);padding:0.8rem 1rem;border-radius:10px;border:1px solid var(--border-light)">
        <strong style="font-size:0.9rem;color:var(--text);display:flex;align-items:center;gap:0.35rem">
          ${icon('shield', 16)} 🏛️ Zero-Panic Search Guarantee
        </strong>
        <p class="small muted" style="margin-top:0.25rem;line-height:1.5">
          You don't need to search through complex government portals or download endless PDFs. NoticeMate presents the complete document checklist, why each document is required, and how to validate it right here.
        </p>
      </div>

      <div style="background:var(--bg-subtle);padding:0.8rem 1rem;border-radius:10px;border:1px solid var(--border-light)">
        <strong style="font-size:0.88rem;color:var(--text);display:flex;align-items:center;gap:0.35rem">
          ${icon('docCheck', 16)} 🔍 Private & Honest Document Checking
        </strong>
        <p class="small muted" style="margin-top:0.25rem;line-height:1.5">
          Upload your document file to run instant, private readability and structure checks. NoticeMate never stores sensitive files off-device or sends them to external servers.
        </p>
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
