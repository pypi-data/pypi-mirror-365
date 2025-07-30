from typing import Union, List, Optional, Tuple

from aup_manager.db.DatabaseInterface import DatabaseInterface
from sqlalchemy import (
    create_engine,
    select,
    and_,
)
from sqlalchemy.orm import sessionmaker
from aup_manager.models import (
    AupTable,
    Aup,
    AcceptanceTable,
    Acceptance,
    RequestTable,
    Request,
    Status,
    Base,
)


class SqlAlchemyDatabase(DatabaseInterface):
    def __init__(self, config):
        if not config.get("db_string", None):
            raise KeyError("Missing SqlAlchemyConnector.db_string in config")
        self.db_string = config.get("db_string")
        self.engine = create_engine(self.db_string)
        Base.metadata.create_all(self.engine)
        self.session_maker = sessionmaker(self.engine)

    def insert_aup(self, aup: Aup) -> Union[str, int]:
        delattr(aup, "_id")

        with self.session_maker.begin() as session:
            new_aup = AupTable(
                actual_aup_id=aup.actual_aup_id,
                name=aup.name,
                markdown=aup.markdown,
                html=aup.html,
                version=aup.version,
                entitlement=aup.entitlement,
                additional_data=aup.additional_data,
                conditions=aup.conditions,
            )
            new_aup.acceptances = aup.acceptances

            session.add(new_aup)
            return new_aup.id

    def insert_acceptance(self, acceptance: Acceptance) -> Union[str, int]:
        delattr(acceptance, "_id")

        with self.session_maker.begin() as session:
            new_acceptance = AcceptanceTable(
                aup_id=acceptance.aup_id,
                user_id=acceptance.user_id,
                date_time=acceptance.date_time,
            )
            session.add(new_acceptance)
            return new_acceptance.id

    def insert_acceptances(
        self, acceptances: List[Acceptance]
    ) -> List[Tuple[str, int]]:
        insert_list = []
        for acceptance in acceptances:
            delattr(acceptance, "_id")
            insert_list.append(acceptance)
        inserted_ids = []

        for insert_item in insert_list:
            result = self.insert_acceptance(insert_item)
            inserted_ids.append(result)

        return inserted_ids

    def get_all_aups_with_acceptances(self) -> List[Aup]:
        with self.session_maker.begin() as session:
            aup_stmt = select(AupTable)
            aup_result = session.scalars(aup_stmt).all()
            aup_dicts = SqlAlchemyDatabase.__prepare_dict_list(aup_result)

            aup_ids = [aup.get("id") for aup in aup_dicts]

            acceptance_query = select(AcceptanceTable).filter(
                AcceptanceTable.aup_id.in_(aup_ids)
            )
            acceptance_result = session.scalars(acceptance_query).all()
            acceptance_dicts = SqlAlchemyDatabase.__prepare_dict_list(acceptance_result)

            return SqlAlchemyDatabase.__aup_sql_list_to_python(
                aup_dicts, acceptance_dicts
            )

    def get_aup_with_acceptances_by_id(self, _id: Union[str, int]) -> Optional[Aup]:
        object_id = str(_id)

        with self.session_maker.begin() as session:
            aup_stmt = select(AupTable).where(AupTable.id == object_id)
            aup_result = session.scalars(aup_stmt).all()
            aup_dicts = SqlAlchemyDatabase.__prepare_dict_list(aup_result)

            aup_ids = [aup.get("id") for aup in aup_dicts]
            acceptance_query = select(AcceptanceTable).filter(
                AcceptanceTable.aup_id.in_(aup_ids)
            )
            acceptance_result = session.scalars(acceptance_query).all()
            acceptance_dicts = SqlAlchemyDatabase.__prepare_dict_list(acceptance_result)

            aups = SqlAlchemyDatabase.__aup_sql_list_to_python(
                aup_dicts, acceptance_dicts
            )
            if not aups:
                return None
            return aups[0]

    def get_all_aups(self) -> List[Aup]:
        with self.session_maker.begin() as session:
            aup_stmt = select(AupTable)
            aup_result = session.scalars(aup_stmt).all()
            aup_dicts = SqlAlchemyDatabase.__prepare_dict_list(aup_result)

            return SqlAlchemyDatabase.__aup_sql_list_to_python(aup_dicts, [])

    def get_aups_by_entitlement(self, entitlement: str) -> List[Aup]:
        with self.session_maker.begin() as session:
            aup_stmt = select(AupTable).filter(AupTable.entitlement == entitlement)
            aup_result = session.scalars(aup_stmt).all()
            aup_dicts = SqlAlchemyDatabase.__prepare_dict_list(aup_result)

            return SqlAlchemyDatabase.__aup_sql_list_to_python(aup_dicts, [])

    def get_aup_by_id(self, _id: Union[str, int]) -> Optional[Aup]:
        object_id = str(_id)

        with self.session_maker.begin() as session:
            aup_stmt = select(AupTable).where(AupTable.id == object_id)
            aup_result = session.scalars(aup_stmt).all()
            aup_dicts = SqlAlchemyDatabase.__prepare_dict_list(aup_result)

            aups = SqlAlchemyDatabase.__aup_sql_list_to_python(aup_dicts, [])
            if not aups:
                return None
            return aups[0]

    def get_all_user_accepted_aups(self, user_id: Union[int, str]) -> List[Aup]:
        with self.session_maker.begin() as session:
            aup_stmt = select(AupTable)
            aup_result = session.scalars(aup_stmt).all()
            aup_dicts = SqlAlchemyDatabase.__prepare_dict_list(aup_result)
            aup_ids = [aup.get("id") for aup in aup_dicts]
            # limit acceptances based on user_id and aup_id
            acceptance_stmt = select(AcceptanceTable).filter(
                and_(
                    (AcceptanceTable.aup_id.in_(aup_ids)),
                    (AcceptanceTable.user_id == user_id),
                )
            )
            acceptance_result = session.scalars(acceptance_stmt).all()
            acceptance_dicts = SqlAlchemyDatabase.__prepare_dict_list(acceptance_result)

            return SqlAlchemyDatabase.__aup_sql_list_to_python(
                aup_dicts, acceptance_dicts
            )

    def get_aups_by_condition(self, condition: List[str]) -> List[Aup]:
        with self.session_maker.begin() as session:
            aup_stmt = select(AupTable).where(AupTable.conditions.contains(condition))
            aup_result = session.scalars(aup_stmt).all()
            aup_dicts = SqlAlchemyDatabase.__prepare_dict_list(aup_result)

            return SqlAlchemyDatabase.__aup_sql_list_to_python(aup_dicts, [])

    def get_aups_by_condition_with_acceptances(self, condition: List[str]) -> List[Aup]:
        with self.session_maker.begin() as session:
            aup_stmt = select(AupTable).filter(AupTable.conditions.in_(condition))
            aup_result = session.scalars(aup_stmt).all()
            aup_dicts = SqlAlchemyDatabase.__prepare_dict_list(aup_result)

            aup_ids = [aup.get("id") for aup in aup_dicts]
            acceptance_query = select(AcceptanceTable).filter(
                AcceptanceTable.aup_id in aup_ids
            )
            acceptance_result = session.scalars(acceptance_query).all()
            acceptance_dicts = SqlAlchemyDatabase.__prepare_dict_list(acceptance_result)

            return SqlAlchemyDatabase.__aup_sql_list_to_python(
                aup_dicts, acceptance_dicts
            )

    def get_user_accepted_aups_by_condition(
        self, user_id: Union[int, str], condition: List[str]
    ) -> List[Aup]:
        with self.session_maker.begin() as session:
            aup_stmt = select(AupTable).filter(AupTable.conditions.contains(condition))
            aup_result = session.scalars(aup_stmt).all()
            aup_dicts = SqlAlchemyDatabase.__prepare_dict_list(aup_result)

            aup_ids = [aup.get("id") for aup in aup_dicts]

            # limit acceptances based on user_id and aup_id
            acceptance_stmt = select(AcceptanceTable).filter(
                and_(
                    (AcceptanceTable.aup_id.in_(aup_ids)),
                    (AcceptanceTable.user_id == user_id),
                )
            )
            acceptance_result = session.scalars(acceptance_stmt).all()
            acceptance_dicts = SqlAlchemyDatabase.__prepare_dict_list(acceptance_result)

            return SqlAlchemyDatabase.__aup_sql_list_to_python(
                aup_dicts, acceptance_dicts
            )

    def get_user_not_accepted_aups_by_condition(
        self, user_id: Union[int, str], condition: List[str]
    ) -> List[Aup]:
        with self.session_maker.begin as session:
            aup_stmt = select(AupTable).filter(
                and_(
                    AupTable.conditions.contains(condition),
                    AupTable.actual.is_(None),
                )
            )
            aup_result = session.scalars(aup_stmt).all()
            aup_dicts = SqlAlchemyDatabase.__prepare_dict_list(aup_result)

            aup_ids = [aup.get("id") for aup in aup_dicts]
            # limit acceptances based on user_id and aup_id
            acceptance_stmt = select(AcceptanceTable).filter(
                and_(
                    (AcceptanceTable.aup_id.in_(aup_ids)),
                    (AcceptanceTable.user_id == user_id),
                )
            )
            acceptance_result = session.scalars(acceptance_stmt).all()
            acceptance_dicts = SqlAlchemyDatabase.__prepare_dict_list(acceptance_result)

            return SqlAlchemyDatabase.__aup_sql_list_to_python(
                aup_dicts, acceptance_dicts
            )

    def delete_aup_by_id(self, aup_id: Union[int, str]):
        object_id = str(aup_id)

        with self.session_maker.begin() as session:
            aup_to_del = session.query(AupTable).filter_by(AupTable.id == object_id)
            acceptance_to_del = session.query(AcceptanceTable).filter_by(
                AcceptanceTable.aup_id == object_id
            )

            if aup_to_del and acceptance_to_del:
                session.delete(aup_to_del)
                session.delete(acceptance_to_del)

                # updates session.query(User).filter(User.id == user_id_to_update).first()
                aup_sel_query = (
                    select(AupTable)
                    .filter(AupTable.actual_aup_id == object_id)
                    .order_by(AupTable.version.desc())
                )

                aup_sel_result = session.scalars(aup_sel_query).first()

                if aup_sel_result:
                    highest_aup_id = aup_sel_result.__dict__.get("id")

                    aup_update_one = (
                        session.query(AupTable)
                        .filter(AupTable.id == highest_aup_id)
                        .first()
                    )
                    if aup_update_one:
                        aup_update_one.actual_aup_id = None

                    aup_update_many = session.query(AupTable).filter(
                        AupTable.actual_aup_id == object_id
                    )
                    if aup_update_many:
                        for aup in aup_update_many:
                            aup.actual_aup_id = highest_aup_id

                    return highest_aup_id

            return None

    def delete_all_aups(self):
        with self.session_maker.begin() as session:
            aups_to_delete = session.query(AupTable).all()
            for aup in aups_to_delete:
                session.delete(aups_to_delete)

    def set_aup_name(self, aup_id: Union[str, int], new_name: str):
        object_id = str(aup_id)

        with self.session_maker.begin() as session:
            aup_update_one = (
                session.query(AupTable).filter(AupTable.id == object_id).first()
            )
            aup_update_one.name = new_name

            aup_update_many = (
                session.query(AupTable)
                .filter(AupTable.actual_aup_id == object_id)
                .all()
            )
            for aup in aup_update_many:
                aup.name = new_name

    def update_aup_text(
        self, aup_id: Union[str, int], markdown: str, html: str
    ) -> Optional[Union[str, int]]:
        object_id = str(aup_id)
        aup = self.get_aup_by_id(aup_id)
        if not aup:
            return None
        new_aup = Aup(
            aup.name,
            markdown,
            html,
            aup.conditions,
            aup.entitlement,
            version=aup.version + 1,
        )
        inserted_id = self.insert_aup(new_aup)
        if not inserted_id:
            return None

        with self.session_maker.begin() as session:
            aup_update_one = (
                session.query(AupTable).filter(AupTable.id == object_id).first()
            )
            aup_update_one.actual_aup_id = inserted_id

            aup_update_many = (
                session.query(AupTable)
                .filter(AupTable.actual_aup_id == object_id)
                .all()
            )
            for aup in aup_update_many:
                aup.actual_aup_id = inserted_id

            return inserted_id

    def set_aup_conditions(self, aup_id: Union[str, int], conditions: List[List[str]]):
        object_id = str(aup_id)

        with self.session_maker.begin() as session:
            aup_update_one = (
                session.query(AupTable).filter(AupTable.id == object_id).first()
            )
            aup_update_one.conditions = conditions

            aup_update_many = (
                session.query(AupTable)
                .filter(AupTable.actual_aup_id == object_id)
                .all()
            )
            for aup in aup_update_many:
                aup.conditions = conditions

    def save_request(self, request: Request) -> str:
        delattr(request, "_id")

        new_request = RequestTable(
            nonce=request.nonce, user_id=request.user_id, status=request.status.value
        )

        with self.session_maker.begin() as session:
            session.add(new_request)

            return new_request.id

    def get_request_by_id(self, request_id: Union[str, int]) -> Optional[Request]:
        object_id = str(request_id)

        with self.session_maker.begin() as session:
            stmt = select(RequestTable).filter(RequestTable.id == object_id)
            result = session.scalars(stmt).all()
            requests = SqlAlchemyDatabase.__prepare_dict_list(result)

            if requests == []:
                return None
            return self.__create_request(
                requests[0] if isinstance(requests, list) else requests
            )

    def get_request_by_nonce(self, nonce: str) -> Optional[Request]:
        with self.session_maker.begin() as session:
            stmt = select(RequestTable).filter(RequestTable.nonce == nonce)
            result = session.scalars(stmt).all()
            requests = SqlAlchemyDatabase.__prepare_dict_list(result)

            if requests == []:
                return None
            return self.__create_request(
                requests[0] if isinstance(requests, list) else requests
            )

    def __create_request(self, request_dict: dict):
        if not request_dict:
            return None
        return Request(
            request_dict["nonce"],
            request_dict["user_id"],
            request_dict["id"],
            Status(request_dict["status"]),
        )

    def make_request_success(self, request_id: Union[str, int]):
        object_id = str(request_id)

        with self.session_maker.begin() as session:
            request_to_update = (
                session.query(RequestTable).filter(RequestTable.id == object_id).all()
            )

            for request in request_to_update:
                request.status = Status.SUCCESS.value

    def make_request_invalid(self, request_id: Union[str, int]):
        object_id = str(request_id)

        with self.session_maker.begin() as session:
            request_to_update = (
                session.query(RequestTable).filter(RequestTable.id == object_id).all()
            )

            for request in request_to_update:
                request.status = Status.INVALID.value

    # Maps 'id' to '_id' so classes can be created
    @staticmethod
    def __id_to__id_dict(src: dict) -> dict:
        src_id = src.get("id")
        if src_id:
            src.pop("id")
        src["_id"] = src_id
        return src

    @staticmethod
    def __aup_sql_list_to_python(aup_list, acceptance_list):
        return [
            SqlAlchemyDatabase.__aup_sql_to_python(
                aup_item,
                [x for x in acceptance_list if x.get("aup_id") == aup_item.get("id")],
            )
            for aup_item in aup_list
        ]

    @staticmethod
    def __aup_sql_to_python(aup_item, acceptance_list_filtered):
        aup = Aup(**SqlAlchemyDatabase.__id_to__id_dict(aup_item))
        aup.acceptances = [
            Acceptance(**SqlAlchemyDatabase.__id_to__id_dict(ac))
            for ac in acceptance_list_filtered
        ]
        return aup

    @staticmethod
    def __prepare_dict(mapping_dict):
        mapping_dict.pop("_sa_instance_state")
        return mapping_dict

    @staticmethod
    def __prepare_dict_list(mapping_list):
        for row in mapping_list:
            row = SqlAlchemyDatabase.__prepare_dict(row)
        return mapping_list
