<script lang="ts">
  import { timeAt, type Site } from "./data";

  // Month by month across the whole window: answers "the launch slipped, which month is still good?"
  let { site, date, onpick }: { site: Site; date: Date; onpick: (d: Date) => void } = $props();

  const NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  type Month = { y: number; m: number; sun: number; earth: number; both: number };

  const months = $derived.by(() => {
    const out: Month[] = [];
    let cur: (Month & { n: number }) | null = null;
    for (let i = 0; i < site.time.n; i++) {
      const t = timeAt(site, i), y = t.getUTCFullYear(), m = t.getUTCMonth();
      if (!cur || cur.y !== y || cur.m !== m) {
        if (cur) out.push(close(cur));
        cur = { y, m, sun: 0, earth: 0, both: 0, n: 0 };
      }
      const lit = site.sun.frac[i] >= 0.5, seen = site.earth.visible[i] === 1;
      cur.sun += site.sun.frac[i]; cur.earth += +seen; cur.both += +(lit && seen); cur.n++;
    }
    if (cur) out.push(close(cur));
    return out;
  });
  function close(c: Month & { n: number }): Month {
    return { y: c.y, m: c.m, sun: c.sun / c.n, earth: c.earth / c.n, both: c.both / c.n };
  }

  const label = (mo: Month) => `${NAMES[mo.m]} ${mo.y}`;
  const pct = (v: number) => `${Math.round(v * 100)}%`;
  const current = $derived(months.findIndex((mo) => mo.y === date.getUTCFullYear() && mo.m === date.getUTCMonth()));
  const ranked = $derived([...months].sort((a, b) => b.both - a.both));
  const sel = $derived(current >= 0 ? months[current] : null);

  // keep the day and hour, move to that month (clamped to its length)
  function pick(mo: Month) {
    const last = new Date(Date.UTC(mo.y, mo.m + 1, 0)).getUTCDate();
    onpick(new Date(Date.UTC(mo.y, mo.m, Math.min(date.getUTCDate(), last), date.getUTCHours())));
  }
</script>

<div class="months">
  <div class="scroll-x">
    <div class="grid" style:--n={months.length}>
      <span class="rl">Sun</span><span class="rl">Earth</span><span class="rl">Both</span>
      {#each months as mo, k}
        <button class="col" class:on={k === current} onclick={() => pick(mo)}
          aria-label="{label(mo)}: Sun {pct(mo.sun)}, Earth {pct(mo.earth)}, both {pct(mo.both)}. Move the selected time to this month."
          title="{label(mo)} · Sun {pct(mo.sun)} · Earth {pct(mo.earth)} · both {pct(mo.both)}">
          <i class="c sun" style:opacity={0.08 + 0.92 * mo.sun}></i>
          <i class="c earth" style:opacity={0.08 + 0.92 * mo.earth}></i>
          <i class="c both" style:opacity={0.08 + 0.92 * mo.both}></i>
          <span class="ml">{mo.m === 0 || k === 0 ? `${NAMES[mo.m]} ’${String(mo.y).slice(2)}` : mo.m % 3 === 0 ? NAMES[mo.m][0] : ""}</span>
        </button>
      {/each}
    </div>
  </div>
  <p class="read">
    {#if sel}<b>{label(sel)}:</b> Sun {pct(sel.sun)} · Earth {pct(sel.earth)} · both {pct(sel.both)}.{/if}
    {#if ranked.length}
      Best month for Sun and Earth together: <b>{label(ranked[0])}</b> ({pct(ranked[0].both)}); worst: <b>{label(ranked[ranked.length - 1])}</b> ({pct(ranked[ranked.length - 1].both)}).
    {/if}
  </p>
</div>

<style>
  .scroll-x { overflow-x: auto; }
  .grid { display: grid; grid-template-columns: 44px repeat(var(--n), minmax(20px, 1fr)); grid-template-rows: repeat(3, 18px) 22px; column-gap: 2px; row-gap: 3px; min-width: calc(44px + var(--n) * 22px); }
  .rl { grid-column: 1; font: 500 12px/18px var(--sans); color: var(--text-dim); }
  .rl:nth-child(1) { grid-row: 1; } .rl:nth-child(2) { grid-row: 2; } .rl:nth-child(3) { grid-row: 3; }
  .col { all: unset; cursor: pointer; grid-row: 1 / 5; display: grid; grid-template-rows: subgrid; row-gap: 3px; position: relative; border-radius: 2px; }
  .col:focus-visible { outline: 2px solid var(--focus); outline-offset: 1px; }
  .c { display: block; border-radius: 2px; }
  .c.sun { background: var(--sun); }
  .c.earth { background: var(--earth); }
  .c.both { background: var(--text); }
  .col.on { box-shadow: 0 0 0 1px var(--text); }
  @media (hover: hover) and (pointer: fine) { .col:hover { box-shadow: 0 0 0 1px var(--text-dim); } .col.on:hover { box-shadow: 0 0 0 1px var(--text); } }
  .ml { font: 500 12px/22px var(--mono); color: var(--text-dim); white-space: nowrap; overflow: visible; }
  .read { margin: 8px 0 0; font-size: 12px; color: var(--text-dim); line-height: 1.5; }
  .read b { color: var(--text); font-weight: 600; }
</style>
