// =====================================================================
//  MINICURSO NEO4J - TORNEIO DE ROBÓTICA (versão em grafo)
//
//  Os mesmos dados do MySQL, agora como um GRAFO:
//    - cada linha de tabela vira um NÓ (com um rótulo, ex.: :Equipe)
//    - cada chave estrangeira vira um RELACIONAMENTO (uma seta entre nós)
//
//  Modelo:
//    (:Robo)-[:PERTENCE_A]->(:Equipe)
//    (:Integrante)-[:MEMBRO_DE]->(:Equipe)
//    (:Robo)-[:PARTICIPOU_DE {classificacao, pontuacao}]->(:Prova)
//
//  Observação: no SQL a "prova" era só uma coluna (nome_prova) da tabela
//  resultado. No grafo ela vira um nó próprio, e a tabela resultado vira
//  o relacionamento PARTICIPOU_DE, com classificacao e pontuacao como
//  propriedades da seta.
//
//  Como usar: abra o Neo4j Browser (ou Neo4j Aura / Sandbox) e execute
//  um bloco por vez (cada bloco termina com ";").
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


// ---------------------------------------------------------------------
// 7) CREATE de um único nó + relacionamento (exemplo simples para o vídeo)
//    SQL equivalente:
//      INSERT INTO robo VALUES (13, 'Hermes', 'Resgate', '2025-06-01', 8);
// ---------------------------------------------------------------------
MATCH (e:Equipe {id_equipe: 8})
CREATE (r:Robo {id_robo: 13, nome_robo: 'Hermes', categoria: 'Resgate',
                data_criacao: date('2025-06-01')})-[:PERTENCE_A]->(e)
RETURN r, e;


// =====================================================================
//  R - READ (consultar dados) com MATCH
// =====================================================================

// ---------------------------------------------------------------------
// 8) Ver o grafo inteiro (no Neo4j Browser aparece desenhado)
//    SQL: não há equivalente direto; seria um SELECT de cada tabela.
// ---------------------------------------------------------------------
MATCH (n) RETURN n;


// ---------------------------------------------------------------------
// 9) Listar equipes de Recife
//    SQL: SELECT nome_equipe, escola FROM equipe WHERE cidade = 'Recife';
// ---------------------------------------------------------------------
MATCH (e:Equipe {cidade: 'Recife'})
RETURN e.nome_equipe AS equipe, e.escola AS escola;


// ---------------------------------------------------------------------
// 10) Robôs com o nome da sua equipe
//     SQL: SELECT r.nome_robo, r.categoria, e.nome_equipe
//          FROM robo r JOIN equipe e ON e.id_equipe = r.id_equipe;
//     No grafo não existe JOIN: seguimos a seta PERTENCE_A.
// ---------------------------------------------------------------------
MATCH (r:Robo)-[:PERTENCE_A]->(e:Equipe)
RETURN r.nome_robo AS robo, r.categoria AS categoria, e.nome_equipe AS equipe
ORDER BY equipe, robo;


// ---------------------------------------------------------------------
// 11) RANKING DE EQUIPES (soma das pontuações), incluindo equipes sem pontos
//     SQL: SELECT e.nome_equipe, COUNT(DISTINCT r.id_robo), COALESCE(SUM(res.pontuacao), 0)
//          FROM equipe e
//          LEFT JOIN robo r ON r.id_equipe = e.id_equipe
//          LEFT JOIN resultado res ON res.id_robo = r.id_robo
//          GROUP BY e.id_equipe, e.nome_equipe ORDER BY 3 DESC;
//     OPTIONAL MATCH funciona como o LEFT JOIN: se não achar, devolve null.
//     A agregação (count, sum) agrupa sozinha pelas outras colunas do RETURN,
//     então não existe GROUP BY no Cypher.
// ---------------------------------------------------------------------
MATCH (e:Equipe)
OPTIONAL MATCH (e)<-[:PERTENCE_A]-(r:Robo)
OPTIONAL MATCH (r)-[p:PARTICIPOU_DE]->(:Prova)
RETURN e.nome_equipe            AS equipe,
       count(DISTINCT r)        AS qtd_robos,
       coalesce(sum(p.pontuacao), 0) AS pontuacao_total
ORDER BY pontuacao_total DESC, equipe;


// ---------------------------------------------------------------------
// 12) ROBÔS SEM PARTICIPAÇÃO EM PROVAS
//     SQL (LEFT JOIN exclusivo):
//          SELECT r.nome_robo FROM robo r
//          LEFT JOIN resultado res ON res.id_robo = r.id_robo
//          WHERE res.id_robo IS NULL;
//     No grafo basta perguntar: "não existe a seta PARTICIPOU_DE".
// ---------------------------------------------------------------------
MATCH (r:Robo)-[:PERTENCE_A]->(e:Equipe)
WHERE NOT EXISTS { (r)-[:PARTICIPOU_DE]->(:Prova) }
RETURN r.nome_robo AS robo, e.nome_equipe AS equipe;


// ---------------------------------------------------------------------
// 13) Pódio de uma prova
//     SQL: SELECT res.classificacao, r.nome_robo, res.pontuacao
//          FROM resultado res JOIN robo r ON r.id_robo = res.id_robo
//          WHERE res.nome_prova = 'Arena_A' ORDER BY res.classificacao;
// ---------------------------------------------------------------------
MATCH (r:Robo)-[p:PARTICIPOU_DE]->(:Prova {nome: 'Arena_A'})
RETURN p.classificacao AS posicao, r.nome_robo AS robo, p.pontuacao AS pontos
ORDER BY posicao;


// ---------------------------------------------------------------------
// 14) Caminho de 2 saltos: integrantes e os robôs da sua equipe
//     SQL: precisaria de dois JOINs (integrante -> equipe -> robo).
//     No grafo é só desenhar o caminho.
// ---------------------------------------------------------------------
MATCH (i:Integrante)-[:MEMBRO_DE]->(e:Equipe)<-[:PERTENCE_A]-(r:Robo)
RETURN e.nome_equipe AS equipe, collect(DISTINCT i.nome) AS integrantes,
       collect(DISTINCT r.nome_robo) AS robos
ORDER BY equipe;


// ---------------------------------------------------------------------
// 15) Média de pontuação por categoria com filtro (equivale ao HAVING)
//     SQL: SELECT r.categoria, AVG(res.pontuacao) FROM robo r
//          JOIN resultado res ON res.id_robo = r.id_robo
//          GROUP BY r.categoria HAVING AVG(res.pontuacao) >= 87;
//     WITH passa o resultado agregado adiante e o WHERE depois dele
//     faz o papel do HAVING.
// ---------------------------------------------------------------------
MATCH (r:Robo)-[p:PARTICIPOU_DE]->(:Prova)
WITH r.categoria AS categoria, avg(p.pontuacao) AS media
WHERE media >= 87
RETURN categoria, round(media, 2) AS media
ORDER BY media DESC;


// =====================================================================
//  U - UPDATE (alterar dados) com SET
// =====================================================================

// ---------------------------------------------------------------------
// 16) Alterar a cidade de uma equipe
//     SQL: UPDATE equipe SET cidade = 'Recife' WHERE id_equipe = 3;
// ---------------------------------------------------------------------
MATCH (e:Equipe {id_equipe: 3})
SET e.cidade = 'Recife'
RETURN e;


// ---------------------------------------------------------------------
// 17) Alterar uma propriedade de RELACIONAMENTO (a pontuação de um resultado)
//     SQL: UPDATE resultado SET pontuacao = 86.50
//          WHERE nome_prova = 'Arena_B' AND classificacao = 2;
//     Diferença: no Neo4j não há trigger nativo; a regra "0 a 100"
//     teria de ser garantida pela aplicação (ou por plugins como APOC).
// ---------------------------------------------------------------------
MATCH (:Robo)-[p:PARTICIPOU_DE {classificacao: 2}]->(:Prova {nome: 'Arena_B'})
SET p.pontuacao = 86.50
RETURN p;


// ---------------------------------------------------------------------
// 18) Adicionar uma propriedade nova sem alterar "esquema"
//     SQL: exigiria ALTER TABLE robo ADD COLUMN peso_kg DECIMAL(5,2); antes do UPDATE.
//     No grafo cada nó pode ter propriedades diferentes.
// ---------------------------------------------------------------------
MATCH (r:Robo {id_robo: 1})
SET r.peso_kg = 12.5
RETURN r;


// ---------------------------------------------------------------------
// 19) Trocar um robô de equipe (mudar a "chave estrangeira")
//     SQL: UPDATE robo SET id_equipe = 8 WHERE id_robo = 12;
//     No grafo: apagamos a seta antiga e criamos uma nova.
// ---------------------------------------------------------------------
MATCH (r:Robo {id_robo: 12})-[antiga:PERTENCE_A]->(:Equipe)
MATCH (nova:Equipe {id_equipe: 8})
DELETE antiga
CREATE (r)-[:PERTENCE_A]->(nova)
RETURN r, nova;


// =====================================================================
//  D - DELETE (excluir dados) com DELETE / DETACH DELETE
// =====================================================================

// ---------------------------------------------------------------------
// 20) Apagar apenas um relacionamento (um resultado)
//     SQL: DELETE FROM resultado WHERE nome_prova = 'Arena_C' AND classificacao = 3;
// ---------------------------------------------------------------------
MATCH (:Robo)-[p:PARTICIPOU_DE {classificacao: 3}]->(:Prova {nome: 'Arena_C'})
DELETE p;


// ---------------------------------------------------------------------
// 21) DELETE simples falha se o nó ainda tiver relacionamentos
//     (parecido com uma FK sem CASCADE, que bloqueia a exclusão do "pai").
//     Este comando dá ERRO de propósito, pois o robô 13 tem a seta PERTENCE_A:
// ---------------------------------------------------------------------
MATCH (r:Robo {id_robo: 13})
DELETE r;


// ---------------------------------------------------------------------
// 22) DETACH DELETE: apaga o nó e todas as suas setas
//     SQL: DELETE FROM robo WHERE id_robo = 13;
//     (no MySQL, o ON DELETE CASCADE apagaria também os resultados dele)
// ---------------------------------------------------------------------
MATCH (r:Robo {id_robo: 13})
DETACH DELETE r;


// ---------------------------------------------------------------------
// 23) "Cascata" manual: excluir uma equipe com seus robôs e integrantes
//     SQL: DELETE FROM equipe WHERE id_equipe = 5;
//          (o ON DELETE CASCADE remove robôs, resultados e integrantes sozinho)
//     No Neo4j não há cascata automática: precisamos dizer o que apagar.
//     As setas PARTICIPOU_DE somem junto com os robôs pelo DETACH.
// ---------------------------------------------------------------------
MATCH (e:Equipe {id_equipe: 5})
OPTIONAL MATCH (e)<-[:PERTENCE_A]-(r:Robo)
OPTIONAL MATCH (e)<-[:MEMBRO_DE]-(i:Integrante)
DETACH DELETE e, r, i;


// ---------------------------------------------------------------------
// 24) Conferir o que sobrou
// ---------------------------------------------------------------------
MATCH (n)
RETURN labels(n)[0] AS tipo, count(*) AS quantidade
ORDER BY tipo;
