from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_content_task(topic=None):
    from .models import Post
    from .services import PostService
    post = PostService.generate_content(topic)
    has_image = PostService.generate_image_for_post(post)
    logger.info(f"Generated post: {post.id} - {post.title} (image: {has_image})")
    return {"post_id": post.id, "title": post.title, "has_image": has_image}


@shared_task
def auto_publish_post():
    from .models import Post
    from .services import PostService
    pending = PostService.get_pending_scheduled()
    if not pending.exists():
        return "No scheduled posts to publish"

    results = []
    for post in pending:
        try:
            PostService.mark_posting(post)
            from ai.services import InstagramAutomationService
            success = InstagramAutomationService.publish_post(post)
            if success:
                PostService.mark_published(post)
                results.append(f"Published: {post.id} - {post.title}")
                logger.info(f"Published post: {post.id}")
            else:
                PostService.mark_failed(post, "Publishing failed")
                results.append(f"Failed: {post.id}")
                logger.error(f"Failed to publish post: {post.id}")
        except Exception as e:
            PostService.mark_failed(post, str(e))
            results.append(f"Error: {post.id} - {str(e)}")
            logger.exception(f"Error publishing post {post.id}")

    return results


@shared_task
def retry_failed_posts():
    from .models import Post
    from .services import PostService
    failed_posts = Post.objects.filter(status="failed", retry_count__lt=10)
    results = []
    for post in failed_posts:
        try:
            PostService.mark_posting(post)
            from ai.services import InstagramAutomationService
            success = InstagramAutomationService.publish_post(post)
            if success:
                PostService.mark_published(post)
                results.append(f"Retry success: {post.id}")
            else:
                PostService.mark_failed(post, "Retry failed")
                results.append(f"Retry failed: {post.id}")
        except Exception as e:
            PostService.mark_failed(post, str(e))
            results.append(f"Retry error: {post.id}")
    return results
