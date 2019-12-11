# -*- coding: utf-8 -*-
import sqlite3

class Banco():

    def ajeitarTabelas(self):
        with sqlite3.connect('db1.db') as connection:
            cursor = connection.cursor() 
            #cursor.execute("UPDATE eventos SET tipo = ? WHERE id = 9",("Pode chorar",))
    def criarTabelas(self):

        connection = sqlite3.connect('db1.db')


        # if connection.is_connected():
        #     db_Info = connection.get_server_info()
        #     print("Connected to MySQL Server version ", db_Info)
        #     cursor = connection.cursor()
        #     cursor.execute("select database();")
        #     record = cursor.fetchone()
        #     print("You're connected to database: ", record)
        cursor = connection.cursor()

        cursor.execute (

        """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY,
                usuario TEXT NOT NULL,
                email TEXT NOT NULL,
                senha TEXT NOT NULL,
                classe TEXT, 
                sugestoes INTEGER, 
                sug_aceitas INTEGER, 
                sug_Naceitas INTEGER
                );
        """
        )

        cursor.execute (
        """
            CREATE TABLE IF NOT EXISTS grade (
                id INTEGER PRIMARY KEY,
                userId INTEGER,
                eventoId INTEGER,
                FOREIGN KEY (userId) REFERENCES user(id),
                FOREIGN KEY (eventoId) REFERENCES evento(id)
            );
        """
        )
        
        cursor.execute (
        """
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL, 
                descricao TEXT NOT NULL,
                local TEXT,
                data TEXT,
                data_fim TEXT,
                horario_de_inicio TEXT,
                horario_de_fim TEXT,
                tipo TEXT,  
                aceito INTEGER NOT NULL, 
                autor INTEGER

            );
        """
        )

        cursor.execute (
        """
            CREATE TABLE IF NOT EXISTS local (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL, 
                bloco TEXT NOT NULL,
                sala TEXT,
                descricao TEXT NOT NULL, 
                aceito INTEGER NOT NULL, 
                autor INTEGER

            );
        """
        )

        cursor.execute (

        """
            CREATE TABLE IF NOT EXISTS informacao (
                id INTEGER PRIMARY KEY,
                texto TEXT NOT NULL, 
                aceito INTEGER NOT NULL, 
                autor INTEGER
                );
        """
        )

        cursor.execute (
        """
            CREATE TABLE IF NOT EXISTS assuntosXeventos (
                id INTEGER PRIMARY KEY,
                eventoId INTEGER,
                assuntoId INTEGER,
                FOREIGN KEY (eventoId) REFERENCES eventos(id),
                FOREIGN KEY (assuntoId) REFERENCES assuntos(id)
            );
        """
        )
        cursor.execute (
        """
            CREATE TABLE IF NOT EXISTS assuntos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL
            );
        """
        )
        cursor.execute(
        """       
            CREATE TABLE IF NOT EXISTS grade(
                id INTEGER PRIMARY KEY,
                userId INTEGER,
                segunda TEXT,
                terca TEXT,
                quarta TEXT, 
                quinta TEXT,
                sexta TEXT,
                sabado TEXT
            );
        """
        )

        connection.commit()
        cursor.close()
        connection.close()

    def adicionarInfo(self, texto, user):
        deuCerto = False
        with sqlite3.connect('db1.db') as connection:
            
            cursor = connection.cursor()    
            cursor.execute("""
                            INSERT INTO informacao (texto, autor, aceito)
                            VALUES (?, ?, 0)
                            """, (texto, user))

            cursor.execute("UPDATE user SET sugestoes = sugestoes + 1 WHERE id = ?", (user,))

            connection.commit()
            deuCerto = True
        return deuCerto

    def adicionarLocal(self, nome, bloco, sala, descricao, user):
        deuCerto = False
        with sqlite3.connect('db1.db') as connection:
            
            cursor = connection.cursor()    
            cursor.execute("""
                            INSERT INTO local(nome, bloco, sala, descricao, autor, aceito)
                            VALUES (?, ?, ?, ?, ?, 0)
                            """, (nome, bloco, sala, descricao, user))

            cursor.execute("UPDATE user SET sugestoes = sugestoes + 1 WHERE id = ?", (user,))
            
            connection.commit()
            deuCerto = True
        return deuCerto

    def adicionarEvento(self, nome, descricao, local, data, horarioIn, horarioFim, tipo, assunto, user_id = False):
        """
        Assunto deve ser uma lista com nome(s) do(s) assunto(s) do evento. Retorna False se o evento já existir ou se houver erro.
        """
        deuCerto = False
        if type(user_id) == int:
            if user_id>0:
                with sqlite3.connect('db1.db') as connection:
            
                    cursor = connection.cursor()    
                    repetido = cursor.execute("SELECT id FROM eventos WHERE nome = ? AND data = ? AND local = ?", (nome, data, local)).fetchall()
                    
                    if repetido != []:
                        return deuCerto 
                    
                    else:
                        cursor = connection.cursor()    
                        cursor.execute("""
                                    INSERT INTO eventos(nome, descricao, local, data, horario_de_inicio, horario_de_fim, tipo, autor, aceito)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                                    """, (nome, descricao, local, data, horarioIn, horarioFim, tipo, user_id))
                        connection.commit()
                
                        id_ev = cursor.execute("SELECT id FROM eventos WHERE nome = ? AND data = ? AND local = ?", (nome, data, local)).fetchall()
                        id_ev = id_ev[0][0]
                        #print ("id_ev: " + str(id_ev))
                        
                        for a in assunto:
                
                            id_ass = cursor.execute("SELECT id FROM assuntos WHERE nome = ?", (a,)).fetchall()
                            id_ass = id_ass[0][0]
                            #print("id_ass: " + str(id_ass))
                            cursor.execute("INSERT INTO assuntosXeventos (eventoId, assuntoId) VALUES (?, ?)", (id_ev, id_ass))

                        cursor.execute("UPDATE user SET sugestoes = sugestoes + 1 WHERE id = ?", (user_id,))

                        connection.commit()
                        deuCerto = True
        return deuCerto

    def listarInfos(self):

        with sqlite3.connect('db1.db') as connection:

            cursor = connection.cursor()

            lista = ("SELECT * FROM informacao WHERE aceito = 1")
            result = cursor.execute(lista).fetchall()

        return result

    def listarLocais(self):

        with sqlite3.connect('db1.db') as connection:

            cursor = connection.cursor()

            lista = ("SELECT * FROM local WHERE aceito = 1")
            result = cursor.execute(lista).fetchall()
            
        return result
      
    def listarEventos(self, data, dataFim, horarioIn="00", horarioFim="24", tipo=False, assunto=False):    
        """
        Assunto deve ser uma lista com nome(s) do(s) assunto(s) do evento. 
        data e dataFim são os limitadores de periodo da busca.
        Ex: de hj (variavel sistema) até daqui a 1 semana (hj+7)
        """
        result = []

        with sqlite3.connect('db1.db') as connection:

            cursor = connection.cursor()

            lista = ("""SELECT id FROM eventos WHERE aceito = 1
            AND data >= ? 
            AND data <= ? 
            AND horario_de_inicio >= ? 
            AND horario_de_fim <= ?
            """)
            if not tipo == False:
                lista = lista + "AND tipo = " + str(tipo)
            #ids dos eventos q cumprem requisitos de horario e tipo 
            filtro1 = cursor.execute(lista, (data, dataFim, horarioIn, horarioFim)).fetchall()
            
            for i in range(len(filtro1)):
                filtro1[i] = filtro1[i][0]

            if not assunto == False:
                filtro2 = []

                for a in assunto:
                    ids = cursor.execute("SELECT id FROM assuntos WHERE nome = ?", (a,)).fetchall()
                    ids = ids[0][0]

                    #ids dos eventos q cumprem os requisitos de assunto 
                    filtro2 = cursor.execute("SELECT eventoId FROM assuntosXeventos WHERE assuntoId = ?", (ids,)).fetchall()
                    
                    for i in range(len(filtro2)):
                        filtro2[i] = filtro2[i][0]
                    
                    for ev in filtro1:
                        if ev in filtro2:
                            result.append(ev)
            else:
                for i in filtro1:
                    result.append(cursor.execute("SELECT * FROM eventos WHERE id = ?", (i,)).fetchall()[0])
            
        #remove duplicatas
        rep =[]
        for i  in range(len(result)):
    
            for e in range(i+1, len(result)):
    
                if result[i][0] == result[e][0]:
                    rep.append(result[i])
            
        for ev in rep:
            result.remove(ev)
    
        return result

    def cadastrar_pessoa(self,user, senha, email, classe = "usuario"):
        try:
            with sqlite3.connect('db1.db') as connection:
                cursor = connection.cursor()
                cursor.execute('INSERT INTO user(usuario, email, senha, classe, sugestoes, sug_aceitas, sug_Naceitas ) VALUES(?, ?, ?, ?, 0, 0, 0)', (user, email, senha, classe))
                connection.commit()
                return True
        except:
            return False
   
    def buscar_pessoa(self, usr, senha):
        with sqlite3.connect('db1.db') as connection:
            cursor = connection.cursor()
            find_user = ("SELECT * FROM user WHERE usuario = ? AND senha = ?")
            results = cursor.execute(find_user, (usr, senha)).fetchall()
        return results

    def colocarNaGrade(self, usr, matriz):
        """
        user deve ser o id do usuario. matriz = [dia semana][horario]
        """
        try:
            with sqlite3.connect('db1.db') as connection:
                cursor = connection.cursor()
                
                procura_grade = connection.execute("SELECT id FROM grade WHERE userId = ?", (user,)).fetchall()
                
                if procura_grade == []:

                    cursor.execute("""INSERT INTO grade (userId, segunda, terca, quarta, quinta, sexta, sabado) 
                                VALUES (?, '', '', '', '', '', '')""", (user,))
                
                cursor.execute("""UPDATE grade SET segunda = ?, terca = ?, quarta = ?, quinta = ?, sexta = ?, sabado = ? 
                                WHERE userId = ?""", (matriz[0], matriz[1], matriz[2], matriz[3], matriz[4], matriz[5]))
                
                connection.commit()
            
            return True
        except:
            print("Deu ruim no coloacarNaGrade")
            return False    

    def listarGrade(self, user):
        """
        Input: id do user.
        Output: matriz grade
        """
        with sqlite3.connect('db1.db') as connection:
            cursor = connection.cursor()

            tbl = cursor.execute("SELECT segunda, terca, quarta, quinta, sexta, sabado FROM grade WHERE userId = ?", (user,)).fetchall()
            
            for i in range(len(tbl)):
                tbl[i] = tbl[i].split(",")
            connection.commit()

        result = tbl
        return result 

    def listarNAceitos(self):
        """
        Retorna uma lista de 3 tuplas. 1 = lista de eventos, 2 = lista de locais, 3 = lista de informaçoes
        (tablas de locais e informacoes ainda n tem conluna aceito)
        """
        with sqlite3.connect('db1.db') as connection:
            cursor = connection.cursor() 
            
            res_eventos = cursor.execute("SELECT * FROM eventos WHERE aceito = 0").fetchall() 
            res_local = cursor.execute("SELECT * FROM local WHERE aceito = 0").fetchall()
            res_informacao = cursor.execute("SELECT * FROM informacao WHERE aceito = 0").fetchall()
            
            results = []
            results.append(res_eventos)
            results.append(res_local)
            results.append(res_informacao)

            connection.commit()
        
        return results

    def aceitarCoisas(self, lista_eve, lista_loc, lista_info):
        """
        Atualiza as tabelas de eventos, locais e info. 
        Cada uma das lista do input deve ser um dicionário com o ID e o resultado da sugestao(s ou n)
        """
        with sqlite3.connect('db1.db') as connection:
            cursor = connection.cursor()

            aceitos = []
            recusados = []
            
            form1 = "UPDATE # SET aceito = 1 WHERE id = ?"
            form2 = "DELETE FROM # WHERE id = ?"
            form3 = "SELECT autor FROM # WHERE id = ?" 

            for evento in lista_eve:
                tabela  = "eventos"

                if lista_eve[evento] == 's':
                    
                    cursor.execute(form1.replace("#", tabela), (evento,))
                    #add id do autor da sugestao
                    aceitos.append(cursor.execute(form3.replace("#", tabela), (evento,)).fetchall()) 

                if lista_eve[evento] == 'n':
                    recusados.append(cursor.execute(form3.replace("#", tabela), (evento,)).fetchall())
                    cursor.execute(form2.replace("#", tabela), (evento,))
                    
            
            for local in lista_loc:

                if lista_loc[local] == 's':

                    cursor.execute(form1.replace("#", tabela), (local,))
                    aceitos.append(cursor.execute(form3.replace("#", tabela), (local,)).fetchall())
                    
                if lista_loc[local] == 'n':
                    recusados.append(cursor.execute(form3.replace("#", tabela), (local,)).fetchall())
                    cursor.execute(form2.replace("#", tabela), (local,))
                    

            for info in lista_info:

                if lista_info[info] == 's':

                    cursor.execute(form1, (tabela, info))
                    aceitos.append(cursor.execute(form3, (tabela, info,)).fetchall())
                
                if lista_info[info] == 'n':
                    recusados.append(cursor.execute(form3, (tabela, info,)).fetchall())
                    cursor.execute(form2, (tabela, info))
                    
        print(aceitos)  
        print(recusados)            
                
        for user_id in aceitos:
            cursor.executemany("UPDATE user SET sug_aceitas = sug_aceitas + 1 WHERE id = ?", user_id)

        for user_id in recusados:
            cursor.executemany("UPDATE user SET sug_Naceitas = sug_Naceitas + 1 WHERE id = ?", user_id)

        connection.commit()


    def gerenciarColab(self, user):
        """
        Input: lista de ids dos users que vao ser promovidos
        """
        with sqlite3.connect('db1.db') as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE user
                SET classe = "coordenador"
                WHERE id = ?
                """, (user))
            connection.commit()



