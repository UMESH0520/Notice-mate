/** Screen 2 — Notice input: sample notice, file upload, or pasted text. */

import api from '../api.js';
import { navigate } from '../router.js';
import { state, setState, resetNotice } from '../state.js';
import { t } from '../i18n.js';
import { icon, categoryIcon } from '../icons.js';
import {
  alert,
  badge,
  button,
  esc,
  emptyState,
  errorState,
  formatBytes,
  progress,
  screenHead,
  setBusy,
  spinner,
} from '../ui.js';
import { friendlyError, showError } from './shared.js';

const TABS = [
  ['demo', 'input.tabDemo', 'eye'],
  ['upload', 'input.tabUpload', 'upload'],
  ['paste', 'input.tabPaste', 'keyboard'],
];

let pendingFile = null;

/* ---- Panels -------------------------------------------------------------- */

function demoPanel(demos) {
  if (!demos?.length) {
    return emptyState({
      title: t('docs.emptyTitle'),
      body: t('error.generic'),
    });
  }
  return `<div class="stack--sm stack">
    <div>
      <p class="card__label">${esc(t('input.demoHeading'))}</p>
      <p class="small muted">${esc(t('input.demoSub'))}</p>
    </div>
    ${demos
      .map(
        (d) => `<button class="option-card" data-demo-id="${esc(d.id)}">
          <span class="option-card__icon">${icon(categoryIcon(d.icon), 24)}</span>
          <span class="option-card__body">
            <span class="option-card__title">${esc(d.title)}</span>
            <span class="option-card__meta">${esc(d.authority)}</span>
            <span class="option-card__blurb">${esc(d.blurb)}</span>
          </span>
          <span class="option-card__chevron" aria-hidden="true">${icon(
            'chevronRight',
            20,
          )}</span>
        </button>`,
      )
      .join('')}
  </div>`;
}

function uploadPanel() {
  return `<div class="stack">
    <div>
      <p class="card__label">${esc(t('input.uploadHeading'))}</p>
    </div>
    <div class="upload" id="drop">
      <div class="upload__icon">${icon('upload', 26)}</div>
      <label class="btn btn--secondary" for="file-input" style="display:inline-flex">
        ${icon('doc', 18)} ${esc(t('input.uploadDrop'))}
      </label>
      <input id="file-input" type="file" class="hidden"
             accept=".pdf,.png,.jpg,.jpeg,.txt,.webp" />
      <p class="upload__hint">${esc(t('input.uploadHint'))}</p>
      <div id="file-chip"></div>
    </div>
    ${button({
      label: t('input.uploadCta'),
      iconName: 'arrowRight',
      iconAfter: true,
      attrs: 'data-upload-go',
      disabled: true,
    })}
    ${alert(esc(t('input.privacy')), 'info', 'shield')}
  </div>`;
}

function pastePanel() {
  return `<div class="stack">
    <div class="field">
      <label class="field__label" for="paste">${esc(t('input.pasteLabel'))}</label>
      <textarea id="paste" class="textarea"
        placeholder="${esc(t('input.pastePlaceholder'))}"></textarea>
    </div>
    ${button({
      label: t('input.pasteCta'),
      iconName: 'arrowRight',
      iconAfter: true,
      attrs: 'data-paste-go',
    })}
    ${alert(esc(t('input.privacy')), 'info', 'shield')}
  </div>`;
}

function noticeSubmissionGuide() {
  return `<div class="card card--accent" style="border-left:4px solid var(--brand);background:var(--bg-subtle);margin-bottom:1.25rem;padding:1.1rem 1.25rem;border-radius:14px">
    <div class="row-between" style="flex-wrap:wrap;gap:0.5rem;margin-bottom:0.6rem">
      <strong style="color:var(--brand);font-size:1.05rem;display:flex;align-items:center;gap:0.45rem">
        ${icon('sparkles', 20)} How NoticeMate Works For You
      </strong>
      ${badge('GOVERNMENT & PRIVATE NOTICES', 'brand', true)}
    </div>
    <p style="font-size:0.94rem;line-height:1.6;color:var(--text);margin-bottom:0.8rem">
      NoticeMate is an independent platform that simplifies and assists users to understand any government or private notice, official letter, or bill — turning dense legalese into simple, step-by-step guidance.
    </p>
    <div class="grid grid--2" style="gap:0.75rem">
      <div style="background:var(--bg-surface);padding:0.75rem 0.9rem;border-radius:10px;border:1px solid var(--border-light)">
        <strong style="font-size:0.88rem;color:var(--text);display:flex;align-items:center;gap:0.3rem">
          ${icon('doc', 16)} 1. Add Any Notice
        </strong>
        <p class="small muted" style="margin-top:0.25rem;line-height:1.45">Select a sample notice, upload a PDF/Image, or paste text from any government department or private organization.</p>
      </div>
      <div style="background:var(--bg-surface);padding:0.75rem 0.9rem;border-radius:10px;border:1px solid var(--border-light)">
        <strong style="font-size:0.88rem;color:var(--text);display:flex;align-items:center;gap:0.3rem">
          ${icon('sparkles', 16)} 2. Get Plain-English Output
        </strong>
        <p class="small muted" style="margin-top:0.25rem;line-height:1.45">Instantly see deadlines, key dates, direct official website links, required documents, and what steps to take next.</p>
      </div>
    </div>
  </div>`;
}

/* ---- Screen -------------------------------------------------------------- */

export default async function input({ main, query = {} } = {}) {
  const activeTab = TABS.some(([k]) => k === query?.tab) ? query.tab : 'demo';

  main.innerHTML = `<section class="screen">
    ${progress(1)}
    ${screenHead({
      eyebrow: t('input.eyebrow'),
      title: t('input.title'),
      subtitle: t('input.subtitle'),
    })}
    ${noticeSubmissionGuide()}
    <div class="tabs" role="tablist" aria-label="${esc(t('input.subtitle'))}">
      ${TABS.map(
        ([key, label, ico]) => `<button class="tab" role="tab" id="tab-${key}"
            aria-selected="${key === activeTab}" aria-controls="panel"
            aria-label="${esc(t(label))}" data-tab="${key}">
            ${icon(ico, 18)}<span>${esc(t(label))}</span>
          </button>`,
      ).join('')}
    </div>
    <div id="panel" role="tabpanel" aria-labelledby="tab-${activeTab}"></div>
  </section>`;

  const panel = main.querySelector('#panel');

  main.querySelectorAll('[data-tab]').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (btn.dataset.tab === activeTab) return;
      navigate(`/input?tab=${btn.dataset.tab}`);
    });
  });

  if (activeTab === 'demo') {
    await renderDemos(panel);
  } else if (activeTab === 'upload') {
    renderUpload(panel);
  } else {
    renderPaste(panel);
  }
}

/* ---- Demo ---------------------------------------------------------------- */

async function renderDemos(panel) {
  panel.innerHTML = spinner();
  let demos = state.demoNotices;
  if (!demos) {
    try {
      demos = await api.demoNotices();
      setState({ demoNotices: demos });
    } catch (err) {
      panel.innerHTML = errorState(friendlyError(err));
      panel
        .querySelector('[data-retry]')
        ?.addEventListener('click', () => renderDemos(panel));
      return;
    }
  }
  panel.innerHTML = demoPanel(demos);
  panel.querySelectorAll('[data-demo-id]').forEach((card) => {
    card.addEventListener('click', async () => {
      card.setAttribute('aria-busy', 'true');
      card.disabled = true;
      try {
        resetNotice();
        const notice = await api.createFromDemo(
          card.dataset.demoId,
          state.sessionId,
        );
        setState({ noticeId: notice.id, notice });
        navigate('/processing');
      } catch (err) {
        card.removeAttribute('aria-busy');
        card.disabled = false;
        showError(err);
      }
    });
  });
}

/* ---- Upload -------------------------------------------------------------- */

function renderUpload(panel) {
  pendingFile = null;
  panel.innerHTML = uploadPanel();

  const fileInput = panel.querySelector('#file-input');
  const chip = panel.querySelector('#file-chip');
  const go = panel.querySelector('[data-upload-go]');
  const drop = panel.querySelector('#drop');

  const setFile = (file) => {
    pendingFile = file || null;
    if (!file) {
      chip.innerHTML = '';
      go.disabled = true;
      return;
    }
    chip.innerHTML = `<div class="file-chip">
      <span>${icon('doc', 20)}</span>
      <span class="file-chip__meta">
        <span class="file-chip__name">${esc(file.name)}</span>
        <span class="file-chip__size">${formatBytes(file.size)}</span>
      </span>
      <button class="btn btn--ghost" style="min-height:36px;padding:0 .4rem"
        data-clear aria-label="${esc(t('common.cancel'))}">${icon('x', 18)}</button>
    </div>`;
    go.disabled = false;
    chip.querySelector('[data-clear]')?.addEventListener('click', () => setFile(null));
  };

  fileInput.addEventListener('change', () => setFile(fileInput.files?.[0]));

  ['dragenter', 'dragover'].forEach((evt) =>
    drop.addEventListener(evt, (e) => {
      e.preventDefault();
      drop.classList.add('is-drag');
    }),
  );
  ['dragleave', 'drop'].forEach((evt) =>
    drop.addEventListener(evt, (e) => {
      e.preventDefault();
      drop.classList.remove('is-drag');
    }),
  );
  drop.addEventListener('drop', (e) => {
    const file = e.dataTransfer?.files?.[0];
    if (file) setFile(file);
  });

  go.addEventListener('click', async () => {
    if (!pendingFile) return;
    setBusy(go, true);
    try {
      resetNotice();
      const notice = await api.createFromUpload(pendingFile, state.sessionId);
      setState({ noticeId: notice.id, notice });
      navigate('/processing');
    } catch (err) {
      setBusy(go, false);
      showError(err);
    }
  });
}

/* ---- Paste --------------------------------------------------------------- */

function renderPaste(panel) {
  panel.innerHTML = pastePanel();
  const ta = panel.querySelector('#paste');
  const go = panel.querySelector('[data-paste-go]');

  go.addEventListener('click', async () => {
    const text = ta.value.trim();
    if (text.length < 40) {
      showErrorMessage(panel, t('input.pasteTooShort'));
      ta.focus();
      return;
    }
    setBusy(go, true);
    try {
      resetNotice();
      const notice = await api.createFromText(text, state.sessionId);
      setState({ noticeId: notice.id, notice });
      navigate('/processing');
    } catch (err) {
      setBusy(go, false);
      showError(err);
    }
  });
}

function showErrorMessage(panel, message) {
  let holder = panel.querySelector('#inline-error');
  if (!holder) {
    holder = document.createElement('div');
    holder.id = 'inline-error';
    panel.prepend(holder);
  }
  holder.innerHTML = alert(esc(message), 'danger');
}
