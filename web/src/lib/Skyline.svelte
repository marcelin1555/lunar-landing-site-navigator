<script lang="ts">
  import { scaleLinear, line, area, curveLinear } from "d3";
  import type { Site } from "./data";

  let { site, index, spanH = 24 * 14 }: { site: Site; index: number; spanH?: number } = $props();

  let width = $state(800);
  const height = 300;
  const m = { top: 14, right: 16, bottom: 30, left: 44 };

  const hz = $derived(site.horizon.el_deg.map((el, k) => [k * site.horizon.az_step_deg, el] as [number, number]));
  const closedHz = $derived([...hz, [360, hz[0][1]] as [number, number]]);

  function path(az: number[], el: number[]) {
    const pts: [number, number][] = [];
    const end = Math.min(index + spanH, az.length);
    for (let i = Math.max(index, 0); i < end; i++) {
      if (pts.length && Math.abs(az[i] - pts[pts.length - 1][0]) > 180) pts.push([NaN, NaN]);
      pts.push([az[i], el[i]]);
    }
    return pts;
  }
  const sunPts = $derived(path(site.sun.az, site.sun.el));
  const earthPts = $derived(path(site.earth.az, site.earth.el));

  const yDomain = $derived.by(() => {
    const vals = [...site.horizon.el_deg, ...sunPts.map((p) => p[1]), ...earthPts.map((p) => p[1])].filter(Number.isFinite);
    return [Math.floor(Math.min(...vals, -2)) - 0.5, Math.ceil(Math.max(...vals, 2)) + 0.5];
  });

  const x = $derived(scaleLinear().domain([0, 360]).range([m.left, width - m.right]));
  const y = $derived(scaleLinear().domain(yDomain).range([height - m.bottom, m.top]));
  const ln = $derived(line<[number, number]>().defined((p) => Number.isFinite(p[0])).x((p) => x(p[0])).y((p) => y(p[1])).curve(curveLinear));
  const terrain = $derived(area<[number, number]>().x((p) => x(p[0])).y0(height - m.bottom).y1((p) => y(p[1]))(closedHz) ?? "");

  const sunNow = $derived(index >= 0 ? [site.sun.az[index], site.sun.el[index]] : null);
  const earthNow = $derived(index >= 0 ? [site.earth.az[index], site.earth.el[index]] : null);
  const compass = [
    [0, "N"], [90, "E"], [180, "S"], [270, "W"], [360, "N"],
  ] as const;
</script>

<div class="skyline" bind:clientWidth={width}>
  <svg {width} {height} role="img" aria-label="Local horizon of {site.name} with the Sun and Earth paths for the next 14 days">
    {#each y.ticks(6) as t}
      <line class="grid" x1={m.left} x2={width - m.right} y1={y(t)} y2={y(t)} />
      <text class="tick" x={m.left - 8} y={y(t)} dy="0.32em" text-anchor="end">{t}°</text>
    {/each}
    {#each compass as [az, label]}
      <line class="grid" x1={x(az)} x2={x(az)} y1={m.top} y2={height - m.bottom} />
      <text class="tick" x={x(az)} y={height - 10} text-anchor="middle">{label} {az % 360}°</text>
    {/each}
    <line class="zero" x1={m.left} x2={width - m.right} y1={y(0)} y2={y(0)} />

    <path class="earth-path" d={ln(earthPts)} />
    <path class="sun-path" d={ln(sunPts)} />
    <path class="terrain" d={terrain} />
    <path class="ridge" d={ln(closedHz)} />

    {#if earthNow}
      <circle class="earth-now" cx={x(earthNow[0])} cy={y(earthNow[1])} r="6" />
    {/if}
    {#if sunNow}
      <circle class="sun-now" cx={x(sunNow[0])} cy={y(sunNow[1])} r="7" />
    {/if}
  </svg>
</div>

<style>
  .skyline { width: 100%; }
  svg { display: block; overflow: visible; }
  .grid { stroke: var(--line); stroke-width: 1; }
  .zero { stroke: var(--line-strong); stroke-dasharray: 2 4; }
  .tick { fill: var(--text-dim); font: 500 11px/1 var(--mono); }
  .terrain { fill: var(--terrain); }
  .ridge { fill: none; stroke: var(--ridge); stroke-width: 1.25; }
  .sun-path { fill: none; stroke: var(--sun); stroke-width: 1.5; opacity: 0.55; }
  .earth-path { fill: none; stroke: var(--earth); stroke-width: 1.5; opacity: 0.55; }
  .sun-now { fill: var(--sun); stroke: var(--bg); stroke-width: 2; }
  .earth-now { fill: var(--earth); stroke: var(--bg); stroke-width: 2; }
</style>
