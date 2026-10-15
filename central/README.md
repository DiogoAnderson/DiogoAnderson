# Central Angioletti

Sistema gratuito que opera as redes do Diogo com o mínimo de trabalho manual.

| Parte | Onde | O que faz |
|---|---|---|
| Painel | https://claude.ai/artifact/DAJDqAtrAMBuJXvpyM6wNH (código em `central/pagina/central.html`) | Calendário único (Metricool, LinkedIn e fila própria), cota do mês, pedidos ao Claude, criação de textos, sugestões, WhatsApp, relatórios e conexões. |
| Operador | tarefa "Central Angioletti — operador de pedidos" | Recebe cada pedido feito no painel e executa: capas, recortes, legendas, agendamentos, análises. Responde no próprio painel. |
| Motor de vídeo | `central/video.py` | Confere, converte (30 fps, H.264, abaixo de 100 MB), transcreve, sugere trechos e corta com legenda animada opcional. |
| Instagram direto | `central/instagram.py` + `central/fila.py` + `.github/workflows/central.yml` | Publica Reels, Stories, posts e carrosséis pela API oficial da Meta, sem cota. O GitHub roda a fila a cada 15 minutos. Guia: `COMO-LIGAR-O-INSTAGRAM.md`. |
| Peças | `crescimento/pecas.py` | Capas e cards com as fotos e a marca do Diogo (Reel, carrossel, Mentor Sincerão, Doutor Di, LinkedIn). |

## O banco do painel

| Coleção | Quem escreve | Para quê |
|---|---|---|
| `config/geral` | Claude | id da tarefa operadora; `instagramDireto` = "ligado" quando a publicação direta estiver ativa |
| `pedidos` | painel e operador | pedido, situação (enviado, em andamento, feito, erro) e resposta |
| `sugestoes` | orquestrador, operador e o próprio painel | melhorias com aprovar ou recusar; aprovar manda o operador aplicar |
| `whatsapp` | pacote de terça | mensagens prontas por vídeo |
| `fila` | operador e pacote de terça | espelho da fila do Instagram direto |
| `painel/estado` | lista diária | alertas do dia |

## Como evolui

Segunda, o orquestrador analisa a semana e grava sugestões; o Diogo aprova no painel; o operador aplica e registra a decisão no REGISTRO-DE-DECISOES.md. Conexões novas (Facebook, Threads, YouTube e TikTok diretos, Pinterest) entram como novos destinos da fila.
