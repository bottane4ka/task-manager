# -*- coding: utf-8 -*-
from uuid import uuid4
from sqlalchemy.orm import exc

from orm.manage import app
from orm.models import MethodModuleModel, ModuleModel, TaskLogModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine


if __name__ == '__main__':
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    session = Session(bind=engine)
    s = "task_manager"
    try:
        a = session.query(TaskLogModel).filter(TaskLogModel.action == s).all()
    except exc.NoResultFound as ex:
        print(f"Не существует службы с системным именем {s}")
    except exc.MultipleResultsFound as ex:
        print(f"Существует несколько служб с системным именем {s}")

    print(111)


