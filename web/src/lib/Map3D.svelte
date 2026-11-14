<script lang="ts">
  import { onMount, type Snippet } from "svelte";
  import * as THREE from "three";
  import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
  import { fromStereo, stereoSouth } from "./free";
  import type { SiteIndex } from "./data";

  let { sites, selected, hoverId = null, pinned = [], sunDir, busy = false, onpick, onselect, children }: {
    sites: SiteIndex[];
    selected: string;
    hoverId?: string | null; // site hovered elsewhere (table, verdict): highlight its pin
    pinned?: string[]; // sites whose name must always show (verdict winners, compared sites)
    sunDir: [number, number, number] | null; // unit vector to the Sun, MOON_ME frame
    busy?: boolean;
    onpick: (lat: number, lon: number) => void;
    onselect: (id: string) => void;
    children?: Snippet;
  } = $props();

  // Scene frame (km): the real curved surface, south pole at the origin, local "up" = away from the Moon's center.
  // MOON_ME (x, y, z) -> scene (y, -z - R, -x): a proper rotation, so the Sun vector maps the same way.
  const R = 1737.4;
  const toScene = (p: [number, number, number]) => new THREE.Vector3(p[1], -p[2] - R, -p[0]);
  const meOf = (lat: number, lon: number, hKm: number): [number, number, number] => {
    const la = (lat * Math.PI) / 180, lo = (lon * Math.PI) / 180, r = R + hKm;
    return [r * Math.cos(la) * Math.cos(lo), r * Math.cos(la) * Math.sin(lo), r * Math.sin(la)];
  };

  type Mode = "now" | "mean";
  let mode = $state<Mode>("now");
  const base = import.meta.env.BASE_URL;
  let host: HTMLDivElement;
  let width = $state(400);
  let height = $state(520);
  let hover = $state<{ lat: number; lon: number } | null>(null);
  let hoverPin = $state<string | null>(null);
  let labels = $state<{ id: string; name: string; x: number; y: number; dy: number; kind: "sel" | "hot" | "key" | "dim" }[]>([]);
  let failed = $state("");
  let ready = $state(false);

  let scene: THREE.Scene, camera: THREE.PerspectiveCamera, renderer: THREE.WebGLRenderer, controls: OrbitControls;
  let mesh: THREE.Mesh, sun: THREE.DirectionalLight, fill: THREE.HemisphereLight, pins: THREE.Group;
  let matNow: THREE.MeshStandardMaterial, matMean: THREE.MeshStandardMaterial;
  let heightKm: (lat: number, lon: number) => number = () => 0;
  let frame = 0;

  async function load() {
    const meta = await fetch(`${base}data/free/terrain.json`).then((r) => r.json());
    const [hBuf, iBuf] = await Promise.all(
      ["terrain_512.i16", "illum_512.u8"].map((f) => fetch(`${base}data/free/${f}`).then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.arrayBuffer();
      })),
    );
    return { meta, h: new Int16Array(hBuf), ill: new Uint8Array(iBuf) };
  }

  onMount(() => {
    let disposed = false;
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(36, width / height, 1, 6000);
    camera.position.set(0, 330, 360);
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch {
      failed = "3D view needs WebGL, which this browser does not provide. Use the table or coordinates below.";
      return;
    }
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    host.prepend(renderer.domElement);
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.maxPolarAngle = Math.PI * 0.49;
    controls.minDistance = 30;
    controls.maxDistance = 1400;
    controls.target.set(0, -8, 0);

    fill = new THREE.HemisphereLight(0x8fa3bf, 0x05070a, 0.05); // faint earthshine, so shadows read as black
    sun = new THREE.DirectionalLight(0xfff4e0, 3.2);
    sun.castShadow = true;
    sun.shadow.mapSize.set(4096, 4096);
    Object.assign(sun.shadow.camera, { left: -340, right: 340, top: 340, bottom: -340, near: 1, far: 3000 });
    sun.shadow.bias = -0.0004;
    sun.shadow.normalBias = 0.6;
    scene.add(fill, sun, sun.target);
    pins = new THREE.Group();
    scene.add(pins);

    load().then(({ meta, h, ill }) => {
      if (disposed) return;
      const n = meta.n, res = meta.res;
      const geo = new THREE.PlaneGeometry(1, 1, n - 1, n - 1); // reused for its index; positions are replaced
      const pos = geo.attributes.position as THREE.BufferAttribute;
      const colors = new Float32Array(n * n * 3);
      const dark = new THREE.Color("#050608"), lit = new THREE.Color("#e2dccd"), c = new THREE.Color();
      for (let row = 0; row < n; row++) {
        for (let col = 0; col < n; col++) {
          const k = row * n + col;
          const [lat, lon] = fromStereo(meta.x0 + col * res, meta.y0 - row * res);
          const v = toScene(meOf(lat, lon, h[k] / 1000)); // true relief, no exaggeration
          pos.setXYZ(k, v.x, v.y, v.z);
          c.copy(dark).lerp(lit, Math.pow(ill[k] / 255, 1.3));
          colors.set([c.r, c.g, c.b], k * 3);
        }
      }
      geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
      geo.computeVertexNormals();
      matNow = new THREE.MeshStandardMaterial({ color: 0xb8b2a6, roughness: 1, metalness: 0 });
      matMean = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 1, metalness: 0 });
      mesh = new THREE.Mesh(geo, matNow);
      mesh.castShadow = mesh.receiveShadow = true;
      scene.add(mesh);
      heightKm = (lat, lon) => {
        const [x, y] = stereoSouth(lat, lon);
        const col = Math.round((x - meta.x0) / res), row = Math.round((meta.y0 - y) / res);
        return row >= 0 && col >= 0 && row < n && col < n ? h[row * n + col] / 1000 : 0;
      };
      for (const lat of [-88, -85, -82]) {
        const pts = Array.from({ length: 180 }, (_, k) => toScene(meOf(lat, k * 2, 9)));
        const ring = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts),
          new THREE.LineBasicMaterial({ color: 0x4fa8e8, transparent: true, opacity: 0.22, depthTest: false }));
        ring.renderOrder = 1;
        scene.add(ring);
      }
      ready = true;
      updatePins();
      applyMode();
    }).catch(() => (failed = "Could not load the 3D terrain. Use the table or coordinates below."));

    const tick = () => {
      frame = requestAnimationFrame(tick);
      controls.update();
      renderer.render(scene, camera);
      projectLabels();
    };
    tick();
    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
      controls.dispose();
      renderer.dispose();
      scene.traverse((o) => {
        if (o instanceof THREE.Mesh || o instanceof THREE.Line) o.geometry.dispose();
      });
      matNow?.dispose();
      matMean?.dispose();
    };
  });

  function surface(lat: number, lon: number, liftKm = 0) {
    return toScene(meOf(lat, lon, heightKm(lat, lon) + liftKm));
  }

  function updatePins() {
    if (!pins || !ready) return;
    pins.children.forEach((p) => { (p as THREE.Mesh).geometry.dispose(); ((p as THREE.Mesh).material as THREE.Material).dispose(); });
    pins.clear();
    for (const s of sites) {
      const on = s.id === selected, hot = s.id === hoverId;
      const pin = new THREE.Mesh(
        new THREE.CylinderGeometry(on || hot ? 1.8 : 1.1, 0.15, 18, 10),
        new THREE.MeshBasicMaterial({ color: on || hot ? 0xffffff : s.custom ? 0x4fa8e8 : 0x9aa6b6 }),
      );
      pin.position.copy(surface(s.lat, s.lon, 9));
      pin.userData.id = s.id;
      pins.add(pin);
    }
  }

  // every pin gets a name. Selected, hovered and key sites (verdict winners, compared) always show:
  // when they would overlap they move above or below their pin on a leader line. Other names drop out.
  function projectLabels() {
    if (!pins) return;
    const v = new THREE.Vector3();
    const all = pins.children.map((p) => {
      v.copy(p.position).add(new THREE.Vector3(0, 10, 0)).project(camera);
      const s = sites.find((q) => q.id === p.userData.id)!;
      const kind = s.id === selected ? "sel" : s.id === hoverPin || s.id === hoverId ? "hot" : pinned.includes(s.id) ? "key" : "dim";
      return { id: s.id, name: s.name, x: (v.x * 0.5 + 0.5) * width, y: (-v.y * 0.5 + 0.5) * height, dy: 0, kind, front: v.z < 1 } as const;
    }).filter((l) => l.front);
    const rank = { sel: 0, hot: 1, key: 2, dim: 3 };
    all.sort((a, b) => rank[a.kind] - rank[b.kind]);
    const boxes: { x0: number; x1: number; y0: number; y1: number }[] = [];
    const placed: (typeof labels)[number][] = [];
    for (const l of all) {
      const w = l.name.length * 7 + 12;
      const box = (dy: number) => ({ x0: l.x - w / 2, x1: l.x + w / 2, y0: l.y + dy - 22, y1: l.y + dy });
      const free = (b: ReturnType<typeof box>) => !boxes.some((o) => b.x0 < o.x1 && b.x1 > o.x0 && b.y0 < o.y1 && b.y1 > o.y0);
      const tries = l.kind === "dim" ? [0] : [0, -26, 52, -52, 78, -78];
      const dy = tries.find((d) => free(box(d)));
      if (dy === undefined && l.kind === "dim") continue;
      boxes.push(box(dy ?? 0));
      placed.push({ id: l.id, name: l.name, x: l.x, y: l.y, dy: dy ?? 0, kind: l.kind });
    }
    labels = placed;
  }

  function applyMode() {
    if (!mesh) return;
    const now = mode === "now";
    mesh.material = now ? matNow : matMean;
    sun.intensity = now ? 3.2 : 1.1;
    sun.castShadow = now;
    fill.intensity = now ? 0.05 : 0.9;
  }

  $effect(() => {
    sites; selected; hoverId; pinned; ready;
    updatePins();
  });

  $effect(() => {
    mode; ready;
    applyMode();
  });

  $effect(() => {
    if (!sun) return;
    const d = sunDir ?? [1, 0, -0.03]; // fallback outside the data window: low Sun over 0°E
    const L = new THREE.Vector3(d[1], -d[2], -d[0]).normalize(); // same rotation as toScene, without the R offset (a direction)
    sun.position.copy(L.multiplyScalar(1200));
    sun.target.position.set(0, 0, 0);
  });

  $effect(() => {
    if (!renderer) return;
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  });

  const ray = new THREE.Raycaster();
  type Hit = { kind: "pin"; id: string } | { kind: "ground"; lat: number; lon: number } | null;
  function hit(e: PointerEvent): Hit {
    const r = renderer.domElement.getBoundingClientRect();
    ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), camera);
    const pin = ray.intersectObjects(pins.children)[0];
    if (pin) return { kind: "pin", id: pin.object.userData.id as string };
    const t = mesh && ray.intersectObject(mesh)[0];
    if (!t) return null;
    const p = t.point; // scene -> MOON_ME: x = -z, y = x, z = -(y + R)
    const me = [-p.z, p.x, -(p.y + R)];
    const lat = (Math.asin(me[2] / Math.hypot(me[0], me[1], me[2])) * 180) / Math.PI;
    const lon = ((Math.atan2(me[1], me[0]) * 180) / Math.PI + 360) % 360;
    return { kind: "ground", lat, lon };
  }

  let down: { x: number; y: number; t: number } | null = null;
  function onDown(e: PointerEvent) { down = { x: e.clientX, y: e.clientY, t: performance.now() }; }
  function onMove(e: PointerEvent) {
    if (!renderer || !ready) return;
    const h = hit(e);
    hover = h?.kind === "ground" ? h : null;
    hoverPin = h?.kind === "pin" ? h.id : null;
    renderer.domElement.style.cursor = h ? "pointer" : "grab";
  }
  function onUp(e: PointerEvent) {
    // only a short, still press counts as a click; anything else was an orbit drag
    if (!down || !ready || Math.hypot(e.clientX - down.x, e.clientY - down.y) > 4 || performance.now() - down.t > 450) return;
    const h = hit(e);
    if (!h) return;
    if (h.kind === "pin") onselect(h.id);
    else onpick(Math.round(h.lat * 1e4) / 1e4, Math.round(h.lon * 1e4) / 1e4);
  }
</script>

<div class="wrap">
  <div class="map" bind:this={host} bind:clientWidth={width} bind:clientHeight={height}
    onpointerdown={onDown} onpointermove={onMove} onpointerup={onUp}
    role="application" aria-label="3D terrain of the lunar south pole. Click a pin to select a site, or click the terrain to compute a new point.">
    {#if failed}<p class="fail">{failed}</p>{/if}
    {#each labels as l (l.id)}
      {#if l.dy}<span class="lead" style:left="{l.x}px" style:top="{Math.min(l.y, l.y + l.dy - (l.dy > 0 ? 22 : 0))}px" style:height="{Math.abs(l.dy) - (l.dy > 0 ? 22 : 0)}px"></span>{/if}
      <span class="label {l.kind}" style:left="{l.x}px" style:top="{l.y + l.dy}px">{l.name}</span>
    {/each}
    <div class="hud">
      <span class="hint">{busy ? "Computing point…" : hover ? `${Math.abs(hover.lat).toFixed(3)}°S ${hover.lon.toFixed(3)}°E` : "Drag to orbit · click a pin or the terrain"}</span>
      <span class="modes" role="radiogroup" aria-label="Terrain shading">
        <button role="radio" aria-checked={mode === "now"} onclick={() => (mode = "now")} onpointerdown={(e) => e.stopPropagation()} onpointerup={(e) => e.stopPropagation()}>Sun at selected time</button>
        <button role="radio" aria-checked={mode === "mean"} onclick={() => (mode = "mean")} onpointerdown={(e) => e.stopPropagation()} onpointerup={(e) => e.stopPropagation()}>Mean sunlight (PGDA)</button>
      </span>
    </div>
  </div>
  {#if children}<div class="panel">{@render children()}</div>{/if}
</div>

<style>
  .wrap { position: relative; border-bottom: 1px solid var(--line); }
  .map { position: relative; height: min(68vh, 620px); min-height: 420px; background: #030405; touch-action: none; overflow: hidden; }
  .map :global(canvas) { display: block; }
  .label { position: absolute; transform: translate(-50%, -100%); font: 500 12px/1 var(--sans); padding: 4px 6px; border-radius: 2px; pointer-events: none; white-space: nowrap; }
  .label.key { color: var(--text); background: rgb(3 4 5 / 0.85); border: 1px solid var(--line-strong); }
  .lead { position: absolute; width: 1px; background: var(--text-dim); pointer-events: none; }
  .label.dim { color: var(--text-soft); background: rgb(3 4 5 / 0.72); }
  .label.hot { color: var(--bg); background: var(--text-soft); font-weight: 600; z-index: 1; }
  .label.sel { color: var(--bg); background: #fff; font-weight: 600; z-index: 2; }
  .hud { position: absolute; left: 16px; right: 16px; bottom: 12px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px; font: 500 12px/1.2 var(--mono); color: var(--text-soft); pointer-events: none; }
  .hint { background: rgb(3 4 5 / 0.78); padding: 6px 8px; border-radius: 3px; }
  .modes { display: flex; pointer-events: auto; border: 1px solid var(--line-strong); border-radius: 3px; overflow: hidden; }
  .modes button { all: unset; cursor: pointer; padding: 9px 10px; font: 500 12px/1 var(--sans); color: var(--text-dim); background: rgb(3 4 5 / 0.7); }
  .modes button { transition: color 150ms ease, background-color 150ms ease; }
  .modes button + button { border-left: 1px solid var(--line-strong); }
  .modes button[aria-checked="true"] { color: var(--bg); background: var(--text-soft); }
  .modes button:focus-visible { outline: 2px solid var(--focus); outline-offset: -2px; }
  .panel { position: absolute; top: 16px; left: 16px; width: min(360px, calc(100% - 32px)); }
  .fail { position: absolute; inset: 0; display: grid; place-items: center; padding: 24px; text-align: center; color: var(--text-dim); margin: 0; }
  @media (max-width: 700px) {
    .map { height: 380px; min-height: 0; }
    .panel { position: static; width: auto; padding: 12px 16px 16px; }
  }
</style>
