# Product: Lunar Landing Site Navigator

Owner: Quiral Labs (Marcello M.). Built for NASA Space Apps 2026.

## Users
- **Primary:** a mission planner comparing lunar south-pole landing sites and dates.
- **Secondary:** hackathon judges, who decide in under a minute whether the tool is real.
- **Later, if there is time:** the public and educators.

## Job
For each site and date, the app answers four questions:
1. When will the Sun be up over the real terrain horizon?
2. When will the Earth be visible, for direct communication?
3. How long is the longest darkness?
4. Which site is best?

## Product truths
- Every number comes from NASA data: the LOLA DEM, NAIF SPICE ephemerides, and PGDA for validation.
- Sun and Earth positions are validated against JPL Horizons to 0.005°.
- Energy is shown as hours of sunlight, never in watts.
- Limits are always stated:
  - the DEM resolution is 120 m;
  - there is no refraction, since the Moon has no air;
  - Earth counts as visible when its center is above the horizon.
- The default date is today, so the app is live.

## Surface mode
The app is **Operate**: a tool. Scanability and precision come before expression.

## Visual direction (chosen by owner)
A mission-control console:
- dark, near-black blue background;
- monospaced numbers;
- one warm color reserved for the Sun and one cool color for the Earth;
- dense and precise.

## Language
English UI, as the submission rules require.
