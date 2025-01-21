# ADR: Banco de Dados

## Contexto

A aplicação requer um banco de dados para armazenar o status do processamento de arquivos gerados pelos microserviços. Este banco de dados deve suportar consultas frequentes dos usuários e garantir desempenho e escalabilidade à medida que o volume de eventos aumenta.

Foram consideradas as abordagens SQL e NoSQL para atender às necessidades da aplicação.

## Desafios

- Garantir desempenho consistente e escalabilidade à medida que o volume de dados cresce.
- Minimizar os esforços de gerenciamento e manutenção da infraestrutura do banco de dados.
- Prover flexibilidade para lidar com consultas dinâmicas e diferentes padrões de acesso aos dados.

## Opções Consideradas

1. **RDS (Relational Database Service):**
   - Proporciona um banco de dados relacional gerenciado com suporte para MySQL, PostgreSQL, entre outros.
   - Oferece consistência forte e é ideal para aplicações com estrutura de dados altamente normalizada.

2. **MongoDB:**
   - Banco de dados NoSQL orientado a documentos.
   - Flexível para armazenar dados semi-estruturados e adequado para aplicações com dados dinâmicos.

3. **Redis:**
   - Banco de dados em memória usado principalmente para caching.
   - Oferece baixa latência, mas não é ideal para armazenamento persistente de grandes volumes de dados.

4. **DynamoDB:**
   - Banco de dados NoSQL gerenciado pela AWS, projetado para alta escalabilidade e desempenho.
   - Suporte nativo a operações transacionais e índices secundários para consultas eficientes.

## Decisão

Foi escolhido o **DynamoDB** como banco de dados para armazenamento do status do processamento de arquivos.

## Justificativas

1. **Gerenciamento:**
   - Por ser um serviço totalmente gerenciado pela AWS, reduz significativamente os esforços operacionais e de manutenção.

2. **Desempenho:**
   - Oferece baixa latência para leituras e gravações, mesmo com grandes volumes de dados.

3. **Escalabilidade:**
   - Suporte dinâmico a escalabilidade horizontal, permitindo lidar com aumentos repentinos de tráfego sem interrupções.

4. **Integração com a AWS:**
   - Integra-se nativamente com outros serviços da AWS, como Lambda, SQS e API Gateway, simplificando a arquitetura.

## Consequências

### Positivas:

- Alta disponibilidade e desempenho consistente sem necessidade de configuração manual.
- Redução de custos operacionais devido à natureza gerenciada do serviço.
- Flexibilidade para adicionar índices e realizar consultas dinâmicas sem reestruturação do banco de dados.

### Negativas:

- Maior curva de aprendizado para equipes acostumadas com bancos de dados relacionais.
- Dependência de um serviço específico da AWS, o que pode dificultar uma migração futura para outro provedor.

## Status

**Aceito**
