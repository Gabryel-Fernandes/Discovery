"""
classifier/ml_classifier.py  v2
"""
import os, re, joblib, numpy as np, nltk
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

nltk.download("stopwords", quiet=True)
nltk.download("rslp", quiet=True)
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer

CLASSIFIER_PATH = Path(os.getenv("CLASSIFIER_PATH", "./data/classifier_model.joblib"))
STOP_WORDS_PT = stopwords.words("portuguese")
stemmer = RSLPStemmer()

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " URL_SUSPEITA ", text)
    text = re.sub(r"\d{4,}", " NUMERO ", text)
    text = re.sub(r"r\$\s*[\d.,]+", " VALOR_DINHEIRO ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokens = [stemmer.stem(w) for w in text.split() if w not in STOP_WORDS_PT and len(w) > 2]
    return " ".join(tokens)

TRAINING_DATA = [
    # PHISHING
    ("Sua conta foi suspensa clique aqui para reativar agora", "phishing"),
    ("Atualização de cadastro obrigatória acesse o link urgente", "phishing"),
    ("Você tem uma encomenda aguardando pagamento de taxa", "phishing"),
    ("Verificação de segurança necessária acesse sua conta", "phishing"),
    ("Confirme seus dados bancários para evitar bloqueio", "phishing"),
    ("Receita Federal notificação fiscal acesse imediatamente", "phishing"),
    ("Seu CPF está sendo usado indevidamente clique para resolver", "phishing"),
    ("Clique no link para confirmar seus dados e evitar suspensão", "phishing"),
    ("Seu internet banking será bloqueado atualize agora", "phishing"),
    ("Acesso não reconhecido na sua conta verifique agora", "phishing"),
    ("Bradesco alerta de segurança atualize seus dados agora", "phishing"),
    ("Correios taxa pendente clique para regularizar entrega", "phishing"),
    ("Seu cadastro expira hoje clique para não perder o acesso", "phishing"),
    ("Banco detectou acesso suspeito confirme identidade agora", "phishing"),
    ("Regularize sua situação fiscal clique no link urgente", "phishing"),
    # GOLPE PIX
    ("Identificamos tentativa de fraude no seu PIX entre em contato", "golpe_pix"),
    ("Para proteger seu dinheiro transfira para conta segura temporária", "golpe_pix"),
    ("Seu PIX está comprometido vamos cancelar e fazer estorno", "golpe_pix"),
    ("Central de atendimento banco urgente problema na conta", "golpe_pix"),
    ("Faça um PIX teste para confirmar identidade e proteger conta", "golpe_pix"),
    ("Transação suspeita detectada ligue agora para cancelar", "golpe_pix"),
    ("Sua conta corrente está em risco fale com nosso especialista", "golpe_pix"),
    ("Bloqueio preventivo conta bancária entre em contato urgente", "golpe_pix"),
    ("PIX enviado por engano precisa estornar para nossa conta", "golpe_pix"),
    ("Central antifraude banco detectou movimentação suspeita PIX", "golpe_pix"),
    ("Para cancelar transação não reconhecida transfira agora", "golpe_pix"),
    ("Seu limite PIX foi alterado confirme pelo atendimento", "golpe_pix"),
    # FALSO EMPRESTIMO
    ("Empréstimo aprovado mesmo com CPF negativado sem consulta SPC", "falso_emprestimo"),
    ("Taxa de juros baixíssima aprovação imediata sem burocracia", "falso_emprestimo"),
    ("Antecipe seu FGTS sem burocracia dinheiro na hora", "falso_emprestimo"),
    ("Crédito consignado aposentados pensionistas sem consulta", "falso_emprestimo"),
    ("Para liberar o crédito pague a taxa de seguro antecipada", "falso_emprestimo"),
    ("Empréstimo pessoal online aprovado em minutos negativado aceito", "falso_emprestimo"),
    ("Saque FGTS antecipado deposite taxa de liberação", "falso_emprestimo"),
    ("Microempréstimo sem garantia aprovação em 1 hora", "falso_emprestimo"),
    ("Crédito liberado nome sujo sem comprovante renda", "falso_emprestimo"),
    ("Financiamento veículo sem entrada sem consulta serasa", "falso_emprestimo"),
    ("Empréstimo governo federal beneficiários bolsa família", "falso_emprestimo"),
    ("Portabilidade salário crédito especial taxa zero aprovado", "falso_emprestimo"),
    # FALSA PROMOCAO
    ("Parabéns você foi sorteado ganhou iPhone resgate agora", "falsa_promocao"),
    ("Clique e resgate seu voucher de desconto exclusivo hoje", "falsa_promocao"),
    ("Você é o visitante especial resgate seu prêmio agora", "falsa_promocao"),
    ("Compartilhe com amigos e receba brinde frete grátis", "falsa_promocao"),
    ("Promoção relâmpago 90 por cento de desconto só hoje", "falsa_promocao"),
    ("Ganhou vale presente mercado livre resgate seu prêmio", "falsa_promocao"),
    ("Sorteio especial cliente fiel você ganhou clique aqui", "falsa_promocao"),
    ("Você ganhou Smart TV 50 polegadas resgate pelo link", "falsa_promocao"),
    ("Promoção Shopee cliente especial desconto 95 por cento", "falsa_promocao"),
    ("Parabéns aniversário da loja você ganhou vale compras", "falsa_promocao"),
    ("Resgate seu cashback acumulado antes de expirar hoje", "falsa_promocao"),
    ("Último dia para resgatar seu bônus exclusivo não perca", "falsa_promocao"),
    # FALSO SERVICO
    ("Dedetização completa residencial por preço especial PIX", "falso_servico"),
    ("Chaveiro 24 horas abertura veículos preço acessível", "falso_servico"),
    ("Técnico informática domicílio formatação instalação barato", "falso_servico"),
    ("Conserto geladeira ar condicionado garantia por PIX", "falso_servico"),
    ("Eletricista encanador disponível atendimento imediato barato", "falso_servico"),
    ("Pintor pedreiro serviços gerais preço combinar aceito PIX", "falso_servico"),
    ("Mecânico domicílio revisão carro preço especial", "falso_servico"),
    ("Instalação câmeras segurança sem fio preço especial PIX", "falso_servico"),
    ("Serviço limpeza caixa água dedetização preço justo", "falso_servico"),
    ("Marido de aluguel serviços gerais barato pago por PIX", "falso_servico"),
    ("Faz tudo em casa conserto reparo preço abaixo mercado", "falso_servico"),
    ("Serviço desentupimento esgoto preço especial pagamento PIX", "falso_servico"),
    # FALSO INVESTIMENTO
    ("Rendimento garantido 30 por cento ao mês robô trader", "falso_investimento"),
    ("Multiplique seu capital criptomoeda sem risco grupo VIP", "falso_investimento"),
    ("Bitcoin investimento seguro retorno rápido garantido", "falso_investimento"),
    ("Indique amigos ganhe comissão clube investimento exclusivo", "falso_investimento"),
    ("Robô de investimento automático deposite e lucre diariamente", "falso_investimento"),
    ("Metodologia exclusiva trading sinais vip rendimento mensal", "falso_investimento"),
    ("Grupo telegram sinais gratuitos lucro garantido crypto", "falso_investimento"),
    ("Plataforma investimento 5 por cento ao dia saque rápido", "falso_investimento"),
    ("Pirâmide financeira clube benefícios indique ganhe comissão", "falso_investimento"),
    ("Mineração bitcoin nuvem lucro passivo sem equipamento", "falso_investimento"),
    ("NFT coleção exclusiva valorização garantida oportunidade única", "falso_investimento"),
    ("Forex retorno alto sem risco sistema exclusivo cadastre", "falso_investimento"),
    # ENGENHARIA SOCIAL
    ("Instale este aplicativo para finalizarmos o atendimento", "engenharia_social"),
    ("Preciso do código que chegou no seu celular confirmação", "engenharia_social"),
    ("Sou da operadora preciso atualizar seu cadastro urgente", "engenharia_social"),
    ("Confirmação de segurança passe o código SMS recebido", "engenharia_social"),
    ("Acesso remoto necessário para resolver problema técnico", "engenharia_social"),
    ("Protocolo de segurança ativo confirme seus dados agora", "engenharia_social"),
    ("Sou analista banco preciso verificar código token enviado", "engenharia_social"),
    ("Para cancelar compra indevida informe o código recebido SMS", "engenharia_social"),
    ("Funcionário Claro precisa atualizar chip envie código confirmação", "engenharia_social"),
    ("Central segurança operadora precisa confirmar seus dados pessoais", "engenharia_social"),
    ("Técnico banco liga para confirmar transação informe senha", "engenharia_social"),
    ("Suporte técnico remoto precisa acesso dispositivo agora", "engenharia_social"),
    # CLONAGEM CONTA
    ("Oi tudo bem preciso de favor urgente pode me ajudar", "clonagem_conta"),
    ("Estou em apuros pode me emprestar dinheiro pelo PIX", "clonagem_conta"),
    ("Emergência familiar preciso de transferência urgente PIX", "clonagem_conta"),
    ("Não consigo ligar só pelo WhatsApp situação complicada", "clonagem_conta"),
    ("Pago amanhã prometo está sendo difícil preciso agora", "clonagem_conta"),
    ("Mudei de número esse é meu novo WhatsApp salva aí", "clonagem_conta"),
    ("Mãe preciso de dinheiro urgente pode transferir agora", "clonagem_conta"),
    ("Estou sem crédito celular pode me mandar PIX depois te pago", "clonagem_conta"),
    ("Passei por situação difícil preciso de ajuda financeira hoje", "clonagem_conta"),
    ("Filho aqui é mamãe novo número precisa de ajuda urgente", "clonagem_conta"),
    ("Oi sou eu mudei número pode me fazer um PIX urgente", "clonagem_conta"),
    ("Situação difícil preciso empréstimo rápido me ajuda PIX", "clonagem_conta"),
    # GOLPE SUPORTE TECNICO (nova)
    ("Seu computador está infectado ligue agora para suporte Microsoft", "golpe_suporte_tecnico"),
    ("Vírus detectado no seu dispositivo clique para remover agora", "golpe_suporte_tecnico"),
    ("Windows identificou problema crítico ligue suporte imediatamente", "golpe_suporte_tecnico"),
    ("Seu celular hackeado instale antivírus urgente clique aqui", "golpe_suporte_tecnico"),
    ("Alerta segurança Google seu dispositivo comprometido acesse", "golpe_suporte_tecnico"),
    ("Técnico certificado Apple identifica falha grave no seu iPhone", "golpe_suporte_tecnico"),
    ("Conta Google invadida confirme identidade instale aplicativo segurança", "golpe_suporte_tecnico"),
    ("Suporte Samsung detectou erro crítico bateria ligue urgente", "golpe_suporte_tecnico"),
    ("Pop-up alerta vírus remova agora ligando para número técnico", "golpe_suporte_tecnico"),
    ("Notificação sistema operacional falha grave contate suporte", "golpe_suporte_tecnico"),
    ("Seu antivírus expirou dispositivo em risco renove agora", "golpe_suporte_tecnico"),
    ("Acesso não autorizado detectado conta Google confirme agora", "golpe_suporte_tecnico"),
    # GOLPE QR CODE (nova)
    ("Leia o QR code para receber seu prêmio especial agora", "golpe_qr_code"),
    ("Pague via QR code para liberar sua entrega retida", "golpe_qr_code"),
    ("QR code exclusivo para resgatar desconto imperdível hoje", "golpe_qr_code"),
    ("Escaneie o QR code para confirmar seus dados e receber benefício", "golpe_qr_code"),
    ("Site não solicita QR code mas pediu para ler código câmera", "golpe_qr_code"),
    ("QR code enviado por desconhecido para transferência PIX", "golpe_qr_code"),
    ("Leia QR code para validar identidade e receber cashback", "golpe_qr_code"),
    ("Cobrança indevida QR code enviado por mensagem pague agora", "golpe_qr_code"),
    ("QR code substituído no estabelecimento direciona pagamento errado", "golpe_qr_code"),
    ("Escaneie QR code para ganhar pontos fidelidade cadastre agora", "golpe_qr_code"),
    ("QR code em adesivo colado sobre original no caixa pagamento", "golpe_qr_code"),
    ("Recebeu QR code por WhatsApp de número desconhecido pedindo pagamento", "golpe_qr_code"),
    # GOLPE DELIVERY (nova)
    ("Seu pedido foi retido pague taxa alfândega para liberar", "golpe_delivery"),
    ("Entrega suspensa pague pequena taxa para receber produto", "golpe_delivery"),
    ("Produto comprado retido correios pague imposto para receber", "golpe_delivery"),
    ("Vendedor some após pagamento produto nunca entregue", "golpe_delivery"),
    ("Loja falsa online aceita pagamento não entrega produto", "golpe_delivery"),
    ("Comprei produto site falso cartão cobrado item não chegou", "golpe_delivery"),
    ("Taxa de liberação encomenda internacional pague agora", "golpe_delivery"),
    ("Entregador pede pagamento adicional na porta para entregar", "golpe_delivery"),
    ("Produto anunciado preço absurdo pague antecipado some", "golpe_delivery"),
    ("Site copia loja famosa vende produto não entrega", "golpe_delivery"),
    ("Rastreio encomenda pede pagamento taxa para desbloquear", "golpe_delivery"),
    ("Falsa loja marketplace cobra pix produto inexistente", "golpe_delivery"),
    # ROMANCE SCAM (GOLPE_09)
    ("Estou no exterior meu cartão foi bloqueado pode me ajudar", "romance_scam"),
    ("Preciso de ajuda para pagar hospital estou internado fora do país", "romance_scam"),
    ("Quando chegar ao Brasil te reembolso tudo confio em você", "romance_scam"),
    ("Sou militar no exterior preciso transferência urgente emergência", "romance_scam"),
    ("Médico trabalhando fora do país passagem bloqueada me ajuda", "romance_scam"),
    ("Engenheiro plataforma petróleo offshore precisa ajuda financeira urgente", "romance_scam"),
    ("Situação difícil no exterior confio em você me empresta agora", "romance_scam"),
    ("Dívida urgente hospital exterior não consigo acessar minha conta", "romance_scam"),
    ("Perfil militar americano apaixonado precisa ajuda financeira urgente", "romance_scam"),
    ("Nos conhecemos no app quero te visitar mas preciso de ajuda passagem", "romance_scam"),
    ("Estou preso na alfândega preciso pagamento taxa para sair", "romance_scam"),
    ("Relacionamento à distância ele pediu dinheiro emergência médica exterior", "romance_scam"),
    # LINK MALICIOSO / MALWARE (GOLPE_10)
    ("Veja o vídeo que encontrei você fazendo clique no link agora", "link_malicioso"),
    ("Você apareceu nessa foto olha só clique para ver", "link_malicioso"),
    ("Notícia urgente clique no link encurtado para ver agora", "link_malicioso"),
    ("Clique para ver quem viu seu perfil hoje link aqui", "link_malicioso"),
    ("Vídeo viral encontrei seu filho clique urgente ver agora", "link_malicioso"),
    ("Instalou aplicativo de link desconhecido dispositivo agindo estranho", "link_malicioso"),
    ("Link bit.ly enviado por desconhecido redireciona site suspeito", "link_malicioso"),
    ("Clique para instalar atualização urgente enviado por WhatsApp", "link_malicioso"),
    ("Baixar aplicativo fora da loja oficial link enviado mensagem", "link_malicioso"),
    ("Arquivo APK enviado por WhatsApp instale para receber prêmio", "link_malicioso"),
    ("Seu celular tem vírus instale esse app imediatamente link", "link_malicioso"),
    ("Notícia chocante sobre famoso clique no link ver completo", "link_malicioso"),
    # BOLETO FALSO (GOLPE_11)
    ("Segunda via boleto energia elétrica vencimento 3 dias pague agora", "boleto_falso"),
    ("Boleto atualizado com multa por atraso pague antes de vencer", "boleto_falso"),
    ("Notificação débito automático cancelado novo boleto gerado urgente", "boleto_falso"),
    ("Boleto condomínio mês referência com desconto pague agora", "boleto_falso"),
    ("Segunda via fatura telefone atualizada vencimento amanhã", "boleto_falso"),
    ("Boleto água saneamento vencimento próximo evite corte pague", "boleto_falso"),
    ("Regularize débito boleto enviado pague para evitar negativação", "boleto_falso"),
    ("Novo boleto escola mensalidade vencimento sexta pague pelo app", "boleto_falso"),
    ("Cobrança adicional boleto enviado taxa serviço pague urgente", "boleto_falso"),
    ("Boleto IPTU parcela vencendo pague para evitar multa juros", "boleto_falso"),
    ("Linha digitável atualizada boleto anterior cancelado pague novo", "boleto_falso"),
    ("Boleto enviado por email CNPJ diferente origem suspeita pague", "boleto_falso"),
    # GOLPE CENTRAL DE VENDAS / PORTABILIDADE (GOLPE_12)
    ("Vamos reduzir sua conta de luz 40 por cento código fatura", "golpe_central_vendas"),
    ("Plano celular 100GB por 29 reais migração imediata sem fidelidade", "golpe_central_vendas"),
    ("Desconto especial aposentados conta energia envie RG e CPF", "golpe_central_vendas"),
    ("Portabilidade número celular mais barato confirme código SMS", "golpe_central_vendas"),
    ("Redução conta telefone plano melhor migração hoje informe código", "golpe_central_vendas"),
    ("Enel desconto especial cliente precisamos código fatura energia", "golpe_central_vendas"),
    ("Operadora oferece upgrade plano gratuito confirme dados agora", "golpe_central_vendas"),
    ("Internet fibra mais rápida mesmo preço migração precisa código", "golpe_central_vendas"),
    ("Desconto 50 por cento conta luz programa governo informe código URH", "golpe_central_vendas"),
    ("Plano família celular com desconto portabilidade imediata código", "golpe_central_vendas"),
    ("Equatorial promoção especial cliente fiel redução conta informe código", "golpe_central_vendas"),
    ("Cancelamento cobrança indevida precisa código fatura para estorno", "golpe_central_vendas"),
    # GOLPE LEILÃO / CONSÓRCIO (GOLPE_13)
    ("Leilão Receita Federal carros apreendidos a partir de 5 mil reais", "golpe_leilao_consorcio"),
    ("Consórcio contemplado para negativados carta crédito venda urgente", "golpe_leilao_consorcio"),
    ("Garanta seu lote lance mínimo sinal não reembolsável leilão", "golpe_leilao_consorcio"),
    ("Leilão judicial imóveis abaixo mercado cadastre lance agora", "golpe_leilao_consorcio"),
    ("Carta consórcio contemplada automóvel imóvel venda urgente negativo aceito", "golpe_leilao_consorcio"),
    ("Veículo leilão banco arrematado abaixo tabela FIPE pague sinal", "golpe_leilao_consorcio"),
    ("Imóvel leiloado Caixa apartamento barato pague entrada agora", "golpe_leilao_consorcio"),
    ("Leilão produtos apreendidos eletrônicos celular baratíssimo lance", "golpe_leilao_consorcio"),
    ("Consórcio contemplado transferência nome negativo aprovado taxa", "golpe_leilao_consorcio"),
    ("Arrematação judicial moto carro 30 por cento valor mercado lance", "golpe_leilao_consorcio"),
    ("Site leilão domínio suspeito sem certificado segurança carros baratos", "golpe_leilao_consorcio"),
    ("Leilão exclusivo Detran veículos recuperados pague taxa participação", "golpe_leilao_consorcio"),
    # GOLPE COLETA CARTÃO / MOTOBOY (GOLPE_14 + GOLPE_15)
    ("Vou recolher seu cartão para descarte seguro funcionário banco", "golpe_coleta_cartao"),
    ("Motoboy vai buscar cartão danificado precisa quebrar chip antes", "golpe_coleta_cartao"),
    ("Novo cartão chegará 5 dias úteis entregue o antigo ao motoboy", "golpe_coleta_cartao"),
    ("Enviei motoboy buscar cartão bloqueado não precisa ir agência", "golpe_coleta_cartao"),
    ("Faça PIX chave temporária dinheiro volta 1 hora conta segura", "golpe_coleta_cartao"),
    ("Funcionário banco coleta domiciliar cartão clonado assine recibo", "golpe_coleta_cartao"),
    ("Cartão bloqueado por clonagem motoboy recolhe hoje em casa", "golpe_coleta_cartao"),
    ("Precisa digitar senha no tablet para confirmar bloqueio cartão", "golpe_coleta_cartao"),
    ("Banco envia colaborador retirar cartão suspeito em domicílio", "golpe_coleta_cartao"),
    ("Motoboy entrega novo cartão e coleta antigo informe senha ativar", "golpe_coleta_cartao"),
    ("Coleta domiciliar cartão fraude detectada não saia de casa", "golpe_coleta_cartao"),
    ("PIX para chave temporária enquanto bloqueamos transação fraudulenta", "golpe_coleta_cartao"),
    # GOLPE VEÍCULO OLX / MARKETPLACE (GOLPE_16)
    ("Preço baixo veículo preciso viajar amanhã urgente vendo barato", "golpe_veiculo"),
    ("Carro único dono revisado sem detalhes preço abaixo FIPE urgente", "golpe_veiculo"),
    ("Moro outro estado envio por transportadora mande sinal segurar", "golpe_veiculo"),
    ("Mande sinal 2000 reais PIX para eu guardar o carro para você", "golpe_veiculo"),
    ("Vendo herança veículo divorciando preciso ir embora logo barato", "golpe_veiculo"),
    ("Moto carro barato dívida urgente vendo rápido sem visita presencial", "golpe_veiculo"),
    ("Anúncio OLX veículo preço irreal pede depósito antes de mostrar", "golpe_veiculo"),
    ("Carro 50 por cento FIPE proprietário viajando vende por terceiro", "golpe_veiculo"),
    ("Veículo herança inventário venda rápida transferência após sinal", "golpe_veiculo"),
    ("Comprador envia falso comprovante pagamento venda veículo golpe", "golpe_veiculo"),
    ("Vendedor some após PIX veículo nunca entregue OLX Webmotors", "golpe_veiculo"),
    ("Moto disponível foto perfeita preço ótimo pede sinal antes ver", "golpe_veiculo"),
    # GOLPE INSS / BENEFÍCIO SOCIAL (GOLPE_19)
    ("Seu auxílio-doença foi aprovado pague taxa de processo liberação", "golpe_inss_beneficio"),
    ("Você tem saldo PIS PASEP para sacar pague taxa liberação PIX", "golpe_inss_beneficio"),
    ("INSS atualização cadastral urgente clique para não perder benefício", "golpe_inss_beneficio"),
    ("Benefício social aprovado pague honorários para liberar depósito", "golpe_inss_beneficio"),
    ("FGTS esquecido liberado nome valor saque pague taxa agora", "golpe_inss_beneficio"),
    ("Aposentadoria revisão aprovada receba diferença pague taxa processo", "golpe_inss_beneficio"),
    ("Bolsa família aumento aprovado confirme dados para receber valor", "golpe_inss_beneficio"),
    ("BPC LOAS liberado para você pague taxa cartório para receber", "golpe_inss_beneficio"),
    ("Robô INSS ligou benefício bloqueado regularize cadastro agora", "golpe_inss_beneficio"),
    ("Funcionário INSS falso visita domiciliar atualização cadastral dados", "golpe_inss_beneficio"),
    ("Auxílio emergencial parcela atrasada liberada pague taxa desbloquear", "golpe_inss_beneficio"),
    ("Seguro desemprego aprovado honorários advocatícios pague adiantado", "golpe_inss_beneficio"),
    # LEGÍTIMO — simples
    ("Reunião de equipe amanhã às 14h sala de conferência", "legitimo"),
    ("Aviso de manutenção programada sistema indisponível domingo", "legitimo"),
    ("Resultado do vestibular disponível no portal acesse com login", "legitimo"),
    ("Pagamento confirmado obrigado pela preferência", "legitimo"),
    ("Reunião cancelada reagendaremos para semana que vem", "legitimo"),
    ("Bom dia como você está nos seus estudos hoje", "legitimo"),
    ("Parabéns pelo aniversário muitas felicidades desejo sucesso", "legitimo"),
    ("Confirmação de agendamento consulta médica quarta às 15h", "legitimo"),
    ("Código de rastreamento pedido atualizado saiu para entrega", "legitimo"),
    ("Nota fiscal eletrônica emitida valor correto obrigado", "legitimo"),
    ("Seu pedido foi confirmado previsão entrega 3 dias úteis", "legitimo"),
    ("Atualização sistema disponível reinicie para aplicar mudanças", "legitimo"),
    # LEGÍTIMO — e-mails reais de empresas (casos que falharam)
    ("Nubank buscador boletos encontrou novo boleto CPF emitido assistência saúde agende pagamento assistente equipe nubank mensagem automática", "legitimo"),
    ("Uber nubank clientes desconto próxima viagem pague nupay cartão nubank termos cancelar assinatura privacidade uber brasil", "legitimo"),
    ("Apple dia das mães frete grátis comprar iphone parcelado política privacidade minha conta apple cupertino", "legitimo"),
    ("iFood pedido confirmado restaurante prepara seu pedido previsão entrega rastrear avalie experiência", "legitimo"),
    ("Mercado Livre seu pedido foi enviado código rastreamento transportadora previsão chegada avalie vendedor", "legitimo"),
    ("Claro sua fatura mês referência vencimento valor pagar débito automático segunda via app claro", "legitimo"),
    ("Amazon seu pacote foi entregue avalie sua compra ver detalhes pedido central ajuda cliente", "legitimo"),
    ("Spotify sua assinatura renovada com sucesso próxima cobrança gerenciar plano cancelar preferências", "legitimo"),
    ("Receita Federal consulta CPF situação regular sem pendências declaração entregue recibo", "legitimo"),
    ("Banco do Brasil extrato conta corrente saldo disponível aplicação investimento tesouro direto", "legitimo"),
    ("Correios objeto postado prazo entrega dias úteis rastreamento código disponível site oficial", "legitimo"),
    ("Google segurança sua senha foi alterada dispositivo atividade conta verificar sou eu central ajuda", "legitimo"),
    ("LinkedIn nova mensagem conexão visualizou perfil oportunidade vaga emprego recrutador premium", "legitimo"),
    ("Magazine Luiza boleto gerado vencimento pagamento aprovado produto separado envio transportadora", "legitimo"),
    ("Vivo sua linha habilitada plano ativo consumo dados sms ligações minha vivo app central atendimento", "legitimo"),
    ("Tim fatura digital disponível valor vencimento pix código barras segunda via app tim suporte", "legitimo"),
    ("Bradesco extrato digital últimas transações saldo conta poupança cartão crédito fatura próximo vencimento", "legitimo"),
    ("Itaú você tem mensagem na sua conta acesse app itaú extrato comprovante pix realizado com sucesso", "legitimo"),
    ("Nubank seu pagamento foi realizado valor data comprovante disponível app histórico transações", "legitimo"),
    ("Apple compra realizada app store valor recibo suporte apple cancelar assinatura gerenciar compras", "legitimo"),
    ("Olá seu agendamento foi confirmado data horário local endereço comparecer com documento", "legitimo"),
    ("Sua redefinição de senha foi solicitada se não foi você ignore este email sem clicar", "legitimo"),
    ("Obrigado por sua compra pedido número processando separação estoque envio em breve", "legitimo"),
    ("Lembrete consulta amanhã clínica médica trazer exames anteriores chegar 15 minutos antes", "legitimo"),
    ("Sua nota fiscal foi emitida download disponível portal cliente número série acesse", "legitimo"),
    ("Promoção semana consumidor desconto produtos selecionados válido domingo frete grátis acima valor mínimo", "legitimo"),
    ("Prezado cliente sua solicitação protocolo foi registrada prazo resposta dias úteis ouvidoria", "legitimo"),
    ("Extrato bancário disponível acesse internet banking dados login senha token gerado app", "legitimo"),
    ("Atualização aplicativo disponível nova versão melhorias segurança acesse loja atualizar agora", "legitimo"),
    ("Confirmação cadastro realizado bem vindo plataforma acesse com email senha criar perfil", "legitimo"),
]

def build_pipeline(model_type: str = "logreg") -> Pipeline:
    vectorizer = TfidfVectorizer(
        preprocessor=preprocess_text,
        ngram_range=(1, 2),
        max_features=8000,
        sublinear_tf=True,
        min_df=1,
    )
    if model_type == "naive_bayes":
        from sklearn.naive_bayes import MultinomialNB
        clf = MultinomialNB(alpha=0.3)
    else:
        clf = LogisticRegression(
            max_iter=2000, C=2.0, class_weight="balanced",
            random_state=42, solver="lbfgs",
        )
    return Pipeline([("tfidf", vectorizer), ("clf", clf)])

def train(model_type: str = "logreg") -> dict:
    texts = [d[0] for d in TRAINING_DATA]
    labels = [d[1] for d in TRAINING_DATA]
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.20, random_state=42)
    pipeline = build_pipeline(model_type)
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    CLASSIFIER_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "classes": list(set(labels)), "model_type": model_type}, CLASSIFIER_PATH)
    print(f"[Classifier] Acurácia: {acc:.2%}")
    print(classification_report(y_test, y_pred, zero_division=0))
    return {"accuracy": acc, "report": report, "model_type": model_type, "n_train": len(X_train), "n_test": len(X_test)}

def load_classifier() -> dict:
    if not CLASSIFIER_PATH.exists():
        print("[Classifier] Modelo não encontrado. Treinando...")
        train()
    return joblib.load(CLASSIFIER_PATH)

def predict(text: str) -> dict:
    model_data = load_classifier()
    pipeline = model_data["pipeline"]
    proba = pipeline.predict_proba([text])[0]
    classes = pipeline.classes_
    label = classes[np.argmax(proba)]
    confidence = float(np.max(proba))
    return {
        "label": label,
        "confidence": confidence,
        "is_suspicious": label != "legitimo",
        "probabilities": {c: float(p) for c, p in zip(classes, proba)},
    }

if __name__ == "__main__":
    metrics = train("logreg")
    print(f"\nAcurácia final: {metrics['accuracy']:.2%}")
