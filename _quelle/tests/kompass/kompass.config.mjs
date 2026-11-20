// Einstellungen für den gemeinsamen Test der Kompassseiten (serve.mjs, seiten.mjs und perf.mjs sind in allen Repositories gleich).
// Leistungsbudget: Ziel sind die Grenzen des Vogelkompass (95 Punkte, LCP 2,5 s, Speed Index 2 s, Blockierzeit 250 ms, CLS 0,01).
// kb = Datenmenge höchstens, rund 10 % über dem Stand vom 20.11.2026 (Median, gzip wie bei statichost).
// Startseite, Artseite und Vergleich liegen noch unter dem Ziel: dort gilt vorerst der heutige Stand (score, lcp), er darf nicht schlechter werden.
export default {
  dist: '../../../dist',
  perf: [
    { path: '', name: 'Startseite', kb: 650, score: 90, lcp: 3300 },
    { path: 'arten/igel/', name: 'Artseite', kb: 540, score: 92, lcp: 3200 },
    { path: 'unterscheiden/erdkroete-oder-grasfrosch/', name: 'Vergleich', kb: 500, score: 93, lcp: 3000 },
    { path: 'gartenjahr/november/', name: 'Gartenjahr', kb: 820 },
    { path: 'schadbilder/', name: 'Schadbilder', kb: 140 },
  ],
};
