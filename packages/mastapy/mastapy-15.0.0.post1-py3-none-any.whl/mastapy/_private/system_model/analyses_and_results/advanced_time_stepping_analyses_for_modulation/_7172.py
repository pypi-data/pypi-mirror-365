"""CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
    _7124,
)

_CYCLOIDAL_DISC_PLANETARY_BEARING_CONNECTION_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation",
    "CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2890, _2892, _2894
    from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
        _7161,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7877,
        _7880,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7726
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2978,
    )
    from mastapy._private.system_model.connections_and_sockets.cycloidal import _2559

    Self = TypeVar(
        "Self",
        bound="CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation",
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation._Cast_CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation",
    )


__docformat__ = "restructuredtext en"
__all__ = (
    "CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation",
)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation:
    """Special nested class for casting CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation to subclasses."""

    __parent__: "CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation"

    @property
    def abstract_shaft_to_mountable_component_connection_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7124.AbstractShaftToMountableComponentConnectionAdvancedTimeSteppingAnalysisForModulation":
        return self.__parent__._cast(
            _7124.AbstractShaftToMountableComponentConnectionAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def connection_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7161.ConnectionAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7161,
        )

        return self.__parent__._cast(
            _7161.ConnectionAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def connection_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7880.ConnectionStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7880,
        )

        return self.__parent__._cast(_7880.ConnectionStaticLoadAnalysisCase)

    @property
    def connection_analysis_case(self: "CastSelf") -> "_7877.ConnectionAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7877,
        )

        return self.__parent__._cast(_7877.ConnectionAnalysisCase)

    @property
    def connection_analysis(self: "CastSelf") -> "_2890.ConnectionAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2890

        return self.__parent__._cast(_2890.ConnectionAnalysis)

    @property
    def design_entity_single_context_analysis(
        self: "CastSelf",
    ) -> "_2894.DesignEntitySingleContextAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2894

        return self.__parent__._cast(_2894.DesignEntitySingleContextAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2892.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2892

        return self.__parent__._cast(_2892.DesignEntityAnalysis)

    @property
    def cycloidal_disc_planetary_bearing_connection_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation":
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
class CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation(
    _7124.AbstractShaftToMountableComponentConnectionAdvancedTimeSteppingAnalysisForModulation
):
    """CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _CYCLOIDAL_DISC_PLANETARY_BEARING_CONNECTION_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(
        self: "Self",
    ) -> "_2559.CycloidalDiscPlanetaryBearingConnection":
        """mastapy.system_model.connections_and_sockets.cycloidal.CycloidalDiscPlanetaryBearingConnection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def connection_load_case(
        self: "Self",
    ) -> "_7726.CycloidalDiscPlanetaryBearingConnectionLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.CycloidalDiscPlanetaryBearingConnectionLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def system_deflection_results(
        self: "Self",
    ) -> "_2978.CycloidalDiscPlanetaryBearingConnectionSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.CycloidalDiscPlanetaryBearingConnectionSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation":
        """Cast to another type.

        Returns:
            _Cast_CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation
        """
        return _Cast_CycloidalDiscPlanetaryBearingConnectionAdvancedTimeSteppingAnalysisForModulation(
            self
        )
