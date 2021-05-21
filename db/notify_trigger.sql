CREATE TRIGGER command_log_notify AFTER INSERT OR UPDATE ON manager.command_log FOR EACH ROW EXECUTE PROCEDURE public.refresh_notify_count();
CREATE TRIGGER base_task_log_notify AFTER INSERT OR UPDATE ON manager.base_task_log FOR EACH ROW EXECUTE PROCEDURE public.refresh_notify_count();
CREATE TRIGGER message_notify AFTER INSERT OR UPDATE ON manager.message FOR EACH ROW EXECUTE PROCEDURE public.refresh_notify_count();
CREATE TRIGGER task_log_notify AFTER INSERT OR UPDATE ON manager.task_log FOR EACH ROW EXECUTE PROCEDURE public.refresh_notify_count();

CREATE TRIGGER notify_count_notify BEFORE UPDATE ON manager.notify_count FOR EACH ROW EXECUTE PROCEDURE public.notify_me();
