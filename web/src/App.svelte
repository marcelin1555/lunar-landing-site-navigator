<script lang="ts">
  import { onMount } from "svelte";
  import Skyline from "./lib/Skyline.svelte";
  import Timeline from "./lib/Timeline.svelte";
  import SiteTable from "./lib/SiteTable.svelte";
  import AddPoint from "./lib/AddPoint.svelte";
  import Map3D from "./lib/Map3D.svelte";
  import Compare from "./lib/Compare.svelte";
  import { computePoint, loadSaved, save, newId, validate, sunLonAt, type CustomPoint } from "./lib/custom";
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
  let sunLon = $state<number | null>(null);
  let compare = $state<string[]>([]);
  let compareSites = $state<Site[]>([]);
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
    sunLonAt(d).then((v) => (sunLon = v)).catch(() => (sunLon = null));
  });

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
      else select(sites.some((s) => s.id === hash) ? hash : sites[0].id);
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
    if (selected === id) select(sites[0].id);
  }

  const i = $derived(site ? indexAt(site, date) : -1);
  const inputValue = $derived(date.toISOString().slice(0, 16));
  function setFromInput(v: string) {
    const d = new Date(`${v}:00Z`);
    if (!Number.isNaN(d.getTime())) date = d;
  }

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
  <div class="brand">
    <h1>Lunar Landing Site Navigator</h1>
    <p>Sun and Earth visibility over the real terrain horizon at the lunar south pole</p>
  </div>
  <div class="when">
    <label for="when">Time (UTC)</label>
    <input id="when" type="datetime-local" step="3600" value={inputValue}
      min={meta?.window_utc[0]} max={meta?.window_utc[1]}
      onchange={(e) => setFromInput(e.currentTarget.value)} />
    <button onclick={() => (date = new Date())}>Now</button>
  </div>
</header>

{#if error}
  <p class="error" role="alert">{error} Reload the page to try again.</p>
{/if}

<Map3D sites={allSites} {selected} {sunLon} {busy} onselect={select}
  onpick={(lat, lon) => addPoint(`Point ${Math.abs(lat).toFixed(3)}°S ${lon.toFixed(3)}°E`, lat, lon)} />

<main>
  <aside>
    {#if sites.length}
      <div class="scroll-x"><SiteTable sites={allSites} {selected} {compare} {windowH} onselect={select} onremove={removePoint} ontoggle={toggleCompare} /></div>
      <AddPoint onadd={addPoint} {busy} />
    {:else if !error}
      <p class="muted">Loading sites…</p>
    {/if}
  </aside>

  <section class="detail">
    {#if site}
      <div class="title">
        <h2>{site.name}</h2>
        <p class="coords">{fmtLatLon(site.lat, site.lon)} · ground {site.ground_height_m.toFixed(0)} m · observer {site.observer_height_m} m above ground</p>
      </div>

      {#if now}
        <div class="readout">
          <div class="cell sun-cell">
            <h3><span class="dot sun"></span>Sun</h3>
            <p class="state">{now.sunUp ? "Above horizon" : "Below horizon"}</p>
            <dl>
              <dt>Disk visible</dt><dd>{Math.round(now.sunFrac * 100)}%</dd>
              <dt>Elevation</dt><dd>{fmtDeg(now.sunEl)}</dd>
              <dt>Clearance over terrain</dt><dd>{fmtDeg(now.sunAbove)}</dd>
              <dt>{now.sunUp ? "Sets in" : "Rises in"}</dt><dd>{fmtDuration(now.sunChange)}</dd>
            </dl>
          </div>
          <div class="cell earth-cell">
            <h3><span class="dot earth"></span>Earth</h3>
            <p class="state">{now.earthUp ? "In view: direct link possible" : "Hidden: no direct link"}</p>
            <dl>
              <dt>Elevation</dt><dd>{fmtDeg(now.earthEl)}</dd>
              <dt>Clearance over terrain</dt><dd>{fmtDeg(now.earthAbove)}</dd>
              <dt>{now.earthUp ? "Sets in" : "Rises in"}</dt><dd>{fmtDuration(now.earthChange)}</dd>
            </dl>
          </div>
          <div class="cell">
            <h3>Whole window</h3>
            <p class="state">Nov 2026 to Dec 2028</p>
            <dl>
              <dt>Sunlit</dt><dd>{site.summary.sunlit_pct.toFixed(1)}%</dd>
              <dt>Earth in view</dt><dd>{site.summary.earth_visible_pct.toFixed(1)}%</dd>
              <dt>Longest night</dt><dd>{site.summary.longest_dark_h >= site.time.n ? "never sunlit" : fmtDuration(site.summary.longest_dark_h)}</dd>
              <dt>Longest Earth blackout</dt><dd>{site.summary.longest_no_earth_h >= site.time.n ? "never in view" : fmtDuration(site.summary.longest_no_earth_h)}</dd>
            </dl>
          </div>
        </div>
      {:else}
        <p class="muted">The selected time is outside the computed window ({meta?.window_utc[0]} to {meta?.window_utc[1]} UTC).</p>
      {/if}

      {#if compareSites.length >= 2}
        <Compare sites={compareSites} {date} onpick={(d) => (date = d)} onremove={toggleCompare} />
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
  header { display: flex; flex-wrap: wrap; gap: 16px 32px; align-items: end; justify-content: space-between; padding: 20px 24px 16px; border-bottom: 1px solid var(--line); }
  h1 { font-size: 20px; font-weight: 600; letter-spacing: -0.01em; margin: 0; }
  .brand p { margin: 4px 0 0; color: var(--text-dim); font-size: 13px; }
  .when { display: flex; align-items: center; gap: 8px; }
  .when label { color: var(--text-dim); font-size: 12px; }
  input, .when button { font: 500 13px/1 var(--mono); color: var(--text); background: var(--surface-2); border: 1px solid var(--line-strong); border-radius: 4px; padding: 8px 10px; color-scheme: dark; }
  .when button { cursor: pointer; font-family: var(--sans); }
  .when button:hover { background: var(--surface-3); }
  input:focus-visible, .when button:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }

  main { display: grid; grid-template-columns: minmax(320px, 420px) 1fr; min-height: calc(100vh - 80px); }
  aside { border-right: 1px solid var(--line); padding: 16px 6px; }
  .detail { padding: 20px 28px 40px; min-width: 0; }
  .title h2 { font-size: 24px; font-weight: 600; margin: 0; letter-spacing: -0.01em; }
  .coords { font-family: var(--mono); color: var(--text-dim); font-size: 12px; margin: 6px 0 20px; }

  .readout { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border: 1px solid var(--line); border-radius: 6px; margin-bottom: 24px; }
  .cell { padding: 14px 16px; }
  .cell + .cell { border-left: 1px solid var(--line); }
  h3 { font-size: 13px; font-weight: 600; margin: 0; display: flex; align-items: center; gap: 8px; }
  .dot { width: 8px; height: 8px; border-radius: 50%; }
  .dot.sun { background: var(--sun); }
  .dot.earth { background: var(--earth); }
  .state { margin: 4px 0 12px; color: var(--text-soft); font-size: 13px; }
  dl { display: grid; grid-template-columns: 1fr auto; gap: 6px 12px; margin: 0; font-size: 12px; }
  dt { color: var(--text-dim); }
  dd { margin: 0; text-align: right; font-family: var(--mono); font-variant-numeric: tabular-nums; }

  figure { margin: 0 0 28px; }
  figcaption { color: var(--text-dim); font-size: 12px; margin-bottom: 10px; }
  figcaption { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 6px 16px; }
  .key { display: inline-flex; flex-wrap: wrap; align-items: center; gap: 4px 10px; font-family: var(--mono); }
  .key i { display: inline-block; width: 14px; height: 2px; margin-right: 2px; vertical-align: middle; }
  .k-terrain { background: var(--ridge); height: 8px !important; border-top: 2px solid var(--ridge); background: var(--terrain) !important; }
  .k-sun { background: var(--sun); }
  .k-earth { background: var(--earth); }
  .k-dot { width: 8px !important; height: 8px !important; border-radius: 50%; background: var(--text-soft); }
  footer { border-top: 1px solid var(--line); padding-top: 14px; color: var(--text-dim); font-size: 12px; line-height: 1.6; max-width: 90ch; }
  footer strong { color: var(--text-soft); font-weight: 600; }
  .scroll-x { overflow-x: auto; }
  .muted { color: var(--text-dim); padding: 0 10px; }
  .error { margin: 16px 24px 0; padding: 10px 14px; border: 1px solid var(--danger); border-radius: 4px; color: var(--danger); }

  @media (max-width: 900px) {
    main { grid-template-columns: minmax(0, 1fr); }
    header { padding: 16px; }
    aside { border-right: 0; border-bottom: 1px solid var(--line); }
    .detail { padding: 16px; }
    .readout { grid-template-columns: 1fr; }
    .cell + .cell { border-left: 0; border-top: 1px solid var(--line); }
  }
</style>
