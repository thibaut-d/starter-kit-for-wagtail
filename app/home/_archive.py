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

    # Database fields

    ## The user click on a link like https://explore.ac/item?qid="Q123"
    ## It renders the "default" item page
    ## But if there is a page with the Qid from the query string qid="Q123" :
    ##     the notes will be added to the page
    ## if there is no "qid" query string in the url, the qid from this field is rendered
    item_Qid = models.CharField(max_length=255)

    ## This lets the site contributors add notes to some items internally
    notes = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', BlockQuoteBlock()),
        ('page', PageChooserBlock()),
        ('document', DocumentChooserBlock()),
        ('embed', EmbedBlock()),
        ('wikidata_query', WdQueryBlock()),
    ])

    ## The image is used for the index of pages that have notes
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    ## This override the Pids gathered from WdClass for this item specifically
    featured_Pids = ArrayField(
            models.CharField(max_length=255, blank=True)
        )

    # Search index configuration

    search_fields = Page.search_fields + [
        index.SearchField('item_Qid'),
        index.SearchField('notes'),
        index.SearchField('featured_Pids'),
    ]

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('item_Qid'),
        FieldPanel('notes', classname="full"),
        FieldPanel('featured_Pids'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ImageChooserPanel('feed_image'),
    ]

class ItemsIndexPage(Page):
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