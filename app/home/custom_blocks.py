from wagtail.core import blocks

class WdQueryBlock(blocks.StructBlock):
    query_intro = blocks.RichTextBlock(required=False)
    query_sparql = blocks.TextBlock(help_text='Past here a Wikidata SPARQL request. You can test it before at query.wikidata.org.')

    class Meta:
        icon = 'database'
        template = 'home/templates/blocks/wd_query_block.html'