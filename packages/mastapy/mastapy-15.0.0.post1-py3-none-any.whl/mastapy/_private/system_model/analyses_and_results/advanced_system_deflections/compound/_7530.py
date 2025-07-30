"""AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
    _7562,
)

_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound",
    "AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2892
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
        _7392,
    )
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
        _7551,
        _7571,
        _7573,
        _7612,
        _7626,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7878,
        _7882,
    )

    Self = TypeVar(
        "Self",
        bound="AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection",
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection._Cast_AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = (
    "AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection",
)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection:
    """Special nested class for casting AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection to subclasses."""

    __parent__: (
        "AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection"
    )

    @property
    def connection_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7562.ConnectionCompoundAdvancedSystemDeflection":
        return self.__parent__._cast(_7562.ConnectionCompoundAdvancedSystemDeflection)

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7878.ConnectionCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7878,
        )

        return self.__parent__._cast(_7878.ConnectionCompoundAnalysis)

    @property
    def design_entity_compound_analysis(
        self: "CastSelf",
    ) -> "_7882.DesignEntityCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7882,
        )

        return self.__parent__._cast(_7882.DesignEntityCompoundAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2892.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2892

        return self.__parent__._cast(_2892.DesignEntityAnalysis)

    @property
    def coaxial_connection_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7551.CoaxialConnectionCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7551,
        )

        return self.__parent__._cast(
            _7551.CoaxialConnectionCompoundAdvancedSystemDeflection
        )

    @property
    def cycloidal_disc_central_bearing_connection_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7571.CycloidalDiscCentralBearingConnectionCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7571,
        )

        return self.__parent__._cast(
            _7571.CycloidalDiscCentralBearingConnectionCompoundAdvancedSystemDeflection
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> (
        "_7573.CycloidalDiscPlanetaryBearingConnectionCompoundAdvancedSystemDeflection"
    ):
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7573,
        )

        return self.__parent__._cast(
            _7573.CycloidalDiscPlanetaryBearingConnectionCompoundAdvancedSystemDeflection
        )

    @property
    def planetary_connection_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7612.PlanetaryConnectionCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7612,
        )

        return self.__parent__._cast(
            _7612.PlanetaryConnectionCompoundAdvancedSystemDeflection
        )

    @property
    def shaft_to_mountable_component_connection_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7626.ShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
            _7626,
        )

        return self.__parent__._cast(
            _7626.ShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection
        )

    @property
    def abstract_shaft_to_mountable_component_connection_compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection":
        return self.__parent__

    def __getattr__(self: "CastSelf", name: str) -> "Any":
        try:
            return self.__getattribute__(name)
        except AttributeError:
            class_name = utility.camel(name)
            raise CastException(
                f'Detected an invalid cast. Cannot cast to type "{class_name}"'
            ) from None


@extended_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection(
    _7562.ConnectionCompoundAdvancedSystemDeflection
):
    """AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_ADVANCED_SYSTEM_DEFLECTION
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_7392.AbstractShaftToMountableComponentConnectionAdvancedSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.advanced_system_deflections.AbstractShaftToMountableComponentConnectionAdvancedSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_7392.AbstractShaftToMountableComponentConnectionAdvancedSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.advanced_system_deflections.AbstractShaftToMountableComponentConnectionAdvancedSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection
        """
        return _Cast_AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection(
            self
        )
