/**
 * Tiny inline-SVG icon set. Keeping icons in JS means zero network requests
 * and no icon-font dependency, so the demo works fully offline.
 */

const wrap = (body, size = 20, stroke = 1.7) =>
  `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" ` +
  `stroke="currentColor" stroke-width="${stroke}" stroke-linecap="round" ` +
  `stroke-linejoin="round" aria-hidden="true" focusable="false">${body}</svg>`;

const paths = {
  arrowRight: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  arrowLeft: '<path d="M19 12H5M11 18l-6-6 6-6"/>',
  chevronRight: '<path d="m9 6 6 6-6 6"/>',
  check: '<path d="m5 13 4 4L19 7"/>',
  checkCircle:
    '<circle cx="12" cy="12" r="9"/><path d="m8.5 12.2 2.4 2.4 4.6-5"/>',
  circle: '<circle cx="12" cy="12" r="9"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7.5V12l3.2 2"/>',
  calendar:
    '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8.5 3v4M15.5 3v4"/>',
  doc:
    '<path d="M6.5 3h7l4.5 4.5V20a1 1 0 0 1-1 1h-10a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z"/><path d="M13 3v5h5"/>',
  docCheck:
    '<path d="M6.5 3h7l4.5 4.5V20a1 1 0 0 1-1 1h-10a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z"/><path d="M13 3v5h5"/><path d="m9 14.5 1.8 1.8 3.4-3.8"/>',
  upload:
    '<path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5"/><path d="M4 15v3.5A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5V15"/>',
  keyboard:
    '<rect x="2.5" y="6" width="19" height="12" rx="2"/><path d="M6 10h.01M9.5 10h.01M13 10h.01M16.5 10h.01M8 14h8"/>',
  sparkles:
    '<path d="M12 3.5 13.6 8l4.4 1.6L13.6 11 12 15.5 10.4 11 6 9.6 10.4 8 12 3.5Z"/><path d="M18.5 15.5l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8.8-2Z"/>',
  list: '<path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01"/>',
  send: '<path d="M21 3 10.5 13.5M21 3l-7 18-3.5-7.5L3 10 21 3Z"/>',
  shield:
    '<path d="M12 3.2 19 6v5.5c0 4.2-2.9 7.6-7 9.3-4.1-1.7-7-5.1-7-9.3V6l7-2.8Z"/>',
  globe:
    '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.8 2.6 15.2 0 18M12 3c-2.6 2.8-2.6 15.2 0 18"/>',
  alert:
    '<path d="M12 4.5 21 20H3l9-15.5Z"/><path d="M12 10v4.2M12 17.2h.01"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5.5M12 7.8h.01"/>',
  eye: '<path d="M2.5 12S6 5.8 12 5.8 21.5 12 21.5 12 18 18.2 12 18.2 2.5 12 2.5 12Z"/><circle cx="12" cy="12" r="2.8"/>',
  edit:
    '<path d="M4 20h4L20 8l-4-4L4 16v4Z"/><path d="m14.5 5.5 4 4"/>',
  refresh:
    '<path d="M20 11a8 8 0 0 0-13.7-5.2L4 8"/><path d="M4 4v4h4"/><path d="M4 13a8 8 0 0 0 13.7 5.2L20 16"/><path d="M20 20v-4h-4"/>',
  x: '<path d="M6 6l12 12M18 6 6 18"/>',
  trash:
    '<path d="M4 7h16M9 7V4.5h6V7M6.5 7l.8 12.6a1 1 0 0 0 1 .9h7.4a1 1 0 0 0 1-.9L17.5 7"/>',
  tax:
    '<rect x="4" y="3.5" width="16" height="17" rx="2"/><path d="M8.5 8h7M8.5 12h3M8.5 16h5M15 15l2.5 2.5M17.5 15 15 17.5"/>',
  pension:
    '<circle cx="12" cy="8" r="3.4"/><path d="M5 20c0-3.6 3.1-6 7-6s7 2.4 7 6"/>',
  certificate:
    '<rect x="3.5" y="4" width="17" height="12" rx="2"/><path d="M7 8h6M7 11.5h4"/><circle cx="16.5" cy="11" r="2.2"/><path d="m15 13 -.6 4 2.1-1.2L18.6 17 18 13"/>',
  building:
    '<path d="M4 20V6.5L12 3l8 3.5V20"/><path d="M4 20h16M9 20v-5h6v5M9 9h.01M15 9h.01M9 12.5h.01M15 12.5h.01"/>',
  flag: '<path d="M6 3v18"/><path d="M6 4.5h11l-1.6 4L17 12.5H6"/>',
  clipboard:
    '<rect x="6" y="4.5" width="12" height="16" rx="2"/><path d="M9.5 4.5V3.2h5v1.3"/><path d="M9.5 11h5M9.5 15h3"/>',
  download:
    '<path d="M12 4v12m0 0-4.5-4.5M12 16l4.5-4.5"/><path d="M4 19h16"/>',
  copy:
    '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M15 6.5V5.5a1.5 1.5 0 0 0-1.5-1.5H5.5A1.5 1.5 0 0 0 4 5.5v8A1.5 1.5 0 0 0 5.5 15h1"/>',
  inbox:
    '<path d="M3.5 13 6 5.5h12L20.5 13v5.5a1.5 1.5 0 0 1-1.5 1.5H5a1.5 1.5 0 0 1-1.5-1.5V13Z"/><path d="M3.5 13H8l1.2 2.4h5.6L16 13h4.5"/>',
  question:
    '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.4A2.5 2.5 0 0 1 14.5 10c0 1.7-2.5 2-2.5 3.6M12 17h.01"/>',
};

export function icon(name, size = 20, stroke = 1.7) {
  const body = paths[name];
  if (!body) return '';
  return wrap(body, size, stroke);
}

export const categoryIcon = (key) =>
  ({ tax: 'tax', pension: 'pension', certificate: 'certificate' }[key] ||
  'doc');

export default icon;
