from django.core.cache import cache as default_cache
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from reversion.models import Version


class VersionMixin(object):

    def parse_version(self, request):
        version = request.query_params.get('version', 1)
        try:
            version = int(version)
        except TypeError:
            raise APIException('Version must be an integer')

        if version <= 0:
            raise APIException('Version must be greater than zero.')

        return version

    def get_object(self):
        instance = super().get_object()
        version_number = self.parse_version(self.request)
        versions = Version.objects.get_for_object(instance)
        versions_count = versions.count()

        if version_number > versions_count:
            raise APIException(f'Version {version_number} does not exist.')

        version = versions[versions_count - version_number]
        return version._object_version.object


class ListCreateUndoRedoAPIView(RetrieveUpdateDestroyAPIView):
    cache = default_cache

    # Actions
    COMMIT = 'commit'
    PUSH = 'push'

    _actions = [COMMIT, PUSH]

    def get_action(self, request):
        action = request.data.get('action', None)
        if not action:
            raise APIException('Provide action')
        if action not in self._actions:
            raise APIException(f'Provide one of {",".join(self._actions)}')

        return action

    def get_object_ident(self):
        instance = self.get_object()
        model = self.queryset.model
        return f'{model.__name__}_{instance.pk}'

    def get_versions(self):
        key = self.get_object_ident()
        return self.cache.get(key, [])

    def push(self, request):
        request.data.pop('action')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        versions = self.get_versions()
        versions.append(serializer.data)
        self.cache.set(self.get_object_ident(), versions)

        return {
            'has_next': False,
            'has_previous': len(versions) > 1,
            'data': serializer.data
        }

    def clear_buffer(self):
        ident = self.get_object_ident()
        self.cache.delete(ident)

    def put(self, request, *args, **kwargs):
        action = self.get_action(request)
        if action == self.PUSH:
            pushed_object = self.push(request)
            return Response(pushed_object, status=status.HTTP_200_OK)
        else:
            self.clear_buffer()
            return super().put(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        tmp_versions = request.query_params.get('tmp_versions')
        if tmp_versions:
            versions = self.get_versions()
            return Response(versions)

        return super().retrieve(request, *args, **kwargs)
