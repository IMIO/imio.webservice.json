# -*- coding: utf-8 -*-
import hashlib
import os
import re
import shutil

from zope.interface import implements
from pyramid.events import subscriber

from imio.dataexchange.db.mappers.file import File

from imiowebservicejson.event import ValidatorEvent
from imiowebservicejson.exception import ValidationError
from imiowebservicejson.interfaces import IFileUpload


def handle_exception(rollback, attr):
    def decorator(func):
        def replacement(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                rollback(attr, *args, **kwargs)
                raise e
        return replacement
    return decorator


def remove_file(attr, obj, *args, **kwargs):
    if isinstance(obj, ValidatorEvent):
        obj = obj.context
    os.remove(getattr(obj, attr))


def get_blob_path(id):
    """Return the blob path associated to a given id"""
    full_id = '%014d' % id
    path = os.path.join(*re.findall(r'.{1,2}', full_id[:-2], re.DOTALL))
    return path


class FileUpload(object):
    implements(IFileUpload)

    def __init__(self, request):
        self.request = request
        self._file = request.POST['filedata']

    @property
    def id(self):
        return int(self.request.matchdict.get('id'))

    @property
    def filename(self):
        ext = os.path.splitext(self._file.filename)[-1]
        return '%(name)s%(ext)s' % {'name': self.id, 'ext': ext}

    @property
    def basepath(self):
        path = self.request.registry.settings.get('dms.storage.path')
        return os.path.join(path, get_blob_path(self.id))

    @property
    def filepath(self):
        return os.path.join(self.basepath, self.filename)

    @property
    def tmp_path(self):
        return '/tmp/%s' % self.filename

    @property
    def size(self):
        """ Return the temporary file size """
        stats = os.stat(self.tmp_path)
        return stats.st_size

    @property
    def data(self):
        """ Return the data of the uploaded file """
        if not hasattr(self, '_data'):
            self._data = File.first(id=self.id)
        return self._data

    @property
    def md5(self):
        f = open(self.filepath, 'r')
        return hashlib.md5(f.read()).hexdigest()

    @handle_exception(remove_file, 'tmp_path')
    def save_tmpfile(self):
        input_file = self._file.file
        output_file = open(self.tmp_path, 'wb')
        input_file.seek(0)
        while True:
            data = input_file.read(2 << 16)
            if not data:
                break
            output_file.write(data)
        output_file.close()

    @handle_exception(remove_file, 'tmp_path')
    def move(self):
        """ Move the temporary file """
        if os.path.exists(self.basepath) is False:
            os.makedirs(self.basepath)
        shutil.move(self.tmp_path, self.filepath)

    @handle_exception(remove_file, 'filepath')
    def save_reference(self):
        reference = self.data
        reference.filepath = self.filepath
        reference.file_md5 = self.md5
        reference.update()


@subscriber(ValidatorEvent, implement=IFileUpload)
@handle_exception(remove_file, 'tmp_path')
def validate_file(event):
    if event.context.data is None:
        raise ValidationError(u"There is no metadata for the file id '%s'"
                              % event.context.id)
    if event.context.data.filepath is not None:
        raise ValidationError(u"This file already exist")
    filesize = event.context.size
    metadata_filesize = event.context.data.file_metadata.get('filesize')
    if filesize != metadata_filesize:
        raise ValidationError(u"The filesize does not match (%s != %s)"
                              % (filesize, metadata_filesize))
