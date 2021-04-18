# Enterprise Connection

CPTM

Tipos de Transporte
- Trens
- Veículos de Manutenção

Transporte
- Tipo
- Local Atual
- Horários

Pátio
- Transportes
- Fila(s) de entrada
- Fila(s) de saída
- Linha(s) de acesso

Linha
- Transporte Ocupando
- Pátio
- Linhas (lista ligada)
- solicitações de acesso

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