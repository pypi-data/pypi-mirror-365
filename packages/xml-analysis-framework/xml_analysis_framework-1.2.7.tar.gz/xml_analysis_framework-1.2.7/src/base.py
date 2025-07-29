#!/usr/bin/env python3
"""
Base Interfaces for Analysis Frameworks

This module provides the foundational interfaces and data structures that can be
copied and adapted by other analysis frameworks (document, data, media).

These interfaces establish a consistent pattern across all frameworks while
allowing each to evolve independently without external dependencies.
"""

# ET import removed - not used in this handler
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any


@dataclass
class DocumentTypeInfo:
    """Information about a detected document type"""

    type_name: str
    confidence: float  # 0.0 to 1.0
    version: Optional[str] = None
    schema_uri: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpecializedAnalysis:
    """Results from specialized handler analysis"""

    document_type: str
    key_findings: Dict[str, Any]
    recommendations: List[str]
    data_inventory: Dict[str, int]  # What types of data found and counts
    ai_use_cases: List[str]  # Potential AI/ML applications
    structured_data: Dict[str, Any]  # Extracted structured data
    quality_metrics: Dict[str, float]  # Data quality indicators


class FileHandler(ABC):
    """
    Abstract base class for file document handlers

    This interface can be adapted by other frameworks:
    - XMLHandler: Uses Element for XML-specific processing
    - DocumentHandler: Uses file_path for office documents
    - DataHandler: Uses file_path for structured data
    - MediaHandler: Uses file_path for media files
    """

    @abstractmethod
    def can_handle(self, file_path: str, **kwargs) -> Tuple[bool, float]:
        """
        Check if this handler can process the file

        Args:
            file_path: Path to the file to analyze
            **kwargs: Framework-specific additional parameters
                     (e.g., root: Element for XML, mime_type for others)

        Returns:
            (can_handle: bool, confidence: float)
        """
        pass

    @abstractmethod
    def detect_type(self, file_path: str, **kwargs) -> DocumentTypeInfo:
        """
        Detect and classify the document type

        Args:
            file_path: Path to the file to analyze
            **kwargs: Framework-specific additional parameters

        Returns:
            DocumentTypeInfo with classification details
        """
        pass

    @abstractmethod
    def analyze(self, file_path: str, **kwargs) -> SpecializedAnalysis:
        """
        Perform specialized analysis of the document

        Args:
            file_path: Path to the file to analyze
            **kwargs: Framework-specific additional parameters

        Returns:
            SpecializedAnalysis with comprehensive insights
        """
        pass

    @abstractmethod
    def extract_key_data(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Extract key structured data from the document

        Args:
            file_path: Path to the file to analyze
            **kwargs: Framework-specific additional parameters

        Returns:
            Dictionary of extracted key data
        """
        pass


class XMLHandler(FileHandler):
    """
    XML-specific handler interface

    Extends FileHandler with XML-specific method signatures.
    Other frameworks would create their own specific handler classes:
    - DocumentHandler(FileHandler) for office documents
    - DataHandler(FileHandler) for structured data
    - MediaHandler(FileHandler) for media files
    """

    def can_handle(self, file_path: str, **kwargs) -> Tuple[bool, float]:
        """
        Check if this handler can process the XML document

        Args:
            file_path: Path to the file (not used in XML analysis)
            **kwargs: Must include 'root' (Element) and 'namespaces' (Dict[str, str])

        Returns:
            (can_handle: bool, confidence: float)
        """
        root = kwargs.get("root")
        namespaces = kwargs.get("namespaces", {})
        if root is None:
            return False, 0.0
        return self.can_handle_xml(root, namespaces)

    def detect_type(self, file_path: str, **kwargs) -> DocumentTypeInfo:
        """
        Detect and classify the XML document type

        Args:
            file_path: Path to the file (not used in XML analysis)
            **kwargs: Must include 'root' (Element) and 'namespaces' (Dict[str, str])

        Returns:
            DocumentTypeInfo with classification details
        """
        root = kwargs.get("root")
        namespaces = kwargs.get("namespaces", {})
        if root is None:
            return DocumentTypeInfo(type_name="Unknown", confidence=0.0)
        return self.detect_xml_type(root, namespaces)

    def analyze(self, file_path: str, **kwargs) -> SpecializedAnalysis:
        """
        Perform specialized analysis of the XML document

        Args:
            file_path: Path to the original file
            **kwargs: Must include 'root' (Element)

        Returns:
            SpecializedAnalysis with comprehensive insights
        """
        root = kwargs.get("root")
        if root is None:
            return SpecializedAnalysis(
                document_type="Unknown",
                key_findings={},
                recommendations=[],
                data_inventory={},
                ai_use_cases=[],
                structured_data={},
                quality_metrics={},
            )
        return self.analyze_xml(root, file_path)

    def extract_key_data(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Extract key structured data from the XML document

        Args:
            file_path: Path to the file (not used in XML analysis)
            **kwargs: Must include 'root' (Element)

        Returns:
            Dictionary of extracted key data
        """
        root = kwargs.get("root")
        if root is None:
            return {}
        return self.extract_xml_key_data(root)

    # XML-specific abstract methods that subclasses implement
    @abstractmethod
    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        """XML-specific can_handle implementation"""
        pass

    @abstractmethod
    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        """XML-specific detect_type implementation"""
        pass

    @abstractmethod
    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        """XML-specific analyze implementation"""
        pass

    @abstractmethod
    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        """XML-specific extract_key_data implementation"""
        pass


# Framework Pattern Examples for Copy-Paste to Other Frameworks:

"""
# Document Analysis Framework would use:
class DocumentHandler(FileHandler):
    def can_handle(self, file_path: str, mime_type: str) -> Tuple[bool, float]:
        pass

    def detect_type(self, file_path: str, mime_type: str) -> DocumentTypeInfo:
        pass

    def analyze(self, file_path: str) -> SpecializedAnalysis:
        pass

    def extract_key_data(self, file_path: str) -> Dict[str, Any]:
        pass

# Data Analysis Framework would use:
class DataHandler(FileHandler):
    def can_handle(self, file_path: str, sample_data: Any = None) -> Tuple[bool, float]:
        pass

    def detect_type(self, file_path: str, sample_data: Any = None) -> DocumentTypeInfo:
        pass

    def analyze(self, file_path: str) -> SpecializedAnalysis:
        pass

    def extract_key_data(self, file_path: str) -> Dict[str, Any]:
        pass

# Media Analysis Framework would use:
class MediaHandler(FileHandler):
    def can_handle(self, file_path: str, media_info: Dict = None) -> Tuple[bool, float]:
        pass

    def detect_type(self, file_path: str, media_info: Dict = None) -> DocumentTypeInfo:
        pass

    def analyze(self, file_path: str) -> SpecializedAnalysis:
        pass

    def extract_key_data(self, file_path: str) -> Dict[str, Any]:
        pass
"""
