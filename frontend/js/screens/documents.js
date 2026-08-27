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
  const isOfficial = doc.trust === 'OFFICIAL_SOURCE' || (doc.source_note && !doc.source_note.includes('Listed in your notice'));

  return `<li class="doc" data-doc="${esc(doc.id)}">
    <div class="doc__top">
      <div style="flex:1">
        <p class="doc__name">${icon('doc', 17)} ${esc(doc.name)}</p>
        ${doc.reason ? `<p class="doc__why">${esc(doc.reason)}</p>` : ''}
        
        <div class="chips" style="gap:0.4rem;margin-top:0.6rem;flex-wrap:wrap">
          ${doc.source_note ? `<span class="badge ${isOfficial ? 'badge--brand' : 'badge--muted'}" style="font-size:0.78rem;padding:0.2rem 0.55rem;font-weight:600">🏛️ ${esc(doc.source_note)}</span>` : ''}
          ${doc.doc_format ? `<span class="badge badge--brand" style="font-size:0.78rem;padding:0.2rem 0.55rem;background:rgba(59,130,246,0.12);color:var(--brand);border:1px solid rgba(59,130,246,0.3)">📄 <strong>Format:</strong> ${esc(doc.doc_format)}</span>` : ''}
          ${doc.size_limit ? `<span class="badge badge--brand" style="font-size:0.78rem;padding:0.2rem 0.55rem;background:rgba(16,185,129,0.12);color:#059669;border:1px solid rgba(16,185,129,0.3)">⚖️ <strong>Max Size:</strong> ${esc(doc.size_limit)}</span>` : ''}
          ${doc.stage && doc.stage !== 'unknown' ? `<span class="badge badge--muted" style="font-size:0.78rem;padding:0.2rem 0.55rem">📌 <strong>Stage:</strong> ${esc(doc.stage)}</span>` : ''}
          ${doc.validity ? `<span class="badge badge--muted" style="font-size:0.78rem;padding:0.2rem 0.55rem">⏳ <strong>Validity:</strong> ${esc(doc.validity)}</span>` : ''}
        </div>

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
  const officialCount = docs.filter(
    (d) => d.trust === 'OFFICIAL_SOURCE' || d.trust === 'DERIVED' || (d.source_note && !d.source_note.includes('Listed in your notice'))
  ).length;

  return `<div class="card card--flat" style="border:1px solid var(--border);background:var(--bg-surface);padding:1.35rem;border-radius:14px;margin-bottom:1.35rem;box-shadow:0 4px 12px rgba(0,0,0,0.03)">
    <div class="row-between" style="margin-bottom:0.85rem;flex-wrap:wrap;gap:0.5rem">
      <strong style="font-size:1.08rem;color:var(--brand);display:flex;align-items:center;gap:0.45rem">
        ${icon('sparkles', 20)} Automated Official Portal Document Checklist Resolution
      </strong>
      ${badge(officialCount > 0 ? `🏛️ ${officialCount} ITEMS RESOLVED VIA OFFICIAL RULES` : 'AUTOMATIC OFFICIAL PORTAL LOOKUP', 'brand', true)}
    </div>

    <p style="font-size:0.95rem;line-height:1.6;color:var(--text);margin-bottom:1rem">
      When a notice image or text does not explicitly list required documents, NoticeMate's AI automatically cross-references the issuing department, branch, and statutory regulations to retrieve the exact mandatory document checklist, allowed file formats (e.g. PDF, JPG), and portal size limits.
    </p>

    <div class="stack stack--sm">
      <div style="background:var(--bg-subtle);padding:0.85rem 1.1rem;border-radius:10px;border:1px solid var(--border-light)">
        <strong style="font-size:0.92rem;color:var(--text);display:flex;align-items:center;gap:0.35rem">
          ${icon('shield', 16)} 🏛️ Zero-Manual-Search Guarantee
        </strong>
        <p class="small muted" style="margin-top:0.3rem;line-height:1.55">
          You never have to hunt through complex government portals or download endless PDFs. NoticeMate presents the complete document checklist, why each document is required, allowed file formats, and maximum size limits right here.
        </p>
      </div>

      <div style="background:var(--bg-subtle);padding:0.85rem 1.1rem;border-radius:10px;border:1px solid var(--border-light)">
        <strong style="font-size:0.9rem;color:var(--text);display:flex;align-items:center;gap:0.35rem">
          ${icon('docCheck', 16)} 🔍 Automated Portal Specification Verification
        </strong>
        <p class="small muted" style="margin-top:0.3rem;line-height:1.55">
          Upload your files to run instant readability and portal compliance checks against size and format constraints. Everything is validated privately on your system.
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
