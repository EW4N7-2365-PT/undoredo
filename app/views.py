from django.core.cache import cache as default_cache
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response


class RetrieveUpdateUndoRedoAPIView(RetrieveUpdateAPIView):

    cache = default_cache

    # Actions
    COMMIT = 'commit'
    PUSH = 'push'

    _actions = [COMMIT, PUSH]

    def get_action(self, request):
        action = request.data.pop('action', None)
        if not action:
            raise APIException('Provide action')
        if action not in self._actions:
            raise APIException(f'Wrong action choose one from {",".join(self._actions)}')

        return action

    def get_object_ident(self):
        instance = self.get_object()
        model = self.queryset.model
        return f'{model.__name__}_{instance.pk}'

    def get_versions(self):
        key = self.get_object_ident()
        return self.cache.get(key, [])

    def push(self, request):
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
        if 'tmp_versions' in request.query_params:
            versions = self.get_versions()
            return Response(versions)

        return super().retrieve(request, *args, **kwargs)
