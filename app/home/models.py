from django.db import models

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from django.contrib.postgres.fields import ArrayField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.snippets.models import register_snippet
from wagtail.embeds.blocks import EmbedBlock

from home.custom_blocks import WdQueryBlock

class HomePage(Page): # To be changed to EaHomePage
    pass

class EaHomePage(Page):
    # Making the intro editable from the admin panel
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        articlepages = self.get_children().live().order_by('-first_published_at')
        context['articlepages'] = articlepages
        return context

class ArticlePage(Page):

    '''
    Articles pages handle both hand written articles and Wikidata query results.
    It uses StremField for the best flexibility.
    A StreamField block is generated for Wikidata queries results.
    '''

    # Database fields

    subtitle = models.CharField(max_length=100)

    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', BlockQuoteBlock()),
        ('page', PageChooserBlock()),
        ('document', DocumentChooserBlock()),
        ('embed', EmbedBlock()),
        ('wikidata_query', WdQueryBlock()),
    ])
    
    date = models.DateField("Post date")
    last_edit_date = models.DateField(auto_now=True)

    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)


    # Search index configuration

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.FilterField('date'),
        index.FilterField('last_edit_date'),
    ]


    # Editor panels configuration

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('subtitle'),
            FieldPanel('date'),
            FieldPanel('tags'),
        ], heading="Article information"),
        FieldPanel('body', classname="full"),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ImageChooserPanel('feed_image'),
    ]

class ArticleTagPage(TaggedItemBase):
    '''
    Add tagging capacity to pages.
    Based on Django tag system.
    '''
    content_object = ParentalKey(
        'ArticlePage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

class ArticleTagIndexPage(Page):

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        articlepages = ArticlePage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['articlepages'] = articlepages
        return context=

class ItemPage(Page):
    
    '''
    This pages get a Wikidata's item Qid as an URL parameter.
    It display :
    - The Item name as a printed title
    - The item description as a subheading
    - The item alias
    - The intro from the related Wikipedia article if it exists, 
        - with a "read more on wikipedia" link
        - and links to other articles gathered from Wikidata's external Qids
    - The list of Wikidata's properties + values + qualifiers
        - This list has a "Display more" that hides long content
        - It can be troncated for specific "Instance of" class Qids according to a list of Pids
        - else, it displays the 10 first Pids.
        - It also displays a link "edit on Wikidata"
    - A list of scholarly articles gathered on Wikidata
        - Each article dislays title + date + DOI
        - This list has a "Display more" that hides long content
        - Only the first 10 more recent articles are loaded by the SPARQL in order to avoid very long load times
        - At the end on the list there is a link "see articles from" linking to scholarly articles databases prefilled search
    - A tag cloud / graph of nearby items can be generated on demand (long load time)
        - Links to other visual insights sites are provided
        - Other visual tools & graph algortyhms could be further added
    '''

    pass


@register_snippet
class InstanceOfQidParams(models.Model):
    instance_of_Qid = models.CharField(max_length=255)
    featured_Pids = ArrayField(
            models.CharField(max_length=255, blank=True)
        )

    panels = [
        FieldPanel('instance_of_Qid'),
        FieldPanel('featured_Pids'),
    ]

    def __str__(self):
        return self.instance_of_Qid