# ADR: Arquitetura da Aplicação

## Contexto

A aplicação foi projetada para gerenciar os eventos(Upload, Verificação, Processamento e Noticiação) ocorridos no processamento 
de arquivos nos microserviços. Sua principal responsabilidade é fornecer aos usuários informações sobre o status do processamento de arquivos.

### Requisitos Funcionais

- Cadastro de eventos recebidos através de uma fila.
- Exposição de uma API para consulta dos eventos processados.

### Exemplo de Payload de Evento:

```json
{
    "id_usuario": "U12345",
    "processo": "recepcao",
    "nome_arquivo": "Arquivo1",
    "status": "ok"
}

```

### Desafios

- Garantir o desacoplamento entre regras de negócio e infraestrutura.
- Facilitar a manutenção e evolução do sistema.
- Garantir alta testabilidade para validação de regras e componentes.

### Opções

1. Arquitetura em Camadas
2. Clean Architecture
3. Portas e Adapters (Hexagonal)

### Decisão

Foi escolhida a arquitetura **Portas e Adapters** (também conhecida como Hexagonal Architecture) para o desenvolvimento da aplicação.

### Justificativas

1. **Desacoplamento:**
   - A arquitetura separa claramente as regras de negócio (core) das implementações de infraestrutura (adapters), como fila e banco de dados.

2. **Manutenção:**
   - Alterações em componentes específicos, como mudanças de fila ou banco de dados, podem ser realizadas sem impactar diretamente a lógica de negócio.

3. **Testabilidade:**
   - A lógica de negócio pode ser testada independentemente de integrações externas, utilizando mocks para as dependências injetadas.

4. **Flexibilidade:**
   - A arquitetura permite a introdução de novos canais (adapters), como APIs adicionais ou outros tipos de fila, sem alterações no core.

### Consequências

#### Positivas:

- Redução do impacto de mudanças na infraestrutura.
- Facilidade na introdução de novos canais ou tecnologias.
- Testes unitários mais fáceis e confiáveis.

#### Negativas:

- Exige maior planejamento inicial e definição de contratos claros entre as portas e adapters.

### Status

**ACEITO**
