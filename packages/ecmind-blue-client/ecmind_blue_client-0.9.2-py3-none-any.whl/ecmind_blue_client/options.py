"""
Options object
"""

from typing import Optional

# pylint: skip-file


class Options:
    """
    `dms.XmlImport options`
    """

    def __init__(
        self,
        APPENDFILESTOFRONT: Optional[bool] = None,
        ARCHIVABLE: Optional[bool] = None,
        ARCHIVEIMMEDIATELY: Optional[bool] = None,
        ARCHIVEIMMEDIATELYOBJDEF: Optional[bool] = None,
        CHECKACCESS: Optional[bool] = None,
        CHECKCATALOGUE: Optional[bool] = None,
        CHECKEXISTENCE: Optional[bool] = None,
        CHECKKEYFIELDS: Optional[bool] = None,
        CHECKOBLIGATION: Optional[bool] = None,
        CHECKPOSITION: Optional[bool] = None,
        CHECKREADONLY: Optional[bool] = None,
        DELETECASCADING: Optional[bool] = None,
        COPYCASCADING: Optional[bool] = None,
        FULLTEXTFILEATTACHED: Optional[bool] = None,
        HARDDELETE: Optional[bool] = None,
        INITFIELDS: Optional[bool] = None,
        INUSERTRAY: Optional[bool] = None,
        INWFTRAY: Optional[bool] = None,
        REPLACEFILES: Optional[bool] = None,
        REPLACEMULTIFIELDS: Optional[bool] = None,
        REPLACEREMARKS: Optional[bool] = None,
        REPLACETABLEFIELDS: Optional[bool] = None,
        TRUNCATEVALUES: Optional[bool] = None,
        TYPELESS: Optional[bool] = None,
        UPDATEALLFIELDS: Optional[bool] = None,
        VARIANTSAMELEVEL: Optional[bool] = None,
        VARIANTSETACTIVE: Optional[bool] = None,
        VARIANTTRANSFERRETENTION: Optional[bool] = None,
        LINKDOCUMENT: Optional[bool] = None,
        WFTOUSERTRAY: Optional[bool] = None,
        KEEPLINKWHENEXISTS: Optional[bool] = None,
        DELETEVARIANTMODE: Optional[bool] = None,
        COPYINDEXONLY: Optional[bool] = None,
        COPYCREATEHISTORY: Optional[bool] = None,
    ):
        self.APPENDFILESTOFRONT = APPENDFILESTOFRONT
        self.ARCHIVABLE = ARCHIVABLE
        self.ARCHIVEIMMEDIATELY = ARCHIVEIMMEDIATELY
        self.ARCHIVEIMMEDIATELYOBJDEF = ARCHIVEIMMEDIATELYOBJDEF
        self.CHECKACCESS = CHECKACCESS
        self.CHECKCATALOGUE = CHECKCATALOGUE
        self.CHECKEXISTENCE = CHECKEXISTENCE
        self.CHECKKEYFIELDS = CHECKKEYFIELDS
        self.CHECKOBLIGATION = CHECKOBLIGATION
        self.CHECKPOSITION = CHECKPOSITION
        self.CHECKREADONLY = CHECKREADONLY
        self.DELETECASCADING = DELETECASCADING
        self.COPYCASCADING = COPYCASCADING
        self.FULLTEXTFILEATTACHED = FULLTEXTFILEATTACHED
        self.HARDDELETE = HARDDELETE
        self.INITFIELDS = INITFIELDS
        self.INUSERTRAY = INUSERTRAY
        self.INWFTRAY = INWFTRAY
        self.REPLACEFILES = REPLACEFILES
        self.REPLACEMULTIFIELDS = REPLACEMULTIFIELDS
        self.REPLACEREMARKS = REPLACEREMARKS
        self.REPLACETABLEFIELDS = REPLACETABLEFIELDS
        self.TRUNCATEVALUES = TRUNCATEVALUES
        self.TYPELESS = TYPELESS
        self.UPDATEALLFIELDS = UPDATEALLFIELDS
        self.VARIANTSAMELEVEL = VARIANTSAMELEVEL
        self.VARIANTSETACTIVE = VARIANTSETACTIVE
        self.VARIANTTRANSFERRETENTION = VARIANTTRANSFERRETENTION
        self.LINKDOCUMENT = LINKDOCUMENT
        self.WFTOUSERTRAY = WFTOUSERTRAY
        self.KEEPLINKWHENEXISTS = KEEPLINKWHENEXISTS
        self.DELETEVARIANTMODE = DELETEVARIANTMODE
        self.COPYINDEXONLY = COPYINDEXONLY
        self.COPYCREATEHISTORY = COPYCREATEHISTORY
        return

    def __str__(self):
        result = ""
        if self.APPENDFILESTOFRONT != None:
            result += "APPENDFILESTOFRONT=" + ("1" if self.APPENDFILESTOFRONT else "0") + ";"
        if self.ARCHIVABLE != None:
            result += "ARCHIVABLE=" + ("1" if self.ARCHIVABLE else "0") + ";"
        if self.ARCHIVEIMMEDIATELY != None:
            result += "ARCHIVEIMMEDIATELY=" + ("1" if self.ARCHIVEIMMEDIATELY else "0") + ";"
        if self.ARCHIVEIMMEDIATELYOBJDEF != None:
            result += "ARCHIVEIMMEDIATELYOBJDEF=" + ("1" if self.ARCHIVEIMMEDIATELYOBJDEF else "0") + ";"
        if self.CHECKACCESS != None:
            result += "CHECKACCESS=" + ("1" if self.CHECKACCESS else "0") + ";"
        if self.CHECKCATALOGUE != None:
            result += "CHECKCATALOGUE=" + ("1" if self.CHECKCATALOGUE else "0") + ";"
        if self.CHECKEXISTENCE != None:
            result += "CHECKEXISTENCE=" + ("1" if self.CHECKEXISTENCE else "0") + ";"
        if self.CHECKKEYFIELDS != None:
            result += "CHECKKEYFIELDS=" + ("1" if self.CHECKKEYFIELDS else "0") + ";"
        if self.CHECKOBLIGATION != None:
            result += "CHECKOBLIGATION=" + ("1" if self.CHECKOBLIGATION else "0") + ";"
        if self.CHECKPOSITION != None:
            result += "CHECKPOSITION=" + ("1" if self.CHECKPOSITION else "0") + ";"
        if self.CHECKREADONLY != None:
            result += "CHECKREADONLY=" + ("1" if self.CHECKREADONLY else "0") + ";"
        if self.DELETECASCADING != None:
            result += "DELETECASCADING=" + ("1" if self.DELETECASCADING else "0") + ";"
        if self.COPYCASCADING != None:
            result += "COPYCASCADING=" + ("1" if self.COPYCASCADING else "0") + ";"
        if self.FULLTEXTFILEATTACHED != None:
            result += "FULLTEXTFILEATTACHED=" + ("1" if self.FULLTEXTFILEATTACHED else "0") + ";"
        if self.HARDDELETE != None:
            result += "HARDDELETE=" + ("1" if self.HARDDELETE else "0") + ";"
        if self.INITFIELDS != None:
            result += "INITFIELDS=" + ("1" if self.INITFIELDS else "0") + ";"
        if self.INUSERTRAY != None:
            result += "INUSERTRAY=" + ("1" if self.INUSERTRAY else "0") + ";"
        if self.INWFTRAY != None:
            result += "INWFTRAY=" + ("1" if self.INWFTRAY else "0") + ";"
        if self.REPLACEFILES != None:
            result += "REPLACEFILES=" + ("1" if self.REPLACEFILES else "0") + ";"
        if self.REPLACEMULTIFIELDS != None:
            result += "REPLACEMULTIFIELDS=" + ("1" if self.REPLACEMULTIFIELDS else "0") + ";"
        if self.REPLACEREMARKS != None:
            result += "REPLACEREMARKS=" + ("1" if self.REPLACEREMARKS else "0") + ";"
        if self.REPLACETABLEFIELDS != None:
            result += "REPLACETABLEFIELDS=" + ("1" if self.REPLACETABLEFIELDS else "0") + ";"
        if self.TRUNCATEVALUES != None:
            result += "TRUNCATEVALUES=" + ("1" if self.TRUNCATEVALUES else "0") + ";"
        if self.TYPELESS != None:
            result += "TYPELESS=" + ("1" if self.TYPELESS else "0") + ";"
        if self.UPDATEALLFIELDS != None:
            result += "UPDATEALLFIELDS=" + ("1" if self.UPDATEALLFIELDS else "0") + ";"
        if self.VARIANTSAMELEVEL != None:
            result += "VARIANTSAMELEVEL=" + ("1" if self.VARIANTSAMELEVEL else "0") + ";"
        if self.VARIANTSETACTIVE != None:
            result += "VARIANTSETACTIVE=" + ("1" if self.VARIANTSETACTIVE else "0") + ";"
        if self.VARIANTTRANSFERRETENTION != None:
            result += "VARIANTTRANSFERRETENTION=" + ("1" if self.VARIANTTRANSFERRETENTION else "0") + ";"
        if self.LINKDOCUMENT != None:
            result += "LINKDOCUMENT=" + ("1" if self.LINKDOCUMENT else "0") + ";"
        if self.WFTOUSERTRAY != None:
            result += "WFTOUSERTRAY=" + ("1" if self.WFTOUSERTRAY else "0") + ";"
        if self.KEEPLINKWHENEXISTS != None:
            result += "KEEPLINKWHENEXISTS=" + ("1" if self.KEEPLINKWHENEXISTS else "0") + ";"
        if self.DELETEVARIANTMODE != None:
            result += "DELETEVARIANTMODE=" + ("1" if self.DELETEVARIANTMODE else "0") + ";"
        if self.COPYINDEXONLY != None:
            result += "COPYINDEXONLY=" + ("1" if self.COPYINDEXONLY else "0") + ";"
        if self.COPYCREATEHISTORY != None:
            result += "COPYCREATEHISTORY=" + ("1" if self.COPYCREATEHISTORY else "0") + ";"

        return result.rstrip(";")

    __repr__ = __str__
