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
  // a "best" mark only means something when the sites differ
  const isBest = (key: (typeof rows)[number]["key"], dir: "max" | "min", v: number) => {
    const vals = stats.filter((s) => s).map((s) => s![key]);
    return vals.length > 1 && v === best(key, dir) && vals.some((x) => x !== v);
  };
  const fmt = (key: string, v: number) => (key === "dark" && v === 0 ? "no night" : fmtDuration(v));
  const from = $derived(sites[0] && indexAt(sites[0], date) >= 0 ? timeAt(sites[0], indexAt(sites[0], date)).toISOString().slice(0, 10) : "");
</script>

<section class="compare" aria-labelledby="cmp-title">
  <h2 id="cmp-title">Compare sites: {DAYS} days from {from} UTC</h2>
  <p class="frame">A landing-window view: hours in the {DAYS} days after the selected time. The site table shows the whole two-year record.</p>
  <div class="scroll-x"><table>
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
        <tr>
          <th scope="row">{r.label}</th>
          {#each stats as st}
            <td class="num" class:best={st && isBest(r.key, r.best, st[r.key])}>{st ? fmt(r.key, st[r.key]) : "outside window"}</td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table></div>

  <!-- narrow screens: one card per metric, sites as rows, nothing hidden sideways -->
  <div class="cards">
    {#each rows as r}
      <dl>
        <dt>{r.label}</dt>
        {#each sites as s, k (s.id)}
          {@const st = stats[k]}
          <dd><span>{s.name}</span><b class:best={st && isBest(r.key, r.best, st[r.key])}>{st ? fmt(r.key, st[r.key]) : "outside window"}</b></dd>
        {/each}
      </dl>
    {/each}
    <p class="remove-row">
      {#each sites as s (s.id)}
        <button onclick={() => onremove(s.id)} aria-label="Stop comparing {s.name}">× {s.name}</button>
      {/each}
    </p>
  </div>

  {#each sites as s (s.id)}
    <div class="row">
      <h3>{s.name}</h3>
      <Timeline site={s} index={indexAt(s, date)} days={DAYS} {onpick} />
    </div>
  {/each}
</section>

<style>
  .compare { border: 1px solid var(--line); border-radius: 6px; padding: 16px; margin-bottom: 28px; transition: opacity 220ms var(--ease-out), transform 220ms var(--ease-out); }
  /* appears when the second site is ticked: fade up instead of popping in */
  @starting-style { .compare { opacity: 0; transform: translateY(8px); } }
  h2 { font-size: 15px; font-weight: 600; margin: 0 0 12px; }
  .frame { margin: -6px 0 12px; font-size: 12px; color: var(--text-dim); }
  h3 { font-size: 12px; font-weight: 600; color: var(--text-soft); margin: 14px 0 6px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 8px; }
  th, td { padding: 7px 10px; border-bottom: 1px solid var(--line); text-align: left; font-weight: 400; }
  thead th { color: var(--text-dim); font-size: 12px; }
  thead th.num { color: var(--text); font-weight: 600; }
  tbody th { color: var(--text-dim); }
  .num { text-align: right; font-family: var(--mono); font-variant-numeric: tabular-nums; white-space: nowrap; }
  thead .num { font-family: var(--sans); }
  .scroll-x { overflow-x: auto; }
  .cards { display: none; }
  @media (max-width: 600px) {
    .scroll-x { display: none; }
    .cards { display: grid; gap: 12px; margin-bottom: 8px; }
    .cards dl { margin: 0; border-bottom: 1px solid var(--line); padding-bottom: 10px; }
    .cards dt { font-size: 12px; color: var(--text-dim); margin-bottom: 4px; }
    .cards dd { margin: 0; display: flex; justify-content: space-between; gap: 12px; font-size: 13px; padding: 3px 0; }
    .cards b { font: 400 13px/1.4 var(--mono); white-space: nowrap; }
    .cards b.best { font-weight: 600; }
    .remove-row { display: flex; flex-wrap: wrap; gap: 4px 12px; margin: 0; font-size: 12px; }
    .remove-row button { margin: 0; padding: 0 2px; }
  }
  .best { font-weight: 600; color: var(--text); text-decoration: underline; text-decoration-color: var(--text-dim); text-underline-offset: 4px; }
  button { all: unset; cursor: pointer; color: var(--text-dim); margin-left: 4px; display: inline-grid; place-items: center; min-width: 24px; min-height: 24px; }
  @media (hover: hover) and (pointer: fine) { button:hover { color: var(--danger); } }
  button:focus-visible { outline: 2px solid var(--focus); border-radius: 2px; }
</style>
