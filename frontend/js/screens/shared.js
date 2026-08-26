/** Helpers shared by every screen: guards, loading shells, error rendering. */

import { ApiError } from '../api.js';
import { navigate } from '../router.js';
import { state } from '../state.js';
import { t } from '../i18n.js';
import { errorState, spinner, toast } from '../ui.js';

/**
 * Ensure a notice is in progress. Returns false (and redirects) when there
 * isn't one, so a screen can simply `if (!requireNotice()) return;`.
 */
export function requireNotice() {
  if (!state.noticeId) {
    navigate('/input', { replace: true });
    return false;
  }
  return true;
}

/** Turn any thrown error into a friendly, human sentence. */
export function friendlyError(err) {
  if (err instanceof ApiError) {
    if (err.offline) return t('error.offline');
    if (err.status === 404) return t('error.noNotice');
    if (err.message && err.message !== 'request_failed') return err.message;
  }
  return t('error.generic');
}

export function showError(err) {
  toast(friendlyError(err), 'danger');
}

/**
 * Render a loading placeholder, run `loader`, then render the result.
 * On failure the screen shows a retry affordance instead of a blank page.
 */
export async function loadInto(main, loader, renderView, { label } = {}) {
  main.innerHTML = spinner(label);
  try {
    const data = await loader();
    main.innerHTML = '';
    await renderView(data);
  } catch (err) {
    main.innerHTML = `<div class="screen">${errorState(friendlyError(err))}</div>`;
    main.querySelector('[data-retry]')?.addEventListener('click', () => {
      loadInto(main, loader, renderView, { label });
    });
  }
}

/** Language currently selected by the user. */
export const lang = () => state.language || 'en';
