import operator
from operator import itemgetter
from readinglist.backend.id_generator import UUID4Generator
from readinglist.utils import COMPARISON


class BackendBase(object):
    def __init__(self, id_generator=None, *args, **kwargs):
        if id_generator is None:
            id_generator = UUID4Generator()
        self.id_generator = id_generator

    def flush(self):
        raise NotImplementedError

    def ping(self):
        raise NotImplementedError

    def last_collection_timestamp(self, resource, user_id):
        raise NotImplementedError

    def create(self, resource, user_id, record):
        raise NotImplementedError

    def get(self, resource, user_id, record_id):
        raise NotImplementedError

    def update(self, resource, user_id, record_id, record):
        raise NotImplementedError

    def delete(self, resource, user_id, record_id):
        raise NotImplementedError

    def get_all(self, resource, user_id, filters=None, sorting=None):
        raise NotImplementedError

    def set_record_timestamp(self, resource, user_id, record):
        timestamp = self._bump_timestamp(resource, user_id)
        record[resource.modified_field] = timestamp
        return record


def apply_filters(records, filters):
    operators = {
        COMPARISON.LT: operator.lt,
        COMPARISON.MAX: operator.le,
        COMPARISON.EQ: operator.eq,
        COMPARISON.NOT: operator.ne,
        COMPARISON.MIN: operator.ge,
        COMPARISON.GT: operator.gt,
    }

    for record in records:
        matches = [operators[op](record[k], v) for k, v, op in filters]
        if all(matches):
            yield record


def apply_sorting(records, sorting):
    result = list(records)

    if not result:
        return result

    for field, direction in reversed(sorting):
        is_boolean_field = isinstance(result[0][field], bool)
        reverse = direction < 0 or is_boolean_field
        result = sorted(result, key=itemgetter(field), reverse=reverse)

    return result