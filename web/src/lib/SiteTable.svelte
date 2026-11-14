<script lang="ts">
  import type { SiteIndex, Summary } from "./data";

  let { sites, selected, compare, windowH, onselect, onremove, ontoggle }: {
    sites: SiteIndex[]; selected: string; compare: string[]; windowH: number;
    onselect: (id: string) => void; onremove: (id: string) => void; ontoggle: (id: string) => void;
  } = $props();
  const MAX_COMPARE = 3;

  const cols: { key: keyof Summary; label: string; unit: string; best: "max" | "min" }[] = [
    { key: "sunlit_pct", label: "Sunlit", unit: "%", best: "max" },
    { key: "earth_visible_pct", label: "Earth", unit: "%", best: "max" },
    { key: "sun_and_earth_pct", label: "Both", unit: "%", best: "max" },
    { key: "longest_dark_h", label: "Max dark", unit: "h", best: "min" },
  ];
  let sortKey = $state<keyof Summary>("sunlit_pct");

  const rows = $derived.by(() => {
    const c = cols.find((c) => c.key === sortKey)!;
    const dir = c.best === "max" ? -1 : 1;
    return [...sites].sort((a, b) => dir * (a.summary[sortKey] - b.summary[sortKey]));
  });
  const bestOf = $derived(
    Object.fromEntries(
      cols.map((c) => {
        const v = sites.map((s) => s.summary[c.key]);
        return [c.key, c.best === "max" ? Math.max(...v) : Math.min(...v)];
      }),
    ) as Record<keyof Summary, number>,
  );
</script>

<table>
  <caption>Candidate sites, Nov 2026 to Dec 2028. Tick up to {MAX_COMPARE} to compare.</caption>
  <thead>
    <tr>
      <th scope="col" class="cmp"><span class="sr">Compare</span></th>
      <th scope="col">Site</th>
      {#each cols as c}
        <th scope="col" class="num" aria-sort={sortKey === c.key ? (c.best === "max" ? "descending" : "ascending") : "none"}>
          <button class:active={sortKey === c.key} onclick={() => (sortKey = c.key)}>{c.label}</button>
        </th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each rows as s (s.id)}
      <tr class:selected={s.id === selected} onclick={() => onselect(s.id)}>
        <td class="cmp">
          <input type="checkbox" checked={compare.includes(s.id)} onclick={(e) => e.stopPropagation()} onchange={() => ontoggle(s.id)}
            disabled={!compare.includes(s.id) && compare.length >= MAX_COMPARE} aria-label="Compare {s.name}" />
        </td>
        <th scope="row">
          <button class="site" onclick={(e) => { e.stopPropagation(); onselect(s.id); }} aria-pressed={s.id === selected}>{s.name}</button>
          {#if s.custom}
            <span class="tag">custom</span>
            <button class="remove" onclick={(e) => { e.stopPropagation(); onremove(s.id); }} aria-label="Remove {s.name}">×</button>
          {/if}
        </th>
        {#each cols as c}
          <td class="num" class:best={s.summary[c.key] === bestOf[c.key]}>
            {#if c.unit === "h" && s.summary[c.key] >= windowH}never lit{:else}{s.summary[c.key].toFixed(c.unit === "%" ? 1 : 0)}<span class="unit">{c.unit}</span>{/if}
          </td>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

<style>
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .cmp { width: 28px; padding-right: 0; }
  .cmp input { accent-color: var(--sun); width: 15px; height: 15px; margin: 0; cursor: pointer; vertical-align: middle; }
  .cmp input:disabled { cursor: not-allowed; opacity: 0.35; }
  .sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
  caption { text-align: left; color: var(--text-dim); font-size: 12px; padding: 0 10px 10px; }
  th, td { padding: 8px 10px; border-bottom: 1px solid var(--line); text-align: left; font-weight: 400; }
  thead th { color: var(--text-dim); font-size: 12px; }
  .num { text-align: right; font-family: var(--mono); font-variant-numeric: tabular-nums; white-space: nowrap; }
  .unit { color: var(--text-dim); margin-left: 1px; }
  .best { color: var(--accent); }
  tbody tr { cursor: pointer; }
  tbody tr:hover { background: var(--surface-2); }
  tr.selected { background: var(--surface-3); }
  tr.selected .site { color: var(--text); font-weight: 600; }
  button { all: unset; cursor: pointer; }
  button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }
  thead button.active { color: var(--text); text-decoration: underline; text-underline-offset: 4px; }
  .site { color: var(--text-soft); }
  .tag { font: 500 10px/1 var(--mono); color: var(--earth); border: 1px solid color-mix(in srgb, var(--earth) 50%, transparent); border-radius: 3px; padding: 2px 4px; margin-left: 6px; }
  .remove { color: var(--text-dim); margin-left: 6px; padding: 0 4px; }
  .remove:hover { color: var(--danger); }
</style>
