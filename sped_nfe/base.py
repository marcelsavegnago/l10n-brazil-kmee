from pysped.nfe import ProcessadorNFe as ProcNFe
from pysped.nfe.danfe import DANFE as Danfe
from pysped.nfe.leiaute import ProtNFe_310 as ProtNFe
from pysped.nfe.leiaute.consrecinfe_110 import InfProt as Inf_prot
from pysped.xml_sped import TagDataHoraUTC as dhUTC
import pysped
import pytz


class TagDataHoraUTC(dhUTC):

    def __init__(self, **kwargs):
        super(TagDataHoraUTC, self).__init__(**kwargs)

    @property
    def formato_danfe(self):
        valor = super(TagDataHoraUTC, self).formato_danfe()
        return valor


class InfProt(Inf_prot):
    def __init__(self):
        super(InfProt, self).__init__()
        self.dhRecbto = TagDataHoraUTC(nome='dhRecbto', codigo='PR08',
                                       raiz='//infProt')


class ProtNFe_310(ProtNFe):
    def __init__(self):
        super(ProtNFe_310, self).__init__()
        self.infProt = InfProt()


class DANFE(Danfe):
    def __init__(self):
        super(DANFE, self).__init__()
        self.protNFe = ProtNFe_310()


class ProcessadorNFe(ProcNFe):
    def __init__(self):
        super(ProcessadorNFe, self).__init__()
        self.danfe = DANFE()

pysped.xml_sped.TagDataHoraUTC = TagDataHoraUTC
