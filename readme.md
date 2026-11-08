# 🃏 YGO Booster Bot (Versão 0.1)

Um bot de Discord simples, nostálgico e focado em simular a experiência de comprar boosters clássicos de Yu-Gi-Oh!, abri-los, colecionar as cartas e gerenciar seu próprio inventário.

---

## Licença e Termos de Uso
Este projeto é **Open Source**. Você é totalmente livre para estudar, modificar, hospedar e adaptar o código para o seu servidor. Caso o projeto seja replicado, reproduzido ou distribuído publicamente, **os devidos créditos devem ser dados ao criador original**.

---

## Objetivo do Projeto
O propósito do bot é direto e focado:
- Simular a compra de booster packs de Yu-Gi-Oh!
- Abrir pacotes com mecânicas clássicas (cartas comuns garantidas nas primeiras posições e uma carta rara ou superior na última).
- Salvar permanentemente as cartas na conta do jogador utilizando banco de dados SQLite.
- Permitir a consulta organizada de coleções e informações detalhadas de cartas e caixas.

---

## Lista de Comandos

### Economia e Perfil
* `!daily` — Resgata sua recompensa diária em YGcoins para investir em boosters.
* `!profile` — Consulta o seu saldo atual de moedas e informações da conta.

### Loja e Informações
* `!shop` — Abre a loja oficial de coleções de boosters disponíveis.
* `!buy <id> <quantidade>` — Compra pacotes fechados de uma determinada caixa (com confirmação por botões interativos).
* `!info-box <id>` — Exibe o catálogo completo de cartas de uma coleção, ordenadas por raridade e com paginação por botões.
* `!info-card <nome da carta>` — Pesquisa uma carta específica pelo nome para exibir seus detalhes (raridade, tipo) e a imagem oficial.

### Inventário, Abertura e Coleção
* `!inventory` (ou `!boosters`) — Mostra a quantidade de pacotes fechados que você possui guardados.
* `!open <id>` — Abre um booster da coleção escolhida. Conta com um carrossel interativo (`◀ Voltar` / `Próxima ▶`) para visualizar a imagem e os dados de cada carta tirada, salvando-as automaticamente na sua conta.
* `!collection` — Abre seu fichário pessoal de cartas ganhas, organizadas por raridade e ordem alfabética, navegáveis por páginas interativas.

---

## Features Futuras (Roadmap)
* [ ] **Reciclagem:** Sistema para trocar cartas repetidas por YGcoins.
* [ ] **Emojis Personalizados:** Substituição de textos visuais por emojis temáticos do jogo.
* [ ] **Sistema de Trocas:** Mecânica para negociar cartas diretamente entre jogadores.
* [ ] **Wiki Interna:** Acompanhamento de progresso de completude das caixas (tipo Pokédex).
* [ ] **Perfis Customizáveis:** Personalização de fundo, título e carta de destaque.
* [ ] **Novas Coleções:** Inclusão de expansões clássicas adicionais através de arquivos JSON.
* [ ] **24 barra 7:** Subiro bot em um server.