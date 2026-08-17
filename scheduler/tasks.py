from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_daily_content():
    from posts.services import PostService
    topics = [
        "Berita Jakarta",
        "Wisata Jakarta",
        "Kuliner Jakarta",
        "Kata Kata Motivasi",
        "Fakta Unik Indonesia",
        "Tips Kehidupan",
        "Teknologi",
        "AI",
        "Digital Lifestyle",
        "Viral Indonesia",
    ]
    results = []
    for topic in topics:
        post = PostService.generate_content(topic)
        has_image = PostService.generate_image_for_post(post)
        post.save()
        results.append({
            "post_id": post.id,
            "topic": topic,
            "title": post.title,
            "has_image": has_image,
        })
        logger.info(f"Generated content for topic: {topic}")
    return results
