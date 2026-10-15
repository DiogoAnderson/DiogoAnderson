# Como ligar a publicação direta no Instagram (gratuita)

Uma vez só, cerca de 20 minutos. Depois disso o Instagram sai da cota de 20 publicações do Metricool.

## O que precisa estar certo antes

- O @diogoanderson é conta **profissional** (Criador de conteúdo ou Empresa).
- Ela está **ligada a uma Página do Facebook** (Instagram → Configurações → Central de contas, ou na Página: Configurações → Contas vinculadas).

## 1. Criar o app (Meta for Developers)

1. Entre em https://developers.facebook.com com o seu Facebook → **Meus apps** → **Criar app**.
2. Caso de uso: **Outro** → tipo **Empresa** → nome "Central Angioletti".
3. No painel do app, adicione o produto **Instagram** → opção **API com login do Facebook**.

O app fica em **modo de desenvolvimento** e funciona para a sua própria conta sem análise da Meta, porque você é administrador do app.

## 2. Gerar o token que não expira

1. Abra **Ferramentas → Explorador da Graph API** (https://developers.facebook.com/tools/explorer).
2. Escolha o app "Central Angioletti" → **Gerar token de acesso** → marque: `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`, `pages_show_list`, `pages_read_engagement`, `business_management`.
3. Copie o token, abra o **Depurador de token** (https://developers.facebook.com/tools/debug/accesstoken), cole e clique em **Estender token de acesso** (vale 60 dias).
4. De volta ao Explorador, com o token estendido, rode: `me/accounts`. Na Página ligada ao Instagram, copie o `access_token` dela. **Esse token de página não expira.**
5. Ainda no Explorador, rode: `<id da página>?fields=instagram_business_account`. Copie o número em `instagram_business_account.id`.

## 3. Guardar no GitHub (nunca cole no chat)

GitHub → repositório **DiogoAnderson/DiogoAnderson** → **Settings → Secrets and variables → Actions → New repository secret**:

| Nome | Valor |
|---|---|
| `IG_TOKEN` | o token da página (passo 2.4) |
| `IG_USER_ID` | o número da conta do Instagram (passo 2.5) |

## 4. Testar

GitHub → **Actions → Central — publicar fila → Run workflow** → ação `testar-instagram`. Se aparecer o seu @ e o número de seguidores, está ligado. Avise a Central (ou o Claude) e o Instagram passa a sair pela fila própria.
