# Submission texts (EN to submit, PT to understand)

The **English** text is what goes on the form. The *Português* text is only there so you know what you are signing; do not submit it. Check every number against the live app before you send.

---

## Project name
**EN:** Lunar Landing Site Navigator

## Team
**EN:** Quiral Labs

---

## Summary

**EN**

Lunar Landing Site Navigator helps mission planners choose where and when to land near the lunar south pole. It shows, hour by hour, when the Sun is up for power and when Earth is in view for a direct radio link, over the real terrain horizon of each site.

- **Sun and Earth positions** come from NASA's SPICE ephemerides.
- **The terrain** comes from LRO's LOLA elevation model.
- **Comparison:** you can compare up to three sites.
- **Any point:** you can click any point on a 3D map and get results in under a second.

Our results match JPL Horizons to within 0.005° and NASA's PGDA illumination maps to within 1.5 percentage points on average.

> *Português:* O Lunar Landing Site Navigator ajuda planejadores de missão a escolher onde e quando pousar perto do polo sul lunar. Ele mostra, hora a hora, quando o Sol está acima do horizonte (energia) e quando a Terra está à vista (link de rádio direto), considerando o horizonte real do relevo de cada local.
> - **Posições do Sol e da Terra:** vêm das efemérides SPICE da NASA.
> - **Relevo:** vem do modelo de elevação LOLA, da LRO.
> - **Comparação:** dá para comparar até três locais.
> - **Qualquer ponto:** dá para clicar em qualquer ponto de um mapa 3D e ter o resultado em menos de um segundo.
>
> Nossos resultados batem com o JPL Horizons dentro de 0,005° e com os mapas de iluminação PGDA da NASA com diferença média de 1,5 ponto percentual.

---

## Links
- **Project / website:** https://marcelin1555.github.io/lunar-landing-site-navigator/
- **Code:** https://github.com/marcelin1555/lunar-landing-site-navigator
- **Demo video:** *(fill in after upload)*

---

## Project details

### What does it do?
**EN**

Near the lunar south pole the Sun stays within a few degrees of the horizon, and Earth wobbles above and below it. A hill 10 km away can therefore decide whether a lander has power or can talk to Earth. Flat-horizon estimates are not enough.

Our tool:
1. **Builds the real horizon.** It computes a 360° horizon for each site from NASA's LOLA terrain, including the Moon's curvature.
2. **Tracks the Sun and Earth.** It computes their positions every hour from November 2026 to December 2028.
3. **Reports what a planner needs:**
   - how much of the Sun's disk is visible;
   - whether Earth is in view;
   - when the next sunset or Earthset comes;
   - how long the longest night lasts.

You can:
- pick one of 10 candidate sites;
- search a crater name;
- type coordinates;
- click the 3D map.

You can also compare up to three sites for the next 30 days from any date.

A month-by-month strip shows, for any site, the share of hours with Sun, with Earth and with both in every month from November 2026 to December 2028. If the landing slips, you see at once which month still works: at Malapert, Sun and Earth together go from 37% of hours in April 2028 to 80% in October 2028.

For students and the public, a four-step tour, "Why the south pole is hard", explains why the pole is so unlike Earth: the Sun circles the horizon instead of rising, a few kilometres separate constant light from permanent shadow, Earth hides behind hills, and nights last days. Each step has a "Show me" button that sets the app to the case that proves it.

> *Português:* Perto do polo sul lunar o Sol fica sempre a poucos graus do horizonte, e a Terra oscila acima e abaixo dele. Uma colina a 10 km pode decidir se uma sonda tem energia ou consegue falar com a Terra. Estimativas com horizonte plano não bastam.
>
> Nossa ferramenta:
> 1. **Monta o horizonte real.** Calcula um horizonte de 360° para cada local a partir do relevo LOLA da NASA, incluindo a curvatura da Lua.
> 2. **Acompanha o Sol e a Terra.** Calcula a posição deles a cada hora, de novembro de 2026 a dezembro de 2028.
> 3. **Mostra o que o planejador precisa:**
>    - quanto do disco do Sol está visível;
>    - se a Terra está à vista;
>    - quando vem o próximo pôr do Sol ou da Terra;
>    - quanto dura a noite mais longa.
>
> Dá para:
> - escolher um dos 10 locais candidatos;
> - buscar o nome de uma cratera;
> - digitar coordenadas;
> - clicar no mapa 3D.
>
> Também dá para comparar até três locais nos próximos 30 dias a partir de qualquer data.
>
> Uma faixa mês a mês mostra, para qualquer local, a fração das horas com Sol, com Terra e com os dois em cada mês de novembro de 2026 a dezembro de 2028. Se o pouso atrasar, dá para ver na hora qual mês ainda serve: em Malapert, Sol e Terra juntos vão de 37% das horas em abril de 2028 a 80% em outubro de 2028.
>
> Para estudantes e o público, um tour de quatro passos, "Why the south pole is hard", explica por que o polo é tão diferente da Terra: o Sol gira em volta do horizonte em vez de nascer, poucos quilômetros separam luz constante de sombra permanente, a Terra se esconde atrás dos morros e as noites duram dias. Cada passo tem um botão "Show me" que coloca o app no caso que prova a ideia.

### What did we learn? (key finding)
**EN**

More sunlight does not always mean a better site. For a landing on 14 November 2026:
- **Shackleton Rim:** sunlit 87% of the time overall, but only 13 days with both Sun and Earth in the next 30 days.
- **Malapert Massif:** 22 days with both, because Earth stays in view much longer.
- **Shackleton crater floor**, only about 10 km from the rim: 0% Sun and 0% Earth in two years. It is a permanently shadowed region, where water ice may exist.

> *Português:* Mais Sol nem sempre quer dizer local melhor. Para um pouso em 14 de novembro de 2026:
> - **Shackleton Rim:** iluminada 87% do tempo no total, mas só 13 dias com Sol e Terra juntos nos próximos 30.
> - **Malapert Massif:** 22 dias com os dois, porque a Terra fica à vista por muito mais tempo.
> - **Fundo da cratera Shackleton**, a só uns 10 km da borda: 0% de Sol e 0% de Terra em dois anos. É uma região de sombra permanente, onde pode haver gelo de água.

### How does it work?
**EN**
1. **Terrain.** The NASA LOLA polar elevation model (120 m per pixel) is used to cast 720 rays from each site, up to 150 km. The highest terrain angle in each direction is the horizon.
2. **Sun and Earth.** NASA/NAIF SPICE kernels (DE440) give their direction from the site every hour.
3. **Visibility.** We compare the Sun and Earth with the horizon: the fraction of the Sun's disk above it, and whether Earth's center is above it.
4. **Browser.** The web app is static: Svelte, D3 and three.js. For custom points it repeats the same calculation in the browser on a 240 m version of the terrain.

> *Português:*
> 1. **Relevo.** O modelo de elevação polar LOLA da NASA (120 m por pixel) é usado para lançar 720 raios a partir de cada local, até 150 km. O maior ângulo do relevo em cada direção é o horizonte.
> 2. **Sol e Terra.** Os kernels SPICE da NASA/NAIF (DE440) dão a direção deles a partir do local, a cada hora.
> 3. **Visibilidade.** Comparamos o Sol e a Terra com o horizonte: a fração do disco do Sol acima dele, e se o centro da Terra está acima dele.
> 4. **Navegador.** O app web é estático: Svelte, D3 e three.js. Para pontos personalizados, ele repete o mesmo cálculo no navegador, num relevo de 240 m.

### How do we know it is right?
**EN**
- **Sun and Earth positions** match JPL Horizons within 0.005°. These checks are automated tests.
- **Sunlit share** matches NASA's PGDA average illumination maps within 1.5 percentage points on average, across the 10 sites.
- **Horizon code** is tested on two cases with exact answers: a smooth sphere, and a wall of known height.
- **Limits are stated in the app:**
  - the terrain resolution is 120 m (240 m for custom points);
  - there is no atmosphere, so no refraction;
  - Earth counts as visible when its center is above the horizon.

> *Português:*
> - **Posições do Sol e da Terra:** batem com o JPL Horizons dentro de 0,005°. Essas verificações são testes automáticos.
> - **Tempo iluminado:** bate com os mapas de iluminação média PGDA da NASA, com diferença média de 1,5 ponto percentual nos 10 locais.
> - **Código do horizonte:** é testado em dois casos com resposta exata, uma esfera lisa e uma parede de altura conhecida.
> - **Limites declarados no app:**
>   - a resolução do relevo é de 120 m (240 m para pontos personalizados);
>   - não há atmosfera, então não há refração;
>   - a Terra conta como visível quando o centro dela está acima do horizonte.

### Why does it matter?
**EN**

Artemis missions plan to land near the south pole. A planner can use this tool to:
- choose a landing date that gives the most days with both power and a direct link;
- see the exact hour when the Sun or Earth will disappear;
- check any spot in seconds, without installing special software.

> *Português:* As missões Artemis planejam pousar perto do polo sul. Um planejador pode usar esta ferramenta para:
> - escolher uma data de pouso que dê mais dias com energia e link direto ao mesmo tempo;
> - ver a hora exata em que o Sol ou a Terra vão sumir;
> - verificar qualquer ponto em segundos, sem instalar nenhum software especial.

---

## NASA data used
**EN**
- **LRO LOLA polar elevation model `LDEM_75S_120M`** (PDS Geosciences Node). It is the terrain behind every horizon.
- **NASA PGDA average solar and Earth visibility maps** (product 69, Mazarico et al. 2011). We use them for validation and to color the 3D map.
- **NASA PGDA LOLA 5 m site regions** (Barker et al. 2021). We use them to place 7 of the 10 sites.
- **NASA/NAIF SPICE kernels** (DE440 and lunar frames). They give the Sun and Earth positions.
- **JPL Horizons.** We use it for independent validation.

> *Português:*
> - **Modelo de elevação polar LOLA da LRO, `LDEM_75S_120M`** (PDS Geosciences Node). É o relevo por trás de todo horizonte.
> - **Mapas de visibilidade média do Sol e da Terra do PGDA da NASA** (produto 69, Mazarico et al. 2011). Usamos para validação e para colorir o mapa 3D.
> - **Regiões de pouso LOLA de 5 m do PGDA da NASA** (Barker et al. 2021). Usamos para posicionar 7 dos 10 locais.
> - **Kernels SPICE da NASA/NAIF** (DE440 e referenciais lunares). Dão as posições do Sol e da Terra.
> - **JPL Horizons.** Usamos para validação independente.

## Other data
**EN**
- **IAU Gazetteer of Planetary Nomenclature (USGS):** crater names and centers.
- **LPSC 2024 abstract #1695 and LPSC 2025 abstract #2742:** published coordinates for three sites.

> *Português:*
> - **Gazetteer de Nomenclatura Planetária da IAU (USGS):** nomes e centros das crateras.
> - **Resumos LPSC 2024 nº 1695 e LPSC 2025 nº 2742:** coordenadas publicadas de três locais.

---

## Use of AI
**EN**

We used an AI assistant (Claude, by Anthropic) for:
- research;
- discussing the architecture;
- generating and reviewing code;
- helping translate this written submission from Portuguese to English.

The author made all design decisions, checked the data and results against NASA references (JPL Horizons and PGDA maps), and reviewed the final work. No images or video in this project were generated by AI: the demo is a screen recording of the real app.

> *Português:* Usamos um assistente de IA (Claude, da Anthropic) para:
> - pesquisa;
> - discutir a arquitetura;
> - gerar e revisar código;
> - ajudar a traduzir este texto da submissão do português para o inglês.
>
> O autor tomou todas as decisões de design, conferiu os dados e resultados contra referências da NASA (JPL Horizons e mapas PGDA) e revisou o trabalho final. Nenhuma imagem ou vídeo deste projeto foi gerado por IA: a demo é uma gravação de tela do app real.

---

## References
Copy the "References" section of `README.md`. It lists every dataset, paper, library and font.

> *Português:* Copie a seção "References" do README.md. Ela lista todos os dados, artigos, bibliotecas e fontes.
