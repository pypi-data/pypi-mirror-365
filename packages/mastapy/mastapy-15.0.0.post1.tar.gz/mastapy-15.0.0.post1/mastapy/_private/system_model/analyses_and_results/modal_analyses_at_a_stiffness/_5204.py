"""KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
    _5198,
)

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH_MODAL_ANALYSIS_AT_A_STIFFNESS = (
    python_net_import(
        "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness",
        "KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness",
    )
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2890, _2892, _2894
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7877,
        _7880,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
        _5163,
        _5166,
        _5190,
        _5197,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7785
    from mastapy._private.system_model.connections_and_sockets.gears import _2541

    Self = TypeVar(
        "Self",
        bound="KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness",
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness._Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness",
    )


__docformat__ = "restructuredtext en"
__all__ = ("KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness:
    """Special nested class for casting KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness to subclasses."""

    __parent__: "KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness"

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5198.KlingelnbergCycloPalloidConicalGearMeshModalAnalysisAtAStiffness":
        return self.__parent__._cast(
            _5198.KlingelnbergCycloPalloidConicalGearMeshModalAnalysisAtAStiffness
        )

    @property
    def conical_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5163.ConicalGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5163,
        )

        return self.__parent__._cast(_5163.ConicalGearMeshModalAnalysisAtAStiffness)

    @property
    def gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5190.GearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5190,
        )

        return self.__parent__._cast(_5190.GearMeshModalAnalysisAtAStiffness)

    @property
    def inter_mountable_component_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5197.InterMountableComponentConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5197,
        )

        return self.__parent__._cast(
            _5197.InterMountableComponentConnectionModalAnalysisAtAStiffness
        )

    @property
    def connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5166.ConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5166,
        )

        return self.__parent__._cast(_5166.ConnectionModalAnalysisAtAStiffness)

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
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness":
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
class KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness(
    _5198.KlingelnbergCycloPalloidConicalGearMeshModalAnalysisAtAStiffness
):
    """KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH_MODAL_ANALYSIS_AT_A_STIFFNESS
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
    def connection_load_case(
        self: "Self",
    ) -> "_7785.KlingelnbergCycloPalloidSpiralBevelGearMeshLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.KlingelnbergCycloPalloidSpiralBevelGearMeshLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness
        """
        return (
            _Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness(
                self
            )
        )
