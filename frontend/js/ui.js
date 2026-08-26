/**
 * Reusable UI building blocks. Everything returns an HTML string (or renders
 * into an element) — small enough to stay readable, consistent enough that
 * every screen looks like it came from the same design system.
 */

import { icon } from './icons.js';
import { t } from './i18n.js';

/** Escape untrusted text before it reaches innerHTML. */
export function esc(value) {
  if (value === null || value === undefined) return '';
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

/* ---- Toast --------------------------------------------------------------- */
let toastTimer = null;
export function toast(message, variant = '') {
  const el = document.getElementById('toast');
  if (!el) return;
  el.className = 'toast is-show' + (variant ? ` toast--${variant}` : '');
  el.textContent = message;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.className = 'toast';
  }, 4200);
}

/* ---- Primitives ---------------------------------------------------------- */
export function button({
  label,
  variant = 'primary',
  iconName = '',
  iconAfter = false,
  attrs = '',
  block = true,
  size = '',
  disabled = false,
}) {
  const classes = [
    'btn',
    `btn--${variant}`,
    block ? 'btn--block' : '',
    size ? `btn--${size}` : '',
  ]
    .filter(Boolean)
    .join(' ');
  const ico = iconName
    ? `<span class="btn__icon">${icon(iconName, 19)}</span>`
    : '';
  return `<button class="${classes}" ${disabled ? 'disabled' : ''} ${attrs}>${
    iconAfter ? `${esc(label)}${ico}` : `${ico}${esc(label)}`
  }</button>`;
}

export function badge(label, variant = 'muted', withDot = false) {
  return `<span class="badge badge--${variant}">${
    withDot ? '<span class="badge__dot" aria-hidden="true"></span>' : ''
  }${esc(label)}</span>`;
}

export function alert(message, variant = 'info', iconName) {
  const map = { info: 'info', warn: 'alert', danger: 'alert', success: 'checkCircle' };
  const name = iconName || map[variant] || 'info';
  return `<div class="alert alert--${variant}" role="${
    variant === 'danger' ? 'alert' : 'note'
  }">
    <span class="alert__icon">${icon(name, 19)}</span>
    <div>${message}</div>
  </div>`;
}

export function screenHead({ eyebrow, title, subtitle }) {
  return `<div class="screen__head">
    ${eyebrow ? `<span class="screen__eyebrow">${esc(eyebrow)}</span>` : ''}
    <h1 class="screen__title">${esc(title)}</h1>
    ${subtitle ? `<p class="screen__subtitle">${esc(subtitle)}</p>` : ''}
  </div>`;
}

export function backLink(href, label = t('common.back')) {
  return `<a class="back-link" href="${esc(href)}">${icon('arrowLeft', 17)}${esc(
    label,
  )}</a>`;
}

/** Workflow progress bar: "Step 3 of 6". */
export function progress(step, total = 6) {
  const pct = Math.round((step / total) * 100);
  return `<div class="progress">
    <div class="progress__bar" role="progressbar" aria-valuenow="${step}"
         aria-valuemin="0" aria-valuemax="${total}"
         aria-label="${esc(t('common.step'))} ${step} ${esc(t('common.of'))} ${total}">
      <div class="progress__fill" style="width:${pct}%"></div>
    </div>
    <div class="progress__meta">
      <span><strong>${esc(t('common.step'))} ${step}</strong> ${esc(
        t('common.of'),
      )} ${total}</span>
      <span>${pct}%</span>
    </div>
  </div>`;
}

export function spinner(label) {
  return `<div class="processing">
    <div class="spinner" role="status" aria-label="${esc(
      label || t('common.loading'),
    )}"></div>
    <p class="muted">${esc(label || t('common.loading'))}</p>
  </div>`;
}

export function emptyState({ iconName = 'inbox', title, body, actionHtml = '' }) {
  return `<div class="state">
    <div class="state__icon">${icon(iconName, 28)}</div>
    <p class="state__title">${esc(title)}</p>
    ${body ? `<p class="mt-sm">${esc(body)}</p>` : ''}
    ${actionHtml ? `<div class="actions">${actionHtml}</div>` : ''}
  </div>`;
}

export function errorState(message, retryAttrs = 'data-retry') {
  return `<div class="state">
    <div class="state__icon">${icon('alert', 28)}</div>
    <p class="state__title">${esc(t('error.title'))}</p>
    <p class="mt-sm">${esc(message)}</p>
    <div class="actions">
      ${button({
        label: t('common.retry'),
        variant: 'secondary',
        iconName: 'refresh',
        attrs: retryAttrs,
      })}
    </div>
  </div>`;
}

export function confidenceMeter(value) {
  const pct = Math.round(Math.max(0, Math.min(1, Number(value) || 0)) * 100);
  return `<div class="meter" title="${esc(t('common.confidence'))}: ${pct}%">
    <span>${esc(t('common.confidence'))}</span>
    <span class="meter__track"><span class="meter__fill" style="width:${pct}%"></span></span>
    <span>${pct}%</span>
  </div>`;
}

/* ---- Helpers ------------------------------------------------------------- */
export function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) return '';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function formatDateTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return String(iso);
  return d.toLocaleString(undefined, {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/** Value or the honest "we couldn't determine this" line. */
export function orUnknown(value) {
  const v = (value ?? '').toString().trim();
  return v ? v : t('common.notFound');
}

export function urgencyBadge(urgency) {
  const map = {
    high: ['danger', t('explain.urgency.high')],
    medium: ['warn', t('explain.urgency.medium')],
    low: ['success', t('explain.urgency.low')],
  };
  const [variant, label] = map[urgency] || map.medium;
  return badge(label, variant, true);
}

/** Human label for where an analysis or draft came from. */
export function sourceLabel(source, kind = 'explain') {
  if (source === 'openai') return t(`${kind}.source.openai`);
  if (source === 'demo-curated') return t('explain.source.curated');
  if (source === 'user-edited') return t('response.source.user');
  return t(`${kind}.source.fallback`);
}

export function sourceVariant(source) {
  return source === 'openai' ? 'brand' : 'muted';
}

/** Copy text with a graceful fallback for non-secure contexts. */
export async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    toast(t('common.copied'), 'success');
  } catch {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      toast(t('common.copied'), 'success');
    } catch {
      toast(t('error.generic'), 'danger');
    }
    ta.remove();
  }
}

export function downloadText(filename, text) {
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** Toggle a button into a busy state without losing its label. */
export function setBusy(btn, busy, busyLabel) {
  if (!btn) return;
  if (busy) {
    btn.dataset.label = btn.innerHTML;
    btn.disabled = true;
    btn.setAttribute('aria-busy', 'true');
    btn.innerHTML = `<span class="btn__icon">${icon('refresh', 18)}</span>${esc(
      busyLabel || t('common.loading'),
    )}`;
  } else {
    btn.disabled = false;
    btn.removeAttribute('aria-busy');
    if (btn.dataset.label) btn.innerHTML = btn.dataset.label;
  }
}
