<script lang="ts">
  import { scaleTime, timeDay } from "d3";
  import { timeAt, type Site } from "./data";

  let { site, index, days = 30, onpick }: { site: Site; index: number; days?: number; onpick: (d: Date) => void } = $props();

  let width = $state(800);
  const m = { left: 64, right: 16 };
  const row = 22;
  const height = 2 * row + 40;

  const i0 = $derived(Math.max(0, Math.min(index - 48, site.time.n - days * 24)));
  const i1 = $derived(Math.min(site.time.n, i0 + days * 24));
  const x = $derived(scaleTime().domain([timeAt(site, i0), timeAt(site, i1)]).range([m.left, width - m.right]));
  const w = $derived((width - m.left - m.right) / (i1 - i0));

  // merge consecutive hours with the same value into one rect
  function runs(values: number[]) {
    const out: { a: number; b: number; v: number }[] = [];
    for (let i = i0; i < i1; i++) {
      const v = Math.round(values[i] * 4) / 4;
      const last = out[out.length - 1];
      if (last && last.v === v) last.b = i + 1;
      else out.push({ a: i, b: i + 1, v });
    }
    return out.filter((r) => r.v > 0);
  }
  const sunRuns = $derived(runs(site.sun.frac));
  const earthRuns = $derived(runs(site.earth.visible));

  function key(e: KeyboardEvent) {
    const step = (e.shiftKey ? 24 : 1) * (e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0);
    if (!step || index < 0) return;
    e.preventDefault();
    onpick(timeAt(site, Math.min(site.time.n - 1, Math.max(0, index + step))));
  }

  function pick(e: MouseEvent) {
    const rect = (e.currentTarget as SVGElement).getBoundingClientRect();
    const px = e.clientX - rect.left;
    if (px >= m.left) onpick(x.invert(px));
  }
</script>

<div class="timeline" bind:clientWidth={width}>
  <svg {width} {height} onclick={pick} onkeydown={key} tabindex="0" role="slider"
    aria-label="Selected time on the {days}-day Sun and Earth visibility timeline. Arrow keys move one hour, Shift+arrow one day."
    aria-valuemin={i0} aria-valuemax={i1 - 1} aria-valuenow={index} aria-valuetext={index >= 0 ? timeAt(site, index).toISOString().slice(0, 13) + ' UTC' : 'outside window'}>
    <text class="label" x={m.left - 10} y={row / 2 + 4} text-anchor="end">Sun</text>
    <text class="label" x={m.left - 10} y={row * 1.5 + 10} text-anchor="end">Earth</text>
    <rect class="track" x={m.left} y="0" width={width - m.left - m.right} height={row - 4} />
    <rect class="track" x={m.left} y={row + 4} width={width - m.left - m.right} height={row - 4} />
    {#each sunRuns as r}
      <rect class="sun" x={m.left + (r.a - i0) * w} y="0" width={(r.b - r.a) * w + 0.5} height={row - 4} opacity={r.v} />
    {/each}
    {#each earthRuns as r}
      <rect class="earth" x={m.left + (r.a - i0) * w} y={row + 4} width={(r.b - r.a) * w + 0.5} height={row - 4} />
    {/each}
    {#each x.ticks(timeDay.filter((d) => Math.floor(d.getTime() / 864e5) % (width < 520 ? 10 : 5) === 0)) as t}
      <line class="tickline" x1={x(t)} x2={x(t)} y1="0" y2={row * 2 + 6} />
      <text class="tick" x={x(t)} y={row * 2 + 22} text-anchor="middle">
        {t.toISOString().slice(5, 10)}
      </text>
    {/each}
    {#if index >= i0 && index < i1}
      <line class="now" x1={m.left + (index - i0) * w} x2={m.left + (index - i0) * w} y1="-4" y2={row * 2 + 8} />
    {/if}
  </svg>
</div>

<style>
  .timeline { width: 100%; }
  svg { display: block; cursor: crosshair; }
  svg:focus-visible { outline: 2px solid var(--focus); outline-offset: 4px; }
  .track { fill: var(--surface-2); }
  .sun { fill: var(--sun); }
  .earth { fill: var(--earth); }
  .label { fill: var(--text-dim); font: 500 12px/1 var(--sans); }
  .tick { fill: var(--text-dim); font: 500 12px/1 var(--mono); }
  .tickline { stroke: var(--bg); stroke-width: 1; opacity: 0.6; }
  .now { stroke: var(--text); stroke-width: 2; }
</style>
