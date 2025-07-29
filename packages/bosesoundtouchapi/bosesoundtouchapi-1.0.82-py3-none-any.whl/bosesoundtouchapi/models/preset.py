# external package imports.
import time
from xml.etree.ElementTree import Element, tostring

# our package imports.
from ..bstutils import export, _xmlGetAttrInt
from ..soundtouchmodelrequest import SoundTouchModelRequest
from ..soundtouchsources import SoundTouchSources
from .contentitem import ContentItem

@export
class Preset(SoundTouchModelRequest):
    """
    SoundTouch device Preset configuration object.
       
    This class contains the attributes and sub-items that represent a
    single preset configuration of the device.
    """

    def __init__(self, presetId:int = None, createdOn:int = None, updatedOn: int = None, source: str = None, typeValue: str = None, 
                 location: str = None, sourceAccount: str = None, isPresetable: bool = None, name: str = None, containerArt:str = None,
                 root : Element = None
                 ) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            presetId (int):
                Preset identifier; valid values are 1 thru 6.
            createdOn (int):
                Date time (in epoch format) the preset was created; 
                the current epoch time is used if the value is zero or None.
            updatedOn (int):
                Date time (in epoch format) the preset was last updated;
                the current epoch time is used if the value is zero or None.
            source (str):
                ContentItem node source value.
            typeValue (str):
                ContentItem node type value.
            location (str):
                ContentItem node location value.
            sourceAccount (str):
                ContentItem node sourceAccount value.
            isPresetable (bool):
                ContentItem node isPresetable value.
            name (str):
                ContentItem node itemName value.
            containerArt (str)
                ContentItem node containerArt value.
            root (Element):
                xmltree Element item to load arguments from.  
                If specified, then other passed arguments are ignored.
        """
        self._PresetId:int = 0
        self._CreatedOn:int = 0
        self._UpdatedOn:int = 0
        self._ContentItem:ContentItem = ContentItem()

        # helper properties (non-xml).
        self._SourceTitle:str = None

        if (root is None):
            
            if isinstance(source, SoundTouchSources):
                source = str(source.value)

            if isinstance(presetId, int):
                self._PresetId = int(presetId) 
            if isinstance(createdOn, int):
                self._CreatedOn = int(createdOn)
            if isinstance(updatedOn, int):
                self._UpdatedOn = int(updatedOn)

            self._ContentItem._Source = source
            self._ContentItem._TypeValue = typeValue
            self._ContentItem._Location = location
            self._ContentItem._SourceAccount = sourceAccount
            self._ContentItem._IsPresetable = isPresetable
            self._ContentItem._Name = name
            self._ContentItem._ContainerArt = containerArt
        
            # use current epoch time if created / updated on are not set.
            epoch_time:int = int(time.time())
            if createdOn == 0:
                self._CreatedOn = epoch_time
            if updatedOn == 0:
                self._UpdatedOn = epoch_time

        else:

            self._CreatedOn = _xmlGetAttrInt(root, 'createdOn')
            self._PresetId = _xmlGetAttrInt(root, 'id')
            self._UpdatedOn = _xmlGetAttrInt(root, 'updatedOn')

            rootCI:Element = root.find('ContentItem')
            if rootCI is not None:
                self._ContentItem:ContentItem = ContentItem(root=rootCI)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.PresetId == other.PresetId
        except Exception as ex:
            if (isinstance(self, Preset )) and (isinstance(other, Preset )):
                return self.PresetId == other.PresetId
            return False

    def __lt__(self, other):
        try:
            return self.PresetId < other.PresetId
        except Exception as ex:
            if (isinstance(self, Preset )) and (isinstance(other, Preset )):
                return self.PresetId < other.PresetId
            return False


    @property
    def ContentItem(self) -> ContentItem:
        """ ContentItem value. """
        return self._ContentItem


    @property
    def ContainerArt(self) -> str:
        """ Content item's container art url. """
        if self._ContentItem is None:
            return None
        return self._ContentItem._ContainerArt


    @property
    def CreatedOn(self) -> int:
        """ 
        Date and time (in epoch format) of when the preset was created. 
        
        It seems that on some devices (ST-10) the SoundTouch WebServices API only returns 
        this attribute for the LAST preset that was stored; the value will not be present 
        for any other presets.  Other devices (ST-300) return this attribute on all items.
        """
        return self._CreatedOn

    @CreatedOn.setter
    def CreatedOn(self, value:int):
        """ 
        Sets the CreatedOn property value.
        """
        if isinstance(value, int) and value > -1:
            self._CreatedOn = value


    @property
    def IsPresetable(self) -> str:
        """ Returns True if the content item can be saved as a Preset; otherwise, False. """
        if self._ContentItem is None:
            return None
        return self._ContentItem._IsPresetable


    @property
    def Location(self) -> str:
        """ If present, the content item's direct link to the media. """
        if self._ContentItem is None:
            return None
        return self._ContentItem._Location


    @property
    def Name(self) -> str:
        """ Content item's name. """
        if self._ContentItem is None:
            return None
        return self._ContentItem._Name


    @property
    def PresetId(self) -> int:
        """ Preset identifier (1 - 6). """
        return self._PresetId


    @property
    def Source(self) -> str:
        """ 
        Content item source type. 
        
        This value is defined at `bosesoundtouchapi.soundtouchsources.SoundTouchSources`. 
        """
        if self._ContentItem is None:
            return None
        return self._ContentItem._Source


    @property
    def SourceAccount(self) -> str:
        """ The account associated with the Source. """
        if self._ContentItem is None:
            return None
        return self._ContentItem._SourceAccount


    @property
    def SourceTitle(self) -> str:
        """ 
        The source title of media content (e.g. "Tunein", "Airplay", "NAS Music Server", etc). 
        
        This property is not part of the returned xml of the configuration, but is set after
        a call to `SoundTouchClient.GetPresetList(resolveSourceTitles=True)' so that source
        titles can be displayed by user-interfaces.
        """
        return self._SourceTitle

    @SourceTitle.setter
    def SourceTitle(self, value:str):
        """ 
        Sets the SourceTitle property value.
        """
        self._SourceTitle = value


    @property
    def TypeValue(self) -> str:
        """ Specifies the type of the content item. """
        if self._ContentItem is None:
            return None
        return self._ContentItem._TypeValue


    @property
    def UpdatedOn(self) -> int:
        """ 
        Date and time (in epoch format) of when the preset was last updated. 
        
        It seems that on some devices (ST-10) the SoundTouch WebServices API only returns 
        this attribute for the LAST preset that was stored; the value will not be present 
        for any other presets.  Other devices (ST-300) return this attribute on all items.
        """
        return self._UpdatedOn

    @UpdatedOn.setter
    def UpdatedOn(self, value:int):
        """ 
        Sets the UpdatedOn property value.
        """
        if isinstance(value, int) and value > -1:
            self._UpdatedOn = value


    def ToDictionary(self, encoding:str='utf-8') -> dict:
        """
        Returns a dictionary representation of the class.
        
        Args:
            encoding (str):
                encode type (e.g. 'utf-8', 'unicode', etc).  
                Default is 'utf-8'.
        """
        if encoding is None:
            encoding = 'utf-8'
            
        contentItem:dict = {}
        if self._ContentItem is not None:
            contentItem = self._ContentItem.ToDictionary(encoding)
        
        result:dict = {}
        
        if self._PresetId is not None: 
            result['PresetId'] = self._PresetId
        if self._CreatedOn is not None: 
            result['CreatedOn'] = self._CreatedOn
        if self._UpdatedOn is not None: 
            result['UpdatedOn'] = self._UpdatedOn
        if self._SourceTitle is not None: 
            result['SourceTitle'] = self._SourceTitle
        result['ContentItem'] = contentItem

        return result
        

    def ToElement(self, isRequestBody:bool=False) -> Element:
        """ 
        Overridden.  
        Returns an xmltree Element node representation of the class. 

        Args:
            isRequestBody (bool):
                True if the element should only return attributes needed for a POST
                request body; otherwise, False to return all attributes.
        """
        elm = Element('preset')
        if self._PresetId is not None and self._PresetId > 0: elm.set('id', str(self._PresetId))
        if self._CreatedOn is not None and self._CreatedOn > 0: elm.set('createdOn', str(self._CreatedOn))
        if self._UpdatedOn is not None and self._UpdatedOn > 0: elm.set('updatedOn', str(self._UpdatedOn))
        
        if self._ContentItem is not None:
            elmNode = self._ContentItem.ToElement()
            elm.append(elmNode)

        if isRequestBody == False:
            if self._SourceTitle is not None and len(self._SourceTitle) > 0: elm.set('SourceTitle', str(self._SourceTitle))
            
        return elm

        
    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Preset:'
        msg = '%s Id="%s"' % (msg, str(self._PresetId))
        if self._ContentItem is not None: msg = '%s %s' % (msg, str(self._ContentItem))
        msg = '%s CreatedOn="%s"' % (msg, str(self._CreatedOn))
        msg = '%s UpdatedOn="%s"' % (msg, str(self._UpdatedOn))
        if self._SourceTitle is not None: msg = '%s SourceTitle="%s"' % (msg, str(self._SourceTitle))
        return msg 


    def ToXmlString(self, encoding:str='utf-8') -> str:
        """ 
        Returns an xml string representation of the class. 
        
        Args:
            encoding (str):
                encode type (e.g. 'utf-8', 'unicode', etc).  
                Default is 'utf-8'.
        """
        if encoding is None:
            encoding = 'utf-8'
            
        elm:Element = self.ToElement(False)
        xml:str = tostring(elm, encoding=encoding)
        
        # always return a string, as some encodings return a byte array!
        if not isinstance(xml, str):
            xml = xml.decode(encoding=encoding)
        return xml
        