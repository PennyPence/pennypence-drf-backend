from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Question, Comment, Like, Article
from django.contrib.contenttypes.models import ContentType
from .serializers import QuestionSerializer, CommentSerializer, LikeSerializer, ArticleSerializer

def get_or_none(model, id):
    try:
        return model.objects.get(id=id)
    except model.DoesNotExist:
        return None

class CommunityViewMixin:
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs): # 좋아요를 
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['like_count'] = instance.likes.count()
        return Response(data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        instance = self.get_object()
        user = request.user
        content_type = ContentType.objects.get_for_model(instance)
        try:
            like = Like.objects.get(content_type=content_type, object_id=instance.id, user=user)
            like.delete()
            like_count = instance.likes.count()
            return Response({'detail': 'Unliked.', 'like_count': like_count})
        except Like.DoesNotExist:
            like = Like(content_object=instance, user=user)
            like.save()
            like_count = instance.likes.count()
            return Response({'detail': 'Liked.', 'like_count': like_count})
        
class QuestionViewSet(CommunityViewMixin, viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class ArticleViewSet(CommunityViewMixin, viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
        
class CommentViewSet(CommunityViewMixin, viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
        
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        comment_id = request.query_params.get('comment_id', None)
        if comment_id is not None:
            replies_queryset = Comment.objects.filter(parent_id=comment_id)
            replies_serializer = self.get_serializer(replies_queryset, many=True)
            return Response(replies_serializer.data)

        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def replies(self, request, pk=None):
        parent_comment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user, parent=parent_comment)
        return Response(serializer.data)
    
class LikeViewSet(viewsets.ViewSet):
    serializer_class = LikeSerializer

    @action(detail=False, methods=['get'])
    def likes_list(self, request):
        check_list = ['question_id', 'article_id', 'comment_id']
        if not request.GET:
            raise ValidationError('The content type and ID must be provided as query parameters. ex) question_id=1')
        for idx, order in enumerate(check_list):
            id = request.query_params.get(order, None)
            if id:
                if not idx:
                    article = get_or_none(Question, id)
                elif idx == 1:
                    article = get_or_none(Article, id)
                else:
                    article = get_or_none(Comment, id)
                if not article:
                    raise ValidationError('There is no such ID')
                content_type = ContentType.objects.get_for_model(article)
                likes = Like.objects.filter(content_type=content_type, object_id=id)
                serializer = self.serializer_class(likes, many=True)
                return Response(serializer.data)