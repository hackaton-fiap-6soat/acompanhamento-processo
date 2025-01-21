# ADR: Tipo de Comunicação

## Contexto
A aplicação precisa receber eventos de outros microserviços para armazenar o status do processamento e disponibilizar
para o usuário o acompanhamento do processamento.

## Desafios
- Garantir alta disponibilidade e confiabilidade na comunicação.
- Minimizar o esforço de configuração e gerenciamento.
- Prover escalabilidade para aumentar o volume de mensagens sem interrupções.

## Opções
1. **Sincrona:** Aguardar o processamento(gravação no banco) da mensagem
2. **Assincrona:** Não aguardar o processamento(gravação no banco) da mensagem.

## Decisão
Optou-se pela comunicação **Assíncrona**.

## Justificativas
1. **Desempenho**: A comunicação assíncrona permite que a aplicação continue processando outras tarefas enquanto aguarda o recebimento das mensagens, melhorando a eficiência geral.
2. **Escalabilidade**: A comunicação assíncrona facilita a escalabilidade, permitindo que a aplicação gerencie picos de tráfego de maneira mais eficiente, sem depender de uma resposta imediata.
3. **Resiliência**: A comunicação assíncrona aumenta a resiliência, pois as mensagens podem ser enfileiradas e processadas quando a aplicação estiver pronta, sem risco de perda de dados em caso de falhas temporárias.
4. **Desacoplamento**: Facilita o desacoplamento entre os microserviços, permitindo que eles operem de forma independente e sem necessidade de sincronização constante.

## Consequências

### Positivas:
- Menor dependência de sincronização entre os serviços, permitindo maior flexibilidade e resiliência na comunicação.
- Aumenta a capacidade da aplicação de lidar com picos de tráfego sem sobrecarregar os componentes.
- Reduz a complexidade operacional, já que não há necessidade de gerenciar as interações diretas entre serviços de forma contínua.

### Negativas:
- Potencial aumento da latência nas respostas, já que a comunicação não ocorre em tempo real.
- Maior complexidade na gestão de falhas e retrys, uma vez que as mensagens são processadas de forma assíncrona.
- Difícil de garantir a ordem exata de processamento das mensagens em sistemas com alto volume de tráfego.

## Status
**APROVADO**
