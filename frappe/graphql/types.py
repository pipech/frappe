import graphene

from frappe.graphql.utils import make_field_and_resolver

from graphene.types.objecttype import ObjectType, ObjectTypeOptions


class FrappeObjectType(graphene.ObjectType):
    @classmethod
    def __init_subclass_with_meta__(
        cls,
        doctype=None,
        interfaces=(),
        possible_types=(),
        default_resolver=None,
        _meta=None,
        **options
    ):
        cls, fields = make_field_and_resolver(cls, doctype)

        # create _meta object
        if not _meta:
            _meta = ObjectTypeOptions(cls)

        if _meta.fields:
            _meta.fields.update(fields)
        else:
            _meta.fields = fields

        if not _meta.interfaces:
            _meta.interfaces = interfaces
        _meta.possible_types = possible_types
        _meta.default_resolver = default_resolver

        super(ObjectType, cls).__init_subclass_with_meta__(
            _meta=_meta, **options
        )
