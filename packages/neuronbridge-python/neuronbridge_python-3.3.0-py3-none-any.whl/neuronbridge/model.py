from typing import List, Union, Optional, Any, Dict, Literal
from enum import Enum
from pydantic import BaseModel, Field, Extra
from typing_extensions import Annotated


class Gender(str, Enum):
    male = 'm'
    female = 'f'


class AnatomicalArea(BaseModel, extra=Extra.forbid):
    """
    Defines an anatomical areas of the fly brain that can be searched using NeuronBridge. All searches are specific to one area.
    """
    label: str = Field(title="Anatomical area label", description="Label used for the anatomical area in the UI.")
    alignmentSpace: str = Field(title="Alignment space", description="Alignment space to which this images in this area are registered.")


class LibraryConfig(BaseModel, extra=Extra.forbid):
    """
    Configuration for libraries used for custom searches.
    """
    name: str = Field(title="Library identifier", description="Library name or identifier")
    count: int = Field(title="Image count", description="Number of images available for search")
    publishedNamePrefix: Optional[str] = Field(title="Published name prefix", description="Optional value that when set, is used to prefix published names. This is currently used to identify EM data set", default=None)


class CustomSearchConfig(BaseModel, extra=Extra.forbid):
    """
    Configuration for the custom search on a data set.
    """
    searchFolder: str = Field(title="Search folder", description="Name of sub-folder on S3 to traverse when using custom search.")
    lmLibraries: List[LibraryConfig] = Field(title="List of LM libraries", description="List of LM libraries included in this data set.")
    emLibraries: List[LibraryConfig] = Field(title="List of EM libraries", description="List of EM libraries included in this data set.")


class DataStore(BaseModel, extra=Extra.forbid):
    """
    Configuration for a data store. This allows some flexibility for defining the S3 locations for various file types. 
    """
    label: str = Field(title="Data set label", description="Label used for the data set in the UI.")
    anatomicalArea: str = Field(title="Anatomical area name", description="Internal identifier for the anatomical area used for this data set. Can be used to look up additional details by matching to AnatomicalArea.value.")
    prefixes: Dict[str, str] = Field(title="Prefixes", description="Path prefixes for each file type in Files. If no prefix exists for a given file type, then the path should be treated as absolute.")
    customSearch: CustomSearchConfig = Field(title="Custom search", description="Custom search configuration for this data set.")


class DataConfig(BaseModel, extra=Extra.forbid):
    """
    Defines the data configuration for the NeuronBridge. 
    """
    anatomicalAreas: Dict[str, AnatomicalArea] = Field(title="Anatomical areas", description="Anatomical areas that can be searched.")
    stores: Dict[str, DataStore] = Field(title="Data stores", description="A data store provides access to imagery for a given subset of images.")


class Files(BaseModel, extra=Extra.forbid):
    """
    Files associated with a NeuronImage or Match. These are either absolute URLs (e.g. starting with a protocol like http://) or relative paths. For relative paths, the first component should be replaced with its corresponding base URL from the DataConfig.
    """
    store: str = Field(title="Data Store", description="Name of the DataStore that provides access to imagery for any relative paths in this object.")
    CDM: Optional[str] = Field(title="Color Depth MIP", description="The CDM of the image. This is for non-PPPM results only, for PPPM, see CDMBest/CDMBestThumbnail.", default=None)
    CDMThumbnail: Optional[str] = Field(title="Thumbnail of the CDM", description="The thumbnail sized version of the CDM, if available.", default=None)
    CDMInput: Optional[str] = Field(title="CDM input", description="CDM-only. The actual color depth image that was input. 'Matched CDM' in the NeuronBridge GUI.", default=None)
    CDMMatch: Optional[str] = Field(title="CDM match", description="CDM-only. The actual color depth image that was matched. 'Matched CDM' in the NeuronBridge GUI.", default=None)
    CDMBest: Optional[str] = Field(title="CDM of best-matching channel", description="PPPM-only. The CDM of best matching channel of the matching LM stack and called 'Best Channel CDM' in the NeuronBridge GUI.", default=None)
    CDMBestThumbnail: Optional[str] = Field(title="Thumbnail of the CDM of best-matching channel", description="PPPM-only. The thumbnail of the CDM of best matching channel of the matching LM stack and called 'Best Channel CDM Thumbnail' in the NeuronBridge GUI.", default=None)
    CDMSkel: Optional[str] = Field(title="CDM with EM overlay", description="PPPM-only. The CDM of the best matching channel with the matching LM segmentation fragments overlaid. 'LM - Best Channel CDM with EM overlay' in the NeuronBridge GUI.", default=None)
    SignalMip: Optional[str] = Field(title="All-channel MIP of the sample", description="PPPM-only. The full MIP of all channels of the matching sample. 'LM - Sample All-Channel MIP' in the NeuronBridge GUI.", default=None)
    SignalMipMasked: Optional[str] = Field(title="PPPM fragments", description="PPPM-only. LM signal content masked with the matching LM segmentation fragments. 'PPPM Mask' in the NeuronBridge GUI.", default=None)
    SignalMipMaskedSkel: Optional[str] = Field(title="PPPM fragments with EM overlay", description="PPPM-only. LM signal content masked with the matching LM segmentation fragments, overlaid with the EM skeleton. 'PPPM Mask with EM Overlay' in the NeuronBridge GUI.", default=None)
    Gal4Expression: Optional[str] = Field(title="CDM of full LM line expression", description="MCFO-only. A representative CDM image of the full expression of the line.", default=None)
    VisuallyLosslessStack: Optional[str] = Field(title="LM 3D image stack", description="LMImage-only. An H5J 3D image stack of all channels of the LM image.", default=None)
    AlignedBodySWC: Optional[str] = Field(title="EM body in SWC format", description="EMImage-only, A 3D SWC skeleton of the EM body in the alignment space.", default=None)
    AlignedBodyOBJ: Optional[str] = Field(title="EM body in OBJ format", description="EMImage-only. A 3D OBJ representation of the EM body in the alignment space.", default=None)
    CDSResults: Optional[str] = Field(title="Results of CDS matching on this image", description="A JSON file serializing Matches containing CDSMatch objects for the input image.", default=None)
    PPPMResults: Optional[str] = Field(title="Results of PPPM matching on this image", description="EMImage-only, a JSON file serializing Matches containing PPPMatch objects for the input image.", default=None)


class UploadedImage(BaseModel, extra=Extra.forbid):
    """
    An uploaded image containing neurons. 
    """
    filename: str = Field(title="Filename", description="Name of the uploaded file.")
    alignmentSpace: str = Field(title="Alignment space", description="Alignment space to which this image was registered.")
    anatomicalArea: str = Field(title="Anatomical area", description="Anatomical area represented in the image.")
    files: Files = Field(title="Files", description="Files associated with the image.")


class NeuronImage(BaseModel, extra=Extra.forbid):
    """
    A color depth image containing neurons. 
    """
    id: str = Field(title="Image identifier", description="The unique identifier for this image.")
    libraryName: str = Field(title="Library name", description="Name of the image library containing this image.")
    publishedName: str = Field(title="Published name", description="Published name for the contents of this image. This is not a unique identifier.")
    alignmentSpace: str = Field(title="Alignment space", description="Alignment space to which this image was registered.")
    anatomicalArea: str = Field(title="Anatomical area", description="Anatomical area represented in the image.")
    gender: Gender = Field(title="Gender", description="Gender of the sample imaged.")
    files: Files = Field(title="Files", description="Files associated with the image.")
    annotations: Optional[List[str]] = Field(title="List of additional annotations", description="Bag of words associated with this neuron", default=None)


class EMImage(NeuronImage, extra=Extra.forbid):
    """
    A color depth image containing a neuron body reconstructed from EM imagery.
    """
    type: Literal['EMImage'] = 'EMImage'
    neuronType: Optional[str] = Field(title="FlyEM Neuron type", description="Neuron type name from FlyEM's neuPrint", default=None)
    neuronInstance: Optional[str] = Field(title="FlyEM Neuron instance", description="Neuron instance name from FlyEM's neuPrint", default=None)


class LMImage(NeuronImage, extra=Extra.forbid):
    """
    A color depth image of a single channel of an LM image stack.
    """
    type: Literal['LMImage'] = 'LMImage'
    slideCode: str = Field(title="Slide code", description="Unique identifier for the sample that was imaged.")
    objective: str = Field(title="Objective", description="Magnification of the microscope objective used to imaged this image.")
    mountingProtocol: Optional[str] = Field(title="Mounting protocol", description="Description of the protocol used to mount the sample for imaging.", default=None)
    channel: Optional[int] = Field(title="Channel", description="Channel index within the full LM image stack. PPPM matches the entire stack and therefore this is blank.", default=None)


ConcreteNeuronImage = Annotated[Union[LMImage, EMImage], Field(discriminator="type")]


class ImageLookup(BaseModel, extra=Extra.forbid):
    """
    Top level collection returned by the image lookup API.
    """
    results: List[ConcreteNeuronImage] = Field(title="Results", description="List of images matching the query.")


class Match(BaseModel, extra=Extra.forbid):
    """
    Putative matching between two NeuronImages.
    """
    image: Union[LMImage, EMImage] = Field(title="Matched image", description="The NeuronImage that was matched.",discriminator="type")
    files: Files = Field(title="Files", description="Files associated with the match.")
    mirrored: bool = Field(title="Mirror flag", description="Indicates whether the target image was found within a mirrored version of the matching image.")


class PPPMatch(Match, extra=Extra.forbid):
    """
    A PPPMatch is a match generated by the PPPM algorithm between an EMImage and a LMImage.
    """
    type: Literal['PPPMatch'] = 'PPPMatch'
    pppmRank: float = Field(title="PPPM rank", description="Fractional rank reported by the PPPM algorithm. It's generally better to use the index of the image in the results.")
    pppmScore: int = Field(title="PPPM score", description="Match score reported by the PPPM algorithm.")


class CDSMatch(Match, extra=Extra.forbid):
    """
    A CDSMatch is a match generated by the CDS algorithm between an EMImage and a LMImage.
    """
    type: Literal['CDSMatch'] = 'CDSMatch'
    normalizedScore: float = Field(title="Normalized score", description="Match score reported by the matching algorithm")
    matchingPixels: int = Field(title="Matching pixels", description="Number of matching pixels reported by the CDS algorithm")


ConcreteMatch = Annotated[Union[CDSMatch, PPPMatch], Field(discriminator="type")]

class Matches(BaseModel, extra=Extra.forbid):
    """
    The results of a matching algorithm run.
    """
    inputImage: None
    results: List[ConcreteMatch] = Field(title="Results", description="List of other images matching the input image.")


class PrecomputedMatches(Matches, extra=Extra.forbid):
    """
    The results of a matching algorithm run on a NeuronImage.
    """
    inputImage: Union[LMImage, EMImage] = Field(title="Input image", description="Input image to the matching algorithm.",discriminator="type")



class CustomMatches(Matches, extra=Extra.forbid):
    """
    The results of a matching algorithm run on an UploadImage.
    """
    inputImage: UploadedImage = Field(title="Uploaded input image", description="Input image to the matching algorithm.")
