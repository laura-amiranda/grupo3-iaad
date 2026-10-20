-- =====================================================================
--  PROJETO IAAD / UFRPE - BANCO DE DADOS "TORNEIO DE ROBÓTICA"
--  Script único: cria o schema, as tabelas, carrega os dados iniciais
--  e cria o trigger (regra de negócio) e a stored procedure (bônus).
--
--  Como executar no MySQL Workbench:
--    File > Open SQL Script... > escolha este arquivo >
--    clique no raio (Execute) SEM selecionar nenhuma linha.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1) SCHEMA
--    DROP + CREATE garante que o script pode ser executado várias vezes:
--    sempre começa de um banco limpo.
-- ---------------------------------------------------------------------
DROP SCHEMA IF EXISTS torneio_robotica;
CREATE SCHEMA torneio_robotica
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE torneio_robotica;

-- ---------------------------------------------------------------------
-- 2) TABELAS
--    A ordem importa: primeiro as tabelas "pai" (equipe), depois as
--    tabelas "filhas" que apontam para elas por chave estrangeira.
-- ---------------------------------------------------------------------

-- EQUIPE: cada equipe participante do torneio
CREATE TABLE equipe (
    id_equipe   INT          NOT NULL,
    nome_equipe VARCHAR(100) NOT NULL,
    escola      VARCHAR(100),
    cidade      VARCHAR(80),
    CONSTRAINT pk_equipe PRIMARY KEY (id_equipe)
);

-- ROBO: cada robô pertence a uma equipe.
-- ON DELETE CASCADE: se a equipe for excluída, seus robôs também são.
-- ON UPDATE CASCADE: se o id da equipe mudar, o id_equipe do robô acompanha.
CREATE TABLE robo (
    id_robo      INT          NOT NULL,
    nome_robo    VARCHAR(100) NOT NULL,
    categoria    VARCHAR(50),
    data_criacao DATE,
    id_equipe    INT,
    CONSTRAINT pk_robo PRIMARY KEY (id_robo),
    CONSTRAINT fk_robo_equipe FOREIGN KEY (id_equipe)
        REFERENCES equipe (id_equipe)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- RESULTADO: desempenho de um robô em uma prova.
-- A chave primária é COMPOSTA por (nome_prova, classificacao):
-- numa mesma prova não pode haver duas posições iguais.
-- id_robo NÃO faz parte da PK, é apenas chave estrangeira.
CREATE TABLE resultado (
    nome_prova    VARCHAR(100) NOT NULL,
    classificacao INT          NOT NULL,
    pontuacao     DECIMAL(6,2),
    id_robo       INT,
    CONSTRAINT pk_resultado PRIMARY KEY (nome_prova, classificacao),
    CONSTRAINT fk_resultado_robo FOREIGN KEY (id_robo)
        REFERENCES robo (id_robo)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- INTEGRANTE (tabela nova escolhida pelo grupo): pessoas de cada equipe.
-- O e-mail é UNIQUE: duas pessoas não podem ter o mesmo e-mail.
CREATE TABLE integrante (
    id_integrante   INT          NOT NULL,
    nome            VARCHAR(100) NOT NULL,
    funcao          VARCHAR(50),
    email           VARCHAR(100),
    data_nascimento DATE,
    id_equipe       INT,
    CONSTRAINT pk_integrante PRIMARY KEY (id_integrante),
    CONSTRAINT uq_integrante_email UNIQUE (email),
    CONSTRAINT fk_integrante_equipe FOREIGN KEY (id_equipe)
        REFERENCES equipe (id_equipe)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- 3) DADOS INICIAIS
-- ---------------------------------------------------------------------

-- 8 equipes. A equipe 8 (Equipe Gama) propositalmente NÃO tem robôs,
-- para a consulta de ranking mostrar uma equipe sem pontos.
INSERT INTO equipe (id_equipe, nome_equipe, escola, cidade) VALUES
    (1, 'Equipe Alfa',   'IFTech',                 'Recife'),
    (2, 'RoboMasters',   'Escola Futuro',          'Olinda'),
    (3, 'CyberBots',     'Colégio Inovação',       'Jaboatão'),
    (4, 'TechRobots',    'EduPB',                  'João Pessoa'),
    (5, 'Equipe Beta',   'Instituto PE',           'Recife'),
    (6, 'MecaNordeste',  'Escola Técnica Caruaru', 'Caruaru'),
    (7, 'Circuito Vivo', 'IFPE Paulista',          'Paulista'),
    (8, 'Equipe Gama',   'Colégio Atlântico',      'Natal');

-- 12 robôs. Os robôs 8 (Spark) e 12 (Zeus) ficam SEM resultado,
-- para a consulta "robôs sem resultado" (LEFT JOIN exclusivo).
INSERT INTO robo (id_robo, nome_robo, categoria, data_criacao, id_equipe) VALUES
    (1,  'Maximus', 'Combate',           '2023-08-02', 1),
    (2,  'Atlas',   'Combate',           '2020-02-16', 2),
    (3,  'Flash',   'Resgate',           '2025-09-05', 1),
    (4,  'Nexus',   'Resgate',           '2021-04-20', 4),
    (5,  'Titan',   'Seguidor de Linha', '2019-07-10', 5),
    (6,  'Bolt',    'Seguidor de Linha', '2018-06-25', 3),
    (7,  'Vulcan',  'Combate',           '2022-11-15', 6),
    (8,  'Spark',   'Resgate',           '2024-03-12', 7),
    (9,  'Orion',   'Seguidor de Linha', '2023-05-30', 6),
    (10, 'Pixel',   'Sumô',              '2024-10-01', 2),
    (11, 'Kronos',  'Sumô',              '2022-01-18', 3),
    (12, 'Zeus',    'Combate',           '2025-02-14', 7);

-- 10 resultados (todas as pontuações entre 0 e 100).
INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo) VALUES
    ('Arena_A', 1, 98.00, 2),
    ('Arena_A', 2, 92.00, 1),
    ('Arena_A', 3, 88.50, 7),
    ('Arena_B', 1, 90.00, 3),
    ('Arena_B', 2, 85.00, 4),
    ('Arena_C', 1, 93.00, 5),
    ('Arena_C', 2, 87.25, 6),
    ('Arena_C', 3, 80.00, 9),
    ('Arena_D', 1, 95.50, 10),
    ('Arena_D', 2, 89.00, 11);

-- 15 integrantes, distribuídos entre as 8 equipes.
INSERT INTO integrante (id_integrante, nome, funcao, email, data_nascimento, id_equipe) VALUES
    (1,  'Ana Beatriz Souza',    'Capitã',       'ana.souza@email.com',      '2007-03-14', 1),
    (2,  'Lucas Ferreira',       'Programador',  'lucas.ferreira@email.com', '2006-11-02', 1),
    (3,  'Mariana Lima',         'Mecânica',     'mariana.lima@email.com',   '2008-05-21', 2),
    (4,  'Pedro Henrique Alves', 'Capitão',      'pedro.alves@email.com',    '2006-08-30', 2),
    (5,  'Júlia Cavalcanti',     'Eletrônica',   'julia.cavalcanti@email.com','2007-12-09', 3),
    (6,  'Rafael Monteiro',      'Programador',  'rafael.monteiro@email.com','2005-09-17', 3),
    (7,  'Camila Rodrigues',     'Capitã',       'camila.rodrigues@email.com','2006-02-25', 4),
    (8,  'Gabriel Nascimento',   'Mecânico',     'gabriel.nasc@email.com',   '2008-07-04', 4),
    (9,  'Beatriz Araújo',       'Programadora', 'beatriz.araujo@email.com', '2007-06-12', 5),
    (10, 'Thiago Barbosa',       'Eletrônica',   'thiago.barbosa@email.com', '2006-04-01', 5),
    (11, 'Larissa Gomes',        'Capitã',       'larissa.gomes@email.com',  '2005-10-23', 6),
    (12, 'Felipe Andrade',       'Designer',     'felipe.andrade@email.com', '2008-01-15', 6),
    (13, 'Isabela Correia',      'Programadora', 'isabela.correia@email.com','2007-09-08', 7),
    (14, 'Mateus Pereira',       'Mecânico',     'mateus.pereira@email.com', '2006-12-19', 7),
    (15, 'Sofia Ribeiro',        'Capitã',       'sofia.ribeiro@email.com',  '2007-04-27', 8);

-- ---------------------------------------------------------------------
-- 4) TRIGGER (regra de negócio)
--    A pontuação de um resultado precisa estar entre 0 e 100.
--    O tipo DECIMAL(6,2) aceitaria até 9999.99, então quem garante a
--    regra é o trigger. O MySQL exige um trigger para cada evento,
--    por isso há um para INSERT e outro para UPDATE.
--
--    DELIMITER: dentro do corpo (BEGIN...END) usamos ";" várias vezes.
--    Trocamos o delimitador para "$$" para o MySQL entender que o
--    comando CREATE TRIGGER só termina no "$$".
-- ---------------------------------------------------------------------
DELIMITER $$

CREATE TRIGGER trg_resultado_valida_pontuacao_ins
BEFORE INSERT ON resultado
FOR EACH ROW
BEGIN
    IF NEW.pontuacao < 0 OR NEW.pontuacao > 100 THEN
        -- SQLSTATE '45000' = erro definido pelo usuário; cancela o INSERT
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Pontuação inválida: deve estar entre 0 e 100';
    END IF;
END$$

CREATE TRIGGER trg_resultado_valida_pontuacao_upd
BEFORE UPDATE ON resultado
FOR EACH ROW
BEGIN
    IF NEW.pontuacao < 0 OR NEW.pontuacao > 100 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Pontuação inválida: deve estar entre 0 e 100';
    END IF;
END$$

-- ---------------------------------------------------------------------
-- 5) STORED PROCEDURE (bônus)
--    sp_desempenho_equipe(id): retorna o nome da equipe, a quantidade
--    de robôs e a soma das pontuações (0 se a equipe não tiver pontos).
--    LEFT JOIN garante que a equipe aparece mesmo sem robôs/resultados.
--    COUNT(DISTINCT ...) evita contar o mesmo robô duas vezes quando
--    ele tem mais de um resultado.
-- ---------------------------------------------------------------------
CREATE PROCEDURE sp_desempenho_equipe(IN p_id_equipe INT)
BEGIN
    SELECT e.nome_equipe                    AS nome_equipe,
           COUNT(DISTINCT r.id_robo)        AS quantidade_robos,
           COALESCE(SUM(res.pontuacao), 0)  AS soma_pontuacoes
    FROM equipe e
    LEFT JOIN robo r        ON r.id_equipe = e.id_equipe
    LEFT JOIN resultado res ON res.id_robo = r.id_robo
    WHERE e.id_equipe = p_id_equipe
    GROUP BY e.id_equipe, e.nome_equipe;
END$$

DELIMITER ;

-- ---------------------------------------------------------------------
-- 6) TESTES RÁPIDOS (opcional: descomente para executar no Workbench)
-- ---------------------------------------------------------------------
-- CALL sp_desempenho_equipe(1);
-- INSERT INTO resultado VALUES ('Arena_Z', 1, 150.00, 1);  -- erro do trigger
-- INSERT INTO robo VALUES (99, 'Fantasma', 'Combate', '2024-01-01', 999); -- erro de FK
