# Base de Conhecimento - Taxonomia de Golpes Digitais (Brasil)
# Fonte: Febraban, Anatel, CERT.br, SaferNet, Procon, BCB, CVM, MPF, PF, Receita Federal, INSS
# Este arquivo alimenta o RAG do dIscovery

---

## GOLPE_01: Phishing por E-mail ou Mensagem

**Descrição:** Mensagens fraudulentas que se passam por instituições legítimas (bancos, Correios, Receita Federal, operadoras como Claro, Vivo, TIM) para roubar dados pessoais, senhas e informações financeiras.

**Padrões textuais comuns:**
- "Sua conta foi suspensa, clique aqui para reativar"
- "Atualização de cadastro obrigatória"
- "Você tem uma encomenda aguardando pagamento de taxa"
- "Sua fatura está disponível - acesse agora"
- URLs com domínios similares: bradesc0.com, receita-federal.net, caixa-gov.br

**Palavras-chave:** suspensa, bloqueada, clique aqui, urgente, verificar cadastro, atualizar dados, fatura, encomenda, taxa pendente

**Canais:** E-mail, SMS (smishing), WhatsApp, Instagram

---

## GOLPE_02: Golpe do PIX (Falsa Central de Atendimento)

**Descrição:** Criminoso se passa por atendente de banco ou instituição financeira alegando que há um problema com a conta do PIX da vítima, solicitando transferências "para conta segura" ou dados de acesso.

**Padrões textuais comuns:**
- "Identificamos uma tentativa de fraude na sua conta"
- "Para proteger seu dinheiro, transfira para a conta temporária segura"
- "Seu PIX está comprometido, vamos cancelar e estornar"
- "Preciso que você faça um PIX teste para confirmar sua identidade"

**Palavras-chave:** conta segura, PIX comprometido, estorno, cancelar transação, confirmar identidade, temporário, proteger dinheiro

**Canais:** Telefone, WhatsApp

---

## GOLPE_03: Falso Empréstimo / Antecipação FGTS

**Descrição:** Oferta de empréstimo com juros muito baixos ou antecipação do saque FGTS condicionada ao pagamento antecipado de taxas, seguros ou IOF falsos.

**Padrões textuais comuns:**
- "Empréstimo aprovado mesmo com CPF negativado"
- "Taxa de juros 0,5% ao mês - aprovação imediata"
- "Antecipe seu FGTS sem burocracia"
- "Para liberar o crédito, pague a taxa de R$150 de seguro"
- "Crédito consignado para aposentados e pensionistas - sem consulta ao SPC"

**Palavras-chave:** negativado, aprovado, sem consulta, taxa liberação, FGTS antecipação, consignado, pague taxa, crédito fácil, juros baixíssimos

**Canais:** WhatsApp, SMS, Sites falsos, Redes sociais

---

## GOLPE_04: Falsa Promoção / Sorteio

**Descrição:** Publicações alegando que a vítima ganhou prêmios, vouchers ou descontos exclusivos de empresas conhecidas (Mercado Livre, iFood, Americanas, Lojas Renner), exigindo cadastro ou pagamento de frete/taxa para retirar o prêmio.

**Padrões textuais comuns:**
- "Parabéns! Você foi sorteado(a) e ganhou um iPhone 15"
- "Clique e resgate seu voucher de R$500 no Mercado Livre"
- "Só hoje: frete grátis + 90% de desconto"
- "Você é o visitante número 1.000.000 - RESGATE SEU PRÊMIO"
- "Compartilhe com 10 amigos para receber seu brinde"

**Palavras-chave:** sorteado, ganhou, prêmio, voucher, resgate, compartilhe, brinde, desconto exclusivo, clique e ganhe, visitante especial

**Canais:** WhatsApp, Facebook, Instagram, Sites

---

## GOLPE_05: Falso Serviço / Prestador

**Descrição:** Anúncios de prestadores de serviços inexistentes ou clonados (eletricistas, encanadores, dedetizadoras, chaveiros) com preços muito abaixo do mercado. Cobram visita ou material antecipado e somem.

**Padrões textuais comuns:**
- "Dedetização completa por R$80 - atendemos toda a cidade"
- "Chaveiro 24h - abertura de veículos R$40"
- "Conserto de geladeira com garantia - R$50 mão de obra"
- "Técnico em informática a domicílio - formatação R$30"

**Palavras-chave:** preço abaixo do mercado, atendimento imediato, parcela no PIX, garantia estendida, sem taxa de visita, 24h disponível

**Canais:** OLX, Facebook Marketplace, Google Maps (perfis falsos), WhatsApp

---

## GOLPE_06: Golpe do Falso Funcionário / Engenharia Social

**Descrição:** O criminoso se apresenta como funcionário de empresa legítima (telecom, banco, governo) solicitando dados pessoais, instalação de aplicativos de acesso remoto (AnyDesk, TeamViewer) ou confirmação de senhas.

**Padrões textuais comuns:**
- "Sou da Vivo/Claro/TIM e preciso atualizar seu cadastro"
- "Instale este aplicativo para finalizarmos o atendimento"
- "Preciso do código que chegou no seu celular"
- "É apenas uma confirmação de segurança, pode passar o código"

**Palavras-chave:** instale o aplicativo, código de verificação, confirmação, acesso remoto, atualizar cadastro, central de atendimento, protocolo de segurança

**Canais:** Telefone, WhatsApp

---

## GOLPE_07: Clonagem de WhatsApp / Redes Sociais

**Descrição:** Criminoso assume o controle da conta de WhatsApp ou Instagram da vítima e passa a pedir dinheiro emprestado para seus contatos, geralmente via PIX.

**Padrões textuais comuns:**
- "Oi, tudo bem? Preciso de um favor urgente"
- "Estou em apuros, pode me emprestar R$500 pelo PIX?"
- "Vou te pagar amanhã, é uma emergência"
- "Não consigo ligar agora, só no WhatsApp"

**Palavras-chave:** emergência, emprestar, PIX urgente, pagar amanhã, favor urgente, não consigo ligar, apuros

**Canais:** WhatsApp, Instagram, Facebook

---

## GOLPE_08: Falso Investimento (Pirâmide / Crypto)

**Descrição:** Promessas de retorno financeiro extraordinário em curto prazo, geralmente envolvendo criptomoedas, robôs de investimento ou grupos de sinais. Estrutura de pirâmide disfarçada de clube de investimento.

**Padrões textuais comuns:**
- "Rendimento de 30% ao mês garantido"
- "Robô de investimento automático - deposite e lucre"
- "Entre no grupo VIP de trading e multiplique seu capital"
- "Indique amigos e ganhe comissão"
- "Bitcoin sem risco - metodologia exclusiva"

**Palavras-chave:** rendimento garantido, robô trader, % ao mês, grupo VIP, indique e ganhe, multiplique, sem risco, criptomoeda exclusivo, retorno rápido

**Canais:** Telegram, Instagram, WhatsApp, YouTube (lives falsas)

---

## GOLPE_09: Falso Perfil em App de Relacionamento (Romance Scam)

**Descrição:** Perfil falso criado em apps de relacionamento ou redes sociais que desenvolve relacionamento afetivo com a vítima para eventualmente pedir dinheiro, geralmente alegando emergência médica, viagem frustrada ou investimento.

**Padrões textuais comuns:**
- "Estou no exterior e meu cartão foi bloqueado"
- "Preciso de ajuda para pagar o hospital"
- "Quando chegar, vou te reembolsar tudo"
- "Confio em você, pode me ajudar nessa situação?"
- Perfis com fotos de militares, médicos, engenheiros no exterior

**Palavras-chave:** exterior, emergência médica, bloqueado, reembolso, confio em você, situação difícil, passagem, hospital, dívida urgente

**Canais:** Tinder, Badoo, Instagram, Facebook

---

## GOLPE_10: Link Malicioso / Malware

**Descrição:** Links disfarçados que instalam vírus, spyware ou ransomware no dispositivo da vítima. Frequentemente vêm em mensagens sobre notícias chocantes, vídeos virais ou promoções falsas.

**Padrões textuais comuns:**
- "Veja o vídeo que encontrei seu filho fazendo"
- "Notícia urgente: [link encurtado]"
- "Você apareceu nessa foto? Olha só"
- "Clique para ver quem viu seu perfil"
- Links encurtados: bit.ly, tinyurl, cutt.ly direcionando para domínios suspeitos

**Palavras-chave:** clique no link, assista agora, você aparece, veja o vídeo, notícia urgente, link encurtado, domínio suspeito, instalar aplicativo

**Canais:** WhatsApp, SMS, E-mail, Redes sociais

---

## INDICADORES GERAIS DE FRAUDE

**Urgência artificial:** Frases que criam pressão temporal ("só hoje", "últimas horas", "expira em 10 minutos")

**Promessas irreais:** Retornos financeiros absurdos, prêmios sem participação, serviços com preços impossíveis

**Pedido de sigilo:** "Não comente com ninguém", "É confidencial", "Não fale para seu banco"

**Solicitação de dados sensíveis:** Senha, token, código SMS, número de cartão

**Pedido de pagamento antecipado:** Pagamento necessário para "liberar" benefício ou serviço

**Links suspeitos:**
- Domínios com erros ortográficos (bradesco → bradesc0, bradescc)
- Uso excessivo de subdomínios (banco.seguro.xpto.com)
- HTTP em vez de HTTPS
- Encurtadores de URL escondendo destino

---

## REFERÊNCIAS
- CERT.br - Centro de Estudos, Resposta e Tratamento de Incidentes de Segurança
- Febraban - Federação Brasileira de Bancos
- Anatel - Agência Nacional de Telecomunicações
- SaferNet Brasil
- Polícia Federal - Cartilha de Crimes Cibernéticos
