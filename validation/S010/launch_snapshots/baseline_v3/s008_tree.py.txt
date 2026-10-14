"""CAM-0009A: same necessary full constraints with totalizer counters."""
import sys
from pysat.card import CardEnc as OriginalCardEnc, EncType
import triangulation_cover
import s007_cover
import s008_cover


class TreeCardEnc:
    @staticmethod
    def atmost(*args, **kwargs):
        kwargs['encoding']=EncType.totalizer
        return OriginalCardEnc.atmost(*args,**kwargs)

    @staticmethod
    def atleast(*args, **kwargs):
        kwargs['encoding']=EncType.totalizer
        return OriginalCardEnc.atleast(*args,**kwargs)

    @staticmethod
    def equals(*args, **kwargs):
        kwargs['encoding']=EncType.totalizer
        return OriginalCardEnc.equals(*args,**kwargs)


# Dedicated process scope; neither previous generators nor running files are changed.
triangulation_cover.CardEnc=TreeCardEnc
s007_cover.CardEnc=TreeCardEnc


class TreeFullCover(s008_cover.FullCover):
    def __init__(self,edges,lex=False,short_links=False):
        super().__init__(edges,lex,short_links)
        self.static['s008_cardinality']='pysat-totalizer-v1'


if __name__=='__main__':
    s008_cover.FullCover=TreeFullCover
    s008_cover.main()
