CREATE EXTENSION "uuid-ossp";

CREATE OR REPLACE FUNCTION public.notify_me()
  RETURNS trigger AS
$BODY$
BEGIN
  -- Создание сообщения в канал DB_NOTIFY и сообщением с наименованием сущности-инициатора
  EXECUTE 'SELECT pg_notify(''DB_NOTIFY'', ''' || TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME || ''')';
  RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 1;
ALTER FUNCTION public.notify_me()
  OWNER TO postgres;

CREATE SCHEMA manager;

ALTER SCHEMA manager OWNER TO postgres;


CREATE TABLE manager.action (
    s_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    task_id uuid,
    method_id uuid,
    name character varying,
    number integer
);

ALTER TABLE manager.action OWNER TO postgres;

COMMENT ON TABLE manager.action IS 'Действие';

COMMENT ON COLUMN manager.action.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.action.task_id IS 'Задача';
COMMENT ON COLUMN manager.action.method_id IS 'Метод';
COMMENT ON COLUMN manager.action.name IS 'Наименование';
COMMENT ON COLUMN manager.action.number IS 'Порядковый номер';


CREATE TABLE manager.base_task
(
  s_id uuid NOT NULL DEFAULT uuid_generate_v4(),
  name character varying
);

ALTER TABLE manager.base_task OWNER TO postgres;

COMMENT ON TABLE manager.base_task IS 'Базовые задачи';

COMMENT ON COLUMN manager.base_task.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.base_task.name IS 'Наименование';


CREATE TABLE manager.command (
    s_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    action_id uuid,
    method_id uuid,
    parent_id uuid,
    name character varying,
    is_parallel boolean DEFAULT false,
    number integer
);

ALTER TABLE manager.command OWNER TO postgres;

COMMENT ON TABLE manager.command IS 'Команда';

COMMENT ON COLUMN manager.command.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.command.action_id IS 'Операция';
COMMENT ON COLUMN manager.command.method_id IS 'Метод';
COMMENT ON COLUMN manager.command.parent_id IS 'Родительская команда';
COMMENT ON COLUMN manager.command.name IS 'Наименование';
COMMENT ON COLUMN manager.command.is_parallel IS 'Признак параллельности';
COMMENT ON COLUMN manager.command.number IS 'Порядковый номер';


CREATE TABLE manager.command_log (
    s_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    task_log_id uuid,
    parent_id uuid,
    command_id uuid,
    status_id uuid
);

ALTER TABLE manager.command_log OWNER TO postgres;

COMMENT ON TABLE manager.command_log IS 'Аудит выполнения команд';

COMMENT ON COLUMN manager.command_log.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.command_log.task_log_id IS 'Аудит выполнения задач';
COMMENT ON COLUMN manager.command_log.parent_id IS 'Родительская команда';
COMMENT ON COLUMN manager.command_log.command_id IS 'Команда';
COMMENT ON COLUMN manager.command_log.status_id IS 'Статус выполнения задачи';


CREATE TABLE manager.main_task_log (
    s_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    base_task_id uuid,
    status_id uuid,
    add_task_date timestamp with time zone,
    exec_task_date timestamp with time zone,
    end_task_date timestamp with time zone
);

ALTER TABLE manager.main_task_log OWNER TO postgres;

COMMENT ON TABLE manager.main_task_log IS 'Аудит выполнения базовых задач';

COMMENT ON COLUMN manager.main_task_log.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.main_task_log.base_task_id IS 'Базовая задача';
COMMENT ON COLUMN manager.main_task_log.status_id IS 'Статус выполнения задачи';
COMMENT ON COLUMN manager.main_task_log.add_task_date IS 'Дата и время постановки задачи';
COMMENT ON COLUMN manager.main_task_log.exec_task_date IS 'Дата и время начала выполнения задачи';
COMMENT ON COLUMN manager.main_task_log.end_task_date IS 'Дата и время окончания выполнения задачи';


CREATE TABLE manager.message (
    s_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    task_log_id uuid,
    command_log_id uuid,
    parent_msg_id uuid,
    send_id uuid,
    get_id uuid,
    data jsonb,
    msg_type character varying,
    status character varying,
    date_created timestamp with time zone
);


ALTER TABLE manager.message OWNER TO postgres;

COMMENT ON TABLE manager.message IS 'Сообщения';

COMMENT ON COLUMN manager.message.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.message.task_log_id IS 'Аудит выполнения задач';
COMMENT ON COLUMN manager.message.command_log_id IS 'Аудит выполнения команд';
COMMENT ON COLUMN manager.message.parent_msg_id IS 'Родительское сообщение';
COMMENT ON COLUMN manager.message.send_id IS 'Отправитель';
COMMENT ON COLUMN manager.message.get_id IS 'Получатель';
COMMENT ON COLUMN manager.message.data IS 'Сообщение';
COMMENT ON COLUMN manager.message.msg_type IS 'Тип сообщения';
COMMENT ON COLUMN manager.message.status IS 'Статус отправки';
COMMENT ON COLUMN manager.message.date_created IS 'Дата создания';


CREATE TABLE manager.method_module (
    s_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    module_id uuid,
    name character varying,
    system_name character varying
);

ALTER TABLE manager.method_module OWNER TO postgres;

COMMENT ON TABLE manager.method_module IS 'Методы служб';

COMMENT ON COLUMN manager.method_module.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.method_module.module_id IS 'Служба';
COMMENT ON COLUMN manager.method_module.name IS 'Наименование';
COMMENT ON COLUMN manager.method_module.system_name IS 'Системное наименование';


CREATE TABLE manager.module (
    s_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying,
    system_name character varying,
    channel_name character varying,
    status boolean
);

ALTER TABLE manager.module OWNER TO postgres;

COMMENT ON TABLE manager.module IS 'Службы';

COMMENT ON COLUMN manager.module.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.module.name IS 'Наименование модуля';
COMMENT ON COLUMN manager.module.system_name IS 'Системное наименование модуля';
COMMENT ON COLUMN manager.module.channel_name IS 'Наименование канала';
COMMENT ON COLUMN manager.module.status IS 'Статус';


CREATE TABLE manager.object_to_command_log (
    s_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    command_log_id uuid,
    object_id uuid
);

ALTER TABLE manager.object_to_command_log OWNER TO postgres;

COMMENT ON TABLE manager.object_to_command_log IS 'Связь Аудита выполнения команд с записью объекта';

COMMENT ON COLUMN manager.object_to_command_log.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.object_to_command_log.command_log_id IS 'Аудит выполнения команд';
COMMENT ON COLUMN manager.object_to_command_log.object_id IS 'Объект';


CREATE TABLE manager.object_to_task_log (
    s_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    task_log_id uuid,
    object_id uuid
);

ALTER TABLE manager.object_to_task_log OWNER TO postgres;

COMMENT ON TABLE manager.object_to_task_log IS 'Связь Аудита выполнения задачи с записью объекта';

COMMENT ON COLUMN manager.object_to_task_log.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.object_to_task_log.task_log_id IS 'Аудит выполнения задач';
COMMENT ON COLUMN manager.object_to_task_log.object_id IS 'Объект';


CREATE TABLE manager.task (
    s_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying
);


ALTER TABLE manager.task OWNER TO postgres;

COMMENT ON TABLE manager.task IS 'Задачи';

COMMENT ON COLUMN manager.task.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.task.name IS 'Наименование';


CREATE TABLE manager.task_log (
    s_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    main_task_log_id uuid,
    action_id uuid,
    status_id uuid
);

ALTER TABLE manager.task_log OWNER TO postgres;

COMMENT ON TABLE manager.task_log IS 'Аудит выполнения задач';

COMMENT ON COLUMN manager.task_log.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.task_log.main_task_log_id IS 'Аудит выполнения базовых задач';
COMMENT ON COLUMN manager.task_log.action_id IS 'Операция';
COMMENT ON COLUMN manager.task_log.status_id IS 'Статус выполнения задачи';


CREATE TABLE manager.task_sequence (
    s_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    base_task_id uuid,
    task_id uuid,
    number integer
);

ALTER TABLE manager.task_sequence OWNER TO postgres;

COMMENT ON TABLE manager.task_sequence IS 'Последовательность задач';

COMMENT ON COLUMN manager.task_sequence.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.task_sequence.base_task_id IS 'Базовая задача';
COMMENT ON COLUMN manager.task_sequence.task_id IS 'Задача';
COMMENT ON COLUMN manager.task_sequence.number IS 'Порядковый номер';


CREATE TABLE manager.task_completion_status
(
  s_id uuid NOT NULL DEFAULT uuid_generate_v4(),
  name character varying,
  system_name character varying
);

ALTER TABLE manager.task_completion_status OWNER TO postgres;

COMMENT ON TABLE manager.task_completion_status IS 'Статус выполнения задачи';

COMMENT ON COLUMN manager.task_completion_status.s_id IS 'Идентификатор';
COMMENT ON COLUMN manager.task_completion_status.name IS 'Наименование';
COMMENT ON COLUMN manager.task_completion_status.system_name IS 'Системное наименование';


ALTER TABLE ONLY manager.action ADD CONSTRAINT action_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.command_log ADD CONSTRAINT command_log_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.command ADD CONSTRAINT command_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.main_task_log ADD CONSTRAINT main_task_log_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.message ADD CONSTRAINT message_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.method_module ADD CONSTRAINT method_module_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.module ADD CONSTRAINT module_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.object_to_command_log ADD CONSTRAINT object_to_command_log_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.object_to_task_log ADD CONSTRAINT object_to_task_log_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.task_log ADD CONSTRAINT task_log_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.task ADD CONSTRAINT task_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.task_sequence ADD CONSTRAINT task_sequence_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.task_completion_status ADD CONSTRAINT task_completion_status_pkey PRIMARY KEY (s_id);
ALTER TABLE ONLY manager.base_task ADD CONSTRAINT base_task_pkey PRIMARY KEY (s_id);


CREATE TRIGGER command_log_notify AFTER INSERT OR UPDATE ON manager.command_log FOR EACH ROW EXECUTE PROCEDURE public.notify_me();
CREATE TRIGGER main_task_log_notify AFTER INSERT OR UPDATE ON manager.main_task_log FOR EACH ROW EXECUTE PROCEDURE public.notify_me();
CREATE TRIGGER message_notify AFTER INSERT OR UPDATE ON manager.message FOR EACH ROW EXECUTE PROCEDURE public.notify_me();
CREATE TRIGGER task_log_notify AFTER INSERT OR UPDATE ON manager.task_log FOR EACH ROW EXECUTE PROCEDURE public.notify_me();


ALTER TABLE ONLY manager.action ADD CONSTRAINT action_method_id_fkey FOREIGN KEY (method_id) REFERENCES manager.method_module(s_id);
ALTER TABLE ONLY manager.action ADD CONSTRAINT action_task_id_fkey FOREIGN KEY (task_id) REFERENCES manager.task(s_id);

ALTER TABLE ONLY manager.command_log ADD CONSTRAINT command_log_command_id_fkey FOREIGN KEY (command_id) REFERENCES manager.command(s_id);
ALTER TABLE ONLY manager.command_log ADD CONSTRAINT command_log_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES manager.command_log(s_id);
ALTER TABLE ONLY manager.command_log ADD CONSTRAINT command_log_status_id_fkey FOREIGN KEY (status_id) REFERENCES manager.task_completion_status(s_id);
ALTER TABLE ONLY manager.command_log ADD CONSTRAINT command_log_task_log_id_fkey FOREIGN KEY (task_log_id) REFERENCES manager.task_log(s_id);

ALTER TABLE ONLY manager.command ADD CONSTRAINT command_action_id_fkey FOREIGN KEY (action_id) REFERENCES manager.action(s_id);
ALTER TABLE ONLY manager.command ADD CONSTRAINT command_method_id_fkey FOREIGN KEY (method_id) REFERENCES manager.method_module(s_id);
ALTER TABLE ONLY manager.command ADD CONSTRAINT command_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES manager.command(s_id);

ALTER TABLE ONLY manager.main_task_log ADD CONSTRAINT main_task_log_status_id_fkey FOREIGN KEY (status_id) REFERENCES manager.task_completion_status(s_id);
ALTER TABLE ONLY manager.main_task_log ADD CONSTRAINT main_task_log_base_task_id_fkey FOREIGN KEY (base_task_id) REFERENCES manager.base_task(s_id);

ALTER TABLE ONLY manager.message ADD CONSTRAINT message_command_log_id_fkey FOREIGN KEY (command_log_id) REFERENCES manager.command_log(s_id);
ALTER TABLE ONLY manager.message ADD CONSTRAINT message_get_id_id_fkey FOREIGN KEY (get_id) REFERENCES manager.module(s_id);
ALTER TABLE ONLY manager.message ADD CONSTRAINT message_parent_msg_id_fkey FOREIGN KEY (parent_msg_id) REFERENCES manager.message(s_id);
ALTER TABLE ONLY manager.message ADD CONSTRAINT message_send_id_fkey FOREIGN KEY (send_id) REFERENCES manager.module(s_id);
ALTER TABLE ONLY manager.message ADD CONSTRAINT message_task_log_id_fkey FOREIGN KEY (task_log_id) REFERENCES manager.task_log(s_id);

ALTER TABLE ONLY manager.method_module ADD CONSTRAINT method_module_module_id_id_fkey FOREIGN KEY (module_id) REFERENCES manager.module(s_id);

ALTER TABLE ONLY manager.object_to_command_log ADD CONSTRAINT object_to_command_log_command_log_id_id_fkey FOREIGN KEY (command_log_id) REFERENCES manager.command_log(s_id);

ALTER TABLE ONLY manager.object_to_task_log ADD CONSTRAINT object_to_task_log_task_log_id_id_fkey FOREIGN KEY (task_log_id) REFERENCES manager.task_log(s_id);

ALTER TABLE ONLY manager.task_log ADD CONSTRAINT task_log_action_id_fkey FOREIGN KEY (action_id) REFERENCES manager.action(s_id);
ALTER TABLE ONLY manager.task_log ADD CONSTRAINT task_log_main_task_log_id_fkey FOREIGN KEY (main_task_log_id) REFERENCES manager.main_task_log(s_id);
ALTER TABLE ONLY manager.task_log ADD CONSTRAINT task_log_status_id_fkey FOREIGN KEY (status_id) REFERENCES manager.task_completion_status(s_id);

ALTER TABLE ONLY manager.task_sequence ADD CONSTRAINT task_sequence_task_id_fkey FOREIGN KEY (task_id) REFERENCES manager.task(s_id);
ALTER TABLE ONLY manager.task_sequence ADD CONSTRAINT task_sequence_base_task_id_fkey FOREIGN KEY (base_task_id) REFERENCES manager.base_task(s_id);

INSERT INTO manager.task_completion_status (name, system_name) VALUES ('Отменено', 'cancel');
INSERT INTO manager.task_completion_status (name, system_name) VALUES ('Поставлена', 'set');
INSERT INTO manager.task_completion_status (name, system_name) VALUES ('Выполняется', 'progress');
INSERT INTO manager.task_completion_status (name, system_name) VALUES ('Выполнена', 'finish');
INSERT INTO manager.task_completion_status (name, system_name) VALUES ('Ошибка выполнения', 'error');

INSERT INTO manager.module (name, system_name, channel_name) VALUES ('Менеджер задач','task_manager', 'manager_svc');
