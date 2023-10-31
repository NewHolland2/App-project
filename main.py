import kivy
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

# kivy.require('2.2.0')  # Verifique a versão do Kivy
class CarreiroApp(App):

    def build(self):
        self.title = 'Marcação de Carreiro'

        # Layout principal
        self.layout = BoxLayout(orientation='vertical', padding=10)

        # Entradas para nome, comprimento da linha e espaçamento
        self.name_input = TextInput(hint_text='Nome da Pessoa')
        self.comprimento_linha_input = TextInput(hint_text='Comprimento da Linha (metros)')
        self.espacamento_entre_mudas = TextInput(hint_text='Espaçamento entre Mudas (centímetros)') # espacamento

        # Botões para ações
        self.comecando_carreiro_button = Button(text='Iniciar Carreiro')
        self.finalizando_carreiro_button = Button(text='Finalizar Carreiro')
        self.adicionando_nome_button = Button(text='Adicionar Nome')
        self.visualizacao_carreiro_button = Button(text='Ver Carreiros')

        # Rótulando os registros de carreiros
        self.registro_carreiros = Label(text='Registros de Carreiros:')

        # Layout para nomes e botões de edição
        self.layout_button_names = BoxLayout(orientation='vertical')

        # Vinculação de eventos
        self.comecando_carreiro_button.bind(on_press=self.iniciando_carreiro)
        self.finalizando_carreiro_button.bind(on_press=self.finalizando_carreiro)
        self.adicionando_nome_button.bind(on_press=self.adicionando_nome)
        self.visualizacao_carreiro_button.bind(on_press=self.visualizacao_de_carreiros)

        # Adicionar widgets ao layout principal
        self.layout.add_widget(self.name_input)
        self.layout.add_widget(self.comprimento_linha_input)
        self.layout.add_widget(self.espacamento_entre_mudas)
        self.layout.add_widget(self.comecando_carreiro_button)
        self.layout.add_widget(self.finalizando_carreiro_button)
        self.layout.add_widget(self.adicionando_nome_button)
        self.layout.add_widget(self.visualizacao_carreiro_button)
        self.layout.add_widget(self.registro_carreiros)
        self.layout.add_widget(self.layout_button_names)

        # Conectando banco de dados SQLite
        self.conn = sqlite3.connect('nomes.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS nomes (id INTEGER PRIMARY KEY, nome TEXT)')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS carreiros (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                quantidade INTEGER
            )
        ''')
        self.conn.commit()

        # Dicionário para armazenar o número de carreiros por pessoa
        self.carreiros_por_pessoa = {}

        # Carregar nomes do banco de dados e criar botões
        self.carregando_nomes()

        return self.layout

    def iniciando_carreiro(self, instance):
        nome = self.name_input.text
        comprimento_linha = float(self.comprimento_linha_input.text)
        espacamento_mudas = float(self.espacamento_entre_mudas.text) # espacamento

        num_mudas = int(comprimento_linha * 100 / espacamento_mudas)  # Converter metros em centímetros
        num_carreiros = num_mudas // 2000  # Uma muda a cada 2000 pés

        if nome in self.carreiros_por_pessoa:
            self.carreiros_por_pessoa[nome] += num_carreiros
        else:
            self.carreiros_por_pessoa[nome] = num_carreiros

        self.registro_carreiros.text += f'\nCarreiro iniciado por {nome}. {num_carreiros} carreiros a serem feitos.'

    def finalizando_carreiro(self, instance):
        nome = self.name_input.text
        comprimento_linha = float(self.comprimento_linha_input.text)
        espacamento_mudas = float(self.espacamento_entre_mudas.text) # espacamento

        num_mudas = int(comprimento_linha * 100 / espacamento_mudas)  # Converter metros em centímetros
        num_carreiros = num_mudas // 2000  # Uma muda a cada 2000 pés

        if nome in self.carreiros_por_pessoa:
            self.carreiros_por_pessoa[nome] += num_carreiros
        else:
            self.carreiros_por_pessoa[nome] = num_carreiros

        self.registro_carreiros.text += f'\nCarreiro finalizado por {nome}. {num_carreiros} carreiros concluídos.'

    def adicionando_nome(self, instance):
        # Abra um popup para adicionar um novo nome
        content = BoxLayout(orientation="vertical")
        nome_input = TextInput(hint_text="Nome da Pessoa")
        salvando_button = Button(text="Salvar")
        content.add_widget(Label(text="Adicionar Novo Nome:"))
        content.add_widget(nome_input)
        content.add_widget(salvando_button)

        popup = Popup(title="Novo Nome", content=content, auto_dismiss=False, size_hint=(None, None), size=(300, 200))

        def salvando_novo_nome(instance):
            new_name = nome_input.text.strip()
            if new_name:
                self.cursor.execute("INSERT INTO nomes (nome) VALUES (?)", (new_name,))
                self.conn.commit()
                popup.dismiss()
                self.carregando_nomes()
                self.registro_carreiros.text += f'\nNome "{new_name}" adicionado.'

        salvando_button.bind(on_press=salvando_novo_nome)
        popup.open()

    def carregando_nomes(self):
        # Limpando a posição atual dos nomes
        self.layout_button_names.clear_widgets()

        # Carregue nomes do banco de dados e crie botões
        self.cursor.execute("SELECT nome FROM nomes")
        nomes = self.cursor.fetchall()
        for nome in nomes:
            nome_button = Button(text=nome[0])
            nome_button.bind(on_press=self.editando_carreiros)
            self.layout_button_names.add_widget(nome_button)

    def editando_carreiros(self, instance):
        nome = instance.text

        # Abrindo um popup para editar carreiros
        content = BoxLayout(orientation="vertical")
        quantidade_input = TextInput(hint_text="Quantidade de Carreiros")
        salvando_button = Button(text="Salvar")
        content.add_widget(Label(text=f"Editar Carreiros para {nome}:"))
        content.add_widget(quantidade_input)
        content.add_widget(salvando_button)

        popup = Popup(title=f"Editar Carreiros para {nome}", content=content, auto_dismiss=False,
                      size_hint=(None, None), size=(300, 200))

        def salvando_os_carreiros(instance):
            try:
                quantidade = int(quantidade_input.text)
                if nome in self.carreiros_por_pessoa:
                    self.carreiros_por_pessoa[nome] = quantidade
                else:
                    self.carreiros_por_pessoa[nome] = quantidade
                self.cursor.execute("INSERT OR REPLACE INTO carreiros (nome, quantidade) VALUES (?, ?)",
                                    (nome, quantidade))
                self.conn.commit()
                popup.dismiss()
                self.registro_carreiros.text += f'\nQuantidade de carreiros para {nome} atualizada para {quantidade}.'
            except ValueError:
                self.registro_carreiros.text += f'\nPor favor, insira um valor válido.'

        salvando_button.bind(on_press=salvando_os_carreiros)
        popup.open()

    def visualizacao_de_carreiros(self, instance):
        nome = self.name_input.text

        if nome in self.carreiros_por_pessoa:
            num_carreiros = self.carreiros_por_pessoa[nome]
            self.registro_carreiros.text += f'\n{nome} fez um total de {num_carreiros} carreiros.'
        else:
            self.registro_carreiros.text += f'\n{nome} não tem carreiros registrados.'

    def on_stop(self):
        self.conn.close()  # Fechando a conexão com o banco de dados ao fechar o aplicativo


if __name__ == '__main__':
    CarreiroApp().run()
