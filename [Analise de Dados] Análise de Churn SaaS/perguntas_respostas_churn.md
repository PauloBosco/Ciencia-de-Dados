# Perguntas e Respostas - Análise de Churn SaaS

## 1. Qual era o objetivo da análise?
Identificar padrões de churn (cancelamento de clientes), avaliar impactos na receita, entender os principais motivos de cancelamento e encontrar sinais que possam ajudar na retenção de clientes.

## 2. Quais bases de dados foram utilizadas?
- Accounts
- Subscriptions
- Feature Usage
- Support Tickets
- Churn Events

## 3. Quais verificações de qualidade dos dados foram realizadas?
- Quantidade de registros por tabela.
- Verificação de valores nulos.
- Validação de relacionamentos entre tabelas.
- Busca por registros duplicados.
- Conversão de colunas de data para formato adequado.

## 4. O que representa a taxa de churn?
A porcentagem de clientes que cancelaram seus serviços em relação ao total de clientes.

## 5. Por que analisar churn é importante?
Porque o churn impacta diretamente a receita recorrente, o crescimento da empresa e os custos de aquisição de novos clientes.

## 6. O que é MRR Churn?
É a porcentagem da receita recorrente mensal perdida devido ao cancelamento de assinaturas.

## 7. Quais análises de churn foram realizadas?
- Churn geral.
- Churn por indústria.
- Churn de receita (MRR).
- Motivos de cancelamento.
- Clientes reincidentes.
- Feedbacks dos clientes.
- Relação entre suporte e churn.
- Relação entre uso da plataforma e churn.
- Churn por país.

## 8. O que os motivos de churn ajudam a identificar?
Eles mostram as causas mais frequentes dos cancelamentos e ajudam a priorizar melhorias no produto, atendimento e estratégia comercial.

## 9. Por que analisar clientes reincidentes?
Porque clientes que cancelam mais de uma vez podem indicar problemas recorrentes de experiência, produto ou onboarding.

## 10. Qual a importância dos feedbacks de churn?
Os feedbacks ajudam a transformar dados quantitativos em insights qualitativos, revelando problemas específicos relatados pelos clientes.

## 11. O que a análise de suporte buscou avaliar?
A relação entre:
- Quantidade de tickets.
- Satisfação dos clientes.
- Tempo de resposta.
- Escalações de chamados.
- Probabilidade de churn.

## 12. Qual hipótese foi levantada sobre o suporte?
Mesmo quando a satisfação aparente é boa, o suporte pode não estar resolvendo completamente os problemas do cliente, contribuindo para cancelamentos.

## 13. Por que analisar o uso das funcionalidades?
Clientes que utilizam mais recursos tendem a extrair mais valor do produto e geralmente possuem menor propensão ao churn.

## 14. O que a análise por país pode revelar?
Diferenças regionais de comportamento, qualidade do atendimento, adaptação do produto e oportunidades de expansão.

## 15. Quais possíveis ações podem reduzir o churn?
- Melhorar onboarding.
- Atuar sobre os principais motivos de cancelamento.
- Criar campanhas de retenção.
- Monitorar clientes com baixa utilização.
- Melhorar a resolução dos chamados de suporte.
- Realizar pesquisas de satisfação periódicas.

## 16. Qual é a principal conclusão da análise?
As evidências apontam que o churn está sendo impulsionado principalmente por:

Baixo engajamento com a plataforma (principal fator).
1.Falta de funcionalidades desejadas.
2.Percepção de preço elevado.
3.Migração para concorrentes.
4.Problemas complexos de suporte (escalonamentos).

Recomendações
Alta Prioridade
- Criar alertas para clientes com queda de uso.
- Implementar Customer Health Score.
- Melhorar onboarding e adoção das funcionalidades.
- Investigar necessidades específicas do segmento DevTools.

Média Prioridade
- Revisar posicionamento de preço.
- Priorizar funcionalidades mais solicitadas.
- Estudar os concorrentes citados nos feedbacks.

Baixa Prioridade
- Investigar diferenças regionais, principalmente na Alemanha.
