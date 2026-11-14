<script lang="ts">
  // A four-step tour for students and the public. Every number comes from this app's own results
  // (2026-2028 window, see sites.json); "Show me" puts the app in the state that proves it.
  let { onshow }: { onshow: (step: number) => void } = $props();

  const steps = [
    {
      title: "The Sun never rises or sets. It circles.",
      text: "At Earth's poles the summer Sun climbs to 23°. Here it never gets more than 1.9° above a flat horizon, because the Moon's axis is tilted only 1.5°. A 100 m hill then casts a shadow almost 4 km long.",
      show: "Show the Sun skimming the horizon",
    },
    {
      title: "A few kilometres change everything.",
      text: "The rim of Shackleton crater is in sunlight 87% of the time. Its floor, about 10 km away, gets 0%: no sunlight in two years. That permanent cold is why water ice can survive there.",
      show: "Compute the crater floor",
    },
    {
      title: "Earth hides behind the hills too.",
      text: "Earth hangs low and drifts up and down by about 7° every month. On Shackleton's rim it is in view only half the time, with blackouts of up to 14 days. Malapert, a 5 km high massif facing Earth, sees it 74% of the time.",
      show: "Show the Earth visibility timeline",
    },
    {
      title: "Nights last days, not hours.",
      text: "A lunar day lasts 29.5 Earth days. Even on the best rims the Sun disappears for days: the longest night is 3 days on Shackleton's rim and 11 days at Malapert. Every hour of darkness is battery a lander must carry.",
      show: "Play a lunar day at Malapert",
    },
  ];
  let k = $state(0);
  const s = $derived(steps[k]);
</script>

<section class="learn" aria-labelledby="learn-title">
  <div class="head">
    <h2 id="learn-title">Why the south pole is hard</h2>
    <span class="count" aria-live="polite">{k + 1} / {steps.length}</span>
  </div>
  <h3>{s.title}</h3>
  <p>{s.text}</p>
  <div class="actions">
    <button class="show" onclick={() => onshow(k)}>{s.show}</button>
    <span class="nav">
      <button onclick={() => (k = (k + steps.length - 1) % steps.length)} aria-label="Previous step">←</button>
      <button onclick={() => (k = (k + 1) % steps.length)} aria-label="Next step">→</button>
    </span>
  </div>
</section>

<style>
  .learn { padding: 4px 10px 18px; border-bottom: 1px solid var(--line); margin-bottom: 14px; }
  .head { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; }
  h2 { font-size: 15px; font-weight: 600; margin: 0; }
  .count { font: 500 12px/1 var(--mono); color: var(--text-dim); }
  h3 { font-size: 14px; font-weight: 600; margin: 12px 0 4px; color: var(--text); }
  p { margin: 0; font-size: 13px; line-height: 1.55; color: var(--text-soft); max-width: 60ch; }
  .actions { display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-top: 12px; }
  button { font: 500 12px/1 var(--sans); color: var(--text); background: var(--surface-2); border: 1px solid var(--line-strong); border-radius: 3px; padding: 8px 10px; min-height: 30px; cursor: pointer; transition: transform 160ms var(--ease-out), border-color 150ms ease; }
  button:active { transform: scale(0.97); }
  button:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  @media (hover: hover) and (pointer: fine) { button:hover { border-color: var(--text-dim); } }
  .show { background: var(--text); color: var(--bg); border-color: var(--text); font-weight: 600; }
  .nav { display: flex; gap: 4px; }
  .nav button { min-width: 32px; font-family: var(--mono); }
</style>
