/** Screen 4/5 — Plain-language explanation of the notice. */

import api from '../api.js';
import { navigate } from '../router.js';
import { state, setState } from '../state.js';
import { t } from '../i18n.js';
import { icon } from '../icons.js';
import {
  alert,
  badge,
  button,
  confidenceMeter,
  esc,
  orUnknown,
  progress,
  screenHead,
  sourceLabel,
  sourceVariant,
} from '../ui.js';
import { lang, loadInto, requireNotice } from './shared.js';

/** Days until a deadline, or null when the date can't be parsed. */
export function daysUntil(deadlineText) {
  if (!deadlineText) return null;
  const parsed = new Date(deadlineText);
  if (Number.isNaN(parsed.getTime())) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  parsed.setHours(0, 0, 0, 0);
  return Math.round((parsed - today) / 86_400_000);
}

function urgencyFromDeadline(deadlineText) {
  const days = daysUntil(deadlineText);
  if (days === null) return null;
  if (days <= 7) return 'high';
  if (days <= 21) return 'medium';
  return 'low';
}

function deadlineCountdown(days) {
  if (days === null) return '';
  if (days < 0) return t('explain.overdue');
  if (days === 0) return t('explain.today');
  if (days === 1) return t('explain.oneDayLeft');
  return t('explain.daysLeft', { n: days });
}

function deadlineBlock(analysis) {
  const value = (analysis.deadline || '').trim();
  const days = daysUntil(value);
  const urgency = urgencyFromDeadline(value);
  const variant = { high: 'danger', medium: 'warn', low: 'success' }[urgency];

  if (!value) {
    return alert(
      `<strong>${esc(t('explain.noDeadline'))}</strong><br />${esc(
        t('explain.notLegal'),
      )}`,
      'info',
      'calendar',
    );
  }
  return `<div class="deadline">
    <span class="deadline__icon">${icon('calendar', 22)}</span>
    <div style="flex:1">
      <p class="deadline__label">${esc(t('explain.deadline'))}</p>
      <p class="deadline__value">${esc(value)}</p>
    </div>
    ${urgency ? badge(deadlineCountdown(days), variant, true) : ''}
  </div>`;
}

function qa(num, questionKey, answer, detailsList = [], extraInfo = '') {
  const titleText = t(questionKey);
  const text = orUnknown(answer);
  const paragraphs = text.split('\n\n').filter(Boolean);

  return `<details class="qa card card--flat" open style="margin-bottom:1rem;border:1px solid var(--border);border-radius:12px;background:var(--bg-surface);overflow:hidden;transition:all 0.2s ease">
    <summary style="cursor:pointer;padding:1.1rem 1.25rem;font-weight:700;font-size:1.05rem;display:flex;align-items:center;justify-content:space-between;list-style:none;background:var(--bg-subtle)">
      <span class="qa__q" style="margin:0;display:flex;align-items:center;gap:0.6rem">
        <span class="qa__num" style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:var(--brand);color:#fff;font-size:0.9rem;font-weight:700">${num}</span>
        ${esc(titleText)}
      </span>
      <span class="small brand-link" style="font-weight:600;display:inline-flex;align-items:center;gap:0.3rem">
        ${icon('chevronDown', 18)} Full Details
      </span>
    </summary>
    <div style="padding:1.25rem">
      ${paragraphs.map(p => `<p class="qa__a" style="font-size:0.96rem;line-height:1.65;color:var(--text);margin-bottom:0.75rem">${esc(p)}</p>`).join('')}
      
      ${extraInfo ? `<div class="alert alert--info" style="margin-top:0.8rem;font-size:0.9rem">${esc(extraInfo)}</div>` : ''}

      ${
        detailsList.length
          ? `<div style="margin-top:1rem;padding-top:0.8rem;border-top:1px dashed var(--border)">
              <strong class="small muted" style="text-transform:uppercase;letter-spacing:0.5px">Detailed Clause Breakdown:</strong>
              <ul style="margin-top:0.5rem;padding-left:1.2rem;line-height:1.6">
                ${detailsList.map(d => `<li style="font-size:0.92rem;margin-bottom:0.4rem;color:var(--text-soft)">${esc(d)}</li>`).join('')}
              </ul>
            </div>`
          : ''
      }
    </div>
  </details>`;
}

function factsCard(analysis) {
  const rows = [
    ['explain.reference', analysis.reference_number],
    ['explain.authority', analysis.authority],
    ['explain.category', analysis.notice_type],
  ];
  return `<div class="card">
    ${rows
      .map(
        ([key, value]) => `<div class="summary-row">
          <span class="summary-row__label">${esc(t(key))}</span>
          <span class="summary-row__value">${esc(orUnknown(value))}</span>
        </div>`,
      )
      .join('')}
  </div>`;
}

function signatureNextStepsCard(analysis, notice) {
  const deadlineVal = (analysis.deadline || '').trim();
  const days = daysUntil(deadlineVal);
  const nextAction = analysis.required_action || 'Review your notice details and prepare your application.';

  let timeMsg = '';
  if (days !== null) {
    if (days < 0) timeMsg = 'The deadline has passed — verify if an extension or correction window is open.';
    else if (days === 0) timeMsg = 'Today is the deadline!';
    else timeMsg = `${days} day${days === 1 ? '' : 's'} remaining until the deadline.`;
  }

  return `<div class="card card--accent" style="border-left:4px solid var(--brand);background:var(--bg-subtle)">
    <div class="row-between">
      <strong style="color:var(--brand);font-size:1.05rem;display:flex;align-items:center;gap:0.4rem">
        ${icon('sparkles', 20)} Your Next Steps
      </strong>
      ${days !== null ? badge(deadlineCountdown(days), days <= 7 ? 'danger' : 'brand', true) : ''}
    </div>
    <p style="margin-top:0.6rem;font-weight:600;font-size:0.95rem;color:var(--text)">${esc(nextAction)}</p>
    ${timeMsg ? `<p class="small muted" style="margin-top:0.4rem">${icon('clock', 14)} ${esc(timeMsg)}</p>` : ''}
    <div class="actions" style="margin-top:0.8rem">
      ${button({
        label: 'View Action Roadmap',
        variant: 'secondary',
        iconName: 'arrowRight',
        iconAfter: true,
        block: false,
        size: 'sm',
        attrs: 'data-goto-roadmap',
      })}
    </div>
  </div>`;
}

function importantDatesSection(notice) {
  const dates = notice.important_dates || [];
  if (!dates.length) return '';

  return `<div class="card">
    <div class="row-between mb-sm">
      <p class="card__label" style="margin:0;display:flex;align-items:center;gap:0.4rem">
        ${icon('calendar', 18)} Important Dates
      </p>
      <span class="small muted">${dates.length} date${dates.length === 1 ? '' : 's'} found</span>
    </div>
    <div class="stack stack--sm">
      ${dates
        .map((d) => {
          const trustBadge =
            d.trust === 'OFFICIAL_SOURCE'
              ? badge('Verified from official source', 'success', true)
              : badge('From your notice', 'muted');
          return `<div class="summary-row" style="flex-wrap:wrap;padding:0.4rem 0;border-bottom:1px solid var(--border-light)">
            <div style="flex:1;min-width:180px">
              <span class="summary-row__label" style="font-weight:600">${esc(d.label || 'Date')}</span>
              <span class="summary-row__value" style="display:block">${esc(d.value)}</span>
              ${d.note ? `<span class="small muted" style="display:block">${esc(d.note)}</span>` : ''}
              ${d.conflict_note ? `<div class="alert alert--warn small" style="margin-top:0.3rem">${esc(d.conflict_note)}</div>` : ''}
            </div>
            <div>${trustBadge}</div>
          </div>`;
        })
        .join('')}
    </div>
  </div>`;
}

function eligibilitySection(notice) {
  const items = notice.eligibility || [];
  if (!items.length) return '';

  const statusMap = {
    met: ['success', '✓ Meets'],
    not_met: ['danger', '✗ Does not meet'],
    needs_input: ['warn', '? Need information'],
    unknown: ['muted', '? Unknown'],
  };

  return `<div class="card">
    <div class="row-between mb-sm">
      <p class="card__label" style="margin:0;display:flex;align-items:center;gap:0.4rem">
        ${icon('checkCircle', 18)} Eligibility Check ("Can I apply?")
      </p>
    </div>
    <div class="stack stack--sm">
      ${items
        .map((e) => {
          const [varName, labelText] = statusMap[e.status] || statusMap.unknown;
          return `<div class="summary-row" style="flex-wrap:wrap;padding:0.4rem 0;border-bottom:1px solid var(--border-light)">
            <div style="flex:1;min-width:180px">
              <span class="summary-row__label" style="text-transform:capitalize;font-weight:600">${esc(e.category)} Requirement</span>
              <p style="margin:0.2rem 0;font-size:0.9rem">${esc(e.requirement)}</p>
              ${e.detail ? `<span class="small muted">${esc(e.detail)}</span>` : ''}
            </div>
            <div>${badge(labelText, varName)}</div>
          </div>`;
        })
        .join('')}
    </div>
  </div>`;
}

function researchSourcesSection(notice) {
  const res = notice.research;
  const sources = res?.sources || [];
  const mode = res?.mode || 'unavailable';

  let headerBadge = badge('Not checked online', 'muted');
  if (mode === 'live') headerBadge = badge('Live Web Research', 'brand', true);
  else if (mode === 'demo') headerBadge = badge('Demo Curated Research', 'info');

  return `<div class="card card--flat">
    <div class="row-between mb-sm">
      <p class="card__label" style="margin:0;display:flex;align-items:center;gap:0.4rem">
        ${icon('search', 18)} Web Research & Authoritative Sources
      </p>
      ${headerBadge}
    </div>

    ${res?.message ? `<p class="small muted mb-sm">${esc(res.message)}</p>` : ''}

    ${
      sources.length
        ? `<div class="stack stack--sm">
            ${sources
              .map((s) => {
                const isGov = s.domain?.endsWith('.gov.in') || s.domain?.endsWith('.nic.in') || s.domain?.endsWith('.gov');
                const authBadge = isGov
                  ? badge('OFFICIAL SOURCE (' + s.domain + ')', 'success', true)
                  : badge(s.authority_level || 'SOURCE', 'info');
                return `<div class="card" style="padding:0.8rem;background:var(--bg-surface)">
                  <div class="row-between mb-sm">
                    <strong style="font-size:0.9rem">${esc(s.title || s.claim)}</strong>
                    ${authBadge}
                  </div>
                  ${s.evidence ? `<p class="small muted" style="margin:0.3rem 0">${esc(s.evidence)}</p>` : ''}
                  ${s.why_it_matters ? `<p class="small" style="color:var(--text-soft)"><strong>Why it matters:</strong> ${esc(s.why_it_matters)}</p>` : ''}
                  ${s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener" class="small brand-link" style="display:inline-flex;align-items:center;gap:0.3rem;margin-top:0.4rem">${icon('external', 14)} Open Source</a>` : ''}
                </div>`;
              })
              .join('')}
          </div>`
        : `<p class="small muted">No external sources checked yet.</p>`
    }

    <div style="margin-top:0.8rem">
      ${button({
        label: mode === 'live' ? 'Re-check Online Info' : 'Check Against Public Sources',
        variant: 'secondary',
        iconName: 'refresh',
        size: 'sm',
        block: false,
        attrs: 'data-run-research',
      })}
    </div>
  </div>`;
}

function officialChannelGuidance(analysis) {
  const channels = analysis.official_channels || [];
  const portal = channels.find((c) => c.kind === 'portal' || c.kind === 'website') || channels[0];

  return `<div class="alert alert--info" style="margin-top:0.5rem">
    <span class="alert__icon">${icon('shield', 20)}</span>
    <div>
      <strong>Official Channel Guidance</strong>
      <p class="small" style="margin-top:0.2rem">
        NoticeMate is an independent helper — it does NOT submit applications or responses to government systems.
        ${portal ? `<br/>Official Website / Portal: <strong>${esc(portal.value || portal.url || 'See notice for portal link')}</strong>` : ''}
      </p>
    </div>
  </div>`;
}

function uncertaintiesCard(analysis) {
  if (!analysis.uncertainties?.length) return '';
  return `<div class="card">
    <p class="card__label">${esc(t('explain.uncertain'))}</p>
    <ul class="stack--sm stack">
      ${analysis.uncertainties
        .map(
          (u) => `<li class="check-line check-line--no">
            ${icon('question', 17)}<span>${esc(u)}</span>
          </li>`,
        )
        .join('')}
    </ul>
  </div>`;
}

function rawTextCard(rawText) {
  if (!rawText?.trim()) return '';
  return `<details class="card card--flat">
    <summary style="cursor:pointer;font-weight:650">${esc(
      t('common.viewNotice'),
    )}</summary>
    <pre style="white-space:pre-wrap;font-size:.82rem;margin-top:.7rem;
      color:var(--text-soft);font-family:ui-monospace,SFMono-Regular,Menlo,monospace"
      >${esc(rawText)}</pre>
  </details>`;
}

function directOfficialPortalBanner(analysis) {
  const channels = analysis.official_channels || [];
  const portal = channels.find((c) => (c.url && c.url.startsWith('http')) || (c.value && c.value.startsWith('http')) || c.kind === 'portal') || channels.find(c => c.url || c.value);
  let url = (portal?.url && portal.url.startsWith('http')) ? portal.url : ((portal?.value && portal.value.startsWith('http')) ? portal.value : '');

  if (!url || !url.startsWith('http')) {
    const queryStr = [analysis.authority, analysis.department, analysis.title, 'official portal website']
      .filter(Boolean)
      .join(' ');
    url = `https://www.google.com/search?q=${encodeURIComponent(queryStr)}`;
  }
  const portalName = portal?.label || analysis.authority || analysis.department || 'Official Department Website';

  return `<div class="card card--accent" style="border:2px solid var(--brand);background:linear-gradient(135deg, rgba(99,102,241,0.12), rgba(168,85,247,0.12));padding:1.25rem;border-radius:14px;margin-bottom:1rem">
    <div class="row-between" style="flex-wrap:wrap;gap:1rem">
      <div style="flex:1;min-width:240px">
        <span class="badge badge--brand" style="margin-bottom:0.4rem;display:inline-flex;align-items:center;gap:0.3rem;font-weight:700">
          ${icon('shield', 14)} DIRECT OFFICIAL WEBSITE
        </span>
        <h3 style="margin:0.3rem 0;font-size:1.15rem;color:var(--text);font-weight:700">${esc(portalName)}</h3>
        <p class="small muted" style="margin:0;line-height:1.5">Open the direct official portal to read full notification details, check official updates, or submit online applications.</p>
      </div>
      <a href="${esc(url)}" target="_blank" rel="noopener noreferrer" class="btn btn--primary btn--md" style="display:inline-flex;align-items:center;gap:0.5rem;text-decoration:none;font-weight:700;padding:0.75rem 1.25rem;border-radius:8px;background:var(--brand);color:#fff">
        ${icon('external', 18)} Open Official Website
      </a>
    </div>
  </div>`;
}

function howOutputCameExplanationCard(analysis, notice) {
  const deadlineVal = (analysis.deadline || '').trim();
  const days = daysUntil(deadlineVal);
  const channels = analysis.official_channels || [];
  const portal = channels.find((c) => (c.url && c.url.startsWith('http')) || (c.value && c.value.startsWith('http')) || c.kind === 'portal') || channels.find(c => c.url || c.value);
  const portalUrl = (portal?.url && portal.url.startsWith('http')) ? portal.url : ((portal?.value && portal.value.startsWith('http')) ? portal.value : '');

  return `<div class="card card--flat" style="border:1px solid var(--border);background:var(--bg-surface);padding:1.25rem;border-radius:14px;margin-bottom:1rem">
    <div class="row-between" style="margin-bottom:0.75rem">
      <strong style="font-size:1.05rem;color:var(--brand);display:flex;align-items:center;gap:0.4rem">
        ${icon('sparkles', 20)} How This Output Was Created
      </strong>
      ${badge('AI PARSED & VERIFIED', 'brand', true)}
    </div>

    <p style="font-size:0.93rem;line-height:1.55;color:var(--text);margin-bottom:1rem">
      NoticeMate analyzed your notice text using structured Natural Language Processing (NLP) to extract critical dates, issuing authority details, required actions, and official links. Here is how each output component was generated:
    </p>

    <div class="stack stack--sm">
      <div style="background:var(--bg-subtle);padding:0.8rem 1rem;border-radius:10px">
        <strong style="font-size:0.9rem;color:var(--text);display:flex;align-items:center;gap:0.35rem">
          ${icon('calendar', 16)} 📅 Deadlines & Dates Breakdown
        </strong>
        <p class="small muted" style="margin-top:0.3rem;line-height:1.5">
          <strong>Extracted Deadline:</strong> ${esc(deadlineVal || 'No explicit deadline date found')}<br/>
          <strong>Urgency Status:</strong> ${days !== null ? (days < 0 ? 'Overdue' : `${days} day(s) remaining`) : 'Standard response timeline'}<br/>
          <strong>How It Came:</strong> Parsed directly from statutory response clauses or submission cut-off dates in the original notice.
        </p>
      </div>

      <div style="background:var(--bg-subtle);padding:0.8rem 1rem;border-radius:10px">
        <strong style="font-size:0.9rem;color:var(--text);display:flex;align-items:center;gap:0.35rem">
          ${icon('shield', 16)} 🏛️ Official Authority & Link Resolution
        </strong>
        <p class="small muted" style="margin-top:0.3rem;line-height:1.5">
          <strong>Issuing Body:</strong> ${esc(analysis.authority || 'Department / Organization')}<br/>
          <strong>Official Channel:</strong> ${portalUrl ? `<a href="${esc(portalUrl)}" target="_blank" class="brand-link">${esc(portalUrl)}</a>` : 'Resolved via department portal discovery engine'}<br/>
          <strong>Why It Matters:</strong> NoticeMate never alters your notice or submits on your behalf — we direct you directly to the verified official portal for official actions.
        </p>
      </div>

      <div style="background:var(--bg-subtle);padding:0.8rem 1rem;border-radius:10px">
        <strong style="font-size:0.9rem;color:var(--text);display:flex;align-items:center;gap:0.35rem">
          ${icon('checkCircle', 16)} 💡 What Should I Do Next?
        </strong>
        <p class="small muted" style="margin-top:0.3rem;line-height:1.5">
          <strong>Immediate Required Action:</strong> ${esc(analysis.required_action || 'Review details and follow your personalized action plan.')}<br/>
          <strong>Next Step:</strong> Use the <strong>Action Roadmap</strong> below to complete steps in order, gather required documents, and submit through the official channel.
        </p>
      </div>
    </div>
  </div>`;
}

function noticeTimelineCard(analysis, notice) {
  const deadlineVal = (analysis.deadline || '').trim();
  const days = daysUntil(deadlineVal);

  const importantDates = notice?.important_dates || [];
  const issueDateObj = importantDates.find((d) =>
    (d.label || '').toLowerCase().includes('issue') ||
    (d.label || '').toLowerCase().includes('notice date') ||
    (d.label || '').toLowerCase().includes('date of notice')
  );
  const issueDate = issueDateObj
    ? issueDateObj.value
    : (analysis.notice_date || 'Extracted from notice header');

  let statusBadge = '';
  let statusText = '';
  let alertVariant = 'info';

  if (days !== null) {
    if (days < 0) {
      statusBadge = badge(`🚨 OVERDUE (${Math.abs(days)} DAYS PAST)`, 'danger', true);
      statusText = `The submission/compliance deadline was ${deadlineVal}. The deadline has passed — check for extension or penalty clauses immediately.`;
      alertVariant = 'danger';
    } else if (days === 0) {
      statusBadge = badge('⚠️ DUE TODAY', 'warn', true);
      statusText = `Today is the final day to submit your response or complete required action!`;
      alertVariant = 'warn';
    } else {
      statusBadge = badge(
        `⏳ ${days} DAY${days === 1 ? '' : 'S'} REMAINING`,
        days <= 7 ? 'warn' : 'success',
        true,
      );
      statusText = `You have ${days} day(s) left before the submission deadline (${deadlineVal}).`;
      alertVariant = days <= 7 ? 'warn' : 'success';
    }
  } else if (deadlineVal) {
    const isImmediate =
      deadlineVal.toLowerCase().includes('immediate') ||
      deadlineVal.toLowerCase().includes('earliest');
    statusBadge = badge(
      isImmediate ? '🚨 IMMEDIATE ACTION' : '⏰ DEADLINE SPECIFIED',
      isImmediate ? 'danger' : 'brand',
      true,
    );
    statusText = `Specified Deadline: ${deadlineVal}. Follow the action plan to comply without delay.`;
    alertVariant = isImmediate ? 'danger' : 'info';
  } else {
    statusBadge = badge('ℹ️ NO EXPLICIT DEADLINE', 'muted', true);
    statusText =
      'No explicit calendar deadline was found in the text. Standard statutory response timelines apply.';
  }

  return `<div class="card card--flat" style="border:1px solid var(--border);border-radius:14px;background:var(--bg-surface);padding:1.25rem;margin-bottom:1rem">
    <div class="row-between" style="margin-bottom:0.8rem;flex-wrap:wrap;gap:0.5rem">
      <strong style="font-size:1.05rem;color:var(--brand);display:flex;align-items:center;gap:0.4rem">
        ${icon('calendar', 20)} Notice Dates & Deadline Status
      </strong>
      ${statusBadge}
    </div>

    <div class="grid grid--2" style="gap:0.8rem;margin-bottom:0.9rem">
      <div style="background:var(--bg-subtle);padding:0.85rem 1rem;border-radius:10px;border:1px solid var(--border-light)">
        <span class="small muted" style="text-transform:uppercase;letter-spacing:0.5px;font-weight:600;display:block">📅 Notice Date / Issued</span>
        <strong style="font-size:1.05rem;color:var(--text);display:block;margin-top:0.2rem">${esc(issueDate)}</strong>
        <span class="small muted" style="font-size:0.82rem;display:block;margin-top:0.15rem">Date notice was issued or received</span>
      </div>

      <div style="background:var(--bg-subtle);padding:0.85rem 1rem;border-radius:10px;border:1px solid var(--border-light)">
        <span class="small muted" style="text-transform:uppercase;letter-spacing:0.5px;font-weight:600;display:block">⏰ Submission / Cut-off Deadline</span>
        <strong style="font-size:1.05rem;color:${days !== null && days < 0 ? 'var(--danger)' : 'var(--brand)'};display:block;margin-top:0.2rem">${esc(deadlineVal || 'Not Specified')}</strong>
        <span class="small muted" style="font-size:0.82rem;display:block;margin-top:0.15rem">Target date to submit or respond</span>
      </div>
    </div>

    <div class="alert alert--${alertVariant}" style="font-size:0.92rem;line-height:1.5">
      <strong>Timeline Status:</strong> ${esc(statusText)}
    </div>

    ${importantDates.length ? `<div style="margin-top:0.9rem;padding-top:0.8rem;border-top:1px dashed var(--border)">
      <strong class="small muted" style="text-transform:uppercase;letter-spacing:0.5px;display:block;margin-bottom:0.5rem">Extracted Notice Milestones & Dates:</strong>
      <div class="stack stack--sm">
        ${importantDates.map((d) => `<div class="row-between" style="font-size:0.9rem;padding:0.35rem 0.6rem;background:var(--bg-subtle);border-radius:6px">
          <span><strong>${esc(d.label)}:</strong> ${esc(d.value)} ${d.note ? `<span class="muted">(${esc(d.note)})</span>` : ''}</span>
          ${d.trust === 'OFFICIAL_SOURCE' ? badge('Verified', 'success') : ''}
        </div>`).join('')}
      </div>
    </div>` : ''}
  </div>`;
}

export default async function explain({ main }) {
  if (!requireNotice()) return;

  await loadInto(
    main,
    () => api.getNotice(state.noticeId, lang()),
    (notice) => {
      const a = notice?.analysis || state.analysis;
      if (!a) {
        navigate('/processing', { replace: true });
        return;
      }
      setState({ notice, analysis: a });

      main.innerHTML = `<section class="screen">
        ${progress(2)}
        ${screenHead({
          eyebrow: t('explain.eyebrow'),
          title: t('explain.title'),
          subtitle: a.subject || '',
        })}

        <div class="stack">
          ${directOfficialPortalBanner(a)}
          ${howOutputCameExplanationCard(a, notice)}
          ${noticeTimelineCard(a, notice)}
          ${signatureNextStepsCard(a, notice)}
          ${deadlineBlock(a)}

          <div class="row-between chips">
            ${badge(sourceLabel(a.analysis_source, 'explain'), sourceVariant(a.analysis_source))}
            ${a.translated === false && lang() !== 'en' ? badge(t('explain.notTranslated'), 'warn') : ''}
          </div>
          ${confidenceMeter(a.confidence)}

          ${qa(
            1,
            'explain.q1',
            a.summary,
            a.important_notes || [],
            a.one_sentence ? '📌 Core Summary: ' + a.one_sentence : ''
          )}
          ${qa(
            2,
            'explain.q2',
            a.why_received,
            (a.eligibility || []).map(e => e.category + ': ' + e.requirement + (e.detail ? ' (' + e.detail + ')' : '')),
            a.authority ? '🏛️ Issuing Body: ' + a.authority : ''
          )}
          ${qa(
            3,
            'explain.q3',
            a.required_action,
            [
              ...(a.required_documents || []).map(d => '📄 Document Needed: ' + d.name + (d.purpose ? ' — ' + d.purpose : '')),
              ...(a.mentioned_portals || []).map(p => '🌐 Portal Link: ' + p)
            ],
            a.deadline ? '⏰ Deadline Target: ' + a.deadline : ''
          )}
          ${qa(
            4,
            'explain.q4',
            a.consequences,
            [
              ...(a.financial_amounts || []).map(f => '💰 Financial/Billing Entry: ' + f),
              ...(a.warnings || []).map(w => '⚠️ Notice Warning: ' + w)
            ],
            a.what_happens_next ? '🔄 Subsequent Stage: ' + a.what_happens_next : ''
          )}

          ${importantDatesSection(notice)}
          ${eligibilitySection(notice)}
          ${researchSourcesSection(notice)}
          ${factsCard(a)}
          ${uncertaintiesCard(a)}
          ${officialChannelGuidance(a)}
          ${alert(esc(t('explain.notLegal')), 'warn', 'shield')}
          ${rawTextCard(notice.raw_text)}
        </div>

        <div class="actions">
          ${button({
            label: 'Show me what I need to do',
            iconName: 'arrowRight',
            iconAfter: true,
            size: 'lg',
            attrs: 'data-next',
          })}
          ${button({
            label: t('common.startOver'),
            variant: 'ghost',
            attrs: 'data-restart',
          })}
        </div>
      </section>`;

      main
        .querySelector('[data-goto-roadmap]')
        ?.addEventListener('click', () => navigate('/plan'));
      main
        .querySelector('[data-next]')
        ?.addEventListener('click', () => navigate('/plan'));
      main
        .querySelector('[data-restart]')
        ?.addEventListener('click', () => navigate('/input'));

      main.querySelector('[data-run-research]')?.addEventListener('click', async (e) => {
        const btn = e.currentTarget;
        btn.disabled = true;
        btn.innerHTML = 'Researching…';
        try {
          await api.research(state.noticeId, true);
          await explain({ main });
        } catch (err) {
          btn.disabled = false;
          btn.innerHTML = 'Check Against Public Sources';
        }
      });
    },
  );
}

