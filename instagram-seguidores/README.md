# Seguidores do Instagram

App de uma página só, que roda no navegador, para descobrir:

- quem você segue e **não te segue de volta**;
- quem te segue e você **não segue de volta**;
- quem **parou de te seguir** (e quem começou) entre duas datas.

## Como usar

1. Abra `index.html` no navegador.
2. No Instagram: **Central de Contas → Suas informações e permissões → Baixar suas informações**,
   marque só **Seguidores e seguindo** e escolha o formato **JSON**.
3. Solte o `.zip` no app e clique em **Salvar fotografia**.
4. Repita o download de tempos em tempos (ex.: toda semana). O app compara as fotografias
   e mostra quem deixou de te seguir no período escolhido.

## Fila para deixar de seguir

- Mostra um perfil por vez, entre os que não te seguem de volta. **Abrir perfil** leva ao Instagram;
  você deixa de seguir lá e volta para marcar **Já deixei de seguir**. Também dá para **Pular** ou **Manter**.
- **Lista de exceções:** perfis que você quer seguir mesmo sem ser seguido de volta (marcas, referências,
  notícias). Eles nunca entram na fila. Também dá para marcar pelo botão **Manter** na lista.
- **Limite diário** (padrão 50): o app avisa quando você chega nele, porque volume alto em pouco tempo
  costuma gerar bloqueio temporário de ações no Instagram.
- **Desfazer** a última marcação.
- Se uma fotografia mais nova mostrar que você ainda segue alguém marcado como feito, a pessoa volta para a fila.

O app nunca age sozinho na sua conta: cada "deixar de seguir" é um toque seu no próprio Instagram.

## Por que não conecta direto no Instagram?

A API oficial do Instagram não fornece a lista de seguidores. Apps que pedem sua senha
fazem isso por automação não autorizada, o que viola os termos do Instagram e pode levar
ao bloqueio da conta. Este app usa só o arquivo oficial que o próprio Instagram te entrega.

## Privacidade

Nada é enviado para servidor nenhum. As fotografias ficam salvas no navegador
(`localStorage`); use **Exportar backup** para guardar uma cópia ou levar para outro computador
(o backup inclui as fotografias, as exceções e o que já foi marcado na fila).
