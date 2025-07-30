"""VirtualComponentLoadCase"""

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
from mastapy._private.system_model.analyses_and_results.static_loads import _7792

_VIRTUAL_COMPONENT_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads",
    "VirtualComponentLoadCase",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2892, _2894, _2898
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7703,
        _7787,
        _7788,
        _7796,
        _7806,
        _7807,
        _7849,
    )
    from mastapy._private.system_model.part_model import _2711

    Self = TypeVar("Self", bound="VirtualComponentLoadCase")
    CastSelf = TypeVar(
        "CastSelf", bound="VirtualComponentLoadCase._Cast_VirtualComponentLoadCase"
    )


__docformat__ = "restructuredtext en"
__all__ = ("VirtualComponentLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_VirtualComponentLoadCase:
    """Special nested class for casting VirtualComponentLoadCase to subclasses."""

    __parent__: "VirtualComponentLoadCase"

    @property
    def mountable_component_load_case(
        self: "CastSelf",
    ) -> "_7792.MountableComponentLoadCase":
        return self.__parent__._cast(_7792.MountableComponentLoadCase)

    @property
    def component_load_case(self: "CastSelf") -> "_7703.ComponentLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7703,
        )

        return self.__parent__._cast(_7703.ComponentLoadCase)

    @property
    def part_load_case(self: "CastSelf") -> "_7796.PartLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7796,
        )

        return self.__parent__._cast(_7796.PartLoadCase)

    @property
    def part_analysis(self: "CastSelf") -> "_2898.PartAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2898

        return self.__parent__._cast(_2898.PartAnalysis)

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
    def mass_disc_load_case(self: "CastSelf") -> "_7787.MassDiscLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7787,
        )

        return self.__parent__._cast(_7787.MassDiscLoadCase)

    @property
    def measurement_component_load_case(
        self: "CastSelf",
    ) -> "_7788.MeasurementComponentLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7788,
        )

        return self.__parent__._cast(_7788.MeasurementComponentLoadCase)

    @property
    def point_load_load_case(self: "CastSelf") -> "_7806.PointLoadLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7806,
        )

        return self.__parent__._cast(_7806.PointLoadLoadCase)

    @property
    def power_load_load_case(self: "CastSelf") -> "_7807.PowerLoadLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7807,
        )

        return self.__parent__._cast(_7807.PowerLoadLoadCase)

    @property
    def unbalanced_mass_load_case(self: "CastSelf") -> "_7849.UnbalancedMassLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7849,
        )

        return self.__parent__._cast(_7849.UnbalancedMassLoadCase)

    @property
    def virtual_component_load_case(self: "CastSelf") -> "VirtualComponentLoadCase":
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
class VirtualComponentLoadCase(_7792.MountableComponentLoadCase):
    """VirtualComponentLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _VIRTUAL_COMPONENT_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2711.VirtualComponent":
        """mastapy.system_model.part_model.VirtualComponent

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_VirtualComponentLoadCase":
        """Cast to another type.

        Returns:
            _Cast_VirtualComponentLoadCase
        """
        return _Cast_VirtualComponentLoadCase(self)
