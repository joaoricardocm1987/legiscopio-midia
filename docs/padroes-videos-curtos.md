# Padrões dos vídeos curtos do Legiscópio

O padrão da semana fica em `config/padrao_semana.json` (`"padrao": 1` ou `2`). Ele vale para os vídeos curtos da rotina diária: o Short do YouTube (`short.json`), o Resumo de ~2 min dos Reels e do TikTok (`resumo.json`) e o Short avulso. Não muda o vídeo longo, os posts, a agenda nem a série "Quem Faz o Quê?".

As regras editoriais da rotina (factual, apartidário, dois lados, números de fonte oficial, sem nome de parlamentar) valem nos dois padrões.

---

## Regra comum aos dois padrões — "O que está em jogo" (a partir de 13/11/2026)

Decisão do João: todo Short, Short avulso e Resumo dos Reels/TikTok mostra **o impacto de o tema do dia ser aprovado ou não**.

1. **Uma cena própria**, com o visual:
   `{"tipo": "lista", "titulo": "O que está em jogo", "itens": ["Se aprovar: <efeito concreto>", "Se não aprovar: <o que continua ou acontece>"]}`
   Cada item com até ~45 caracteres. Fala de 25 a 45 palavras.
2. **Onde entra:** logo depois do dado principal (2ª ou 3ª cena no Short; entre a 3ª e a 5ª no Resumo). Nunca na última cena.
3. **Adapte os rótulos à fase da proposta:**
   - em tramitação: "Se aprovar:" / "Se não aprovar:" (o que continua valendo hoje: a regra atual, o valor atual, o prazo atual);
   - medida provisória: "Se o Congresso aprovar:" (vira lei de vez) / "Se não votar até DD/MM:" (perde a validade e o que volta a valer);
   - já aprovada ou sancionada: "O que muda agora:" / "Como era antes:";
   - rejeitada ou arquivada: "O que fica como está:" / "O que mudaria se passasse:".
4. **Concreto e para o cidadão:** bolso, trabalho, serviço público, prazo, quem é afetado. Ex.: "Se aprovar: teto do MEI sobe para R$ 110 mil" / "Se não aprovar: o teto segue em R$ 81 mil".
5. **Só com base no texto da proposta, em dados oficiais ou em estimativas citadas.** Projeções de terceiros vêm atribuídas na fala ("segundo o governo", "pela estimativa da IFI"). Sem adivinhação, sem adjetivo de juízo e sem dizer se aprovar é bom ou ruim: os dois lados têm o mesmo peso e o mesmo tom.
6. **Legendas:** a legenda do Reel (`legenda` do post.json) e a descrição do Short no YouTube ganham uma linha logo depois do resumo do fato: `O que está em jogo: se aprovar, <efeito>; se não, <o que continua>.`

---

## Padrão 1 — Resumo de notícia

O formato usado até 08/11/2026. Segue exatamente os PASSOS 4b, 4d e 4e da rotina diária (mais a regra comum acima):

- Abre no fato: "<Tema> em um minuto!" com visual `numero` ou `comparacao`.
- Selo padrão ("RESUMO EM 1 MINUTO" / "RESUMO EM 2 MINUTOS").
- Short: 135 a 150 palavras (~1 min). Resumo: 270 a 320 palavras (~2 min).
- Fecha com o visual `cta` chamando para o vídeo completo no canal.

---

## Padrão 2 — Estilo das referências ("como funciona")

Inspirado em 9 Reels de 33 mil a 300 mil visualizações analisados em 09/11/2026 (`videos/referencias/`). Modelo pronto: `videos/reel-ranking-propostas/short.json`.

O tema continua sendo o do dia (PASSO 2 da rotina). Muda a forma de contar.

### Regras

1. **Selo fixo com o tema** no campo `"selo"` do JSON, em até 24 caracteres e caixa alta (ex.: `"MP DAS BETS"`, `"RANKING DAS PROPOSTAS"`). Ele fica no topo o vídeo inteiro.
2. **Gancho na primeira frase (até 3 s)**, de um destes tipos:
   - situação que a pessoa já viveu: "Sabe quando o jornal diz que a MP trancou a pauta?";
   - ideia comum corrigida: "Quase todo mundo acha que X. Não é bem assim." (só quando a correção for factual e verificável);
   - promessa de lista: "As 3 coisas que mudam pra você com…".
   Nunca "Olá", nunca "<Tema> em um minuto". A 1ª cena pode usar o visual `capa` (título curto + subtítulo).
3. **Uma estrutura visível**, escolhida conforme o tema:
   - **Ranking ou contagem** ("em 3º lugar…", "primeiro… segundo…"): visual `numero` com `valor` = posição ou número-chave;
   - **Como funciona**: o mecanismo passo a passo (visual `etapas`, `numero`, `comparacao`);
   - **Cadeia "Mas… Então…"**: cada passo dá nome a um conceito ("Essa é a urgência."), com o nome no título do visual.
   O título de cada cena funciona como rótulo de capítulo (ex.: "3º · Lei complementar").
4. **Duração**: Short de 60 a 90 s (160 a 230 palavras, 6 a 9 cenas). Resumo dos Reels/TikTok de 90 a 130 s (230 a 320 palavras, 8 a 12 cenas). Frases curtas; cada cena com 15 a 35 palavras.
5. **Os dois lados** continuam obrigatórios quando houver debate: uma cena própria, atribuída e equilibrada.
6. **Fechamento com comentário de uma palavra**: a última cena usa o visual `texto` com `"titulo": "Comenta aí"` e um texto curto que termina com `www.legiscopio.com.br/baixar`. A fala faz uma pergunta neutra, fácil e pessoal ("Isso te afeta? Comenta SIM ou NÃO.", "Comenta EU SABIA ou APRENDI.", "Qual dessas você já ouviu no jornal sem entender?"), e depois: "E pra acompanhar essa proposta, baixe o Legiscópio. O link está na legenda." Nos dias com vídeo longo, acrescente: "O vídeo completo está no canal do Legiscópio no YouTube." Não use o visual `cta` no Padrão 2.
7. **Legendas e 1º comentário**: a legenda do Reel repete a pergunta do fechamento logo antes da linha do app, e o `firstCommentText` do Reel no Instagram leva a mesma pergunta com 👇.

### Exemplo de abertura (tema: MP das bets entrando em urgência)

- Selo: `MP DAS BETS`
- Cena 1 (`capa`): "Sabe quando o jornal diz que uma medida provisória trancou a pauta? Parece que o Congresso parou. Não parou. A partir desta segunda, é isso que acontece com a MP das bets."
- Cena 2 (`numero`, "Dia 46"): "A MP vale desde vinte e cinco de setembro. No quadragésimo sexto dia sem votação, ela entra em regime de urgência…"
- Cena 3 (`lista`, "O que está em jogo"): "Se o Congresso aprovar até 23/11: a proibição vira lei" / "Se não votar a tempo: a MP perde a validade".

---

## Histórico de uso

| Semana | Padrão | Observações |
| --- | --- | --- |
| 09/11/2026 | 2 | Primeira semana do Padrão 2. A partir de 13/11, cena "O que está em jogo" nos dois padrões. |
