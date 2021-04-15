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

```yaml
Locais:
- nome: Lapa
  tipo: patio
  trens: 0
- nome: Altino
  tipo: patio
  trens: 0
- nome: Calmon Viana
  tipo: patio
  trens: 0
- nome: "7"
  tipo: linha
  trens: 26
- nome: "10"
  tipo: linha
  trens: 26
- nome: "8"
  tipo: linha
  trens: 26
- nome: "9"
  tipo: linha
  trens: 26
- nome: "11"
  tipo: linha
  trens: 26
- nome: "12"
  tipo: linha
  trens: 26

Conexoes:
- "7-Lapa"
- "10-Lapa"
- "8-Altino"
- "9-Altino"
- "11-Calmon Viana"
- "12-Calmon Viana"
```
