# Enterprise Connection

## Organização e Entidades

Local: Destino que um transporte pode ter. Patio ou Linha
* `nome`: Nome do local (deve ser único)

Agendamento: Agrupamento de um Local e horario
* `local`: Local de destino
* `horario`: Horário planejado

Transporte: Representa um trem ou veículo de manutenção que se locomove por um Trilho
* `tipo` (`C`): C (comercial) ou M (manutenção)
* `agendamento` (`None`): Próximo local e horario agendado

Trilho: Uma fila (padrão), pilha ou lista de transportes
* `tipo` (`fila`): Como o conjunto se comporta
* `maximo` (`-1`): Número máximo de transportes que cabem no trilho

Patio (Local): Um conjunto de trilhos que conectam com uma Linha
* `nome`: Nome do Local
* `trilhos`: uma ou mais pilhas que acomodam transportes e devem ser gerenciadas
* `trilho_max`: Máximo de transportes que cada pilha acomoda
* `trilho_entrada`: Fila de entrada que recebe transportes originando da Linha conectada
* `trilho_saida`: Fila de saída que possibilita os transportes de um pátio de sairem para a Linha conectada

Linha (Local): Representa os trilhos externos ao pátio associado
* `patio_dest`: O pátio de destino que os tranportes daquela linha utilizam
* `trilho`: Lista contendo os transportes

Simulação: Executa a lógica e relacionamento entre as entidades
* A simulação acontece a cada intervalo de tempo especificado na configuração em `intervalo_simulacao_segundos`
* Ao chegar no horário de termino de manutenção, a simulação é encerrada

## Config

Exemplo de configuração

```python

config = {
    # Horário que os trens comerciais começam a voltar aos patios
    "horario_termino_comercial": "00:00",

    # Tempo a partir do termino comercial que os veiculos de manutenção podem sair dos pátios
    "tempo_inicio_manutencao": "01:00",

    # Tempo a partir do termino comercial que os veiculos de manutenção devem estar de volta aos patios
    "tempo_termino_manutencao": "03:30",

    # Tempo entre avaliações
    "intervalo_simulacao_segundos": 60,

    # Estado de cada pátio no inicio da simulação
    "patios": [
        {
            "nome": "Lapa", # 37 + 2
            "trilhos": [
                ["M", "M"],
                ["M"],
                [],
                [],
            ],
            "trilho_max": 10,
            "solicitacoes_de_acesso": [
                {
                    "inicio": "02:00",
                    "termino": "03:00"
                },
                {
                    "inicio": "02:30",
                    "termino": "03:30"
                },
                {
                    "inicio": "02:30",
                    "termino": "03:30"
                }
            ]
        },
        {
            "nome": "Altino",
            "trilhos": [
                [],
                [],
                ["M", "M"],
                [],
                [],
                []
            ],
            "trilho_max": 10,
            "solicitacoes_de_acesso": [
                {
                    "inicio": "01:00",
                    "termino": "03:00"
                }
            ]
        },
        {
            "nome": "Calmon Viana",
            "trilhos": [
                ["M"],
                ["M"],
                [],
                [],
                [],
                []
            ],
            "trilho_max": 10,
            "solicitacoes_de_acesso": [
                {
                    "inicio": "02:00",
                    "termino": "03:00"
                }
            ]
        },
    ],

    # Generalização das linhas
    "linhas": [
        {
            "nome": "7+10",
            "trens_n": 22 + 15, # 37
            "patio": "Lapa"
        },
        {
            "nome": "8+9",
            "trens_n": 19 + 2 + 17, # 38
            "patio": "Altino"
        },
        {
            "nome": "11+12+13",
            "trens_n": 28 + 19 + 4, # 51
            "patio": "Calmon Viana"
        },
    ],

}
```

## Executando

```python
python main.py
```


## Processo

O usuário cadastra patios, linhas, e solicitacoes de acesso na configuracao

Restrições:
- Pátios devem suportar a quantidade de veículos de manutenção somados à quantidade de trens comerciais de uma linha
- Uma pilha no patio tem capacidade mínima para caber todos os veículos de manutenção daquele pátio
- Pilhas no pátio podem começar somente com veículos de manutenção (e não comerciais)
- Solicitações de acesso devem ter início depois do início da manutenção e término antes do término de manutenção
- O número mínimo de veículos de manutenção de um pátio deve é o número de solicitações de acesso daquele patio
- Horário de volta de um veículo de manutenção não pode ser anterior ao horário de saída de um outro veículo de manutenção do mesmo pátio


### Algoritmo


```
-- Inicialização

Definir veículos de manutenção que sairão e colocá-los na mesma fila

Cada pátio começará com fila reservada para veículos de manutenção indefinida


-- A cada iteração

Colocar na fila de entrada os transportes vindo da Linha

Verificar se há solicitações agendadas para esse horário. Se houver, mandar um veiculo de manutenção para a fila de saída

Para cada pátio:
    Para transporte na fila de entrada:
        Se fila reservada aos veículos de manutenção não está definida E espaços sobrando em uma fila é exatamente a quantidade de veículos de manutenção que sairão:
        {
            Definir essa fila como a fila reservada aos veículos de manutenção
            Mover para a fila reservada todos os veículos de manutenção que sairão
        }
        Se transporte for do tipo comercial:
            Colocar C em qualquer fila com as condições (se não funcionar, erro):
            - tem espaço 
            - não é a fila definida
            - não tenha veículos de manutenção que sairão
        Se transporte for do tipo manutenção:
            Se fila reservada está definida:
                Colocar na fila reservada
            senão:
                colocar na que estiver menos ocupada


Mover transportes da fila de saída para a Linha
```