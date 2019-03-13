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
