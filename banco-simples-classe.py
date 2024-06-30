import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica (Cliente):
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
    
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero,cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @saldo.setter
    def saldo(self, valor):
        self._saldo = valor
    
    @property
    def numero(self):
        return self._numero
    
    @property 
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    def sacar (self, valor):
        
        excedeu_saldo = valor > self.saldo

        if excedeu_saldo:
            print("Operação falhou! Você não tem saldo suficiente.")

        elif valor > 0:
            self.saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True

        else:
            print("Operação falhou! O valor informado é inválido.")

        return False
        
    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("@@@ Operação falhou! O valor informado é inválido. @@@")
            return False
        
        return True
    
class ContaCorrente(Conta): 
    def __init__(self, numero, cliente, limite = 500, limite_saques = 3):
        super().__init__(numero,cliente)
        self.limite = limite
        self.limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques
        
        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self.transacoes = []
        
    def adicionar_transacao(self, transacao):
        self.transacoes.append (
            {
                "tipo" : transacao.__class__.__name__,
                "valor": transacao.valor,
                "data" : datetime.now().strftime("%d-%m-%Y %H:%M:%s")
            }
        )

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    
    @abstractmethod
    def registrar(conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
        
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Control:
    
    @staticmethod
    def menu():
        menu = f"""\n
        {"MENU".center(40,"=")}
        [d]\tDepositar
        [s]\tSacar
        [e]\tExtrato
        [nc]\tNova Conta
        [lc]\tListar Contas
        [nu]\tNovo usuário
        [q]\tSair

        => """
        return input(textwrap.dedent(menu))
    
    @classmethod
    def main(cls):
        clientes = []
        contas = []

        while True:

            opcao = cls.menu()
                    
            if opcao == "d":
                cls.depositar(clientes)

            elif opcao == "s":
                cls.sacar(clientes)

            elif opcao == "e":
                cls.exibir_extrato(clientes)
            
            elif opcao == "nu":
                cls.criar_cliente(clientes)
                
            elif opcao == "nc":
                numero_conta = len(contas)
                cls.criar_conta (numero_conta,clientes, contas)
            
            elif opcao == "lc":
                cls.listar_contas(contas)

            elif opcao == "q":
                break

            else:
                print("Operação inválida, por favor selecione novamente a operação desejada.")
    
    @staticmethod
    def recuperar_conta_cliente(cliente):
        if not cliente.contas:
            print("\n@@@ Cliente não possui conta! @@@")
            return
        
        #FIXME: não permite o cliente escolher a conta
        return cliente.contas[0]
    
    @classmethod
    def depositar(cls,clientes):
        cpf = input("Informe o CPF do cliente: ")
        cliente = cls.filtrar_cliente(cpf,clientes)
        
        if not cliente:
            print("\n@@@ Cliente não encontrado! @@@")
            return
        
        valor = float(input("Informe o valor do depósito: "))
        transacao = Deposito(valor)
        
        conta = cls.recuperar_conta_cliente(cliente)
        if not conta:
            return
        
        cliente.realizar_transacao(conta, transacao)
    
    @classmethod
    def criar_cliente(cls,clientes):
        cpf = input("Informe o CPF (somente números): ")
        cliente = cls.filtrar_cliente(cpf,clientes)
        
        if cliente:
            print("\n@@@ Já existe usuário com esse CPF! @@@")
            return
        
        nome = input("Informe o nome completo: ")
        data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
        endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
        
        cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco = endereco)
        
        clientes.append(cliente)
        print("=== Cliente criado com sucesso! ===")  

    @staticmethod
    def filtrar_cliente(cpf,clientes):
        clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
        return clientes_filtrados[0] if clientes_filtrados else None

    @staticmethod
    def listar_contas(contas):
        for conta in contas:
            print("="*80)
            print(textwrap.dedent(str(conta)))
    
    @classmethod
    def sacar (cls, clientes):
        
        cpf = input("Informe o CPF do cliente: ")
        cliente = cls.filtrar_cliente(cpf,clientes)
        
        if not cliente:
            print("\n@@@ Cliente não encontrado! @@@")
            return
        
        valor = float(input("Informe o valor do saque: "))
        transacao = Saque(valor)
        
        conta = cls.recuperar_conta_cliente(cliente)
        if not conta:
            return
        
        cliente.realizar_transacao(conta, transacao)
        
    @classmethod
    def criar_conta(cls, numero_conta, clientes, contas):
        cpf = input("Informe o CPF do cliente: ")
        cliente = cls.filtrar_cliente(cpf, clientes)
        
        if not clientes:
            print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
            return
        
        conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
        contas.append(conta)
        cliente.contas.append(conta)
        
        print("\n=== Conta criada com sucesso! ===")

    @classmethod
    def exibir_extrato(cls, clientes):
        cpf = input("Informe o CPF do cliente: ")
        cliente = cls.filtrar_cliente(cpf, clientes)
        
        if not cliente:
            print("\n@@@ Cliente não encontrado! @@@")
            return
        
        conta = cls.recuperar_conta_cliente(cliente)
        if not conta:
            return
        
        print(f"\n {'EXTRATO'.center(30,'=')}")
        transacoes = conta.historico.transacoes
        
        extrato = ""
        if not transacoes:
            extrato = "Não foram realizadas movimentações."
        else:
            for transacao in transacoes:
                extrato += f"\n{transacao['tipo']}:\n\tR${transacao['valor']:.2f}"
        print(extrato)
        print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
        print("="*37)
        
Control.main()

