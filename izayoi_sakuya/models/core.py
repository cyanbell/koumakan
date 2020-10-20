from copy import copy
from datetime import datetime
from typing import Optional, Type, Any, Tuple

from tortoise.queryset import QuerySet, UpdateQuery, DeleteQuery, Q, \
    QuerySetSingle, AwaitableQuery
from tortoise.models import Model, MODEL
from tortoise.fields import UUIDField, DatetimeField
from tortoise.backends.base.client import BaseDBAsyncClient
from tortoise.exceptions import OperationalError, IntegrityError, \
    TransactionManagementError
from tortoise.transactions import in_transaction


class SoftDeleteQuerySet(QuerySet, AwaitableQuery[MODEL]):
    __slots__ = (
        "fields",
        "_prefetch_map",
        "_prefetch_queries",
        "_single",
        "_raise_does_not_exist",
        "_db",
        "_limit",
        "_offset",
        "_fields_for_select",
        "_filter_kwargs",
        "_orderings",
        "_q_objects",
        "_distinct",
        "_having",
        "_custom_filters",
        "_group_bys",
        "_select_for_update",
        "_select_related",
        "_select_related_idx",
    )

    def _clone(self) -> "SoftDeleteQuerySet[MODEL]":
        queryset = SoftDeleteQuerySet.__new__(SoftDeleteQuerySet)
        queryset.fields = self.fields
        queryset.model = self.model
        queryset.query = self.query
        queryset.capabilities = self.capabilities
        queryset._prefetch_map = copy(self._prefetch_map)
        queryset._prefetch_queries = copy(self._prefetch_queries)
        queryset._single = self._single
        queryset._raise_does_not_exist = self._raise_does_not_exist
        queryset._db = self._db
        queryset._limit = self._limit
        queryset._offset = self._offset
        queryset._fields_for_select = self._fields_for_select
        queryset._filter_kwargs = copy(self._filter_kwargs)
        queryset._orderings = copy(self._orderings)
        queryset._joined_tables = copy(self._joined_tables)
        queryset._q_objects = copy(self._q_objects)
        queryset._distinct = self._distinct
        queryset._annotations = copy(self._annotations)
        queryset._having = copy(self._having)
        queryset._custom_filters = copy(self._custom_filters)
        queryset._group_bys = copy(self._group_bys)
        queryset._select_for_update = self._select_for_update
        queryset._select_related = self._select_related
        queryset._select_related_idx = self._select_related_idx
        return queryset

    def delete(self) -> "UpdateQuery":
        """
        Soft delete all objects in QuerySet, just update `deleted_time` field.
        """
        return UpdateQuery(
            db=self._db,
            model=self.model,
            update_kwargs={'deleted_time': datetime.utcnow()},
            q_objects=self._q_objects,
            annotations=self._annotations,
            custom_filters=self._custom_filters,
        )

    def erasure(self) -> "DeleteQuery":
        """
        Erasure all objects in QuerySet.
        """
        return DeleteQuery(
            db=self._db,
            model=self.model,
            q_objects=self._q_objects,
            annotations=self._annotations,
            custom_filters=self._custom_filters,
        )


class SoftDeleteModel(Model):
    uid = UUIDField(
        source_field="uid", pk=True
    )
    created_time = DatetimeField(
        source_field="created_time", auto_now_add=True, index=True
    )
    updated_time = DatetimeField(
        source_field="updated_time", auto_now=True, index=True
    )
    deleted_time = DatetimeField(
        source_field="deleted_time", null=True, index=True
    )

    queryset = SoftDeleteQuerySet

    # --------------------------------- fake ----------------------------------

    @classmethod
    def all(cls: Type[MODEL]) -> QuerySet[MODEL]:
        """
        Returns the complete QuerySet.
        """
        return cls.queryset(cls).filter(deleted_time__isnull=True)

    @classmethod
    def filter(cls: Type[MODEL], *args: Q, **kwargs: Any) -> QuerySet[MODEL]:
        """
        Generates a QuerySet with the filter applied.
        :param args: Q funtions containing constraints. Will be AND'ed.
        :param kwargs: Simple filter constraints.
        """
        return cls.queryset(cls).filter(
            deleted_time__isnull=True).filter(*args, **kwargs)

    @classmethod
    def exclude(cls: Type[MODEL], *args: Q, **kwargs: Any) -> QuerySet[MODEL]:
        """
        Generates a QuerySet with the exclude applied.
        :param args: Q funtions containing constraints. Will be AND'ed.
        :param kwargs: Simple filter constraints.
        """
        return cls.queryset(cls).filter(
            deleted_time__isnull=True).exclude(*args, **kwargs)

    @classmethod
    def get(
        cls: Type[MODEL], *args: Q, **kwargs: Any
    ) -> QuerySetSingle[MODEL]:
        """
        Fetches a single record for a Model type
        using the provided filter parameters.
        .. code-block:: python3
            user = await User.get(username="foo")
        :param args: Q funtions containing constraints. Will be AND'ed.
        :param kwargs: Simple filter constraints.
        :raises MultipleObjectsReturned: If provided
                                         search returned more than one object.
        :raises DoesNotExist: If object can not be found.
        """
        return cls.queryset(cls).filter(
            deleted_time__isnull=True).get(*args, **kwargs)

    @classmethod
    def get_or_none(
        cls: Type[MODEL], *args: Q, **kwargs: Any
    ) -> QuerySetSingle[Optional[MODEL]]:
        """
        Fetches a single record for a Model type
        using the provided filter parameters or None.
        .. code-block:: python3
            user = await User.get_or_none(username="foo")
        :param args: Q funtions containing constraints. Will be AND'ed.
        :param kwargs: Simple filter constraints.
        """
        return cls.queryset(cls).filter(
            deleted_time__isnull=True).get_or_none(*args, **kwargs)

    @classmethod
    def first(cls: Type[MODEL]) -> QuerySetSingle[Optional[MODEL]]:
        """
        Generates a QuerySet that returns the first record.
        """
        return cls.queryset(cls).filter(deleted_time__isnull=True).first()

    @classmethod
    async def get_or_create(cls: Type[MODEL]) -> None:
        raise NotImplementedError

    async def delete(
        self, using_db: Optional[BaseDBAsyncClient] = None
    ) -> None:
        """
        Soft deletes the current model object.
        :param using_db: Specific DB connection to use instead of default bound
        :raises OperationalError: If object has never been persisted.
        """
        if not self._saved_in_db:
            raise OperationalError("Can't delete unpersisted record")
        if self.deleted_time is None:
            self.deleted_time = datetime.utcnow()
            await self.save(using_db=using_db, update_fields=["deleted_time"])

    # --------------------------------- real ----------------------------------

    @classmethod
    def whole(cls: Type[MODEL]) -> QuerySet[MODEL]:
        """
        Returns the complete QuerySet.
        """
        return cls.queryset(cls)

    @classmethod
    def sift(cls: Type[MODEL], *args: Q, **kwargs: Any) -> QuerySet[MODEL]:
        """
        Generates a QuerySet with the filter applied.
        :param args: Q funtions containing constraints. Will be AND'ed.
        :param kwargs: Simple filter constraints.
        """
        return cls.queryset(cls).filter(*args, **kwargs)

    @classmethod
    def rule_out(cls: Type[MODEL], *args: Q, **kwargs: Any) -> QuerySet[MODEL]:
        """
        Generates a QuerySet with the exclude applied.
        :param args: Q funtions containing constraints. Will be AND'ed.
        :param kwargs: Simple filter constraints.
        """
        return cls.queryset(cls).exclude(*args, **kwargs)

    @classmethod
    def find(
        cls: Type[MODEL], *args: Q, **kwargs: Any
    ) -> QuerySetSingle[MODEL]:
        """
        Fetches a single record for a Model type
        using the provided filter parameters.
        .. code-block:: python3
            user = await User.find(username="foo")
        :param args: Q funtions containing constraints.
                     Will be AND'ed.
        :param kwargs: Simple filter constraints.
        :raises MultipleObjectsReturned: If provided
                                         search returned more than one object.
        :raises DoesNotExist: If object can not be found.
        """
        return cls.queryset(cls).get(*args, **kwargs)

    @classmethod
    def find_or_none(
        cls: Type[MODEL], *args: Q, **kwargs: Any
    ) -> QuerySetSingle[Optional[MODEL]]:
        """
        Fetches a single record for a Model type
        using the provided filter parameters or None.
        .. code-block:: python3
            user = await User.get(username="foo")
        :param args: Q funtions containing constraints. Will be AND'ed.
        :param kwargs: Simple filter constraints.
        """
        return cls.queryset(cls).get_or_none(*args, **kwargs)

    @classmethod
    def opening(cls: Type[MODEL]) -> QuerySetSingle[Optional[MODEL]]:
        """
        Generates a QuerySet that returns the first record.
        """
        return cls.queryset(cls).first()

    @classmethod
    async def find_or_create(
        cls: Type[MODEL],
        defaults: Optional[dict] = None,
        using_db: Optional[BaseDBAsyncClient] = None,
        **kwargs: Any,
    ) -> Tuple[MODEL, bool]:
        """
        Fetches the object if exists (filtering on the provided parameters),
        else creates an instance
        with any unspecified parameters as default values.
        :param defaults: Default values to be added to a created instance
                         if it can't be fetched.
        :param using_db: Specific DB connection to use instead of default bound
        :param kwargs: Query parameters.
        """
        if not defaults:
            defaults = {}
        db = using_db if using_db else cls._meta.db
        async with in_transaction(connection_name=db.connection_name):
            instance = await cls.sift(**kwargs).first()
            if instance:
                return instance, False
            try:
                return await cls.create(**defaults, **kwargs), True
            except (IntegrityError, TransactionManagementError):
                # Let transaction close
                pass
        # Try after transaction in case transaction error
        return await cls.find(**kwargs), False

    async def erasure(
        self, using_db: Optional[BaseDBAsyncClient] = None
    ) -> None:
        """
        Erasures the current model object.
        :param using_db: Specific DB connection to use instead of default bound
        :raises OperationalError: If object has never been persisted.
        """
        await super().delete(using_db=using_db)

    class Meta:
        ordering = ["-updated_time", "-created_time"]
        abstract = True
