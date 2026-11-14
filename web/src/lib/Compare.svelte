<script lang="ts">
  import Timeline from "./Timeline.svelte";
  import { indexAt, timeAt, fmtDuration, type Site } from "./data";

  let { sites, date, onpick, onremove }: { sites: Site[]; date: Date; onpick: (d: Date) => void; onremove: (id: string) => void } = $props();

  const DAYS = 30;
  // stats for the 30 days shown, starting at the selected time
  function next(s: Site) {
    const i = indexAt(s, date);
    if (i < 0) return null;
    const end = Math.min(s.time.n, i + DAYS * 24);
    let sun = 0, earth = 0, both = 0, dark = 0, run = 0;
    for (let k = i; k < end; k++) {
      const lit = s.sun.frac[k] >= 0.5, seen = s.earth.visible[k] === 1;
      sun += s.sun.frac[k]; earth += +seen; both += +(lit && seen);
      run = lit ? 0 : run + 1; dark = Math.max(dark, run);
    }
    const h = s.time.step_s / 3600;
    return { sun: sun * h, earth: earth * h, both: both * h, dark: dark * h, span: (end - i) * h };
  }
  const stats = $derived(sites.map(next));
  const rows: { key: "sun" | "earth" | "both" | "dark"; label: string; best: "max" | "min" }[] = [
    { key: "sun", label: "Sunlight", best: "max" },
    { key: "earth", label: "Earth in view", best: "max" },
    { key: "both", label: "Sun and Earth together", best: "max" },
    { key: "dark", label: "Longest night", best: "min" },
  ];
  const best = (key: (typeof rows)[number]["key"], dir: "max" | "min") => {
    const v = stats.filter((s) => s).map((s) => s![key]);
    return dir === "max" ? Math.max(...v) : Math.min(...v);
  };
  const from = $derived(sites[0] && indexAt(sites[0], date) >= 0 ? timeAt(sites[0], indexAt(sites[0], date)).toISOString().slice(0, 10) : "");
</script>

<section class="compare" aria-labelledby="cmp-title">
  <h2 id="cmp-title">Compare sites: {DAYS} days from {from} UTC</h2>
  <table>
    <thead>
      <tr>
        <th scope="col">Hours in the next {DAYS} days</th>
        {#each sites as s (s.id)}
          <th scope="col" class="num">{s.name}
            <button onclick={() => onremove(s.id)} aria-label="Stop comparing {s.name}">×</button>
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each rows as r}
        {@const b = best(r.key, r.best)}
        <tr>
          <th scope="row">{r.label}</th>
          {#each stats as st}
            <td class="num" class:best={st && st[r.key] === b && sites.length > 1}>{st ? fmtDuration(st[r.key]) : "outside window"}</td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>

  {#each sites as s (s.id)}
    <div class="row">
      <h3>{s.name}</h3>
      <Timeline site={s} index={indexAt(s, date)} days={DAYS} {onpick} />
    </div>
  {/each}
</section>

<style>
  .compare { border: 1px solid var(--line); border-radius: 6px; padding: 16px; margin-bottom: 28px; }
  h2 { font-size: 15px; font-weight: 600; margin: 0 0 12px; }
  h3 { font-size: 12px; font-weight: 600; color: var(--text-soft); margin: 14px 0 6px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 8px; }
  th, td { padding: 7px 10px; border-bottom: 1px solid var(--line); text-align: left; font-weight: 400; }
  thead th { color: var(--text-dim); font-size: 12px; }
  thead th.num { color: var(--text); font-weight: 600; }
  tbody th { color: var(--text-dim); }
  .num { text-align: right; font-family: var(--mono); font-variant-numeric: tabular-nums; white-space: nowrap; }
  thead .num { font-family: var(--sans); }
  .best { color: var(--accent); }
  button { all: unset; cursor: pointer; color: var(--text-dim); margin-left: 6px; padding: 0 3px; }
  button:hover { color: var(--danger); }
  button:focus-visible { outline: 2px solid var(--accent); border-radius: 2px; }
</style>
