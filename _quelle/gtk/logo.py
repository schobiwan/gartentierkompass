"""Logo-Symbol (Blatt im Kompassring), wird inline in jede Seite eingebettet."""

LEAF = ('<path d="M23.3 12.8C14.6 16.6 14 28.6 23.3 36.4Z"/>'
        '<path d="M24.7 12.8C33.4 16.6 34 28.6 24.7 36.4Z"/>'
        '<path d="M23.3 36.4 22 40.6h1.6l1-4.2Z"/>')
LOGO_SYMBOL = ('<symbol id="logo-mark" viewBox="0 0 48 48"><circle cx="24" cy="24" r="21" fill="none" stroke="currentColor" stroke-width="2.2"></circle>'
               '<circle cx="24" cy="24" r="17" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="1.5 2.5" stroke-opacity=".6"></circle>'
               f'<g fill="currentColor">{LEAF}</g><path d="M24 1.8 26.6 7.4H21.4z" fill="var(--logo-accent)"></path></symbol>')
