from django.db import models
from django.db.models.base import ModelBase
from rest_framework import serializers as drf_serializers


class ModelsInfo(object):
    # map of the models created by `AppBaseModelMeta`
    # Model class name -> class object
    registered_models = {}

    # model serializers map which was auto created
    # Model class name -> serializer class
    serializers = {}

    # serializer class which will be used as the base class
    # for all autogenerated serializers
    base_serializer_class = drf_serializers.ModelSerializer

    @classmethod
    def register_serializer(cls, model, serializer):
        """
        :param model: django Model subclass
        :param serializer:  model serializer
        """
        cls.serializers[model.__name__] = serializer

    @classmethod
    def register_model(cls, model):
        """
        :param model: django Model subclass
        """
        cls.registered_models[model.__name__] = model

    @classmethod
    def get_serializer(cls, class_name):
        """Returns model serializer
        :param class_name: class name of the registered model
        """
        return cls.serializers.get(class_name)

    @classmethod
    def get_model(cls, class_name):
        """Returns registered model
        :param class_name: class name of the registered model
        """
        return cls.registered_models.get(class_name)

    @classmethod
    def get_base_serializer_class(cls):
        return cls.base_serializer_class


class AppMetaOptions(object):
    __slots__ = 'ModelsInfo',

    def __init__(self):
        self.ModelsInfo = ModelsInfo


class AppBaseModelMeta(ModelBase):
    SERIALIZER_NAME_PATTERN = '{0}Serializer'
    SERIALIZER_ATTR_NAME = 'app_serializer'
    APP_META_ATTR_NAME = 'app_meta'

    @classmethod
    def create_serializer(mcs, model_name, app_meta):
        # get base serializer class for model serializer
        BaseSerializer = ModelsInfo.get_base_serializer_class()

        # get model serializer fields
        fields = app_meta.get('fields') or '__all__'

        # create model serializer
        serializer = type(
            mcs.SERIALIZER_NAME_PATTERN.format(model_name),
            (BaseSerializer,),
            {
                'Meta': type(
                    'Meta', (object,),
                    {
                        'fields': fields
                    }
                )
            }
        )

        return serializer

    @classmethod
    def __new__(mcs, *args, **kwargs):
        metaclass, name, bases, attrs = args

        # get django model Meta class attribute
        meta = attrs.get('Meta', None)

        # check that model is abstract
        abstract = getattr(meta, 'abstract', False)

        # pop app specific meta info
        app_meta = {}
        if meta:
            app_meta = getattr(meta, 'app_meta', None)
            if app_meta:
                delattr(meta, 'app_meta')
                attrs['Meta'] = meta
            else:
                app_meta = {}

        # provide all necessary args for django model metaclass
        model = super().__new__(mcs, name, bases, attrs)

        # do not register abstract models
        if abstract:
            return model

        # register created django model in ModelsInfo class
        ModelsInfo.register_model(model)

        # create model serializer
        serializer = mcs.create_serializer(name, app_meta)

        # register created model serializer in ModelsInfo class
        ModelsInfo.register_serializer(model, serializer)

        # add created serializer to model
        setattr(model, mcs.SERIALIZER_ATTR_NAME, serializer)

        # add app specific meta attrs to model
        setattr(model, mcs.APP_META_ATTR_NAME, AppMetaOptions())

        return model


class AppBaseModel(models.Model, metaclass=AppBaseModelMeta):
    class Meta:
        abstract = True


class Author(AppBaseModel):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'author'
        app_meta = {
            'fields': ('id', 'name')
        }
