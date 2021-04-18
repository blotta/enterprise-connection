# Enterprise Connection

## Organização e Entidades

Local: Destino que um transporte pode ter.
* `nome`: Nome do local (deve ser único)

Agendamento: Agrupamento de um Local e horario
* `local`: Local de destino
* `horario`: Horário planejado

Transporte: Representa um trem ou veículo de manutenção.
* `tipo` (`C`): C (comercial) ou M (manutenção)
* `agendamento` (`None`): Próximo local e horario agendado

Trilho: Uma fila (padrão), pilha ou lista de transportes
* `maximo` (`-1`): Número máximo de transportes que cabem no trilho
* `sem_saída` (`False`): Torna fila em pilha (Last In First Out)
* `e_fila` (`True`): indica se é uma fila (queue) ou lista. Se for lista, os valores de `máximo` e `sem_saida` são ignorados

Conector: O único jeito de transferir um transporte de um trilho para outro
* `trilho_from`: triho de origem
* `trilho_to`: triho de destino

Patio (Local): Um conjunto de trilhos
* `nome`: Nome do Local
* `trilho_max`: Máximo de transportes que cada pilha acomoda
* `conectores_n`: Número de conectores que estão disponíveis para gerenciar as pilhas
* `trilhos`: uma ou mais pilhas que acomodam transportes e devem ser gerenciadas
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

    # # Horário que os trens comerciais iniciam a operação
    # "horario_inicio_comercial": "04:00",

    # Tempo entre avaliações
    "intervalo_simulacao_segundos": 60,

    # Estado de cada pátio no inicio da simulação
    "patios": [
        {
            "nome": "Lapa",
            "trilhos": [
                ["M", "M"],
                [],
                [],
                [],
                []
            ],
            "trilho_max": 5,
            "conectores_n": 1,
        },
        {
            "nome": "Altino",
            "trilhos": [
                ["M", "M"],
                [],
                [],
                [],
                []
            ],
            "trilho_max": 5,
            "conectores_n": 1,
        },
        {
            "nome": "Calmon Viana",
            "trilhos": [
                ["M"],
                [],
                [],
                [],
                []
            ],
            "trilho_max": 5,
            "conectores_n": 1,
        },
    ],

    # Generalização das linhas
    "linhas": [
        {
            "nome": "7+10",
            "trens_n": 22 + 15,
            "patio": "Lapa"
        },
        {
            "nome": "8+9",
            "trens_n": 19 + 2 + 17,
            "patio": "Altino"
        },
        {
            "nome": "11+12+13",
            "trens_n": 28 + 19 + 4,
            "patio": "Calmon Viana"
        },
    ],
}
```

## Executando

```python
python main.py
```