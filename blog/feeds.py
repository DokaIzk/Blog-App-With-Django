import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Post


class LatestPostsFeed(Feed):
    title = "Blog App"
    link = reverse_lazy('blog:post_list')
    description = "New Posts on Blog."

    def items(self):
        return Post.publish.all()[:5]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.body), 25)
    
    def item_pubdate(self, item):
        return item.published