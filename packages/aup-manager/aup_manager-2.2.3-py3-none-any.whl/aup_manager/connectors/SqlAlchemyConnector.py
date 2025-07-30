from typing import Union, List, Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from aup_manager.connectors.ConnectorInterface import ConnectorInterface
from aup_manager.models import AdminTable, Admin, EntityTable, Entity, Base


class SqlAlchemyConnector(ConnectorInterface):
    def __init__(self, config):
        if not config.get("db_string", None):
            raise KeyError("Missing SqlAlchemyConnector.db_string in config")
        self.db_string = config.get("db_string")
        self.engine = create_engine(self.db_string)
        Base.metadata.create_all(self.engine)
        self.session_maker = sessionmaker(self.engine)

    def get_admin(self, ext_login: str, ext_name: str = None) -> Optional[Admin]:
        with self.session_maker.begin() as session:
            stmt = select(AdminTable).where(AdminTable.ext_login == ext_login)
            admin_response = session.scalars(stmt).first()

            if admin_response is None:
                return None

            return SqlAlchemyConnector.__admin_response_to_python(admin_response)

    def get_relevant_entity_id_types(
        self, entity_type_id: str, user_id: Union[str, int]
    ) -> List[str]:
        return [entity_type_id]

    def get_entities_for_admin(
        self, admin_uid: Union[str, int] = None
    ) -> dict[str, List[Entity]]:
        with self.session_maker.begin() as session:
            stmt = select(EntityTable)

            entities = session.scalars(stmt).all()
            result = {}

            for entity_sql in entities:
                entity = SqlAlchemyConnector.__entity_response_to_python(entity_sql)
                if not result.get(entity.get_entity_type()):
                    result[entity.get_entity_type()] = [entity]
                else:
                    result[entity.get_entity_type()].append(entity)
            return result

    def get_user_id(self, ext_login: str, ext_name: str = None) -> Union[int, str]:
        return ext_login

    @staticmethod
    def __admin_response_to_python(admin_m):
        return Admin(admin_m.id, admin_m.ext_login)

    @staticmethod
    def __entity_response_to_python(entity_m):
        return Entity(entity_m.id, entity_m.name, entity_m.type)
