CREATE EXTENSION "uuid-ossp";

ALTER TABLE manager.action ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.command_log ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.command ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.base_task_log ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.message ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.method_module ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.module ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.object_to_command_log ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.object_to_task_log ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.task_log ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.task ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.task_sequence ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.task_status ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.base_task ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();
ALTER TABLE manager.notify_count ALTER COLUMN s_id SET DEFAULT public.uuid_generate_v4();

INSERT INTO manager.task_status (name, system_name) VALUES
('Отменено', 'cancel'),
('Поставлена', 'set'),
('Выполняется', 'progress'),
('Выполнена', 'finish'),
('Ошибка выполнения', 'error'),

INSERT INTO manager.module (name, system_name, channel_name, status) VALUES
('Менеджер задач','task_manager', 'manager_svc', FALSE );

INSERT INTO manager.notify_count (table_schema, "table_name", "count", last_update_datetime, max_count, wait_time) VALUES
('manager', 'command_log', 0, null, 10, 60),
('manager', 'base_task_log', 0, null, 10, 60),
('manager', 'message', 0, null, 100, 60),
('manager', 'task_log', 0, null, 10, 60);