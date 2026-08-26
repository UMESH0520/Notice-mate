/** Screen 8 — Response preparation: generate a draft, edit it, save it. */

import api, { ApiError } from '../api.js';
import { navigate } from '../router.js';
import { state, setState } from '../state.js';
import { t } from '../i18n.js';
import { icon } from '../icons.js';
import {
  alert,
  badge,
  button,
  copyText,
  downloadText,
  esc,
  progress,
  screenHead,
  setBusy,
  sourceLabel,
  sourceVariant,
  backLink,
  toast,
} from '../ui.js';
import { friendlyError, lang, requireNotice, showError } from './shared.js';

/** Existing draft, or null when there isn't one yet. */
async function loadDraft(noticeId) {
  try {
    return await api.getResponse(noticeId);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

function draftView(draft) {
  return `<div class="stack">
    <div class="row-between chips">
      ${badge(
        sourceLabel(draft.draft_source, 'response'),
        sourceVariant(draft.draft_source),
      )}
      ${badge(`v${draft.version}`, 'muted')}
    </div>
    <div class="field">
      <label class="field__label" for="draft">${esc(t('response.label'))}</label>
      <textarea id="draft" class="textarea" style="min-height:300px">${esc(
        draft.content,
      )}</textarea>
    </div>
    ${alert(esc(t('response.checkWarning')), 'warn', 'alert')}
    <div class="doc__actions">
      <button class="btn btn--secondary" data-regen>
        ${icon('refresh', 17)} ${esc(t('response.regenerate'))}
      </button>
      <button class="btn btn--ghost" data-copy>
        ${icon('copy', 17)} ${esc(t('common.copy'))}
      </button>
      <button class="btn btn--ghost" data-download>
        ${icon('download', 17)} ${esc(t('common.download'))}
      </button>
    </div>
  </div>`;
}

function emptyView() {
  return `<div class="stack">
    <div class="field">
      <label class="field__label" for="extra">${esc(
        t('response.extraLabel'),
      )}</label>
      <textarea id="extra" class="textarea" style="min-height:110px"
        placeholder="${esc(t('response.extraPlaceholder'))}"></textarea>
    </div>
    ${button({
      label: t('response.generate'),
      iconName: 'sparkles',
      size: 'lg',
      attrs: 'data-generate',
    })}
  </div>`;
}

export default async function response({ main }) {
  if (!requireNotice()) return;

  main.innerHTML = `<section class="screen">
    ${progress(5)}
    ${backLink('#/documents')}
    ${screenHead({
      eyebrow: t('response.eyebrow'),
      title: t('response.title'),
      subtitle: t('response.subtitle'),
    })}
    <div id="body"></div>
    <div class="actions" id="foot"></div>
  </section>`;

  const body = main.querySelector('#body');
  const foot = main.querySelector('#foot');

  let draft;
  try {
    draft = await loadDraft(state.noticeId);
  } catch (err) {
    body.innerHTML = alert(esc(friendlyError(err)), 'danger');
    return;
  }

  const paint = (d) => {
    if (!d) {
      body.innerHTML = emptyView();
      foot.innerHTML = '';
      body.querySelector('[data-generate]')?.addEventListener('click', async (e) => {
        const btn = e.currentTarget;
        const extra = body.querySelector('#extra')?.value?.trim() || '';
        setBusy(btn, true);
        try {
          const created = await api.generateResponse(state.noticeId, lang(), extra);
          setState({ response: created });
          paint(created);
        } catch (err) {
          setBusy(btn, false);
          showError(err);
        }
      });
      return;
    }

    setState({ response: d });
    body.innerHTML = draftView(d);
    foot.innerHTML = button({
      label: t('response.cta'),
      iconName: 'arrowRight',
      iconAfter: true,
      size: 'lg',
      attrs: 'data-next',
    });

    const textarea = body.querySelector('#draft');

    body.querySelector('[data-regen]')?.addEventListener('click', async (e) => {
      const btn = e.currentTarget;
      setBusy(btn, true);
      try {
        const created = await api.generateResponse(state.noticeId, lang(), '');
        paint(created);
        toast(t('response.saved'), 'success');
      } catch (err) {
        setBusy(btn, false);
        showError(err);
      }
    });

    body
      .querySelector('[data-copy]')
      ?.addEventListener('click', () => copyText(textarea.value));

    body.querySelector('[data-download]')?.addEventListener('click', () => {
      downloadText('noticemate-draft-response.txt', textarea.value);
    });

    foot.querySelector('[data-next]')?.addEventListener('click', async (e) => {
      const btn = e.currentTarget;
      const content = textarea.value.trim();
      if (!content) {
        showError(new Error('empty'));
        return;
      }
      setBusy(btn, true);
      try {
        const saved = await api.saveResponse(state.noticeId, content, true);
        setState({ response: saved });
        navigate('/review');
      } catch (err) {
        setBusy(btn, false);
        showError(err);
      }
    });
  };

  paint(draft);
}
