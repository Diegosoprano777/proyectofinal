import { Component } from '@angular/core';

/** Isotipo de aguacate en SVG (sin dependencias de imágenes). */
@Component({
  selector: 'app-logo',
  host: { class: 'inline-block' },
  template: `
    <svg viewBox="0 0 48 48" class="h-full w-full drop-shadow-sm" aria-hidden="true">
      <defs>
        <linearGradient id="avo-piel" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#4e8022" />
          <stop offset="1" stop-color="#14532d" />
        </linearGradient>
        <linearGradient id="avo-pulpa" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#ecfccb" />
          <stop offset="1" stop-color="#bef264" />
        </linearGradient>
      </defs>
      <path d="M24 2.5c-6.5 0-9.6 7.4-11.6 13.4C10.3 21.5 6 25.6 6 32.6 6 41 13.4 46 24 46s18-5 18-13.4c0-7-4.3-11.1-6.4-16.7C33.6 9.9 30.5 2.5 24 2.5z" fill="url(#avo-piel)" />
      <path d="M24 8.5c-4.3 0-6.4 5.4-8.3 10.6-1.6 4.2-5.2 7.3-5.2 13.4 0 6.3 5.8 9.5 13.5 9.5s13.5-3.2 13.5-9.5c0-6.1-3.6-9.2-5.2-13.4C30.4 13.9 28.3 8.5 24 8.5z" fill="url(#avo-pulpa)" />
      <circle cx="24" cy="31.5" r="7.2" fill="#7c4a24" />
      <circle cx="21.8" cy="29.2" r="2.2" fill="#b07445" opacity=".9" />
    </svg>
  `,
})
export class LogoComponent {}
