BEGIN TRANSACTION;
DROP TABLE IF EXISTS "core_anamnese";
CREATE TABLE "core_anamnese" (
	"id"	integer NOT NULL,
	"queixas"	text NOT NULL,
	"alergias"	text NOT NULL,
	"medicamentos_uso_continuo"	text NOT NULL,
	"consulta_id"	bigint NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("consulta_id") REFERENCES "core_consulta"("id") DEFERRABLE INITIALLY DEFERRED
);
DROP TABLE IF EXISTS "core_atestado";
CREATE TABLE "core_atestado" (
	"id"	integer NOT NULL,
	"periodo_dias"	integer NOT NULL,
	"cid"	varchar(10) NOT NULL,
	"assinatura_digital"	varchar(100) NOT NULL,
	"consulta_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("consulta_id") REFERENCES "core_consulta"("id") DEFERRABLE INITIALLY DEFERRED
);
DROP TABLE IF EXISTS "core_consulta";
CREATE TABLE "core_consulta" (
	"id"	integer NOT NULL,
	"data_hora"	datetime NOT NULL,
	"status"	varchar(10) NOT NULL,
	"medico_id"	bigint NOT NULL,
	"paciente_id"	bigint NOT NULL,
	"stripe_checkout_id"	varchar(100),
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("medico_id") REFERENCES "core_customuser"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("paciente_id") REFERENCES "core_customuser"("id") DEFERRABLE INITIALLY DEFERRED
);
DROP TABLE IF EXISTS "core_customuser";
CREATE TABLE "core_customuser" (
	"id"	integer NOT NULL,
	"password"	varchar(128) NOT NULL,
	"last_login"	datetime,
	"is_superuser"	bool NOT NULL,
	"username"	varchar(150) NOT NULL UNIQUE,
	"first_name"	varchar(150) NOT NULL,
	"last_name"	varchar(150) NOT NULL,
	"is_staff"	bool NOT NULL,
	"is_active"	bool NOT NULL,
	"date_joined"	datetime NOT NULL,
	"tipo_usuario"	varchar(15) NOT NULL,
	"cpf"	varchar(14) NOT NULL UNIQUE,
	"data_nascimento"	date,
	"telefone"	varchar(15),
	"email"	varchar(254) NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "core_exame";
CREATE TABLE "core_exame" (
	"id"	integer NOT NULL,
	"tipo"	varchar(100) NOT NULL,
	"data_solicitacao"	date NOT NULL,
	"data_laudo"	date,
	"profissional_resp"	varchar(100) NOT NULL,
	"arquivo_resultado"	varchar(100),
	"paciente_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("paciente_id") REFERENCES "core_customuser"("id") DEFERRABLE INITIALLY DEFERRED
);
DROP TABLE IF EXISTS "core_receita";
CREATE TABLE "core_receita" (
	"id"	integer NOT NULL,
	"medicamentos"	text NOT NULL,
	"posologia"	text NOT NULL,
	"assinatura_digital"	varchar(100) NOT NULL,
	"qrcode"	varchar(255) NOT NULL,
	"consulta_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("consulta_id") REFERENCES "core_consulta"("id") DEFERRABLE INITIALLY DEFERRED
);
INSERT INTO "core_anamnese" ("id","queixas","alergias","medicamentos_uso_continuo","consulta_id") VALUES (1,'Dor nas costas','nao tem','dipirona 1mg',4),
 (2,'dor de cabeca','nao tem','nenhum',6);
INSERT INTO "core_atestado" ("id","periodo_dias","cid","assinatura_digital","consulta_id") VALUES (1,1,'','Dr(a). Gregory House (Assinado Digitalmente)',4),
 (2,2,'','Dr(a). Gregory House (Assinado Digitalmente)',6),
 (3,1,'','Dr(a). Gregory House (Assinado Digitalmente)',7);
INSERT INTO "core_consulta" ("id","data_hora","status","medico_id","paciente_id","stripe_checkout_id") VALUES (4,'2025-11-07 11:00:00','CONCLUIDA',3,1,NULL),
 (5,'2025-11-08 15:00:00','CANCELADA',3,1,NULL),
 (6,'2025-11-07 12:00:00','CONCLUIDA',3,4,'cs_test_a1rXa6NC9IIiPFtgnBXZ2RNnsITL34JUbAa3blNzVBqfrt3OAk9mn9k8gF'),
 (7,'2025-11-13 18:00:00','CONCLUIDA',3,1,'cs_test_a1E0kP4NsMUt3FMZJyX98YXUwVhjOCcS9GuNHVzRVnRQyW498Cj4HLo69T'),
 (8,'2025-11-13 20:00:00','MARCADA',3,1,NULL);
INSERT INTO "core_customuser" ("id","password","last_login","is_superuser","username","first_name","last_name","is_staff","is_active","date_joined","tipo_usuario","cpf","data_nascimento","telefone","email") VALUES (1,'pbkdf2_sha256$1000000$G5imZULkYPPIJgRpBJPZGD$XupFOtbdqUl3pF36KC3C7hu/Eqsgw2aodNkYLhZN++Y=','2025-11-21 19:49:51.863770',0,'Sun','Lucas','Rodrigues',0,1,'2025-11-05 13:47:25.153312','PACIENTE','12329637713','2004-07-20','22992834325','gamesspider754@gmail.com'),
 (2,'pbkdf2_sha256$1000000$EVuhhws6VDurnGBtdd8e7Y$mhahtgtx4fPbl9uFBgIDTRRSc+Sj6QNlFg8bnIE/5dY=','2025-11-21 18:58:06.927296',1,'admin','','',1,1,'2025-11-05 13:59:34','RECEPCIONISTA','945.361.200-68',NULL,NULL,''),
 (3,'pbkdf2_sha256$1000000$EpsrDhkLyWbk2qaMXCuxWF$GRT1gNVfpYhke+L65YOg5pEdNJ5A/cbk1F2TxJMAhcA=','2025-11-21 19:44:55.435305',0,'Dr_House','Gregory','House',0,1,'2025-11-05 14:18:34','MEDICO','994.516.250-03','1959-06-11','21999998888','drhouse@clinica.com'),
 (4,'pbkdf2_sha256$1000000$AgRxeuPtli2HX7XpLwHWXE$WGt+rKH50e51dJGPcKCpQEoZlVbWl26ujunpaIeSWU8=','2025-11-07 00:45:44.349648',0,'teste@teste.com','Rogerio','Pinto',0,1,'2025-11-06 22:30:40.343565','PACIENTE','11111111111111','2004-07-20','111111111111111','teste@teste.com');
INSERT INTO "core_exame" ("id","tipo","data_solicitacao","data_laudo","profissional_resp","arquivo_resultado","paciente_id") VALUES (1,'Raio X do Tórax','2025-11-06','2025-11-06','Dr.Imagem','exames/raiox.pdf',1);
INSERT INTO "core_receita" ("id","medicamentos","posologia","assinatura_digital","qrcode","consulta_id") VALUES (1,'Amoxilina 500mg','durante 7 dias, 1x ao dia','Dr(a). Gregory House (Assinado Digitalmente)','validar-receita/1',4),
 (2,'dipirona','7 dias','Dr(a). Gregory House (Assinado Digitalmente)','validar-receita/None',6),
 (3,'jnspk;lfsslkjdfsja','aosipfskajf','Dr(a). Gregory House (Assinado Digitalmente)','validar-receita/None',7);
DROP INDEX IF EXISTS "core_atestado_consulta_id_062a1f5f";
CREATE INDEX "core_atestado_consulta_id_062a1f5f" ON "core_atestado" (
	"consulta_id"
);
DROP INDEX IF EXISTS "core_consulta_medico_id_9ccdc56f";
CREATE INDEX "core_consulta_medico_id_9ccdc56f" ON "core_consulta" (
	"medico_id"
);
DROP INDEX IF EXISTS "core_consulta_paciente_id_296515b0";
CREATE INDEX "core_consulta_paciente_id_296515b0" ON "core_consulta" (
	"paciente_id"
);
DROP INDEX IF EXISTS "core_exame_paciente_id_83c419bd";
CREATE INDEX "core_exame_paciente_id_83c419bd" ON "core_exame" (
	"paciente_id"
);
DROP INDEX IF EXISTS "core_receita_consulta_id_722ec922";
CREATE INDEX "core_receita_consulta_id_722ec922" ON "core_receita" (
	"consulta_id"
);
COMMIT;
