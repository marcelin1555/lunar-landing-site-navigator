<script lang="ts">
  import { onMount } from "svelte";
  import * as THREE from "three";
  import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
  import { fromStereo, stereoSouth } from "./free";
  import type { SiteIndex } from "./data";

  let { sites, selected, sunLon, busy = false, onpick, onselect }: {
    busy?: boolean;
    sites: SiteIndex[];
    selected: string;
    sunLon: number | null; // longitude of the subsolar direction, drives the light azimuth
    onpick: (lat: number, lon: number) => void;
    onselect: (id: string) => void;
  } = $props();

  const EXAG = 4; // vertical exaggeration
  const base = import.meta.env.BASE_URL;
  let host: HTMLDivElement;
  let width = $state(400);
  let height = $state(440);
  let hover = $state<{ lat: number; lon: number } | null>(null);
  let hoverPin = $state<string | null>(null);
  let labels = $state<{ id: string; name: string; x: number; y: number; on: boolean; custom: boolean }[]>([]);
  let failed = $state("");

  let scene: THREE.Scene, camera: THREE.PerspectiveCamera, renderer: THREE.WebGLRenderer, controls: OrbitControls;
  let mesh: THREE.Mesh, sun: THREE.DirectionalLight, pins: THREE.Group;
  let heightAt: (x: number, y: number) => number = () => 0;
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
    camera = new THREE.PerspectiveCamera(40, width / height, 1, 5000);
    camera.position.set(0, 430, 330);
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch {
      failed = "3D view needs WebGL, which this browser does not provide. Use the table or coordinates instead.";
      return;
    }
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.setSize(width, height);
    host.prepend(renderer.domElement);
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.maxPolarAngle = Math.PI * 0.47;
    controls.minDistance = 60;
    controls.maxDistance = 1200;

    scene.add(new THREE.HemisphereLight(0x9fb4d0, 0x0a0e14, 0.55));
    sun = new THREE.DirectionalLight(0xfff1d6, 2.2);
    scene.add(sun, sun.target);
    pins = new THREE.Group();
    scene.add(pins);

    load().then(({ meta, h, ill }) => {
      if (disposed) return;
      const n = meta.n, km = meta.res / 1000, size = n * km;
      const geo = new THREE.PlaneGeometry(size, size, n - 1, n - 1);
      geo.rotateX(-Math.PI / 2); // row 0 (max stereo y) ends at z = -size/2, so scene z = -y
      const pos = geo.attributes.position as THREE.BufferAttribute;
      const colors = new Float32Array(n * n * 3);
      const dark = new THREE.Color("#06080c"), lit = new THREE.Color("#ddd6c6"), c = new THREE.Color();
      for (let k = 0; k < n * n; k++) {
        pos.setY(k, (h[k] / 1000) * EXAG);
        c.copy(dark).lerp(lit, Math.pow(ill[k] / 255, 1.3));
        colors.set([c.r, c.g, c.b], k * 3);
      }
      geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
      geo.computeVertexNormals();
      mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 1, metalness: 0 }));
      scene.add(mesh);
      heightAt = (x, y) => {
        const col = Math.round((x / 1000 - (-size / 2 + km / 2)) / km), row = Math.round((size / 2 - km / 2 - y / 1000) / km);
        return row >= 0 && col >= 0 && row < n && col < n ? (h[row * n + col] / 1000) * EXAG : 0;
      };
      // latitude rings for orientation
      for (const lat of [-88, -85, -82]) {
        const r = Math.hypot(...stereoSouth(lat, 0)) / 1000;
        const ring = new THREE.LineLoop(
          new THREE.BufferGeometry().setFromPoints(Array.from({ length: 128 }, (_, k) => new THREE.Vector3(r * Math.sin((k / 128) * 2 * Math.PI), 0, -r * Math.cos((k / 128) * 2 * Math.PI)))),
          new THREE.LineBasicMaterial({ color: 0x4fa8e8, transparent: true, opacity: 0.25, depthTest: false }),
        );
        ring.position.y = 30;
        scene.add(ring);
      }
      updatePins();
    }).catch(() => (failed = "Could not load the 3D terrain. Use the table or coordinates instead."));

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
        if (o instanceof THREE.Mesh || o instanceof THREE.Line) { o.geometry.dispose(); (o.material as THREE.Material).dispose(); }
      });
    };
  });

  function scenePos(lat: number, lon: number) {
    const [x, y] = stereoSouth(lat, lon);
    return new THREE.Vector3(x / 1000, heightAt(x, y), -y / 1000);
  }

  function updatePins() {
    if (!pins || !mesh) return;
    pins.children.forEach((p) => { (p as THREE.Mesh).geometry.dispose(); ((p as THREE.Mesh).material as THREE.Material).dispose(); });
    pins.clear();
    for (const s of sites) {
      const on = s.id === selected;
      const pin = new THREE.Mesh(
        new THREE.CylinderGeometry(on ? 2.4 : 1.6, 0.2, 26, 12),
        new THREE.MeshBasicMaterial({ color: on ? 0xf2b544 : s.custom ? 0x4fa8e8 : 0xc2cad6 }),
      );
      pin.position.copy(scenePos(s.lat, s.lon)).add(new THREE.Vector3(0, 13, 0));
      pin.userData.id = s.id;
      pins.add(pin);
    }
  }

  function projectLabels() {
    if (!pins) return;
    const v = new THREE.Vector3();
    labels = pins.children.map((p) => {
      v.copy(p.position).add(new THREE.Vector3(0, 14, 0)).project(camera);
      const s = sites.find((q) => q.id === p.userData.id)!;
      return { id: s.id, name: s.name, x: (v.x * 0.5 + 0.5) * width, y: (-v.y * 0.5 + 0.5) * height, on: (s.id === selected || s.id === hoverPin) && v.z < 1, custom: !!s.custom };
    });
  }

  $effect(() => {
    sites; selected;
    updatePins();
  });

  $effect(() => {
    if (!sun || sunLon === null) return;
    const a = (sunLon * Math.PI) / 180, el = (25 * Math.PI) / 180; // azimuth is real, elevation exaggerated for relief
    sun.position.set(Math.sin(a) * Math.cos(el) * 1000, Math.sin(el) * 1000, -Math.cos(a) * Math.cos(el) * 1000);
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
    const [lat, lon] = fromStereo(t.point.x * 1000, -t.point.z * 1000);
    return { kind: "ground", lat, lon };
  }

  let down: { x: number; y: number } | null = null;
  function onDown(e: PointerEvent) { down = { x: e.clientX, y: e.clientY }; }
  function onMove(e: PointerEvent) {
    if (!renderer) return;
    const h = hit(e);
    hover = h?.kind === "ground" ? h : null;
    hoverPin = h?.kind === "pin" ? h.id : null;
    renderer.domElement.style.cursor = h ? "pointer" : "grab";
  }
  function onUp(e: PointerEvent) {
    if (!down || Math.hypot(e.clientX - down.x, e.clientY - down.y) > 4) return; // it was a drag
    const h = hit(e);
    if (!h) return;
    if (h.kind === "pin") onselect(h.id);
    else onpick(Math.round(h.lat * 1e4) / 1e4, Math.round(h.lon * 1e4) / 1e4);
  }
</script>

<div class="map" bind:this={host} bind:clientWidth={width} bind:clientHeight={height} onpointerdown={onDown} onpointermove={onMove} onpointerup={onUp}
  role="application" aria-label="3D terrain of the lunar south pole. Click a pin to select a site, or click the terrain to compute a new point.">
  {#if failed}
    <p class="fail">{failed}</p>
  {/if}
  {#each labels as l (l.id)}
    {#if l.on}<span class="label" style:left="{l.x}px" style:top="{l.y}px">{l.name}</span>{/if}
  {/each}
  <div class="hud">
    <span>{busy ? "Computing point…" : hover ? `${Math.abs(hover.lat).toFixed(3)}°S ${hover.lon.toFixed(3)}°E` : "Drag to orbit · click a pin or the terrain"}</span>
    <span class="legend"><i class="ramp"></i>PGDA mean sunlight · 4× relief</span>
  </div>
</div>

<style>
  .map { position: relative; height: 440px; background: radial-gradient(ellipse at 50% 30%, #121a26, var(--bg) 70%); border-bottom: 1px solid var(--line); touch-action: none; overflow: hidden; }
  .map :global(canvas) { display: block; }
  .label { position: absolute; transform: translate(-50%, -100%); font: 600 12px/1 var(--sans); color: var(--bg); background: var(--sun); padding: 4px 6px; border-radius: 3px; pointer-events: none; white-space: nowrap; }
  .hud { position: absolute; left: 10px; right: 10px; bottom: 8px; display: flex; justify-content: space-between; gap: 8px; font: 500 11px/1.2 var(--mono); color: var(--text-dim); pointer-events: none; }
  .legend { display: flex; align-items: center; gap: 6px; }
  .ramp { width: 36px; height: 6px; border-radius: 1px; background: linear-gradient(90deg, #06080c, #ddd6c6); outline: 1px solid var(--line-strong); }
  @media (max-width: 600px) { .map { height: 320px; } .legend { display: none; } }
  .fail { position: absolute; inset: 0; display: grid; place-items: center; padding: 24px; text-align: center; color: var(--text-dim); margin: 0; }
</style>
