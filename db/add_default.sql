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