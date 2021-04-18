import pprint
import queue
from datetime import datetime, timedelta
from time import sleep


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


# Locais sao destinos que um transporte pode ter. Patio ou Linha
class Local:
    def __init__(self, nome):
        self.nome = nome

class Agendamento:
    def __init__(self, local: Local, horario: datetime):
        self.local = local
        self.horario = horario
    def __repr__(self):
        return self.local + " " + self.horario.strftime("%H:%M:%S")

# Tipos:
#   C = Comercial
#   M = Manutencao
class Transporte:
    def __init__(self, tipo="C", agendamento : Agendamento = None):
        self.tipo = tipo
        self.agendamento = agendamento
    def __repr__(self):
        return self.tipo

# Uma fila ou pilha de transportes
class Trilho:
    def __init__(self, sem_saida=False, maximo=-1, e_fila=True):
        self.sem_saida = sem_saida
        self._transportes = []
        self.e_fila = e_fila

        if e_fila:
            self._transportes = queue.LifoQueue() if sem_saida else queue.Queue()
            if (maximo > 0):
                self._transportes.maxsize = maximo

    def __repr__(self):
        if self.e_fila:
            return f"[{ ' '.join([str(t) for t in list(self._transportes.queue)]) }]"
        else:
            return f"[{ ' '.join([str(t) for t in self._transportes]) }]"
    
    def transportes(self):
        if self.e_fila:
            return list(self._transportes.queue)
        else:
            return self._transportes

    def esta_vazio(self):
        if self.e_fila:
            return self._transportes.empty()
        else:
            return len(self._transportes) == 0

    def esta_cheio(self):
        if self.e_fila:
            return self._transportes.full()
        else:
            return False

    def add_transporte(self, transporte : Transporte):
        if self.e_fila:
            self._transportes.put(transporte)
        else:
            self._transportes.append(transporte)

    def remove_transporte(self, idx=0):
        if self.e_fila:
            return self._transportes.get()
        else:
            return self._transportes.pop(idx)

# O unico jeito de transferir um transporte de um trilho para outro
class Conector:
    def __init__(self, trilho_from : Trilho = None, trilho_to : Trilho = None):
        self.trilho_from : Trilho = trilho_from
        self.trilho_to : Trilho = trilho_to
    def conectar(self, trilho_from, trilho_to):
        self.trilho_from = trilho_from
        self.trilho_to = trilho_to
    def desconectar(self):
        self.trilho_from = None
        self.trilho_to = None
    def esta_conectado(self):
        return not (self.trilho_from == None or self.trilho_to == None)
    def pode_transferir(self):
        return self.esta_conectado() and not self.trilho_from.esta_vazio() and not self.trilho_to.esta_cheio()
    def transferir(self, idx=0):
        if self.pode_transferir():
            self.trilho_to.add_transporte(self.trilho_from.remove_transporte(idx))
        else:
            raise RuntimeError("Erro ao transferir transporte!")

# Contém uma fila de entrada, uma ou mais pilhas de transporte
class Patio(Local):
    def __init__(self, nome, trilhos, trilho_max, conectores_n=1):
        super().__init__(nome)
        # self.nome = nome
        self.trilhos = []
        for trilho in trilhos:
            trilho_obj = Trilho(sem_saida=True, maximo=trilho_max)
            for transporte in trilho:
                trilho_obj.add_transporte(Transporte(transporte))
            self.trilhos.append(trilho_obj)

        self.trilho_entrada = Trilho()
        self.conector_linha_entrada = None

        self.trilho_saida = Trilho()
        self.conector_saida_linha = None

        self.conectores = [Conector() for i in range(conectores_n)]
    def __repr__(self):
        return f"Patio {self.nome:<20} -- trihos: {self.trilhos} -- entrada: {self.trilho_entrada}" #", {self.saida_q}, {self.conectores}"

# Contém apenas um trilho com transportes
class Linha(Local):
    def __init__(self, nome, patio_dest):
        super().__init__(nome)
        self.patio_dest = patio_dest
        self.trilho = Trilho(e_fila=False)
        self.conector_linha_patioentrada = None
        self.conector_linha_patiosaida = None
    def __repr__(self):
        return f"Linha {self.nome:<20} -- trilho: {self.trilho} -- patio {self.patio_dest.nome}"

class Simulacao:
    def __init__(self, config):
        self.p = pprint.PrettyPrinter(indent=4).pprint
        self.running = False

        # Horarios
        hoje = datetime.today()
        refData = datetime(year=hoje.year, month=hoje.month, day=hoje.day)
        (h,m) = (int(v) for v in config['horario_termino_comercial'].split(':'))
        self.horario_termino_comercial = refData + timedelta(hours=h, minutes=m)

        self.horario_atual : datetime = self.horario_termino_comercial

        (h,m) = (int(v) for v in config['tempo_inicio_manutencao'].split(':'))
        self.horario_inicio_manutencao : datetime = self.horario_termino_comercial + timedelta(hours=h, minutes=m)

        (h,m) = (int(v) for v in config['tempo_termino_manutencao'].split(':'))
        self.horario_termino_manutencao : datetime = self.horario_termino_comercial + timedelta(hours=h, minutes=m)

        # Tempo em que chegarão trens nos patios
        self.tempo_trens_recolhimento = self.horario_inicio_manutencao - self.horario_termino_comercial

        # Intervalo de tick da simulacao
        self.intervalo_simulacao_segundos = config['intervalo_simulacao_segundos']

        self.p(f"{self.horario_termino_comercial}, {self.horario_inicio_manutencao}, {self.horario_termino_manutencao}")
        self.p("Tempo para recolhimento: " + str(self.tempo_trens_recolhimento))

        # Patios
        self.patios = [Patio(**p) for p in config['patios']]
        # self.p(self.patios)

        # Linhas
        self.linhas = []
        for l in config['linhas']:
            patio_dest = [p for p in self.patios if p.nome == l['patio']][0]
            linha = Linha(l['nome'], patio_dest)

            # Conector da Linha para a fila de entrada do patio
            conector_linha_patioentrada = Conector(linha.trilho, patio_dest.trilho_entrada)
            linha.conector_linha_patioentrada = conector_linha_patioentrada
            patio_dest.conector_linha_entrada = conector_linha_patioentrada

            # Conector da fila de saida do patio para a Linha
            conector_patiosaida_linha = Conector(patio_dest.trilho_saida, linha.trilho)
            linha.conector_linha_patiosaida = conector_patiosaida_linha
            patio_dest.conector_saida_linha = conector_patiosaida_linha

            delta = int(self.tempo_trens_recolhimento.total_seconds() // l['trens_n'])
            self.p(f"Linha {l['nome']} n: {l['trens_n']} intervalo: {delta}s")
            for i in range(l['trens_n']):
                horario = self.horario_termino_comercial + timedelta(seconds=delta * i)
                agendamento = Agendamento(l['patio'], horario)
                linha.trilho.add_transporte(Transporte(tipo="C", agendamento=agendamento))
            self.linhas.append(linha)
        # self.p(self.linhas)

        self._print_estado()
    
    def _print_estado(self):
        self.log("Estado")

        print("\nPatios")
        for p in self.patios:
            print(p)

        print("\nLinhas")
        for l in self.linhas:
            print(l)

    
    def log(self, *msg):
        p = "[" + self.horario_atual.strftime("%H:%M:%S") +"]"
        print(p, *msg)

    def run(self):
        self.running = True
        while self.running:
            self.tick()
            if (self.horario_atual >= self.horario_termino_manutencao):
                self.running = False
            else:
                self.horario_atual += timedelta(seconds=self.intervalo_simulacao_segundos)
        self._print_estado()
    
    def tick(self):
        self.log("tick")
        for patio in self.patios:
            linhas = [l for l in self.linhas if l.patio_dest.nome == patio.nome]
            # Todos os trens programados para chegar no local ate esse horario
            for linha in linhas:
                transferir = [t for t in linha.trilho.transportes() if t.agendamento.local == patio.nome and t.agendamento.horario <= self.horario_atual]
                for transporte in transferir:
                    idx = linha.trilho.transportes().index(transporte)
                    self.log(f"Transferindo transporte. tipo='{transporte.tipo}' de='{linha.nome}' para='{patio.nome}' agendamento='{transporte.agendamento}'")
                    # Isso funciona pois sabemos que a linha não é uma pilha ou fila
                    linha.conector_linha_patioentrada.transferir(idx)
    

if __name__ == "__main__":
    sim = Simulacao(config)
    sim.run()
