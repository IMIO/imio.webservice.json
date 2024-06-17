# -*- coding: utf-8 -*-
import hashlib
import logging
import os
import re
import shutil

from zope.interface import implementer
from pyramid.events import subscriber

from imio.dataexchange.db.mappers.file import File

from imiowebservicejson.event import ValidatorEvent
from imiowebservicejson.exception import ValidationError
from imiowebservicejson.interfaces import IFileUpload


logger = logging.getLogger("root")


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
    full_id = "%014d" % id
    path = os.path.join(*re.findall(r".{1,2}", full_id[:-2], re.DOTALL))
    return path


@implementer(IFileUpload)
class FileUpload(object):

    def __init__(self, request):
        self.request = request
        self._file = request.POST["filedata"]
        self._md5 = None

    @property
    def id(self):
        return int(self.request.matchdict.get("id"))

    @property
    def filename(self):
        ext = os.path.splitext(self._file.filename)[-1]
        return "%(name)s%(ext)s" % {"name": self.id, "ext": ext}

    @property
    def basepath(self):
        path = self.request.registry.settings.get("dms.storage.path")
        return os.path.join(path, get_blob_path(self.id))

    @property
    def filepath(self):
        return os.path.join(self.basepath, self.filename)

    @property
    def tmp_path(self):
        return "/tmp/%s" % self.filename

    @property
    def size(self):
        """ Return the temporary file size """
        stats = os.stat(self.tmp_path)
        return stats.st_size

    @property
    def data(self):
        """ Return the data of the uploaded file """
        if not hasattr(self, "_data"):
            self._data = File.first(id=self.id)
        return self._data

    @property
    def md5(self):
        self._md5 = self._md5 and self._md5 or self.calculate_md5()
        return self._md5

    def calculate_md5(self):
        path = os.path.exists(self.filepath) and self.filepath or self.tmp_path
        f = open(path, "r")
        return hashlib.md5(f.read()).hexdigest()

    @handle_exception(remove_file, "tmp_path")
    def save_tmpfile(self):
        input_file = self._file.file
        output_file = open(self.tmp_path, "wb")
        input_file.seek(0)
        while True:
            data = input_file.read(2 << 16)
            if not data:
                break
            output_file.write(data)
        output_file.close()

    @handle_exception(remove_file, "tmp_path")
    def move(self):
        """ Move the temporary file """
        if os.path.exists(self.basepath) is False:
            os.makedirs(self.basepath)
        shutil.move(self.tmp_path, self.filepath)

    @handle_exception(remove_file, "filepath")
    def save_reference(self):
        reference = self.data
        reference.filepath = self.filepath
        reference.file_md5 = self.md5
        reference.update()


@subscriber(ValidatorEvent, implement=IFileUpload)
@handle_exception(remove_file, "tmp_path")
def validate_file(event):
    FileValidator10(event).validate()


@subscriber(ValidatorEvent, implement=IFileUpload, version=">= 1.1")
@handle_exception(remove_file, "tmp_path")
def validate_file_11(event):
    FileValidator11(event).validate()


class FileValidatorBase(object):

    _validations = ()

    def __init__(self, event):
        self.event = event

    def validate(self):
        for validator in self._validations:
            getattr(self, validator)()

    @property
    def context(self):
        return self.event.context

    @property
    def data(self):
        return self.event.context.data

    @property
    def metadata(self):
        return self.data.file_metadata


class FileValidator10(FileValidatorBase):

    _validations = ("_validate_data", "_verify_filepath", "_validate_filesize")

    @property
    def filesize(self):
        return self.context.size

    @property
    def metadata_filesize(self):
        return self.metadata.get("filesize")

    def _validate_data(self):
        if self.data is None:
            raise ValidationError(
                u"MISSING_METADATA",
                u"There is no metadata for the file id '%s'" % self.context.id,
            )

    def _verify_filepath(self):
        if self.data.filepath is not None:
            logger.warning(u"file updated %s" % self.data.filepath)

    def _validate_filesize(self):
        if self.filesize != self.metadata_filesize:
            raise ValidationError(
                u"FILESIZE_MISMATCH",
                u"The filesize does not match (%s != %s)"
                % (self.filesize, self.metadata_filesize),
            )


class FileValidator11(FileValidatorBase):

    _validations = ("_validate_md5",)

    @property
    def md5(self):
        return self.context.md5

    @property
    def metadata_md5(self):
        return self.metadata.get("filemd5")

    def _validate_md5(self):
        if self.md5 != self.metadata_md5.lower():
            raise ValidationError(u"MD5_MISMATCH", u"MD5 check: difference found on external id '{}'".format(self.data.external_id))
