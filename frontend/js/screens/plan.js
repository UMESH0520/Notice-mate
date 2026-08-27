/**
 * Screen 6 — Dynamic Personalized Roadmap Engine (§17, §18).
 * Answers: "I have this notice in front of me. What exactly should I do from now until I finish this process?"
 */

import api from '../api.js';
import { navigate } from '../router.js';
import { state, setState } from '../state.js';
import { t } from '../i18n.js';
import { icon } from '../icons.js';
import {
  alert,
  badge,
  button,
  esc,
  progress,
  screenHead,
  backLink,
} from '../ui.js';
import { lang, loadInto, requireNotice, showError } from './shared.js';

const STATUS_VARIANT = {
  completed: 'success',
  in_progress: 'brand',
  blocked: 'warn',
  needs_verification: 'warn',
  not_applicable: 'muted',
  not_started: 'muted',
};

const PRIORITY_VARIANT = {
  urgent: 'danger',
  high: 'warn',
  normal: 'muted',
  low: 'muted',
};

function heroNextStepCard(roadmap) {
  const nextStep = roadmap.next_step;
  if (!nextStep) {
    return `<div class="card card--accent" style="border-left:4px solid var(--success);background:var(--bg-subtle)">
      <div class="row-between mb-sm">
        <strong style="color:var(--success);font-size:1.1rem;display:flex;align-items:center;gap:0.4rem">
          ${icon('checkCircle', 22)} All NoticeMate Preparation Complete!
        </strong>
        ${badge('READY FOR OFFICIAL CHANNEL', 'success', true)}
      </div>
      <p style="font-size:0.95rem;margin-top:0.4rem;color:var(--text)">
        Everything NoticeMate can help with is done. The final step is yours to complete on the official channel.
      </p>
      <div class="actions" style="margin-top:0.8rem">
        ${button({
          label: 'Proceed to Official Channel Guidance',
          variant: 'primary',
          iconName: 'arrowRight',
          iconAfter: true,
          size: 'md',
          block: false,
          attrs: 'data-goto-docs',
        })}
      </div>
    </div>`;
  }

  const isBlocked = nextStep.status === 'blocked';

  return `<div class="card card--accent" style="border-left:4px solid ${isBlocked ? 'var(--warn)' : 'var(--brand)'};background:var(--bg-subtle)">
    <div class="row-between mb-sm">
      <span style="font-size:0.8rem;letter-spacing:0.05em;text-transform:uppercase;font-weight:700;color:var(--brand)">
        YOUR NEXT STEP
      </span>
      <div style="display:flex;gap:0.4rem">
        ${badge(nextStep.priority.toUpperCase(), PRIORITY_VARIANT[nextStep.priority] || 'muted')}
        ${badge(nextStep.status.replace('_', ' ').toUpperCase(), STATUS_VARIANT[nextStep.status] || 'muted', true)}
      </div>
    </div>

    <h2 style="font-size:1.15rem;margin:0.2rem 0;color:var(--text)">${esc(nextStep.title)}</h2>
    <p style="font-size:0.92rem;color:var(--text-soft);margin-top:0.3rem">${esc(nextStep.short_description || nextStep.detailed_description)}</p>

    ${
      isBlocked && nextStep.blocker_reason
        ? `<div class="alert alert--warn small mt-sm">${icon('alert', 16)} <strong>Blocked:</strong> ${esc(nextStep.blocker_reason)}</div>`
        : ''
    }

    <div class="summary-row" style="margin-top:0.8rem;padding-top:0.6rem;border-top:1px dashed var(--border-light)">
      <span class="small muted">${icon('clock', 14)} Effort: ${esc(nextStep.estimated_effort || '10 mins')}</span>
      ${nextStep.deadline ? `<span class="small muted">${icon('calendar', 14)} Deadline: ${esc(nextStep.deadline)}</span>` : ''}
    </div>

    <div class="actions" style="margin-top:0.8rem">
      ${button({
        label: isBlocked ? 'Unblock This Step' : 'Mark Step Complete',
        variant: isBlocked ? 'secondary' : 'primary',
        iconName: isBlocked ? 'refresh' : 'check',
        size: 'md',
        block: false,
        attrs: `data-hero-toggle="${esc(nextStep.key)}" data-hero-state="${nextStep.status === 'completed' ? 'not_started' : 'completed'}"`,
      })}
      ${button({
        label: 'Help With This Step',
        variant: 'ghost',
        iconName: 'question',
        size: 'md',
        block: false,
        attrs: `data-step-help="${esc(nextStep.key)}"`,
      })}
    </div>
  </div>`;
}

function doThisNowSection(roadmap) {
  return `<div class="stack stack--sm mt-sm">
    <div class="card card--flat" style="padding:0.9rem">
      <div class="row-between mb-xs">
        <strong style="font-size:0.88rem;color:var(--brand);display:flex;align-items:center;gap:0.3rem">
          ${icon('sparkles', 16)} DO THIS NOW
        </strong>
      </div>
      <p style="margin:0;font-size:0.92rem;font-weight:600">${esc(roadmap.do_this_now || 'Focus on your next required step.')}</p>
      ${roadmap.do_this_next ? `<p class="small muted mt-xs"><strong>NEXT:</strong> ${esc(roadmap.do_this_next)}</p>` : ''}
    </div>

    ${
      roadmap.parallel_info
        ? `<div class="alert alert--info small">
            <span class="alert__icon">${icon('info', 16)}</span>
            <div><strong>Parallel Efficiency:</strong> ${esc(roadmap.parallel_info)}</div>
          </div>`
        : ''
    }

    ${
      roadmap.dont_forget?.length
        ? `<details class="card card--flat" style="padding:0.7rem">
            <summary style="cursor:pointer;font-weight:650;font-size:0.88rem;color:var(--warn)">
              ${icon('alert', 16)} DON'T FORGET (${roadmap.dont_forget.length} reminders)
            </summary>
            <ul style="margin:0.5rem 0 0 1.2rem;font-size:0.88rem;color:var(--text-soft)">
              ${roadmap.dont_forget.map((item) => `<li>${esc(item)}</li>`).join('')}
            </ul>
          </details>`
        : ''
    }
  </div>`;
}

function roadmapProgressBar(completed, total) {
  const pct = total ? Math.round((completed / total) * 100) : 0;
  return `<div class="card" style="padding:0.8rem">
    <div class="row-between">
      <p class="card__label" style="margin:0">YOUR ROADMAP PROGRESS</p>
      <strong>${completed} of ${total} steps (${pct}%)</strong>
    </div>
    <div class="progress__bar mt-sm" role="progressbar" aria-valuenow="${completed}"
         aria-valuemin="0" aria-valuemax="${total}">
      <div class="progress__fill" style="width:${pct}%"></div>
    </div>
  </div>`;
}

function renderStepItem(step) {
  const isDone = step.status === 'completed';
  const isBlocked = step.status === 'blocked';

  return `<li class="step-item ${isBlocked ? 'step-item--blocked' : ''}" data-state="${esc(step.status)}" data-id="${esc(step.key)}" style="margin-bottom:0.9rem">
    <span class="step-item__marker" style="background:${isDone ? 'var(--success)' : isBlocked ? 'var(--warn)' : 'var(--brand)'};color:#fff">
      ${isDone ? icon('check', 15, 2.6) : isBlocked ? icon('alert', 15) : step.order}
    </span>
    <div class="step-item__body">
      <div class="row-between">
        <strong class="step-item__title" style="font-size:0.95rem">${esc(step.title)}</strong>
        <div style="display:flex;gap:0.3rem">
          ${step.can_do_in_parallel ? badge('PARALLEL', 'info') : ''}
          ${badge(step.status.replace('_', ' ').toUpperCase(), STATUS_VARIANT[step.status] || 'muted', isDone)}
        </div>
      </div>

      <p class="step-item__desc" style="margin-top:0.3rem">${esc(step.short_description || step.detailed_description)}</p>

      ${
        isBlocked && step.blocker_reason
          ? `<div class="alert alert--warn small" style="margin-top:0.4rem;padding:0.4rem 0.6rem">${icon('alert', 14)} ${esc(step.blocker_reason)}</div>`
          : ''
      }

      <div class="summary-row" style="margin-top:0.4rem;font-size:0.8rem">
        <span class="muted">${icon('clock', 13)} ${esc(step.estimated_effort || '10 mins')}</span>
        ${step.deadline ? `<span class="muted">${icon('calendar', 13)} ${esc(step.deadline)}</span>` : ''}
      </div>

      <div class="doc__actions" style="margin-top:0.6rem;display:flex;gap:0.4rem;flex-wrap:wrap">
        <button class="btn ${isDone ? 'btn--ghost' : 'btn--secondary'} btn--sm"
          data-toggle="${esc(step.key)}"
          data-next-state="${isDone ? 'not_started' : 'completed'}">
          ${icon(isDone ? 'refresh' : 'check', 15)}
          ${esc(isDone ? 'Mark Undone' : 'Mark Done')}
        </button>
        <button class="btn btn--ghost btn--sm"
          data-step-detail="${esc(step.key)}">
          ${icon('info', 15)}
          Detail (6-Questions)
        </button>
        <button class="btn btn--ghost btn--sm"
          data-step-help="${esc(step.key)}">
          ${icon('question', 15)}
          Help Me With This
        </button>
      </div>
    </div>
  </li>`;
}

function renderStepDetailModal(step) {
  return `<div id="step-modal" class="modal-overlay" style="position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:1000;display:flex;align-items:center;justify-content:center;padding:1rem">
    <div class="card" style="max-width:540px;width:100%;max-height:85vh;overflow-y:auto;background:var(--bg-surface)">
      <div class="row-between mb-sm">
        <strong style="font-size:1.1rem">${esc(step.title)}</strong>
        <button class="btn btn--ghost btn--sm" id="close-modal">✕</button>
      </div>
      <p class="small muted">${esc(step.detailed_description || step.short_description)}</p>

      <div class="stack stack--sm mt-sm">
        <div class="card card--flat" style="padding:0.7rem">
          <strong class="small brand-link">1. WHAT do I need to do?</strong>
          <p class="small mt-xs">${esc(step.what || step.title)}</p>
        </div>
        <div class="card card--flat" style="padding:0.7rem">
          <strong class="small brand-link">2. WHY do I need to do it?</strong>
          <p class="small mt-xs">${esc(step.why || 'Required by notice procedures.')}</p>
        </div>
        <div class="card card--flat" style="padding:0.7rem">
          <strong class="small brand-link">3. HOW should I do it?</strong>
          <p class="small mt-xs">${esc(step.how || 'Follow the step instructions carefully.')}</p>
        </div>
        <div class="card card--flat" style="padding:0.7rem">
          <strong class="small brand-link">4. WHEN should I do it?</strong>
          <p class="small mt-xs">${esc(step.when || (step.deadline ? 'Before ' + step.deadline : 'As soon as possible.'))}</p>
        </div>
        <div class="card card--flat" style="padding:0.7rem">
          <strong class="small brand-link">5. WHERE should I do it?</strong>
          <p class="small mt-xs">${esc(step.where || 'NoticeMate / Official Portal')}</p>
        </div>
        <div class="card card--flat" style="padding:0.7rem">
          <strong class="small brand-link">6. WHAT I NEED / WHAT HAPPENS AFTER?</strong>
          <p class="small mt-xs"><strong>Need:</strong> ${esc(step.what_i_need || 'Prepared documents.')}<br/><strong>After:</strong> ${esc(step.what_happens_after || 'Proceed to next step.')}</p>
        </div>
      </div>

      <div class="actions mt-md">
        ${button({
          label: 'Close Detail',
          variant: 'secondary',
          size: 'sm',
          attrs: 'id="close-modal-btn"',
        })}
      </div>
    </div>
  </div>`;
}

function renderStepHelpModal(helpRes) {
  return `<div id="help-modal" class="modal-overlay" style="position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:1000;display:flex;align-items:center;justify-content:center;padding:1rem">
    <div class="card" style="max-width:500px;width:100%;background:var(--bg-surface)">
      <div class="row-between mb-sm">
        <strong style="font-size:1.05rem;display:flex;align-items:center;gap:0.4rem">
          ${icon('sparkles', 18)} NoticeMate AI Step Assistant
        </strong>
        <button class="btn btn--ghost btn--sm" id="close-help-modal">✕</button>
      </div>

      <p class="card__label mb-xs">${esc(helpRes.title)}</p>
      <div class="alert alert--info small mb-sm">
        <div>${esc(helpRes.explanation)}</div>
      </div>

      ${
        helpRes.actionable_tip
          ? `<div class="card card--flat small mb-sm" style="padding:0.6rem">
              <strong>Tip:</strong> ${esc(helpRes.actionable_tip)}
            </div>`
          : ''
      }

      ${
        helpRes.grounded_source
          ? `<p class="small muted"><strong>Source:</strong> ${esc(helpRes.grounded_source)}</p>`
          : ''
      }

      <div class="actions mt-md">
        ${button({
          label: 'Got it',
          variant: 'primary',
          size: 'sm',
          attrs: 'id="close-help-modal-btn"',
        })}
      </div>
    </div>
  </div>`;
}

function directOfficialPortalBanner(analysis) {
  if (!analysis) return '';
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
        <p class="small muted" style="margin:0;line-height:1.5">Open the direct official portal website to read full details, verify dates, or complete your online application.</p>
      </div>
      <a href="${esc(url)}" target="_blank" rel="noopener noreferrer" class="btn btn--primary btn--md" style="display:inline-flex;align-items:center;gap:0.5rem;text-decoration:none;font-weight:700;padding:0.75rem 1.25rem;border-radius:8px;background:var(--brand);color:#fff">
        ${icon('external', 18)} Open Official Website
      </a>
    </div>
  </div>`;
}

function howRoadmapHelpsExplanationCard(roadmap) {
  return `<div class="card card--flat" style="border:1px solid var(--border);background:var(--bg-surface);padding:1.25rem;border-radius:14px;margin-bottom:1rem">
    <div class="row-between" style="margin-bottom:0.75rem">
      <strong style="font-size:1.05rem;color:var(--brand);display:flex;align-items:center;gap:0.4rem">
        ${icon('sparkles', 20)} How This Roadmap Helps You Apply & Understand
      </strong>
      ${badge('STEP-BY-STEP GUIDANCE', 'brand', true)}
    </div>

    <p style="font-size:0.93rem;line-height:1.55;color:var(--text);margin-bottom:1rem">
      Complex government and private notices can be overwhelming. NoticeMate breaks down your notice into clear, prioritized stages so you always know what to do next without missing deadlines:
    </p>

    <div class="grid grid--2" style="gap:0.75rem">
      <div style="background:var(--bg-subtle);padding:0.8rem;border-radius:10px">
        <strong style="font-size:0.88rem;color:var(--text);display:flex;align-items:center;gap:0.3rem">
          ${icon('checkCircle', 16)} 1. Sequential Progression
        </strong>
        <p class="small muted" style="margin-top:0.25rem;line-height:1.45">Steps are ordered by urgency and logical prerequisites so you never waste effort preparing documents before verifying requirements.</p>
      </div>
      <div style="background:var(--bg-subtle);padding:0.8rem;border-radius:10px">
        <strong style="font-size:0.88rem;color:var(--text);display:flex;align-items:center;gap:0.3rem">
          ${icon('clock', 16)} 2. Effort & Deadline Tracking
        </strong>
        <p class="small muted" style="margin-top:0.25rem;line-height:1.45">Every step estimates time required and highlights hard cut-off dates to prevent penalty or disqualification.</p>
      </div>
      <div style="background:var(--bg-subtle);padding:0.8rem;border-radius:10px">
        <strong style="font-size:0.88rem;color:var(--text);display:flex;align-items:center;gap:0.3rem">
          ${icon('doc', 16)} 3. Smart Document Prep
        </strong>
        <p class="small muted" style="margin-top:0.25rem;line-height:1.45">Tells you exactly which certificates, receipts, or forms to assemble before launching your response.</p>
      </div>
      <div style="background:var(--bg-subtle);padding:0.8rem;border-radius:10px">
        <strong style="font-size:0.88rem;color:var(--text);display:flex;align-items:center;gap:0.3rem">
          ${icon('external', 16)} 4. Official Portal Action
        </strong>
        <p class="small muted" style="margin-top:0.25rem;line-height:1.45">Provides direct links to the official issuing department website so you can submit safely on official channels.</p>
      </div>
    </div>
  </div>`;
}

export default async function plan({ main }) {
  if (!requireNotice()) return;

  const load = async () => {
    const roadmap = await api.roadmap(state.noticeId, lang());
    return { roadmap };
  };

  await loadInto(main, load, ({ roadmap }) => {
    setState({ roadmap });

    // Group steps
    const groupOrder = ['Do this first', 'Then', 'Before the deadline', 'Final step'];
    const grouped = {};
    groupOrder.forEach((g) => (grouped[g] = []));
    (roadmap.steps || []).forEach((s) => {
      const g = grouped[s.group] ? s.group : 'Then';
      grouped[g].push(s);
    });

    main.innerHTML = `<section class="screen">
      ${progress(3)}
      ${backLink('#/explain')}
      ${screenHead({
        eyebrow: 'Dynamic Personalized Roadmap Engine',
        title: 'YOUR ROADMAP',
        subtitle: roadmap.headline || 'Here is the simplest path from this notice to completing the required process.',
      })}

      <div class="stack">
        ${directOfficialPortalBanner(state.analysis)}
        ${howRoadmapHelpsExplanationCard(roadmap)}
        ${heroNextStepCard(roadmap)}
        ${doThisNowSection(roadmap)}
        ${roadmapProgressBar(roadmap.completed, roadmap.total)}

        <div class="stack mt-md">
          ${groupOrder
            .map((g) => {
              const list = grouped[g] || [];
              if (!list.length) return '';
              return `<div>
                <h3 style="font-size:0.9rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--text-soft);margin-bottom:0.5rem">
                  ${esc(g)}
                </h3>
                <ul class="stack stack--sm" style="list-style:none;padding:0">
                  ${list.map(renderStepItem).join('')}
                </ul>
              </div>`;
            })
            .join('')}
        </div>
      </div>

      <div class="actions mt-lg">
        ${button({
          label: 'Continue to Document Checklist',
          iconName: 'arrowRight',
          iconAfter: true,
          size: 'lg',
          attrs: 'data-next',
        })}
      </div>
    </section>`;

    // Event listeners
    main.querySelectorAll('[data-toggle], [data-hero-toggle]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const key = btn.dataset.toggle || btn.dataset.heroToggle;
        const nextState = btn.dataset.nextState || btn.dataset.heroState;
        btn.disabled = true;
        try {
          await api.updatePreparation(state.noticeId, key, nextState);
          await plan({ main });
        } catch (err) {
          btn.disabled = false;
          showError(err);
        }
      });
    });

    // 6-question detail modal trigger
    main.querySelectorAll('[data-step-detail]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const key = btn.dataset.stepDetail;
        const step = (roadmap.steps || []).find((s) => s.key === key || s.id === key);
        if (!step) return;
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = renderStepDetailModal(step);
        document.body.appendChild(modalContainer);

        const close = () => modalContainer.remove();
        document.getElementById('close-modal')?.addEventListener('click', close);
        document.getElementById('close-modal-btn')?.addEventListener('click', close);
      });
    });

    // AI Step help drawer trigger
    main.querySelectorAll('[data-step-help]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const key = btn.dataset.stepHelp;
        btn.disabled = true;
        btn.innerHTML = 'Asking AI…';
        try {
          const res = await api.stepHelp(state.noticeId, key, null, lang());
          const modalContainer = document.createElement('div');
          modalContainer.innerHTML = renderStepHelpModal(res);
          document.body.appendChild(modalContainer);

          const close = () => modalContainer.remove();
          document.getElementById('close-help-modal')?.addEventListener('click', close);
          document.getElementById('close-help-modal-btn')?.addEventListener('click', close);
        } catch (err) {
          showError(err);
        } finally {
          btn.disabled = false;
          btn.innerHTML = `${icon('question', 15)} Help Me With This`;
        }
      });
    });

    main.querySelector('[data-goto-docs]')?.addEventListener('click', () => navigate('/documents'));
    main.querySelector('[data-next]')?.addEventListener('click', () => navigate('/documents'));
  });
}
