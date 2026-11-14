<script lang="ts">
  import { onMount } from "svelte";
  import Skyline from "./lib/Skyline.svelte";
  import Timeline from "./lib/Timeline.svelte";
  import SiteTable from "./lib/SiteTable.svelte";
  import AddPoint from "./lib/AddPoint.svelte";
  import Map3D from "./lib/Map3D.svelte";
  import Compare from "./lib/Compare.svelte";
  import { computePoint, loadSaved, save, newId, validate, sunDirAt, type CustomPoint } from "./lib/custom";
  import {
    loadIndex, loadSite, indexAt, hoursUntilChange, sunUp, earthUp, horizonAt,
    fmtDuration, fmtDeg, fmtLatLon, type Meta, type Site, type SiteIndex,
  } from "./lib/data";

  let meta = $state<Meta | null>(null);
  let sites = $state<SiteIndex[]>([]);
  let selected = $state("");
  let site = $state<Site | null>(null);
  let error = $state("");
  let date = $state(new Date());
  let points = $state<CustomPoint[]>([]);
  let computed = $state<Record<string, Site>>({});
  let busy = $state(false);
  let sunDir = $state<[number, number, number] | null>(null);
  let playing = $state(false);
  let compare = $state<string[]>([]);
  let compareSites = $state<Site[]>([]);
  let hoverId = $state<string | null>(null);
  $effect(() => {
    const ids = [...compare];
    Promise.all(ids.map((id) => {
      const p = points.find((q) => q.id === id);
      return p ? (computed[id] ? Promise.resolve(computed[id]) : computePoint(p)) : loadSite(id);
    }))
      .then((list) => { if (ids.join() === compare.join()) compareSites = list; })
      .catch((e) => (error = (e as Error).message));
  });
  function toggleCompare(id: string) {
    compare = compare.includes(id) ? compare.filter((c) => c !== id) : [...compare, id].slice(0, 3);
  }
  const windowH = $derived(meta ? (Date.parse(meta.window_utc[1] + "Z") - Date.parse(meta.window_utc[0] + "Z")) / 3.6e6 + 1 : Infinity);
  $effect(() => {
    const d = date;
    sunDirAt(d).then((v) => (sunDir = v)).catch(() => (sunDir = null));
  });

  // one line per mission need, read straight off the two-year summaries of the candidate sites
  const verdict = $derived.by(() => {
    if (!sites.length) return [];
    const best = (key: keyof SiteIndex["summary"], dir: 1 | -1) => [...sites].sort((a, b) => dir * (a.summary[key] - b.summary[key]))[0];
    const a = best("sunlit_pct", -1), b = best("longest_dark_h", 1), c = best("sun_and_earth_pct", -1);
    return [
      { need: "Most sunlight overall", site: a, value: `${a.summary.sunlit_pct.toFixed(1)}% of hours`, tone: "sun" },
      { need: "Shortest night, smallest battery", site: b, value: `longest night ${fmtDuration(b.summary.longest_dark_h)}`, tone: "sun" },
      { need: "Power and a direct Earth link together", site: c, value: `${c.summary.sun_and_earth_pct.toFixed(1)}% of hours`, tone: "both" },
    ];
  });
  // opens on the site that answers the demo's question best: power and an Earth link together
  const defaultId = $derived(verdict[2]?.site.id ?? sites[0]?.id ?? "");
  const keyIds = $derived([...new Set([...verdict.map((v) => v.site.id), ...compare])]);
  const sunNever = $derived(!!site && site.summary.sunlit_pct === 0);
  const earthNever = $derived(!!site && site.summary.earth_visible_pct === 0);

  const allSites = $derived<SiteIndex[]>([
    ...sites,
    ...points.filter((p) => computed[p.id]).map((p) => ({ ...computed[p.id], custom: true })),
  ]);

  onMount(async () => {
    try {
      const idx = await loadIndex();
      meta = idx.meta;
      sites = idx.sites;
      points = loadSaved();
      const cmp = new URLSearchParams(location.search).get("cmp"); // e.g. ?cmp=malapert-massif,shackleton-rim
      if (cmp) compare = cmp.split(",").filter((id) => sites.some((s) => s.id === id)).slice(0, 3);
      const hash = location.hash.slice(1);
      const shared = hash.match(/^at=(-?[\d.]+),(-?[\d.]+)$/);
      if (shared) await addPoint("Shared point", Number(shared[1]), Number(shared[2]));
      else select(sites.some((s) => s.id === hash) ? hash : defaultId);
      for (const p of points) if (!computed[p.id]) computed[p.id] = await computePoint(p);
    } catch (e) {
      error = (e as Error).message;
    }
  });

  async function select(id: string) {
    selected = id;
    try {
      const p = points.find((q) => q.id === id);
      if (p) {
        computed[id] ??= await computePoint(p);
        site = computed[id];
        history.replaceState(null, "", `#at=${p.lat},${p.lon}`);
      } else {
        site = await loadSite(id);
        history.replaceState(null, "", `#${id}`);
      }
      error = "";
    } catch (e) {
      error = (e as Error).message;
    }
  }

  async function addPoint(name: string, lat: number, lon: number) {
    const invalid = validate(lat, lon);
    if (invalid) {
      error = invalid;
      return;
    }
    busy = true;
    const p = { id: newId(), name, lat, lon };
    points = [...points, p];
    save(points);
    await select(p.id);
    busy = false;
  }

  function removePoint(id: string) {
    points = points.filter((p) => p.id !== id);
    compare = compare.filter((c) => c !== id);
    delete computed[id];
    save(points);
    if (selected === id) select(defaultId);
  }

  const i = $derived(site ? indexAt(site, date) : -1);
  const inputValue = $derived(date.toISOString().slice(0, 16));
  function setFromInput(v: string) {
    const d = new Date(`${v}:00Z`);
    if (!Number.isNaN(d.getTime())) date = d;
  }

  const shift = (hours: number) => (date = new Date(date.getTime() + hours * 3.6e6));
  $effect(() => {
    if (!playing) return;
    const t = setInterval(() => {
      if (!site || indexAt(site, new Date(date.getTime() + 2 * 3.6e6)) < 0) playing = false;
      else shift(2); // 2 h per frame: one lunar day in about 30 s
    }, 80);
    return () => clearInterval(t);
  });
  const subsolar = $derived(sunDir ? {
    lon: ((Math.atan2(sunDir[1], sunDir[0]) * 180) / Math.PI + 360) % 360,
    elPole: (Math.asin(-sunDir[2]) * 180) / Math.PI,
  } : null);

  const now = $derived.by(() => {
    if (!site || i < 0) return null;
    const sunHz = horizonAt(site, site.sun.az[i]);
    const earthHz = horizonAt(site, site.earth.az[i]);
    return {
      sunUp: sunUp(site, i),
      sunFrac: site.sun.frac[i],
      sunEl: site.sun.el[i],
      sunAbove: site.sun.el[i] - sunHz,
      sunChange: hoursUntilChange(site, i, sunUp),
      earthUp: earthUp(site, i),
      earthEl: site.earth.el[i],
      earthAbove: site.earth.el[i] - earthHz,
      earthChange: hoursUntilChange(site, i, earthUp),
    };
  });
</script>

<header>
  <div>
    <h1>Lunar Landing Site Navigator</h1>
    <p>Where the Sun and Earth can be seen from the lunar south pole, over the real terrain, hour by hour.</p>
  </div>
  <a class="badge" href="https://github.com/marcelin1555/lunar-landing-site-navigator/blob/main/docs/validation.md">
    Validated: JPL Horizons ±0.005° · NASA PGDA maps ±1.5 pts
  </a>
</header>

{#if error}
  <p class="error" role="alert">{error}</p>
{/if}

<Map3D sites={allSites} {selected} {hoverId} pinned={keyIds} {sunDir} {busy} onselect={select}
  onpick={(lat, lon) => addPoint(`Point ${Math.abs(lat).toFixed(3)}°S ${lon.toFixed(3)}°E`, lat, lon)}>
  <div class="instr">
    {#if site}
      <div class="instr-head">
        <h2>{site.name}</h2>
        <span class="coords">{fmtLatLon(site.lat, site.lon)} · {site.ground_height_m.toFixed(0)} m</span>
      </div>
    {/if}
    <div class="clock">
      <label class="sr" for="when">Selected time, UTC</label>
      <input id="when" type="datetime-local" step="3600" value={inputValue}
        min={meta?.window_utc[0]} max={meta?.window_utc[1]}
        onchange={(e) => setFromInput(e.currentTarget.value)} />
      <span class="utc">UTC</span>
      <button class="now" onclick={() => { playing = false; date = new Date(); }}>Now</button>
    </div>
    <div class="steps" role="group" aria-label="Move time">
      <button onclick={() => shift(-24)} aria-label="Back one day">−1d</button>
      <button onclick={() => shift(-1)} aria-label="Back one hour">−1h</button>
      <button class="play" onclick={() => (playing = !playing)} aria-pressed={playing}>
        <svg viewBox="0 0 12 12" aria-hidden="true">
          {#if playing}<path d="M3 2h2v8H3zM7 2h2v8H7z" />{:else}<path d="M3 1.5v9l7.5-4.5z" />{/if}
        </svg>
        {playing ? "Pause" : "Play"}
      </button>
      <button onclick={() => shift(1)} aria-label="Forward one hour">+1h</button>
      <button onclick={() => shift(24)} aria-label="Forward one day">+1d</button>
    </div>
    {#if now}
      <dl class="rows">
        <div class="row" class:up={now.sunUp}>
          <dt><i class="dot sun"></i>Sun</dt>
          <dd class="state">{sunNever ? "Never in view, 2026–2028" : now.sunUp ? `Up · ${Math.round(now.sunFrac * 100)}% of disk` : now.sunFrac > 0 ? `Partly up · ${Math.round(now.sunFrac * 100)}% of disk` : "Hidden by terrain"}</dd>
          {#if !sunNever}<dd class="next">{now.sunUp ? "sets in" : "rises in"} <b>{fmtDuration(now.sunChange)}</b></dd>{/if}
          <dd class="sub">{fmtDeg(now.sunAbove)} over terrain · {fmtDeg(now.sunEl)} vs flat horizon</dd>
        </div>
        <div class="row" class:up={now.earthUp}>
          <dt><i class="dot earth"></i>Earth</dt>
          <dd class="state">{earthNever ? "Never in view, 2026–2028" : now.earthUp ? "In view · direct link" : "Hidden · no direct link"}</dd>
          {#if !earthNever}<dd class="next">{now.earthUp ? "sets in" : "rises in"} <b>{fmtDuration(now.earthChange)}</b></dd>{/if}
          <dd class="sub">{fmtDeg(now.earthAbove)} over terrain · {fmtDeg(now.earthEl)} vs flat horizon</dd>
        </div>
      </dl>
      {#if sunNever}
        <p class="psr"><strong>Permanently shadowed.</strong> No sunlight in the whole 2026–2028 window{earthNever ? " and no direct line of sight to Earth" : ""}. A cold trap: this is where water ice can survive.</p>
      {/if}
    {:else if site}
      <p class="out">Outside the computed window ({meta?.window_utc[0].slice(0, 10)} to {meta?.window_utc[1].slice(0, 10)}).</p>
    {/if}
    {#if subsolar}
      <p class="light">Map lit by the Sun at this time: over {subsolar.lon.toFixed(0)}°E, {fmtDeg(subsolar.elPole)} at the pole.</p>
    {/if}
  </div>
</Map3D>

<main>
  <aside>
    {#if verdict.length}
      <section class="verdict" aria-labelledby="verdict-title">
        <h2 id="verdict-title">Best site by mission need</h2>
        <ol>
          {#each verdict as v}
            <li>
              <span class="need">{v.need}</span>
              <button class="pick {v.tone}" onclick={() => select(v.site.id)} onmouseenter={() => (hoverId = v.site.id)} onmouseleave={() => (hoverId = null)}>{v.site.name}</button>
              <span class="val">{v.value}</span>
            </li>
          {/each}
        </ol>
        <p>From hourly Sun and Earth visibility over the real terrain, Nov 2026 to Dec 2028, across the 10 candidate sites.</p>
      </section>
    {/if}
    {#if sites.length}
      <div class="scroll-x"><SiteTable sites={allSites} {selected} {compare} {windowH} onselect={select} onremove={removePoint} ontoggle={toggleCompare} onhover={(id) => (hoverId = id)} /></div>
      <AddPoint onadd={addPoint} {busy} />
    {:else if !error}
      <p class="muted">Loading sites…</p>
    {/if}
  </aside>

  <section class="detail">
    {#if compareSites.length >= 2}
      <Compare sites={compareSites} {date} onpick={(d) => (date = d)} onremove={toggleCompare} />
    {/if}
    {#if site}
      <div class="title">
        <h2>{site.name}<span>: two-year record</span></h2>
        <p class="coords">{fmtLatLon(site.lat, site.lon)} · ground {site.ground_height_m.toFixed(0)} m · observer {site.observer_height_m} m above ground</p>
      </div>
      <dl class="strip">
        <div><dt>Sunlit</dt><dd>{site.summary.sunlit_pct.toFixed(1)}%</dd></div>
        <div><dt>Earth in view</dt><dd>{site.summary.earth_visible_pct.toFixed(1)}%</dd></div>
        <div><dt>Sun &amp; Earth</dt><dd>{site.summary.sun_and_earth_pct.toFixed(1)}%</dd></div>
        <div><dt>Longest night</dt><dd>{sunNever ? "whole window" : fmtDuration(site.summary.longest_dark_h)}</dd></div>
        <div><dt>Longest Earth blackout</dt><dd>{earthNever ? "whole window" : fmtDuration(site.summary.longest_no_earth_h)}</dd></div>
      </dl>
      <p class="window">Share of every hour from Nov 2026 to Dec 2028.</p>
      {#if sunNever}
        <p class="psr-detail"><strong>Permanently shadowed region.</strong> The terrain blocks the Sun at every hour of the window{earthNever ? ", and Earth too" : ""}. Not a landing site for a solar-powered lander, but a prime target for water ice: pair it with a lit rim nearby, like the Artemis plan of landing on a rim and exploring the shadow.</p>
      {/if}

      <figure>
        <figcaption>
          Horizon seen from the site, with the Sun and Earth paths for the next 14 days
          <span class="key"><i class="k-terrain"></i>terrain <i class="k-sun"></i>Sun path <i class="k-earth"></i>Earth path <i class="k-dot"></i>now</span>
        </figcaption>
        <Skyline {site} index={i} />
      </figure>

      <figure>
        <figcaption>Next 30 days. Click to move the selected time.</figcaption>
        <Timeline {site} index={i} onpick={(d) => (date = d)} />
      </figure>

      <footer>
        <p><strong>Site source:</strong> {site.source}.</p>
        {#if points.some((p) => p.id === site?.id)}
          <p><strong>Accuracy:</strong> custom points use a 240 m DEM. Against the 120 m pipeline the sunlit share differs by 1.5 points on average; on sharp summits, where the horizon is the slope just below your feet, Earth visibility can differ much more.</p>
        {/if}
        {#if meta}
          <p><strong>Method:</strong> horizon from {meta.dem}, ray-marched over 150 km on great circles, lunar curvature included. Sun and Earth positions from NAIF SPICE ({meta.kernels.join(", ")}), cross-checked against JPL Horizons to within 0.005°. {meta.notes}</p>
        {/if}
      </footer>
    {/if}
  </section>
</main>

<style>
  header { padding: 16px 24px; border-bottom: 1px solid var(--line); display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px 24px; }
  h1 { font-size: 22px; font-weight: 600; letter-spacing: -0.015em; margin: 0; }
  header p { margin: 2px 0 0; color: var(--text-dim); font-size: 13px; }
  .badge { font: 500 12px/1 var(--mono); color: var(--text-soft); text-decoration: none; border: 1px solid var(--line-strong); border-radius: 3px; padding: 8px 10px; }
  .badge { transition: color 150ms ease, border-color 150ms ease; }
  @media (hover: hover) and (pointer: fine) { .badge:hover { color: var(--text); border-color: var(--text-dim); } }
  .badge:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }

  .instr { background: rgb(6 8 11 / 0.84); backdrop-filter: blur(6px); border: 1px solid var(--line-strong); border-radius: 4px; padding: 14px 16px; box-shadow: 0 8px 24px rgb(0 0 0 / 0.45); }
  .instr-head h2 { font-size: 17px; font-weight: 600; margin: 0; letter-spacing: -0.01em; }
  .instr-head .coords { font: 500 12px/1.4 var(--mono); color: var(--text-dim); }
  .clock { display: flex; align-items: center; gap: 6px; margin-top: 12px; }
  .clock input { flex: 1; min-width: 0; }
  .utc { font: 500 12px/1 var(--mono); color: var(--text-dim); }
  .steps { display: grid; grid-template-columns: 1fr 1fr 1.6fr 1fr 1fr; gap: 4px; margin-top: 6px; }
  .instr input, .instr button { font: 500 12px/1 var(--mono); color: var(--text); background: var(--surface-2); border: 1px solid var(--line-strong); border-radius: 3px; padding: 7px 8px; color-scheme: dark; }
  .instr button { cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 6px; min-height: 30px; }
  .instr button { transition: transform 160ms var(--ease-out), border-color 150ms ease, background-color 150ms ease; }
  .instr button:active { transform: scale(0.97); }
  @media (hover: hover) and (pointer: fine) { .instr button:hover { border-color: var(--text-dim); } }
  .instr button.play { font-family: var(--sans); font-weight: 600; background: var(--text); color: var(--bg); border-color: var(--text); }
  .instr button.play[aria-pressed="true"] { background: transparent; color: var(--text); }
  .play svg { width: 10px; height: 10px; fill: currentColor; }
  .instr button.now { font-family: var(--sans); }
  .instr input:focus-visible, .instr button:focus-visible { outline: 2px solid var(--focus); outline-offset: 1px; }
  .rows { margin: 14px 0 0; display: grid; gap: 10px; }
  .row { display: grid; grid-template-columns: auto 1fr; column-gap: 12px; row-gap: 2px; padding-top: 10px; border-top: 1px solid var(--line); }
  .row dt { grid-row: span 3; font-size: 12px; font-weight: 600; color: var(--text-soft); display: flex; align-items: flex-start; gap: 6px; width: 52px; }
  .row dd { margin: 0; }
  .row .state { font-size: 14px; font-weight: 600; color: var(--text-dim); }
  .row.up .state { color: var(--text); }
  .row .next { font-size: 12px; color: var(--text-dim); }
  .row .next b { font: 500 12px/1 var(--mono); color: var(--text); }
  .row .sub { font: 500 12px/1.4 var(--mono); color: var(--text-dim); }
  .dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 4px; flex: none; }
  .dot.sun { background: var(--sun); }
  .dot.earth { background: var(--earth); }
  .light, .out { margin: 12px 0 0; font-size: 12px; color: var(--text-dim); }
  .psr { margin: 12px 0 0; font-size: 13px; line-height: 1.45; color: var(--text-soft); border-top: 1px solid var(--line); padding-top: 10px; }
  .psr strong, .psr-detail strong { color: var(--text); }
  .psr-detail { max-width: 70ch; color: var(--text-soft); line-height: 1.55; margin: -12px 0 28px; }

  .verdict { padding: 4px 10px 18px; border-bottom: 1px solid var(--line); margin-bottom: 14px; }
  .verdict h2 { font-size: 15px; font-weight: 600; margin: 0 0 10px; }
  .verdict ol { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
  .verdict li { display: grid; grid-template-columns: 1fr auto; column-gap: 12px; }
  .verdict .need { grid-column: 1 / -1; font-size: 12px; color: var(--text-dim); }
  .verdict .pick { all: unset; cursor: pointer; font-size: 15px; font-weight: 600; text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 4px; min-height: 24px; }
  .verdict .pick.sun { text-decoration-color: var(--sun); }
  .verdict .pick.both { text-decoration-color: var(--earth); }
  @media (hover: hover) and (pointer: fine) { .verdict .pick:hover { color: var(--text); text-decoration-thickness: 2px; } }
  .verdict .pick:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .verdict .val { font: 500 12px/24px var(--mono); color: var(--text-soft); text-align: right; }
  .verdict p { margin: 12px 0 0; font-size: 12px; color: var(--text-dim); }

  main { display: grid; grid-template-columns: minmax(340px, 470px) 1fr; }
  aside { border-right: 1px solid var(--line); padding: 16px 6px; }
  .detail { padding: 24px 28px 40px; min-width: 0; }
  .title h2 { font-size: 20px; font-weight: 600; margin: 0; letter-spacing: -0.01em; }
  .title h2 span { color: var(--text-dim); font-weight: 400; }
  .coords { font-family: var(--mono); color: var(--text-dim); font-size: 12px; margin: 6px 0 20px; }
  .strip { display: flex; flex-wrap: wrap; gap: 12px 36px; margin: 0; }
  .strip dt { font-size: 12px; color: var(--text-dim); }
  .strip dd { margin: 2px 0 0; font: 500 20px/1.2 var(--mono); font-variant-numeric: tabular-nums; }
  .window { color: var(--text-dim); font-size: 12px; margin: 8px 0 28px; }

  figure { margin: 0 0 28px; }
  figcaption { color: var(--text-dim); font-size: 12px; margin-bottom: 10px; display: flex; flex-wrap: wrap; justify-content: space-between; gap: 6px 16px; }
  .key { display: inline-flex; flex-wrap: wrap; align-items: center; gap: 4px 10px; font-family: var(--mono); }
  .key i { display: inline-block; width: 14px; height: 2px; margin-right: 2px; vertical-align: middle; }
  .k-terrain { height: 8px !important; border-top: 2px solid var(--ridge); background: var(--terrain) !important; }
  .k-sun { background: var(--sun); }
  .k-earth { background: var(--earth); }
  .k-dot { width: 8px !important; height: 8px !important; border-radius: 50%; background: var(--text-soft); }
  footer { border-top: 1px solid var(--line); padding-top: 14px; color: var(--text-dim); font-size: 12px; line-height: 1.6; max-width: 90ch; }
  footer strong { color: var(--text-soft); font-weight: 600; }
  .scroll-x { overflow-x: auto; }
  .muted { color: var(--text-dim); padding: 0 10px; }
  .error { margin: 12px 24px 0; padding: 10px 14px; border: 1px solid var(--danger); border-radius: 4px; color: var(--danger); }

  @media (max-width: 900px) {
    main { grid-template-columns: minmax(0, 1fr); }
    header { padding: 14px 16px; }
    aside { border-right: 0; border-bottom: 1px solid var(--line); }
    .detail { padding: 16px; }
  }
</style>
