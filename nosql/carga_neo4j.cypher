// =====================================================================
//  CARGA / RESET DO MINICURSO NEO4J - TORNEIO DE ROBÓTICA
//
//  Apaga tudo e recarrega os dados originais. Use antes de cada
//  gravação (ou regravação) do vídeo 2.
//
//  Estes são os blocos 0 a 6 de comandos_neo4j.cypher. Se mudar os
//  dados lá, mude aqui também.
//
//  Como usar: no Neo4j Browser, ative "Enable multi statement query
//  editor" nas configurações, cole o arquivo inteiro e execute.
// =====================================================================


// ---------------------------------------------------------------------
// 0) LIMPAR O BANCO (para poder executar o roteiro do zero)
//    SQL equivalente: DROP SCHEMA ... / DELETE FROM em todas as tabelas
// ---------------------------------------------------------------------
MATCH (n) DETACH DELETE n;


// ---------------------------------------------------------------------
// 1) RESTRIÇÕES DE UNICIDADE
//    SQL equivalente: PRIMARY KEY / UNIQUE
//    No Neo4j não existe esquema obrigatório; as constraints garantem
//    que não haverá dois nós com o mesmo id.
// ---------------------------------------------------------------------
CREATE CONSTRAINT equipe_id IF NOT EXISTS FOR (e:Equipe) REQUIRE e.id_equipe IS UNIQUE;
CREATE CONSTRAINT robo_id IF NOT EXISTS FOR (r:Robo) REQUIRE r.id_robo IS UNIQUE;
CREATE CONSTRAINT integrante_id IF NOT EXISTS FOR (i:Integrante) REQUIRE i.id_integrante IS UNIQUE;
CREATE CONSTRAINT integrante_email IF NOT EXISTS FOR (i:Integrante) REQUIRE i.email IS UNIQUE;
CREATE CONSTRAINT prova_nome IF NOT EXISTS FOR (p:Prova) REQUIRE p.nome IS UNIQUE;


// =====================================================================
//  C - CREATE (criar dados)
// =====================================================================

// ---------------------------------------------------------------------
// 2) CRIAR NÓS :Equipe
//    SQL equivalente: INSERT INTO equipe (id_equipe, nome_equipe, escola, cidade) VALUES (...);
// ---------------------------------------------------------------------
CREATE (:Equipe {id_equipe: 1, nome_equipe: 'Equipe Alfa',   escola: 'IFTech',                 cidade: 'Recife'}),
       (:Equipe {id_equipe: 2, nome_equipe: 'RoboMasters',   escola: 'Escola Futuro',          cidade: 'Olinda'}),
       (:Equipe {id_equipe: 3, nome_equipe: 'CyberBots',     escola: 'Colégio Inovação',       cidade: 'Jaboatão'}),
       (:Equipe {id_equipe: 4, nome_equipe: 'TechRobots',    escola: 'EduPB',                  cidade: 'João Pessoa'}),
       (:Equipe {id_equipe: 5, nome_equipe: 'Equipe Beta',   escola: 'Instituto PE',           cidade: 'Recife'}),
       (:Equipe {id_equipe: 6, nome_equipe: 'MecaNordeste',  escola: 'Escola Técnica Caruaru', cidade: 'Caruaru'}),
       (:Equipe {id_equipe: 7, nome_equipe: 'Circuito Vivo', escola: 'IFPE Paulista',          cidade: 'Paulista'}),
       (:Equipe {id_equipe: 8, nome_equipe: 'Equipe Gama',   escola: 'Colégio Atlântico',      cidade: 'Natal'});


// ---------------------------------------------------------------------
// 3) CRIAR NÓS :Robo E O RELACIONAMENTO [:PERTENCE_A]
//    SQL equivalente: INSERT INTO robo (..., id_equipe) VALUES (..., 1);
//    No SQL a ligação é a coluna id_equipe (chave estrangeira).
//    No grafo, primeiro achamos a equipe (MATCH) e depois criamos a seta.
//    UNWIND transforma a lista em linhas, como vários INSERTs de uma vez.
// ---------------------------------------------------------------------
UNWIND [
  {id: 1,  nome: 'Maximus', cat: 'Combate',           data: '2023-08-02', eq: 1},
  {id: 2,  nome: 'Atlas',   cat: 'Combate',           data: '2020-02-16', eq: 2},
  {id: 3,  nome: 'Flash',   cat: 'Resgate',           data: '2025-09-05', eq: 1},
  {id: 4,  nome: 'Nexus',   cat: 'Resgate',           data: '2021-04-20', eq: 4},
  {id: 5,  nome: 'Titan',   cat: 'Seguidor de Linha', data: '2019-07-10', eq: 5},
  {id: 6,  nome: 'Bolt',    cat: 'Seguidor de Linha', data: '2018-06-25', eq: 3},
  {id: 7,  nome: 'Vulcan',  cat: 'Combate',           data: '2022-11-15', eq: 6},
  {id: 8,  nome: 'Spark',   cat: 'Resgate',           data: '2024-03-12', eq: 7},
  {id: 9,  nome: 'Orion',   cat: 'Seguidor de Linha', data: '2023-05-30', eq: 6},
  {id: 10, nome: 'Pixel',   cat: 'Sumô',              data: '2024-10-01', eq: 2},
  {id: 11, nome: 'Kronos',  cat: 'Sumô',              data: '2022-01-18', eq: 3},
  {id: 12, nome: 'Zeus',    cat: 'Combate',           data: '2025-02-14', eq: 7}
] AS linha
MATCH (e:Equipe {id_equipe: linha.eq})
CREATE (r:Robo {id_robo: linha.id, nome_robo: linha.nome, categoria: linha.cat,
                data_criacao: date(linha.data)})
CREATE (r)-[:PERTENCE_A]->(e);


// ---------------------------------------------------------------------
// 4) CRIAR NÓS :Integrante E O RELACIONAMENTO [:MEMBRO_DE]
//    SQL equivalente: INSERT INTO integrante (...) VALUES (...);
// ---------------------------------------------------------------------
UNWIND [
  {id: 1,  nome: 'Ana Beatriz Souza',    funcao: 'Capitã',       email: 'ana.souza@email.com',        nasc: '2007-03-14', eq: 1},
  {id: 2,  nome: 'Lucas Ferreira',       funcao: 'Programador',  email: 'lucas.ferreira@email.com',   nasc: '2006-11-02', eq: 1},
  {id: 3,  nome: 'Mariana Lima',         funcao: 'Mecânica',     email: 'mariana.lima@email.com',     nasc: '2008-05-21', eq: 2},
  {id: 4,  nome: 'Pedro Henrique Alves', funcao: 'Capitão',      email: 'pedro.alves@email.com',      nasc: '2006-08-30', eq: 2},
  {id: 5,  nome: 'Júlia Cavalcanti',     funcao: 'Eletrônica',   email: 'julia.cavalcanti@email.com', nasc: '2007-12-09', eq: 3},
  {id: 6,  nome: 'Rafael Monteiro',      funcao: 'Programador',  email: 'rafael.monteiro@email.com',  nasc: '2005-09-17', eq: 3},
  {id: 7,  nome: 'Camila Rodrigues',     funcao: 'Capitã',       email: 'camila.rodrigues@email.com', nasc: '2006-02-25', eq: 4},
  {id: 8,  nome: 'Gabriel Nascimento',   funcao: 'Mecânico',     email: 'gabriel.nasc@email.com',     nasc: '2008-07-04', eq: 4},
  {id: 9,  nome: 'Beatriz Araújo',       funcao: 'Programadora', email: 'beatriz.araujo@email.com',   nasc: '2007-06-12', eq: 5},
  {id: 10, nome: 'Thiago Barbosa',       funcao: 'Eletrônica',   email: 'thiago.barbosa@email.com',   nasc: '2006-04-01', eq: 5},
  {id: 11, nome: 'Larissa Gomes',        funcao: 'Capitã',       email: 'larissa.gomes@email.com',    nasc: '2005-10-23', eq: 6},
  {id: 12, nome: 'Felipe Andrade',       funcao: 'Designer',     email: 'felipe.andrade@email.com',   nasc: '2008-01-15', eq: 6},
  {id: 13, nome: 'Isabela Correia',      funcao: 'Programadora', email: 'isabela.correia@email.com',  nasc: '2007-09-08', eq: 7},
  {id: 14, nome: 'Mateus Pereira',       funcao: 'Mecânico',     email: 'mateus.pereira@email.com',   nasc: '2006-12-19', eq: 7},
  {id: 15, nome: 'Sofia Ribeiro',        funcao: 'Capitã',       email: 'sofia.ribeiro@email.com',    nasc: '2007-04-27', eq: 8}
] AS linha
MATCH (e:Equipe {id_equipe: linha.eq})
CREATE (i:Integrante {id_integrante: linha.id, nome: linha.nome, funcao: linha.funcao,
                      email: linha.email, data_nascimento: date(linha.nasc)})
CREATE (i)-[:MEMBRO_DE]->(e);


// ---------------------------------------------------------------------
// 5) CRIAR NÓS :Prova
//    No SQL não havia tabela de provas (só a coluna nome_prova).
// ---------------------------------------------------------------------
UNWIND ['Arena_A', 'Arena_B', 'Arena_C', 'Arena_D'] AS nome
CREATE (:Prova {nome: nome});


// ---------------------------------------------------------------------
// 6) CRIAR O RELACIONAMENTO [:PARTICIPOU_DE] (equivale à tabela resultado)
//    SQL equivalente: INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo) VALUES (...);
//    As colunas classificacao e pontuacao viram PROPRIEDADES da seta.
// ---------------------------------------------------------------------
UNWIND [
  {prova: 'Arena_A', cls: 1, pts: 98.00, robo: 2},
  {prova: 'Arena_A', cls: 2, pts: 92.00, robo: 1},
  {prova: 'Arena_A', cls: 3, pts: 88.50, robo: 7},
  {prova: 'Arena_B', cls: 1, pts: 90.00, robo: 3},
  {prova: 'Arena_B', cls: 2, pts: 85.00, robo: 4},
  {prova: 'Arena_C', cls: 1, pts: 93.00, robo: 5},
  {prova: 'Arena_C', cls: 2, pts: 87.25, robo: 6},
  {prova: 'Arena_C', cls: 3, pts: 80.00, robo: 9},
  {prova: 'Arena_D', cls: 1, pts: 95.50, robo: 10},
  {prova: 'Arena_D', cls: 2, pts: 89.00, robo: 11}
] AS linha
MATCH (r:Robo {id_robo: linha.robo}), (p:Prova {nome: linha.prova})
CREATE (r)-[:PARTICIPOU_DE {classificacao: linha.cls, pontuacao: linha.pts}]->(p);

