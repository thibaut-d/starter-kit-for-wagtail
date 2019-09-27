# Core Django
from django import forms
from django.db import models

# Tags
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

# Classical fields
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from django.contrib.postgres.fields import ArrayField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

# Streamfield
from wagtail.core.fields import StreamField
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.snippets.models import register_snippet
from wagtail.embeds.blocks import EmbedBlock

# Custom streamfield
from home.custom_blocks import WdQueryBlock

#API
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField

class HomePage(Page):

    '''
    These are homepages explore.ac and for sub-sites such as chronic-pain.reviews
    These also store the data relative to the focus.
    '''

    # Database fields
    
    ## Text for the logo like mysite.com
    link = models.URLField(blank=True)
    
    ## Intro message printed over the image
    intro = RichTextField(blank=True)

    ## Full width intro image
    intro_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    ## Feed image, used only when a homepage is a subpage of another homepage
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    ) 

    ## Intro message printed at the start of articles
    intro_articles = RichTextField(blank=True)

    # Search index configuration

    search_fields = Page.search_fields + [
        index.FilterField('link'),
        index.FilterField('intro'),
        index.FilterField('intro_articles'),
    ]

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('link'),
        FieldPanel('intro', classname="full"),
        FieldPanel('intro_articles', classname="full"),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ImageChooserPanel('intro_image'),
        ImageChooserPanel('feed_image'),
    ]

    # Export fields over the API
    api_fields = [
        APIField('link'),
        APIField('intro'),
        APIField('intro_image'),
        APIField('feed_image'),
        APIField('intro_articles'),
    ]

    # Update context to include only published posts, ordered by reverse-chron

    def get_context(self, request):
        context = super().get_context(request)
        articlepages = self.get_children().live().order_by('-first_published_at')
        context['articlepages'] = articlepages
        return context

class ArticlePageTag(TaggedItemBase):
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
    '''
    Adding a page type to display a list of tags
    '''

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        articlepages = ArticlePage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['articlepages'] = articlepages
        return context

class ArticlePage(Page):

    '''
    Articles pages handle both hand written articles and Wikidata query results.
    It uses StremField for the best flexibility.
    A StreamField block is generated for Wikidata queries results.
    '''

    # Database fields

    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', blocks.BlockQuoteBlock()),
        ('page', blocks.PageChooserBlock()),
        ('document', DocumentChooserBlock()),
        ('embed', EmbedBlock()),
        ('wikidata_query', WdQueryBlock()),
    ])
    
    date = models.DateField("Post date")
    last_edit_date = models.DateField(auto_now=True)

    intro_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    categories = ParentalManyToManyField('home.ArticleCategory', blank=True)

    tags = ClusterTaggableManager(through=ArticlePageTag, blank=True)


    # Search index configuration

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.FilterField('date'),
        index.FilterField('last_edit_date'),
    ]


    # Editor panels configuration

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ], heading="Article information"),
        StreamFieldPanel('body', classname="full"),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ImageChooserPanel('feed_image'),
        ImageChooserPanel('intro_image'),
    ]

    # Export fields over the API
    api_fields = [
        APIField('body'),
        APIField('date'),
        APIField('last_edit_date'),
        APIField('intro_image'),
        APIField('feed_image'),
        APIField('categories'),
        APIField('tags'),
    ]

class WikidataClass(Page):

    '''
    This type of page display a table with :
       - Items as rows
       - Featured Pids as columns
    It is also used to store the featured Pids per class for ItemPages.
    '''

    # Database fields

    class_Qid = models.CharField(max_length=255)
    featured_Pids = ArrayField(
            models.CharField(max_length=255, blank=True)
        )

    intro_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    ) 

    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )  

    # Search index configuration

    search_fields = Page.search_fields + [
        index.SearchField('class_Qid'),
        index.SearchField('featured_Pids'),
    ]

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('class_Qid'),
        FieldPanel('featured_Pids'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ImageChooserPanel('feed_image'),
        ImageChooserPanel('intro_image'),
    ]

    # Export fields over the API
    api_fields = [
        APIField('class_Qid'),
        APIField('featured_Pids'),
        APIField('intro_image'),
        APIField('feed_image'),
    ]


## Categories

class ArticleCategory(Page):

    '''
    Articles' categories.
    Used for a limited set of sitewide categories.
    '''

    # Database fields

    ## Icon for articles and menue
    icon_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    ## Image displayed in the feed
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )  

    ## Full width intro image
    intro_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    ## Intro message printed over the image
    intro = RichTextField(blank=True)

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    promote_panels = [
        ImageChooserPanel('icon_image'),
        ImageChooserPanel('feed_image'),
        ImageChooserPanel('intro_image'),
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
    ]

    # Export fields over the API
    api_fields = [
        APIField('icon_image'),
        APIField('feed_image'),
        APIField('intro_image'),
        APIField('intro'),
    ]

    # Meta

    class Meta:
        verbose_name_plural = 'Article categories'

