# Perguntas prováveis (PT para entender, EN se precisar responder em inglês)

### 1. O que o app faz, em uma frase?
**PT:** Mostra, hora a hora, quando o Sol e a Terra aparecem acima do relevo real em locais de pouso no polo sul da Lua.
**EN:** It shows, hour by hour, when the Sun and Earth are above the real terrain at south-pole landing sites.

### 2. Por que o Sol e a Terra importam?
**PT:** Sol é energia (painel solar). Terra à vista é comunicação direta por rádio, sem satélite de retransmissão.
**EN:** Sun means power. Earth in view means a direct radio link, with no relay satellite.

### 3. De onde vêm os dados?
**PT:** O relevo vem do altímetro laser LOLA, da sonda LRO da NASA. As posições do Sol e da Terra vêm do SPICE, o sistema de efemérides da NASA/JPL.
**EN:** Terrain from NASA's LRO LOLA laser altimeter. Sun and Earth positions from NASA/JPL SPICE.

### 4. Como vocês sabem que está certo?
**PT:** Conferimos de dois jeitos.
- As posições do Sol e da Terra batem com o JPL Horizons até 0,005°.
- A porcentagem de tempo com Sol bate com os mapas oficiais de iluminação da NASA (PGDA), com diferença média de 1,5 ponto.

**EN:** The Sun and Earth positions match JPL Horizons within 0.005°, and the sunlit share matches NASA's PGDA maps within 1.5 points on average.

### 5. Por que a diferença de 1,5 ponto com o PGDA?
**PT:** O PGDA é uma média de 18,6 anos (um ciclo completo da órbita lunar); a nossa janela é de 2 anos. Também usamos observador a 2 m do chão.
**EN:** PGDA averages 18.6 years; we cover 2 years. We also put the observer 2 m above the ground.

### 6. Por que 120 m de resolução e não 5 m?
**PT:** O horizonte depende de montanhas a até 150 km de distância, e o mapa de 5 m só cobre cerca de 16 km. O de 120 m cobre todo o polo. O ponto fraco é o relevo bem perto do local, e isso está escrito no app como limite.
**EN:** The horizon depends on terrain up to 150 km away. The 5 m maps only cover about 16 km; the 120 m map covers the whole pole.

### 7. E os pontos que o usuário clica?
**PT:** O próprio navegador calcula, num relevo de 240 m, em menos de 1 segundo. Testamos contra os 10 locais e a diferença média é de 1,5 ponto.
**EN:** The browser computes them on a 240 m terrain in under a second; tested against the 10 sites, 1.5 points on average.

### 8. Por que o Malapert ganha da Shackleton Rim se tem menos Sol?
**PT:** A Shackleton Rim tem mais Sol no total, mas fica muito perto do polo e vê a Terra pouco. O Malapert fica mais longe do polo e, por ser alto, vê a Terra por mais tempo. Para ter energia e comunicação ao mesmo tempo, o Malapert ganha (22 dias contra 13, pousando em 14/11/2026).
**EN:** Shackleton Rim has more Sun overall, but sees Earth less. Malapert is high and farther from the pole, so Earth stays in view longer.

### 9. Por que o fundo da cratera Shackleton dá 0%?
**PT:** As paredes da cratera tapam o Sol, que no polo nunca sobe muito. Essa é a "sombra permanente", e é onde a NASA acha que existe gelo de água.
**EN:** The crater walls block the low Sun. It is a permanently shadowed region, where water ice may exist.

### 10. Tem refração? Atmosfera?
**PT:** Não, a Lua não tem atmosfera. Por isso o cálculo geométrico é exato.
**EN:** No, the Moon has no atmosphere, so pure geometry is correct.

### 11. Vocês usaram IA?
**PT:** Sim, e está declarado. A IA ajudou na pesquisa, na arquitetura, no código e na tradução. As decisões e a validação foram minhas. Nenhuma imagem ou vídeo foi gerado por IA.
**EN:** Yes, and it is declared: research, architecture, code and translation help. Decisions and validation were mine.

### 12. O que vocês fariam com mais tempo?
**PT:**
- Usar o relevo de 5 m perto do local.
- Considerar a altura da antena para o link com a Terra.
- Incluir satélites de retransmissão, como a Gateway.
- Estender a janela além de 2028.

**EN:** Use the 5 m terrain near the site, add antenna height, add relay satellites, extend beyond 2028.
