CREATE OR REPLACE FUNCTION public.notify_me()
  RETURNS trigger AS
$BODY$
BEGIN
    IF NEW.count > 0 AND NEW.last_update_datetime IS NULL THEN
        NEW.last_update_datetime := now();
    END IF;

    IF NEW.count >= NEW.max_count OR (NEW.count > 0 AND (SELECT extract(epoch FROM (now() - NEW.last_update_datetime))) > NEW.wait_time) THEN
        EXECUTE 'SELECT pg_notify(''DB_NOTIFY'', ''' || TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME || ''')';
        NEW.count := 0;
        NEW.last_update_datetime := null;
    END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 1;
ALTER FUNCTION public.notify_me()
  OWNER TO postgres;

CREATE OR REPLACE FUNCTION public.refresh_notify_count()
  RETURNS trigger AS
$BODY$
BEGIN
    EXECUTE 'UPDATE manager.notify_count SET "count" = "count" + 1 ' ||
            'WHERE table_schema = ''' || TG_TABLE_SCHEMA || ''' ' ||
            'AND "table_name" = ''' || TG_TABLE_NAME || '''';
    RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 1;
ALTER FUNCTION public.refresh_notify_count()
  OWNER TO postgres;
