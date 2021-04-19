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


# Locais sao destinos que um transporte pode ter. Patio ou Linha
class Local:
    def __init__(self, nome):
        self.nome = nome

class Agendamento:
    def __init__(self, local: Local, horario: datetime):
        self.local = local
        self.horario = horario
    def __repr__(self):
        return self.local.nome + " " + self.horario.strftime("%H:%M:%S")

class SolicitacaoAcesso:
    def __init__(self, inicio: datetime, termino: datetime):
        # self.local : Local = local
        self.inicio : datetime= inicio
        self.termino : datetime = termino
        self.status = "pendente" # pendente, atendendo, atendida
        self.veiculo_manutencao = None
    def __repr__(self):
        return "inicio='" + self.inicio.strftime("%H:%M:%S") + "' termino='" + self.termino.strftime("%H:%M:%S") + "' status='" + self.status + "'"

# Tipos:
#   C = Comercial
#   M = Manutencao
class Transporte:
    def __init__(self, tipo="C", agendamento : Agendamento = None):
        self.tipo = tipo
        self.agendamento = agendamento
        self.marcado_sair = False
        self.solicitacao = None
    def __repr__(self):
        return self.tipo if not self.marcado_sair else "S"

# Uma fila ou pilha de transportes
class Trilho:
    # def __init__(self, sem_saida=False, maximo=-1, e_fila=True):
    def __init__(self, tipo="fila", maximo=-1):
        self._transportes = []
        self.tipo = tipo # fila, pilha, lista
        self.maximo = maximo

    def __repr__(self):
        return f"[{ ' '.join([str(t) for t in self._transportes]) }]"
    
    def transportes(self):
        return self._transportes

    def esta_vazio(self):
        return len(self._transportes) == 0

    def esta_cheio(self):
        return self.maximo > 0 and not (len(self._transportes) < self.maximo)
    
    def ocupado(self):
        return len(self._transportes)

    def add_transporte(self, transporte : Transporte):
        if self.esta_cheio():
            raise RuntimeError("Trilho cheio!")
        self._transportes.append(transporte)

    def remove_transporte(self, idx=0):
        if self.tipo == "lista":
            return self._transportes.pop(idx)
        elif self.tipo == "fila":
            return self._transportes.pop(0)
        elif self.tipo == "pilha":
            return self._transportes.pop()
    
    def proximo(self):
        if self.esta_vazio():
            return None

        if self.tipo == "lista" or self.tipo == "fila":
            return self._transportes[0]
        elif self.tipo == "pilha":
            return self._transportes[-1]

    def contem(self, transporte: Transporte):
        return transporte in self._transportes
    
    def tamanho_max(self):
        return self.maximo

# Contém uma fila de entrada, uma ou mais pilhas de transporte
class Patio(Local):
    def __init__(self, nome, trilhos, trilho_max, solicitacoes):
        super().__init__(nome)
        self.vms_a_sair = []
        self.solicitacoes = solicitacoes
        self.trilhos = []
        self.trilho_reservado = None
        self.trilho_entrada = Trilho(tipo="fila")
        self.trilho_saida = Trilho(tipo="fila")

        vm_count = 0
        for trilho in trilhos:
            trilho_obj = Trilho(tipo="pilha", maximo=trilho_max)
            for transporte in trilho:
                trilho_obj.add_transporte(Transporte(transporte))
                vm_count += 1
            self.trilhos.append(trilho_obj)
        
        if vm_count < len(self.solicitacoes):
            raise Exception("Não há veículos o suficiente para atender às solicitações")

        # Definindo veiculos de manutencao que vao sair
        while len(self.vms_a_sair) < len(self.solicitacoes):
            for i in range(len(self.trilhos)):
                proximo = self.trilhos[i].proximo()
                if proximo != None:
                    proximo.marcado_sair = True
                    self.vms_a_sair.append(self.trilhos[i].remove_transporte())
                if len(self.vms_a_sair) >= len(self.solicitacoes):
                    break
        
        for vm in self.vms_a_sair:
            for i in range(len(self.trilhos)):
                if not self.trilhos[i].esta_cheio():
                    self.trilhos[i].add_transporte(vm)
                    break
    
    def proximo_vm_a_sair(self):
        for trilho in self.trilhos:
            vm = trilho.proximo()
            if vm in self.vms_a_sair:
                return (trilho, vm)

    def _reservar_trilho(self, t):
        self.trilho_reservado = t
        for trilho in self.trilhos:
            if trilho == self.trilho_reservado:
                continue
            proximo = trilho.proximo()
            while proximo != None and proximo.tipo == "M" and proximo.marcado_sair == True:
                self.trilho_reservado.add_transporte(trilho.remove_transporte())
                proximo = trilho.proximo()

    
    def checar_trilho_reservado(self):
        if self.trilho_reservado != None:
            return False

        tamanho_req = len(self.vms_a_sair)
        for trilho in self.trilhos:
            # Se tem veiculo a sair, nao considere
            if len([t for t in trilho.transportes() if t in self.vms_a_sair]) > 0:
                continue

            # atinge condicao de reserva
            if tamanho_req + trilho.ocupado() == trilho.maximo:
                self._reservar_trilho(trilho)
                return True
        return False

    def __repr__(self):
        ret = f"Patio {self.nome:<20} -- trihos: {self.trilhos} -- entrada: {self.trilho_entrada}"
        ret += "\nSolicitacoes:\n"
        for s in self.solicitacoes:
            ret += '- ' + str(s) + "\n"
        return ret

# Contém apenas um trilho com transportes
class Linha(Local):
    def __init__(self, nome, patio_dest):
        super().__init__(nome)
        self.patio_dest = patio_dest
        self.trilho = Trilho(tipo="lista")

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
        self.patios = []
        for p in config['patios']:
            nome = p['nome']
            trilhos = p['trilhos']
            print(nome, trilhos)
            trilho_max = p['trilho_max']
            solics = []
            for s in p['solicitacoes_de_acesso']:
                (h,m) = (int(v) for v in s['inicio'].split(':'))
                inicio = refData + timedelta(hours=h, minutes=m)
                (h,m) = (int(v) for v in s['termino'].split(':'))
                termino = refData + timedelta(hours=h, minutes=m)
                solics.append(SolicitacaoAcesso(inicio, termino))
            self.patios.append(Patio(nome, trilhos, trilho_max, solics))

        # Linhas
        self.linhas = []
        for l in config['linhas']:
            patio_dest = next(p for p in self.patios if p.nome == l['patio'])
            patio_suporta = len(patio_dest.trilhos) * patio_dest.trilhos[0].tamanho_max()
            vms_no_patio = sum([t.ocupado() for t in patio_dest.trilhos])
            if l['trens_n'] + vms_no_patio > patio_suporta:
                raise Exception(f"Patio {patio_dest.nome} suporta no maximo {patio_suporta} transportes. Tentando usar {l['trens_n']} + {vms_no_patio}")

            linha = Linha(l['nome'], patio_dest)

            delta = int(self.tempo_trens_recolhimento.total_seconds() // l['trens_n'])
            self.log(f"Linha {l['nome']} n: {l['trens_n']} intervalo: {delta}s")
            for i in range(l['trens_n']):
                horario = self.horario_termino_comercial + timedelta(seconds=delta * i)
                agendamento = Agendamento(patio_dest, horario)
                linha.trilho.add_transporte(Transporte(tipo="C", agendamento=agendamento))
            self.linhas.append(linha)

        
        # a partir das solicitacoes de acesso, determinar que veiculos de manutencao precisarao sair do patio que estao

        # Guarda strings dos estados
        self._snapshots = []
        self.salvar_estado() # Guardando estado inicial

        self.log(self._snapshots[0][1])
    
    def salvar_estado(self):
        self._snapshots.append((self.horario_atual.strftime("%H:%M:%S"), self._estado()))
    
    def _estado(self):
        s = "Estado"
        s += "\nPatios\n"
        for p in self.patios:
            s += str(p) + "\n"
        s += "\nLinhas\n"
        for l in self.linhas:
            s += str(l) + "\n"
        return s
    
    def log(self, *msg):
        p = "[" + self.horario_atual.strftime("%H:%M:%S") +"]"
        print(p, *msg)

    def run(self):
        self.running = True
        self.initialize_simulation()
        while self.running:
            self.tick()

            delta = timedelta(seconds=self.intervalo_simulacao_segundos)
            if (self.horario_atual >= self.horario_termino_manutencao):
                self.running = False
            else:
                self.horario_atual += delta
        self.log(self._estado())
    
    def initialize_simulation(self):
        # Definir veiculos de manutencao que vao sair
        pass

    
    def tick(self):
        self.log("tick")
        print_estado = False
        # Iterando sobre patios
        for patio in self.patios:
            # Na modelação utilizada, só existe uma linha por patio
            linha = next(l for l in self.linhas if l.patio_dest == patio)

            # Todos os transportes programados para chegar no local ate esse horario
            transportes_chegando = [t for t in linha.trilho.transportes() if t.agendamento.local == patio and t.agendamento.horario <= self.horario_atual]
            for transporte in transportes_chegando:
                transporte.agendamento = None
                idx = linha.trilho.transportes().index(transporte)
                if transporte.tipo == "M":
                    transporte.solicitacao.status = "atendida"
                    transporte.solicitacao = None
                    self.log("Veiculo de manutencao atendeu à solicitação")
                self.log(f"Transferindo transporte. tipo='{transporte.tipo}' de='{linha.nome}' para='{patio.nome}'")
                patio.trilho_entrada.add_transporte(linha.trilho.remove_transporte(idx))
            
            # Verificar solicitações
            for sol in [s for s in patio.solicitacoes if s.status == "pendente"]:
                if self.horario_atual >= sol.inicio:
                    # Enviar vm
                    (trilho, vm) = patio.proximo_vm_a_sair()
                    vm.agendamento = Agendamento(patio, sol.termino) # Colocando agendamento de volta no veiculo
                    sol.status = "atendendo"
                    sol.veiculo_manutencao = vm
                    vm.solicitacao = sol
                    patio.trilho_saida.add_transporte(trilho.remove_transporte())
                    self.log(f"Enviando veiculo de manutenção para atendimento de solicitacao com inicio {sol.inicio.strftime('%H:%M:%S')}. Agendamento de retorno: '{vm.agendamento}'")
                    print_estado = True
            
            # condicao de entrada no patio
            while not patio.trilho_entrada.esta_vazio():
                if patio.checar_trilho_reservado():
                    print_estado = True
                    self.log(f"Reservou trilho em {patio.nome}")
                transporte_entrando = patio.trilho_entrada.proximo()
                if transporte_entrando.tipo == "C":
                    for trilho in patio.trilhos:
                        if patio.trilho_reservado == trilho:
                            continue
                        if trilho.esta_cheio():
                            continue
                        proximo = trilho.proximo()
                        if proximo != None and proximo.tipo == "M" and proximo.marcado_sair == True:
                            continue
                        trilho.add_transporte(patio.trilho_entrada.remove_transporte())
                        break
                elif transporte_entrando.tipo == "M":
                    if patio.trilho_reservado != None:
                        patio.trilho_reservado.add_transporte(patio.trilho_entrada.remove_transporte())
                    else:
                        ocupado = [t.ocupado() for t in patio.trilhos]
                        menos_ocupado = ocupado.index(min(ocupado))
                        patio.trilhos[menos_ocupado].add_transporte(patio.trilho_entrada.remove_transporte())

                
            # Transportes saindo do patio
            while not patio.trilho_saida.esta_vazio():
                linha.trilho.add_transporte(patio.trilho_saida.remove_transporte())
            
        if (print_estado):
            self.log(self._estado())
                    
    

if __name__ == "__main__":
    sim = Simulacao(config)
    sim.run()
