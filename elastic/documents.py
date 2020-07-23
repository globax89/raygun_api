from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, tokenizer

from logs_manager.models import ErrorLogObject, LogInstance, UserInteraction
from logs_manager.serializers import LogInstanceSerializer, UserInteractionSerializer
from organization.models import Service

NGRAM = analyzer(
    'ngram_analyzer',
    tokenizer=tokenizer("gram", "ngram", min_gram=2, max_gram=3),
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


@registry.register_document
class ErrorLogObjectDocument(Document):
    service = fields.TextField()

    message = fields.TextField(
        analyzer=NGRAM
    )

    stacktrace = fields.TextField(
        analyzer=NGRAM
    )

    loginstances = fields.NestedField(properties={
        'timestamp': fields.TextField(),
        'type': fields.TextField(),
        'log': fields.TextField(analyzer=NGRAM),
    })

    userinteractions = fields.NestedField(properties={
        'element': fields.TextField(),
        'innerText': fields.TextField()
    })

    count = fields.IntegerField()

    def prepare_service(self, instance):
        services = Service.objects.filter(ticket=instance.ticket)
        if services.exists():
            return services[0].name
        else:
            return f"tkt: {instance.ticket}"

    def prepare_count(self, instance):
        return instance.count

    def prepare_loginstances(self, instance):
        instances = LogInstance.objects.filter(log_id=instance.id)
        ser = LogInstanceSerializer(instances, many=True)
        serdata = ser.data
        ddata = dict()
        for i in range(len(instances)):
            ddata[instances[i].id] = serdata[i]
        return ddata

    def prepare_userinteractions(self, instance):
        instances = UserInteraction.objects.filter(log_id=instance.id)
        ser = UserInteractionSerializer(instances, many=True)
        serdata = ser.data
        ddata = dict()
        for i in range(len(instances)):
            ddata[instances[i].id] = serdata[i]
        return ddata

    class Index:
        name = "error_logs"

    class Django:
        model = ErrorLogObject
        fields = ('timestamp',)


@registry.register_document
class LogInstanceDocument(Document):
    log_timestamp = fields.TextField()
    error_timestamp = fields.DateField()
    ticket = fields.TextField()
    message = fields.TextField()
    stacktrace = fields.TextField()

    def prepare_log_timestamp(self, instance):
        return instance.timestamp

    def prepare_error_timestamp(self, instance):
        try:
            ErrorLogObject.objects.get(id=instance.log_id).timestamp
        except ErrorLogObject.DoesNotExist:
            return ""

    def prepare_ticket(self, instance):
        try:
            ErrorLogObject.objects.get(id=instance.log_id).ticket
        except ErrorLogObject.DoesNotExist:
            return ""

    def prepare_message(self, instance):
        try:
            ErrorLogObject.objects.get(id=instance.log_id).message
        except ErrorLogObject.DoesNotExist:
            return ""

    def prepare_stacktrace(self, instance):
        try:
            ErrorLogObject.objects.get(id=instance.log_id).stacktrace
        except ErrorLogObject.DoesNotExist:
            return ""

    class Index:
        name = "log_instances"

    class Django:
        model = LogInstance
        fields = ('type', 'log')
# @registry.register_document
# class UserProfileDocument(Document):
#     pkk = fields.TextField()
#
#     user = fields.ObjectField(properties={
#         'email': fields.TextField(
#             analyzer=NGRAM
#         ),
#         'first_name': fields.TextField(
#             analyzer=NGRAM
#         ),
#         'last_name': fields.TextField(
#             analyzer=NGRAM
#         ),
#     })
#
#     designation = fields.TextField(
#         analyzer=NGRAM
#     )
#
#     organisation = fields.TextField(
#         analyzer=NGRAM
#     )
#
#     profile_img = fields.TextField()
#
#     def prepare_profile_img(self, instance):
#         if instance.profile_img:
#             return instance.profile_img.get_media_url
#         else:
#             return ''
#
#     class Index:
#
#         name = 'user_profile'
#         settings = {'number_of_shards': 1,
#                     'number_of_replicas': 0}
#         stats = True
#
#     class Django:
#
#         model = UserProfile
#
#         fields = [
#             'id'
#         ]
#
#         related_models = [User, MediaManager]
#
#     def get_queryset(self):
#         return self.django.model._default_manager.filter(user__is_active=True)
#
#     def get_instances_from_related(self, related_instance):
#         if isinstance(related_instance, User):
#             return UserProfile.objects.get(user=related_instance)
#         elif isinstance(related_instance, MediaManager):
#             return UserProfile.objects.filter(profile_img=related_instance)
#
#
# @registry.register_document
# class PostDocument(Document):
#     pkk = fields.TextField()
#     post_type = fields.TextField()
#     post_stats = fields.ObjectField()
#
#     author = fields.ObjectField(properties={
#         'email': fields.TextField(
#             analyzer=NGRAM
#         ),
#         'first_name': fields.TextField(
#             analyzer=NGRAM
#         ),
#         'last_name': fields.TextField(
#             analyzer=NGRAM
#         ),
#     })
#
#     title = fields.TextField(
#         analyzer=NGRAM
#     )
#
#     categories = fields.NestedField(properties={
#         'name': fields.TextField(
#             analyzer=NGRAM
#         )
#     })
#
#     media = fields.TextField()
#
#     def prepare_media(self, instance):
#         if instance.media:
#             if instance.media.count():
#                 return instance.media.first().get_media_url
#             else:
#                 return ''
#         else:
#             return ''
#
#     description = fields.TextField(
#         analyzer=NGRAM
#     )
#
#     def prepare_post_type(self, instance):
#         post = Post.objects.get_subclass(id=instance.id)
#
#         if post.__class__.__name__ == 'Feed':
#             return post.feed_type
#         else:
#             return post.__class__.__name__
#
#     def prepare_post_stats(self, instance):
#         useraction_data = UserAction.objects.filter(
#             object_id=instance.pk, content_type=ContentType.objects.get_for_model(Post), is_active=True)
#
#         upvote_count = useraction_data.filter(action_type='upvote').count()
#         downvote_count = useraction_data.filter(action_type='downvote').count()
#         comment_count = Comments.objects.filter(
#             object_pk=instance.pkk, content_type=ContentType.objects.get_for_model(Post)).count()
#
#         if downvote_count == 0:
#             upvote_percent = 100.0
#         else:
#             upvote_percent = round(upvote_count / (downvote_count + upvote_count) * 100, 1)
#
#         return {'upvote_percent': upvote_percent, 'comment_count': comment_count}
#
#     class Index:
#         name = 'post'
#         settings = {'number_of_shards': 1,
#                     'number_of_replicas': 0}
#
#     class Django:
#
#         model = Post
#
#         fields = [
#             'id',
#             'created_on'
#         ]
#
#         related_models = [Feed, Events, Category, UserAction, MediaManager]
#
#     def get_queryset(self):
#         return self.django.model._default_manager.filter(is_published=True)
#
#     def get_instances_from_related(self, related_instance):
#
#         if isinstance(related_instance, Category):
#             return Post.objects.filter(categories__in=[related_instance])
#         elif isinstance(related_instance, UserAction):
#             return Post.objects.get(id=related_instance.object_id)
#         elif isinstance(related_instance, MediaManager):
#             return Post.objects.filter(media__in=[related_instance])
#         else:
#             return related_instance
