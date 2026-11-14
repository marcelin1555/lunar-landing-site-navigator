<script lang="ts">
  import { validate, LAT_LIMIT } from "./custom";

  let { onadd, busy }: { onadd: (name: string, lat: number, lon: number) => void; busy: boolean } = $props();

  let name = $state("");
  let lat = $state("");
  let lon = $state("");
  let message = $state("");

  function submit(e: SubmitEvent) {
    e.preventDefault();
    const la = Number(lat.replace(",", ".")), lo = ((Number(lon.replace(",", ".")) % 360) + 360) % 360;
    message = validate(la, lo) ?? "";
    if (message) return;
    onadd(name.trim() || `Point ${Math.abs(la).toFixed(3)}°S ${lo.toFixed(3)}°E`, la, lo);
    name = lat = lon = "";
  }
</script>

<form onsubmit={submit} aria-describedby="add-help">
  <h2>Add a custom point</h2>
  <p id="add-help">Any point south of {Math.abs(LAT_LIMIT)}°S. Computed in your browser on a 240 m DEM.</p>
  <div class="fields">
    <label>Name <input bind:value={name} placeholder="Optional" maxlength="40" /></label>
    <label>Lat <input bind:value={lat} inputmode="decimal" placeholder="−89.45" required /></label>
    <label>Lon °E <input bind:value={lon} inputmode="decimal" placeholder="222.7" required /></label>
    <button type="submit" disabled={busy}>{busy ? "Computing…" : "Compute"}</button>
  </div>
  {#if message}<p class="error" role="alert">{message}</p>{/if}
</form>

<style>
  form { padding: 16px 10px 4px; border-top: 1px solid var(--line); margin-top: 12px; }
  h2 { font-size: 13px; font-weight: 600; margin: 0; }
  p { color: var(--text-dim); font-size: 12px; margin: 4px 0 10px; }
  .fields { display: grid; grid-template-columns: 1.4fr 1fr 1fr auto; gap: 8px; align-items: end; }
  label { display: grid; gap: 4px; color: var(--text-dim); font-size: 11px; }
  input, button { font: 500 13px/1 var(--mono); color: var(--text); background: var(--surface-2); border: 1px solid var(--line-strong); border-radius: 4px; padding: 8px; min-width: 0; }
  input::placeholder { color: var(--text-dim); opacity: 0.7; }
  button { font-family: var(--sans); cursor: pointer; background: var(--surface-3); }
  button:hover:not(:disabled) { border-color: var(--accent); }
  button:disabled { opacity: 0.6; cursor: progress; }
  input:focus-visible, button:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
  .error { color: var(--danger); margin: 8px 0 0; }
</style>
