"""AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
    _7025,
)

_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_CRITICAL_SPEED_ANALYSIS = (
    python_net_import(
        "SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound",
        "AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis",
    )
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2892
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7878,
        _7882,
    )
    from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
        _6859,
    )
    from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
        _7014,
        _7034,
        _7036,
        _7075,
        _7089,
    )

    Self = TypeVar(
        "Self",
        bound="AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis",
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis._Cast_AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis:
    """Special nested class for casting AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis to subclasses."""

    __parent__: (
        "AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis"
    )

    @property
    def connection_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7025.ConnectionCompoundCriticalSpeedAnalysis":
        return self.__parent__._cast(_7025.ConnectionCompoundCriticalSpeedAnalysis)

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
    def coaxial_connection_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7014.CoaxialConnectionCompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
            _7014,
        )

        return self.__parent__._cast(
            _7014.CoaxialConnectionCompoundCriticalSpeedAnalysis
        )

    @property
    def cycloidal_disc_central_bearing_connection_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7034.CycloidalDiscCentralBearingConnectionCompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
            _7034,
        )

        return self.__parent__._cast(
            _7034.CycloidalDiscCentralBearingConnectionCompoundCriticalSpeedAnalysis
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7036.CycloidalDiscPlanetaryBearingConnectionCompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
            _7036,
        )

        return self.__parent__._cast(
            _7036.CycloidalDiscPlanetaryBearingConnectionCompoundCriticalSpeedAnalysis
        )

    @property
    def planetary_connection_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7075.PlanetaryConnectionCompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
            _7075,
        )

        return self.__parent__._cast(
            _7075.PlanetaryConnectionCompoundCriticalSpeedAnalysis
        )

    @property
    def shaft_to_mountable_component_connection_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7089.ShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
            _7089,
        )

        return self.__parent__._cast(
            _7089.ShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis
        )

    @property
    def abstract_shaft_to_mountable_component_connection_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis":
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
class AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis(
    _7025.ConnectionCompoundCriticalSpeedAnalysis
):
    """AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_CRITICAL_SPEED_ANALYSIS
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
    ) -> "List[_6859.AbstractShaftToMountableComponentConnectionCriticalSpeedAnalysis]":
        """List[mastapy.system_model.analyses_and_results.critical_speed_analyses.AbstractShaftToMountableComponentConnectionCriticalSpeedAnalysis]

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
    ) -> "List[_6859.AbstractShaftToMountableComponentConnectionCriticalSpeedAnalysis]":
        """List[mastapy.system_model.analyses_and_results.critical_speed_analyses.AbstractShaftToMountableComponentConnectionCriticalSpeedAnalysis]

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
    ) -> (
        "_Cast_AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis"
    ):
        """Cast to another type.

        Returns:
            _Cast_AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis
        """
        return _Cast_AbstractShaftToMountableComponentConnectionCompoundCriticalSpeedAnalysis(
            self
        )
