"""KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
    _3162,
)

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH_COMPOUND_SYSTEM_DEFLECTION = (
    python_net_import(
        "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound",
        "KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection",
    )
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2892
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7878,
        _7882,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3015,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
        _3127,
        _3129,
        _3154,
        _3160,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2541

    Self = TypeVar(
        "Self",
        bound="KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection",
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection._Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection:
    """Special nested class for casting KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection to subclasses."""

    __parent__: "KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection"

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3162.KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection":
        return self.__parent__._cast(
            _3162.KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection
        )

    @property
    def conical_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3127.ConicalGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3127,
        )

        return self.__parent__._cast(_3127.ConicalGearMeshCompoundSystemDeflection)

    @property
    def gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3154.GearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3154,
        )

        return self.__parent__._cast(_3154.GearMeshCompoundSystemDeflection)

    @property
    def inter_mountable_component_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3160.InterMountableComponentConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3160,
        )

        return self.__parent__._cast(
            _3160.InterMountableComponentConnectionCompoundSystemDeflection
        )

    @property
    def connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3129.ConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3129,
        )

        return self.__parent__._cast(_3129.ConnectionCompoundSystemDeflection)

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
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection":
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
class KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection(
    _3162.KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection
):
    """KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH_COMPOUND_SYSTEM_DEFLECTION
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(
        self: "Self",
    ) -> "_2541.KlingelnbergCycloPalloidSpiralBevelGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidSpiralBevelGearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def connection_design(
        self: "Self",
    ) -> "_2541.KlingelnbergCycloPalloidSpiralBevelGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidSpiralBevelGearMesh

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
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_3015.KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection]

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
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_3015.KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection
        """
        return (
            _Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection(
                self
            )
        )
