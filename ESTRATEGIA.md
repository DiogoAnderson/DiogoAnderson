# Plano de crescimento orgânico — Diogo Angioleti

Dados: Metricool, 10/07 a 09/10/2026 (Instagram @diogoanderson, TikTok @diogoangioletti, YouTube). O LinkedIn fica fora do Metricool por decisão do Diogo.

> Este plano virou o sistema **Master Growth Angioletti**: veja [`MASTER-GROWTH.md`](MASTER-GROWTH.md).
Os números abaixo saem de `python -m crescimento.diagnostico`, que roda sobre os CSVs em `crescimento/dados/`.

## 1. O que os seus dados dizem

| Rede | Seguidores | Movimento recente | Mediana por post |
|---|---|---|---|
| Instagram | 7.217 | estável/caindo (7.238 em 26/09) | 752 views por reel |
| TikTok | 2.522 | parado (2.517 em 26/09) | 146 views orgânicas |
| YouTube | 807 inscritos | **+26% em 11 dias** (639 em 26/09) | — |
| LinkedIn | — | fora do Metricool (manual) | — |

**O "teto dos 300" tem nome.** Toda rede mostra o vídeo primeiro a um grupo pequeno (parte dos seus seguidores e alguns desconhecidos). Se esse grupo assiste e repassa, o vídeo vai para o próximo grupo; se arrasta para cima, o vídeo para ali. Quando você paga, pula essa prova. Quando não paga, o vídeo precisa passar nela. Por isso o trabalho é passar na prova, e os seus dados mostram onde você está reprovando:

1. **Os 3 primeiros segundos.** No Instagram, a mediana dos seus reels segura só 35,6% das pessoas depois de 3 segundos. Os 10 reels que passaram de 45% tiveram mediana de **1.314 views**; os que ficaram abaixo de 35% tiveram **700**. Quase o dobro com o mesmo vídeo e um começo diferente.
2. **Ninguém manda para ninguém.** 38 dos 76 reels tiveram **zero** compartilhamentos. Envio por DM é o sinal que o Instagram mais usa para mostrar um vídeo a quem não te segue. Os que mais circularam têm o mesmo DNA: alguém específico para quem mandar.
   - Tania Zanella, primeira presidente do Sistema OCB — 27 envios (o público dela repassou)
   - Golpe das vagas home office — 15 (alerta útil: "manda para sua mãe")
   - Rancor adoece, perdão cura — 15 (estudo + emoção)
   - Líder termômetro ou termostato — 14 (manda para o chefe)
   - "Manda para a criaturinha de Jesus" — 14 (o pedido de envio estava no próprio vídeo)
3. **Vídeo longo no TikTok.** Metade dos seus vídeos lá passa de 3 minutos e tem mediana de 119 views. Os de 31 a 90 segundos têm 226. Os episódios do Dr. Di são ótimos, mas entram inteiros no lugar errado.
4. **Post pessoal fala com quem já te segue.** Mãe, livro, viagem e tatuagem têm boas views (mediana 1.205 no IG) e quase nenhum envio (6 no total). É conteúdo de relacionamento: mantém a base aquecida e não traz gente nova. Lugar dele é o Stories e o "close friends", com um ou outro no feed.
5. **Radar de notícias rende pouco.** Mediana de 468 views no IG e 6 a 122 no TikTok. Notícia que qualquer portal dá não tem motivo para ser repassada a partir de você. Mantenha o Radar, mas como carrossel e no LinkedIn, onde o público de cooperativa lê.
6. **Horário pesa pouco.** Madrugada, manhã, tarde e noite ficaram entre 736 e 819 views de mediana. Vale publicar no pico (10h e 18h, quarta a sexta), mas o gancho vale muito mais do que a hora.

**O que está crescendo sozinho:** o YouTube. Abra o YouTube Studio > Alcance > Origens de tráfego e veja se o salto veio dos Shorts do Dr. Di ou de anúncio. Se for Shorts, é a rede para dobrar a aposta.

## 2. O que não fazer (e por quê)

Robôs de seguir/deixar de seguir, compra de seguidores, grupos automáticos de curtida, contas falsas e app que curte por você violam os termos de todas as quatro redes. Além do risco de bloqueio, eles **pioram** o alcance: seguidor que não assiste derruba a taxa de retenção do grupo de teste, e o vídeo seguinte estreia para gente que não liga para ele. Também não vale repostar vídeo com marca d'água de outra rede no Instagram: desde 2026 conteúdo pouco original perde a vitrine de recomendação.

Tudo abaixo é permitido, e a maior parte é gratuita.

## 3. As alavancas, da mais barata para a mais cara

### A. Passar na prova dos 3 segundos (custo zero)
- Gancho falado **e** escrito na tela no segundo zero, até 12 palavras, abrindo uma pergunta que só fecha assistindo. O `crescimento/ganchos.py` gera 5 variações por ideia.
- Corte o "bom dia, pessoal": comece na frase do meio.
- Meta: taxa de 3 segundos acima de 50% no IG; "assistiu vs. passou" acima de 70% no Shorts.

### B. Testar com desconhecidos sem gastar seguidores — Trial Reels
O Instagram deixa publicar um reel que aparece **só para não seguidores**. Se performar, você promove para o feed. Use às quartas e quintas, 18h, para testar o segundo gancho do vídeo do dia. O Metricool já agenda Trial Reel (`instagramData.type = "TRIAL_REEL"`).

### C. Pegar emprestado o público dos outros — Collab
O post em colaboração (co-autor) aparece no feed dos dois perfis, soma as curtidas e é o caminho mais rápido para quem não te conhece. Você já entrevista Confebras, OCB, Sicredi, Unicred, ABRH, HJ Conference, Tania Zanella, Telma Galletti, Heloisa Lopes. A entrevista com a Tania teve 27 envios **sem** collab. Daqui em diante, toda entrevista e todo evento sai como collab com o convidado e a instituição. O Metricool aceita `collaborators` no agendamento.

### D. Fazer o comentário trabalhar — palavra-chave + resposta automática
"Comenta CHECKLIST que eu te mando" gera comentário (sinal de ranking) e abre conversa no Direct, onde você entrega um material e capta o contato. Ferramenta: **ManyChat** (plano gratuito até 1.000 contatos) usa a API oficial da Meta, então é permitido. Material pronto você já tem: checklist do superendividamento, os episódios do Dr. Di, o capítulo do Smart Funny 2, a palestra "Quando o boleto bate o ponto".

### E. Busca, não só feed
- **TikTok:** fale a palavra de busca nos 3 primeiros segundos ("golpe do Pix", "como sair das dívidas", "13º salário") e escreva na legenda. O TikTok lê o áudio e o texto.
- **YouTube:** título de Short como busca + "vídeo relacionado" apontando para o episódio longo. Shorts e vídeos longos hoje são ranqueados separados, então o link manual é o que leva gente de um para o outro.
- **Instagram:** palavra-chave na primeira linha da legenda; o Instagram já indexa legenda na busca.

### F. LinkedIn: o seu público pagante (palestras, SIPAT, consultoria)
Por decisão sua, o LinkedIn fica fora do Metricool e é publicado à mão; os roteiros já trazem o post pronto.
- **Newsletter do LinkedIn**: cada edição notifica todos os seguidores, de graça. O Radar do Cooperativismo pode virar newsletter semanal.
- Texto nativo até 1.500 caracteres ou carrossel em PDF. Link só no primeiro comentário.
- Comentário substantivo nos primeiros 60 minutos em posts de OCB, Confebras, Sescoop e ABRH: seu nome aparece para o público deles.

### G. Uma ideia, quatro peças, quatro horários
A grade oficial é a sua (seg 10h Lições de Vida, ter 18h Radar Cooperativo, qua 10h Educação Financeira, qui 10h RH e Governança, sex 10h Doutor Di). Cada vídeo vira Reel no Instagram, corte de 60-90s no TikTok meia hora depois, Short no YouTube às 16h e texto no LinkedIn às 8h. Trial Reels às quartas e quintas, 18h. Veja `python -m crescimento.calendario`.

### H. O que você já tem e não está usando
- **Palestras:** QR code no último slide para o Instagram + "comenta PALESTRA" para receber os slides. Cada SIPAT com 100 pessoas vira dezenas de seguidores qualificados.
- **Lives:** o TikTok ainda dá alcance a quem faz live com regularidade, e cada live vira 4 a 6 cortes (`python -m crescimento.cortes live.mp4 live.srt`).
- **Canal de transmissão no Instagram e Canal no WhatsApp:** avisos de episódio novo chegam como notificação, sem depender do feed.

### I. Quando pagar (R$ 10 a 20 por dia, só quando valer)
Seus picos pagos (SIPAT no TikTok com 13 mil views, os dias de 14 a 19 mil de alcance no IG) não viraram seguidores na mesma proporção. Regra para o pouco que der para investir: impulsione **só** o post que já passou na prova orgânica (top 10% em envios na semana), com objetivo de visita ao perfil, por 3 dias. Dinheiro em vídeo que não segura 3 segundos compra views que não voltam.

## 4. O que fica automático e o que fica com você

| Tarefa | Quem faz | Como |
|---|---|---|
| Ler métricas e reorganizar o sistema toda segunda | Orquestrador semanal (Claude + Metricool) | `MASTER-GROWTH.md` |
| Escolher o post da semana para Trial Reel, collab ou impulsionar | Orquestrador semanal | regra da seção 3.I |
| Gerar 5 ganchos, legendas por rede, título de Short, post de LinkedIn | `ganchos.py` (Claude) | uma ideia ou transcrição na entrada |
| Cortar vídeos longos em verticais | `cortes.py` (ffmpeg) | vídeo + .srt |
| Agendar nos melhores horários | Pacote de publicação (terça) | rascunhos no Metricool para você aprovar |
| Responder comentário com palavra-chave no Direct | ManyChat | configurar uma vez |
| **Gravar** | você | 3 blocos por semana de 40 min, gancho lido do roteiro |

## 5. Metas para as próximas 6 semanas

- Taxa de 3 segundos no IG: de 35,6% para 50% (mediana).
- Reels com zero envios: de 50% para menos de 20%.
- TikTok: mediana orgânica de 146 para 400 views, só com cortes de 31-90s.
- Pelo menos 2 collabs por semana.
- Newsletter do LinkedIn com a primeira edição publicada.

Medição: rode `python -m crescimento.diagnostico` com os CSVs novos a cada sexta.

## Fontes sobre os algoritmos

Os sinais citados (envio por DM, Trial Reels, originalidade no Instagram; busca e conclusão no TikTok; "assistiu vs. passou" no Shorts; tempo de leitura e comentário no LinkedIn) vêm de análises de terceiros sobre declarações das plataformas. Os percentuais dos blogs não estão confirmados oficialmente e por isso não entraram como meta.

- [SocialPilot — Instagram Reels Algorithm 2026](https://www.socialpilot.co/de/blog/instagram-reels-algorithm)
- [PostEverywhere — How the Instagram Algorithm Works in 2026](https://posteverywhere.ai/blog/how-the-instagram-algorithm-works)
- [TT Calculator — TikTok Algorithm Changes 2026](https://ttcalculator.net/blog/tiktok-algorithm-changes-2026/)
- [OutlierKit — YouTube Shorts algorithm in YouTube's words](https://outlierkit.com/resources/youtube-shorts-algorithm/)
- [vidIQ — YouTube Shorts Algorithm 2026](https://vidiq.com/blog/post/youtube-shorts-algorithm/)
- [Metricool — The LinkedIn Algorithm in 2026](https://metricool.com/linkedin-algorithm/)
