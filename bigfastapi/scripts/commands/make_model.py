import argparse
import os

from dotenv import load_dotenv

from bigfastapi.scripts.command import Command

load_dotenv(".env")

MODELS_FOLDER = os.environ.get("MODELS_FOLDER")


def to_camel_case(snake_str: str) -> str:
    snake_str = snake_str.lower()
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0].title() + "".join(x.title() for x in components[1:])


class MakeModel(Command):
    def run(self, args: list = None):
        parser = argparse.ArgumentParser("Create a model file")

        parser.add_argument("model_name", help="Name of model file", type=str)
        parser.add_argument("table_name", help="Table name", type=str)
        args = parser.parse_args(args)

        model_name = args.model_name.strip()
        args.table_name.strip()
        class_name = to_camel_case(model_name)

        contents = (
            """
        import datetime
        from uuid import uuid4
        import bigfastapi.db.database as db
        from sqlalchemy.schema import Column
        from sqlalchemy.types import String, DateTime, Integer
        import sqlalchemy.orm as orm


        class """
            + class_name
            + """(db.Base):
            __tablename__ = "{table_name}"
            id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)

            date_created = Column(DateTime, default=datetime.datetime.utcnow)
            last_updated = Column(DateTime, default=datetime.datetime.utcnow)
        """
        )

        file_name = model_name + ".py"
        file = open(MODELS_FOLDER + file_name, "a")
        file.write(contents)
        print("Model file " + MODELS_FOLDER + file_name + " created")
