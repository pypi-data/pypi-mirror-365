from flask import g, request
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from mwdb.core.capabilities import Capabilities
from mwdb.core.deprecated import DeprecatedFeature, deprecated_endpoint
from mwdb.core.service import Resource
from mwdb.model import AttributeDefinition, AttributePermission, Group, db
from mwdb.schema.metakey import (
    MetakeyDefinitionItemRequestArgsSchema,
    MetakeyDefinitionItemRequestBodySchema,
    MetakeyDefinitionItemResponseSchema,
    MetakeyDefinitionListResponseSchema,
    MetakeyDefinitionManageItemResponseSchema,
    MetakeyDefinitionManageListResponseSchema,
    MetakeyItemRemoveRequestSchema,
    MetakeyItemRequestSchema,
    MetakeyKeySchema,
    MetakeyListRequestSchema,
    MetakeyListResponseSchema,
    MetakeyPermissionSetRequestArgsSchema,
    MetakeyPermissionSetRequestBodySchema,
    MetakeyUpdateRequestSchema,
)

from . import (
    access_object,
    is_valid_uuid,
    load_schema,
    loads_schema,
    logger,
    requires_authorization,
    requires_capabilities,
)


class MetakeyResource(Resource):
    @deprecated_endpoint(DeprecatedFeature.legacy_metakey_api)
    @requires_authorization
    def get(self, type, identifier):
        """
        ---
        summary: Get object attributes
        description: |
            Returns all attributes of specified object that user is allowed to read.

            Deprecated: use Attributes API instead
        security:
            - bearerAuth: []
        deprecated: true
        tags:
            - metakey
        parameters:
            - in: path
              name: type
              schema:
                type: string
                enum: [file, config, blob, object]
              description: Type of object
            - in: path
              name: identifier
              schema:
                type: string
              description: Object identifier
            - in: query
              name: hidden
              schema:
                type: int
              description: |
                Show hidden attributes
                (requires `reading_all_attributes` capability)
              required: false
        responses:
            200:
                description: Object attributes
                content:
                  application/json:
                    schema: MetakeyListResponseSchema
            403:
                description: |
                    When user requested hidden metakeys
                    but doesn't have `reading_all_attributes` capability
            404:
                description: |
                    When object doesn't exist or user doesn't have
                    access to this object.
            503:
                description: |
                    Request canceled due to database statement timeout.
        """
        schema = MetakeyListRequestSchema()
        obj = load_schema(request.args, schema)

        show_hidden = obj["hidden"]
        if show_hidden and not g.auth_user.has_rights(
            Capabilities.reading_all_attributes
        ):
            raise Forbidden("You are not permitted to read hidden metakeys")

        db_object = access_object(type, identifier)
        if db_object is None:
            raise NotFound("Object not found")

        metakeys = db_object.get_attributes(show_hidden=show_hidden, show_karton=True)
        schema = MetakeyListResponseSchema()
        return schema.dump({"metakeys": metakeys})

    @deprecated_endpoint(DeprecatedFeature.legacy_metakey_api)
    @requires_authorization
    def post(self, type, identifier):
        """
        ---
        summary: Add object attribute
        description: |
            Adds attribute to specified object.

            User must have `set` access to the attribute key
            or `adding_all_attributes` capability.

            Deprecated: use Attributes API instead
        security:
            - bearerAuth: []
        deprecated: true
        tags:
            - metakey
        parameters:
            - in: path
              name: type
              schema:
                type: string
                enum: [file, config, blob, object]
              description: Type of object
            - in: path
              name: identifier
              schema:
                type: string
              description: Object identifier
        requestBody:
            description: Attribute key and value
            content:
              application/json:
                schema: MetakeyItemRequestSchema
        responses:
            200:
                description: When metakey was added successfully
                content:
                  application/json:
                    schema: MetakeyListResponseSchema
            400:
                description: For karton attribute when value is not UUID
            404:
                description: |
                    When object doesn't exist or user doesn't have
                    access to this object.

                    When attribute key is not defined or user doesn't have
                    privileges to set that one.
            503:
                description: |
                    Request canceled due to database statement timeout.
        """
        schema = MetakeyItemRequestSchema()
        obj = loads_schema(request.get_data(as_text=True), schema)

        db_object = access_object(type, identifier)
        if db_object is None:
            raise NotFound("Object not found")

        key = obj["key"]
        value = obj["value"]

        if key == "karton" and not is_valid_uuid(value):
            raise BadRequest("'karton' attribute accepts only UUID values")

        is_new = db_object.add_attribute(key, value)
        if is_new is None:
            raise NotFound(
                f"Attribute '{key}' is not defined or you have "
                f"insufficient permissions to set it"
            )

        db.session.commit()
        db.session.refresh(db_object)
        metakeys = db_object.get_attributes(show_karton=True)
        schema = MetakeyListResponseSchema()
        return schema.dump({"metakeys": metakeys})

    @deprecated_endpoint(DeprecatedFeature.legacy_metakey_api)
    @requires_authorization
    @requires_capabilities("removing_attributes")
    def delete(self, type, identifier):
        """
        ---
        summary: Delete object attribute
        description: |
            Deletes attribute from specified object.

            User must have `removing_attributes` capability.

            If value is not specified, all values under the specified
            key are removed.

            Deprecated: use Attributes API instead
        security:
            - bearerAuth: []
        deprecated: true
        tags:
            - metakey
        parameters:
            - in: path
              name: type
              schema:
                type: string
                enum: [file, config, blob, object]
              description: Type of object
            - in: path
              name: identifier
              schema:
                type: string
              description: Object identifier
            - in: query
              name: key
              schema:
                type: string
              description: Key of attribute object to be deleted
              required: true
            - in: query
              name: value
              schema:
                type: string
              description: Value of attribute key object to be deleted
              required: false
        responses:
            200:
                description: When metakey was deleted successfully
            404:
                description: |
                    When object doesn't exist or user doesn't have access
                    to this object.
                    When attribute key is not defined or user doesn't have privileges
                    to set that one.
            503:
                description: |
                    Request canceled due to database statement timeout.
        """
        schema = MetakeyItemRemoveRequestSchema()
        obj = load_schema(request.args, schema)

        db_object = access_object(type, identifier)
        if db_object is None:
            raise NotFound("Object not found")

        key = obj["key"]
        value = obj.get("value")

        deleted_object = db_object.remove_attribute(key, value)
        if deleted_object is False:
            raise NotFound(
                f"Attribute '{key}' is not defined or you have "
                f"insufficient permissions to delete it"
            )
        db.session.commit()


class MetakeyListDefinitionResource(Resource):
    @deprecated_endpoint(DeprecatedFeature.legacy_metakey_api)
    @requires_authorization
    def get(self, access):
        """
        ---
        summary: Get list of attribute keys
        description: |
            Returns list of attribute keys which currently authenticated user
            can read or set.

            Deprecated: use Attributes API instead
        security:
            - bearerAuth: []
        deprecated: true
        tags:
            - metakey
        parameters:
            - in: path
              name: access
              schema:
                type: string
                enum: [read, set]
              description: Type of desired access
        responses:
            200:
                description: List of attribute keys and definitions
                content:
                  application/json:
                    schema: MetakeyDefinitionListResponseSchema
            400:
                description: When used unknown access type (other than read or set)
            503:
                description: |
                    Request canceled due to database statement timeout.
        """
        if access == "read":
            metakeys = AttributeDefinition.query_for_read()
        elif access == "set":
            metakeys = AttributeDefinition.query_for_set()
        else:
            raise BadRequest(f"Unknown desired access type '{access}'")

        metakeys = metakeys.order_by(AttributeDefinition.key).all()
        schema = MetakeyDefinitionListResponseSchema()
        return schema.dump({"metakeys": metakeys})


class MetakeyListDefinitionManageResource(Resource):
    @deprecated_endpoint(DeprecatedFeature.legacy_metakey_api)
    @requires_authorization
    @requires_capabilities(Capabilities.manage_users)
    def get(self):
        """
        ---
        summary: Get attribute key definitions
        description: |
            Returns list of attribute key definitions.

            Requires `manage_users` capability.

            Deprecated: use Attributes API instead
        security:
            - bearerAuth: []
        deprecated: true
        tags:
            - metakey
        responses:
            200:
                description: List of attribute keys and definitions
                content:
                  application/json:
                    schema: MetakeyDefinitionManageListResponseSchema
            403:
                description: When user doesn't have `manage_users` capability.
            503:
                description: |
                    Request canceled due to database statement timeout.
        """
        metakeys = (
            db.session.query(AttributeDefinition)
            .order_by(AttributeDefinition.key)
            .all()
        )
        schema = MetakeyDefinitionManageListResponseSchema()
        return schema.dump({"metakeys": metakeys})


class MetakeyDefinitionManageResource(Resource):
    @deprecated_endpoint(DeprecatedFeature.legacy_metakey_api)
    @requires_authorization
    @requires_capabilities(Capabilities.manage_users)
    def get(self, key):
        """
        ---
        summary: Get attribute key details
        description: |
            Returns attribute key definition details.

            Requires `manage_users` capability.

            Deprecated: use Attributes API instead
        security:
            - bearerAuth: []
        deprecated: true
        tags:
            - metakey
        parameters:
            - in: path
              name: key
              schema:
                type: string
              description: Attribute key
        responses:
            200:
                description: Attribute key definition
                content:
                  application/json:
                    schema: MetakeyDefinitionManageItemResponseSchema
            403:
                description: When user doesn't have `manage_users` capability.
            404:
                description: When specified attribute key doesn't exist
            503:
                description: |
                    Request canceled due to database statement timeout.
        """
        metakey = (
            db.session.query(AttributeDefinition)
            .filter(AttributeDefinition.key == key)
            .first()
        )
        if metakey is None:
            raise NotFound("No such metakey")
        schema = MetakeyDefinitionManageItemResponseSchema()
        return schema.dump(metakey)

    @deprecated_endpoint(DeprecatedFeature.legacy_metakey_api)
    @requires_authorization
    @requires_capabilities(Capabilities.manage_users)
    def post(self, key):
        """
        ---
        summary: Create attribute key
        description: |
            Creates attribute key definition.

            Requires `manage_users` capability.

            Deprecated: use Attributes API instead
        security:
            - bearerAuth: []
        deprecated: true
        tags:
            - metakey
        parameters:
            - in: path
              name: key
              schema:
                type: string
              description: Attribute key
        requestBody:
            description: Attribute key definition
            content:
              application/json:
                schema: MetakeyDefinitionItemRequestBodySchema
        responses:
            200:
                description: When metakey definition is successfully added
                content:
                  application/json:
                    schema: MetakeyDefinitionItemResponseSchema
            400:
                description: |
                    When one of attribute definition fields is missing or incorrect.
            403:
                description: When user doesn't have `manage_users` capability.
            503:
                description: |
                    Request canceled due to database statement timeout.
        """
        schema = MetakeyDefinitionItemRequestArgsSchema()
        args_obj = load_schema({"key": key}, schema)

        schema = MetakeyDefinitionItemRequestBodySchema()
        obj = loads_schema(request.get_data(as_text=True), schema)

        metakey_definition = AttributeDefinition(
            key=args_obj["key"],
            url_template=obj["url_template"],
            label=obj["label"],
            description=obj["description"],
            hidden=obj["hidden"],
        )
        metakey_definition = db.session.merge(metakey_definition)
        db.session.commit()

        schema = MetakeyDefinitionItemResponseSchema()
        return schema.dump(metakey_definition)

    @deprecated_endpoint(DeprecatedFeature.legacy_metakey_api)
    @requires_authorization
    @requires_capabilities(Capabilities.manage_users)
    def put(self, key):
        """
        ---
        summary: Update attribute key
        description: |
            Update attribute key definition.

            Requires `manage_users` capability.

            Deprecated: use Attribute API instead.
        security:
            - bearerAuth: []
        deprecated: true
        tags:
            - metakey
        parameters:
            - in: path
              name: key
              schema:
                type: string
              description: Attribute key
        requestBody:
            description: Attribute definition to update
            content:
              application/json:
                schema: MetakeyUpdateRequestSchema
        responses:
            200:
                description: When metakey definition is successfully updated
                content:
                  application/json:
                    schema: MetakeyDefinitionItemResponseSchema
            400:
                description: |
                    When one of attribute definition fields is missing or incorrect.
            403:
                description: When user doesn't have `manage_users` capability.
            404:
                description: When metakey doesn't exist.
            503:
                description: |
                    Request canceled due to database statement timeout.
        """
        schema = MetakeyUpdateRequestSchema()
        obj = loads_schema(request.get_data(as_text=True), schema)

        metakey_obj = load_schema({"key": key}, MetakeyKeySchema())
        metakey = (
            db.session.query(AttributeDefinition)
            .filter(AttributeDefinition.key == metakey_obj["key"])
            .first()
        )
        if metakey is None:
            raise NotFound("No such metakey")

        label = obj["label"]
        if label is not None:
            metakey.label = label

        description = obj["description"]
        if description is not None:
            metakey.description = description

        url_template = obj["template"]
        if url_template is not None:
            metakey.url_template = url_template

        hidden = obj["hidden"]
        if hidden is not None:
            metakey.hidden = obj["hidden"]

        db.session.commit()
        logger.info("Attribute updated", extra=obj)

        schema = MetakeyDefinitionItemResponseSchema()
        return schema.dump(metakey)

    @deprecated_endpoint(DeprecatedFeature.legacy_metakey_api)
    @requires_authorization
    @requires_capabilities(Capabilities.manage_users)
    def delete(self, key):
        """
        ---
        summary: Delete attribute key
        description: |
            Deletes attribute key including all related object attributes.

            Requires `manage_users` capability.

            Deprecated: use Attribute API instead.
        security:
            - bearerAuth: []
        deprecated: true
        tags:
            - metakey
        parameters:
            - in: path
              name: key
              schema:
                type: string
              description: Attribute key
        responses:
            200:
                description: When attribute key was deleted
            403:
                description: When user doesn't have `manage_users` capability.
            404:
                description: When specified attribute key doesn't exist
            503:
                description: |
                    Request canceled due to database statement timeout.
        """
        metakey = (
            db.session.query(AttributeDefinition)
            .filter(AttributeDefinition.key == key)
            .first()
        )
        if metakey is None:
            raise NotFound("No such metakey")
        db.session.delete(metakey)
        db.session.commit()


class MetakeyPermissionResource(Resource):
    @deprecated_endpoint(DeprecatedFeature.legacy_metakey_api)
    @requires_authorization
    @requires_capabilities(Capabilities.manage_users)
    def put(self, key, group_name):
        """
        ---
        summary: Add/modify attribute key permission
        description: |
            Adds or modifies attribute key group permission
            for specified key and group name.

            Requires `manage_users` capability.

            Deprecated: use Attribute API instead.
        security:
            - bearerAuth: []
        deprecated: true
        tags:
            - metakey
        parameters:
            - in: path
              name: key
              schema:
                type: string
              description: Attribute key
            - in: path
              name: group_name
              schema:
                type: string
              description: Group name to add/modify
        requestBody:
            description: Attribute key permission definition
            content:
                application/json:
                  schema: MetakeyPermissionSetRequestBodySchema
        responses:
            200:
                description: When group permission has been successfully changed
                content:
                  application/json:
                    schema: MetakeyDefinitionManageItemResponseSchema
            400:
                description: |
                    When one of attribute permission fields is missing or incorrect.
            403:
                description: When user doesn't have `manage_users` capability.
            404:
                description: When attribute key or group doesn't exist
            503:
                description: |
                    Request canceled due to database statement timeout.
        """
        schema = MetakeyPermissionSetRequestArgsSchema()
        args_obj = load_schema({"key": key, "group_name": group_name}, schema)

        schema = MetakeyPermissionSetRequestBodySchema()
        obj = loads_schema(request.get_data(as_text=True), schema)

        metakey_definition = (
            db.session.query(AttributeDefinition)
            .filter(AttributeDefinition.key == args_obj["key"])
            .first()
        )
        if metakey_definition is None:
            raise NotFound("No such metakey")

        group = (
            db.session.query(Group).filter(Group.name == args_obj["group_name"]).first()
        )
        if group is None:
            raise NotFound("No such group")

        permission = AttributePermission(
            key=args_obj["key"],
            group_id=group.id,
            can_read=obj["can_read"],
            can_set=obj["can_set"],
        )
        db.session.merge(permission)
        db.session.commit()

        db.session.refresh(metakey_definition)
        schema = MetakeyDefinitionManageItemResponseSchema()
        return schema.dump(metakey_definition)

    @deprecated_endpoint(DeprecatedFeature.legacy_metakey_api)
    @requires_authorization
    @requires_capabilities(Capabilities.manage_users)
    def delete(self, key, group_name):
        """
        ---
        summary: Delete attribute key permission
        description: |
            Removes attribute key permission for specified key and group name.

            Requires `manage_users` capability.

            Deprecated: use Attribute API instead.
        security:
            - bearerAuth: []
        deprecated: true
        tags:
            - metakey
        parameters:
            - in: path
              name: key
              schema:
                type: string
              description: Attribute key
            - in: path
              name: group_name
              schema:
                type: string
              description: Group name to remove
        responses:
            200:
                description: When group permission has been successfully removed
            403:
                description: When user doesn't have `manage_users` capability.
            404:
                description: |
                    When attribute key or group or group permission doesn't exist
            503:
                description: |
                    Request canceled due to database statement timeout.
        """
        schema = MetakeyPermissionSetRequestArgsSchema()
        args_obj = load_schema({"key": key, "group_name": group_name}, schema)

        group = (
            db.session.query(Group).filter(Group.name == args_obj["group_name"]).first()
        )
        if group is None:
            raise NotFound("No such group")

        metakey_permission = (
            db.session.query(AttributePermission)
            .filter(
                AttributePermission.key == args_obj["key"],
                AttributePermission.group_id == group.id,
            )
            .first()
        )

        if metakey_permission is None:
            raise NotFound("No such metakey permission")

        db.session.delete(metakey_permission)
        db.session.commit()
